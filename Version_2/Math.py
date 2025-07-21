import re
import os
import sys
from typing import Callable
from ICUReadFile import ICUReadFile
from ICUMapping import ICUMapping
from ICUNumberConverting import ConvertingNumber
from ICUHelper import read_number
from ICUConstant import REGEX_FOLDER, MAPPING_FOLDER, F_UNIT_MAPPING_BASE, F_UNIT_MAPPING_CURRENCY

class Math:
    """
    • ROMAN_NUMBER: chuyển La Mã → chữ
    • MEASUREMENT, MEASUREMENT_1: dùng unit_base_mapping, hỗ trợ range A–B unit và A unit
    • NORMAL_NUMBER: chuyển số thường
    • PLAIN_NUMBER: chuyển số thuần túy không có đơn vị
    """
    ROMAN_NUMBER   = 0
    MEASUREMENT    = 1
    MEASUREMENT_1  = 2
    NORMAL_NUMBER  = 3

    F_ROMAN_NUMBER  = "RomanNumber.txt"
    F_MEASUREMENT   = "Measurement.txt"
    F_MEASUREMENT_1 = "Measurement_1.txt"
    F_NORMAL_NUMBER = "NormalNumber.txt"

    def __init__(self):
        self.patterns = {}
        # mapping cho đơn vị đo cơ bản
        self.unit_base_mapping     = ICUMapping()
        self.unit_base_file        = os.path.join(MAPPING_FOLDER, F_UNIT_MAPPING_BASE)
        # (currency mapping vẫn tồn tại nhưng không dùng cho measurement)
        self.unit_currency_mapping = ICUMapping()
        self.unit_currency_file    = os.path.join(MAPPING_FOLDER, F_UNIT_MAPPING_CURRENCY)

        # Load mapping files ngay từ đầu
        self.unit_base_mapping.load_mapping_file(self.unit_base_file)
        self.unit_currency_mapping.load_mapping_file(self.unit_currency_file)

        # nạp regex từ file
        self._load_patterns(Math.ROMAN_NUMBER,   Math.F_ROMAN_NUMBER)
        self._load_patterns(Math.MEASUREMENT,    Math.F_MEASUREMENT)
        self._load_patterns(Math.MEASUREMENT_1,  Math.F_MEASUREMENT_1)
        self._load_patterns(Math.NORMAL_NUMBER,  Math.F_NORMAL_NUMBER)

    def _load_patterns(self, category: int, filename: str):
        path = os.path.join(REGEX_FOLDER, filename)
        reader = ICUReadFile(path)
        if not reader.read_file():
            print(f"[E] Error reading pattern file: {filename}", file=sys.stderr)
            return
        self.patterns.setdefault(category, [])
        pos = 0
        while pos < reader.get_file_length():
            reader.next_line(pos)
            line = reader.get_content_uchar()[reader.get_line_start():reader.get_line_end()].strip()
            if line:
                self.patterns[category].append(line)
            pos = reader.get_line_end()
    
    def _pattern_repl(self, category: str) -> Callable[[re.Match], str]:
        """
        Trả về hàm xử lý tương ứng cho từng nhóm pattern.
        Category có thể là: "Roman", "Measurement", "Measurement_1", "NormalNumber".
        """
        # Đảm bảo category luôn là chuỗi để có .lower()
        cat = str(category).lower()
        if cat == "roman":
            return lambda m: self._replace_roman_pattern(m)
        elif cat == "measurement":
            return lambda m: self._replace_measurement_pattern(m)
        elif cat == "measurement_1":
            return lambda m: self._replace_measurement1_pattern(m)
        elif cat == "normalnumber":
            return lambda m: self._replace_normalnumber_pattern(m)
        else:
            # Mặc định giữ nguyên
            return lambda m: m.group(0)

    def normalize_text(self, text: str) -> str:
        """
        0) Tiền tệ (grouped hoặc plain) + ký hiệu → đọc toàn bộ số
        1a) Range Aunit–Bunit cùng unit
        1b) Range [từ] A–Bunit
        2) Single measurement Nunit
        3) Roman numerals riêng lẻ (ALL-UPPER, không phải unit)
        4) Plain numbers (số thuần túy không có đơn vị)
        5) Dọn khoảng trắng
        """
        
        # Bảo vệ các chuỗi mã dạng LETTERS-NUMBERS hoặc LETTERS-NUMBERS-LETTERS
        protected = {}
        def protect_code(match: re.Match) -> str:
            code = match.group(0)
            placeholder = f"__PROTECTED_{len(protected)}__"
            protected[placeholder] = code
            return placeholder
        
        # Regex bảo vệ các mã như BCH-02273, ACV-083983, TAF-085743-YXN, ORD-090624-XYZ
        code_rx = re.compile(r'\b[A-Za-z]+-\d+(?:-[A-Za-z]+)?\b')
        text = code_rx.sub(protect_code, text)
        
        conv = ConvertingNumber()
        result = text

        # --- 0a) Money: nhóm hàng nghìn bằng , + symbol --- 
        currency_rx = re.compile(
            r'\b(\d{1,3}(?:[.,]\d{3})+)\s*([$€£₫¥₽₩đ])(?=\s|$|[^\w])'
        )
        def _rep_grouped(m: re.Match) -> str:
            raw, sym = m.group(1), m.group(2)
            num = raw.replace(',', '').replace('.', '')
            num_txt = conv.convert_number(num)
            unit_txt = self.unit_currency_mapping.mapping_of(sym)
            if not unit_txt:
                unit_txt = sym
            return f"{num_txt} {unit_txt}"
        result = currency_rx.sub(_rep_grouped, result)

        plain_currency_rx = re.compile(r'\b(\d+)(?:[,.](\d+))?\s*([$€£₫¥₽₩đ])(?=\s|$|[^\w])')
        def _rep_plain(m: re.Match) -> str:
            integer_part, decimal_part, sym = m.group(1), m.group(2), m.group(3)
            num_txt = conv.convert_number(integer_part)
            if decimal_part:
                dec_txt = " phẩy " + " ".join(conv.convert_number(d) for d in decimal_part)
                num_txt += dec_txt
            unit_txt = self.unit_currency_mapping.mapping_of(sym)
            if not unit_txt:
                unit_txt = sym
            return f"{num_txt} {unit_txt}"
        result = plain_currency_rx.sub(_rep_plain, result)

        # # Số thập phân (1.5, 2.75, etc.)
        # rx_decimal = re.compile(r'\b(\d+)[\.,](\d+)\b')
        # def _rep_decimal(m: re.Match) -> str:
        #     integer_part = m.group(1)
        #     decimal_part = m.group(2)
        #     int_txt = conv.convert_number(integer_part)
        #     dec_txt = conv.convert_number(decimal_part)
        #     return f"{int_txt} phẩy {dec_txt}"
        # result = rx_decimal.sub(_rep_decimal, result)

        # --- 1a) Range cả hai cùng unit: "3km2-6km2" ---
        rx_range_both = re.compile(
            r'\b(\d+)\s*([A-Za-zÀ-ỹ]+[23]?)\s*-\s*(\d+)\s*\2\b',
            re.IGNORECASE
        )
        def _rep_range_both(m: re.Match) -> str:
            a, unit, b = m.group(1), m.group(2).lower(), m.group(3)
            txt_a = conv.convert_number(a)
            txt_b = conv.convert_number(b)
            u_txt = self.unit_base_mapping.mapping_of(unit)
            return f"{txt_a} {u_txt} đến {txt_b} {u_txt}"
        result = rx_range_both.sub(_rep_range_both, result)

        # --- 1b) Range chỉ unit sau: "[từ ]A-Bunit" ---
        rx_range_single = re.compile(
            r'\b(?:từ\s*)?(\d+)\s*-\s*(\d+)\s*([A-Za-zÀ-ỹ]+[23]?)\b',
            re.IGNORECASE
        )
        def _rep_range_single(m: re.Match) -> str:
            a, b, unit = m.group(1), m.group(2), m.group(3).lower()
            txt_a = conv.convert_number(a)
            txt_b = conv.convert_number(b)
            u_txt = self.unit_base_mapping.mapping_of(unit)
            return f"{txt_a} {txt_b} {u_txt}"
        result = rx_range_single.sub(_rep_range_single, result)
        
        # --- 1.5) Decimal measurement: "2.5kg", "3.7cm" ---
        rx_decimal_measure = re.compile(r'\b(\d+)\.(\d+)\s*([A-Za-zÀ-ỹ]+[23]?)\b', re.IGNORECASE)
        def _rep_decimal_measure(m: re.Match) -> str:
            integer_part = m.group(1)
            decimal_part = m.group(2)
            unit = m.group(3).lower()
            
            int_txt = conv.convert_number(integer_part)
            dec_txt = conv.convert_number(decimal_part)
            u_txt = self.unit_base_mapping.mapping_of(unit)
            
            if u_txt:
                return f"{int_txt} phẩy {dec_txt} {u_txt}"
            return m.group(0)
        result = rx_decimal_measure.sub(_rep_decimal_measure, result)
        
        # --- 2) Single measurement: "2dm", "3km2", "5km3" ---
        rx_single = re.compile(r'\b(\d+)\s*([A-Za-zÀ-ỹ]+[23]?)\b', re.IGNORECASE)
        def _rep_single(m: re.Match) -> str:
            num, unit = m.group(1), m.group(2).lower()
            u_txt = self.unit_base_mapping.mapping_of(unit)
            if u_txt:
                return f"{conv.convert_number(num)} {u_txt}"
            return m.group(0)
        result = rx_single.sub(_rep_single, result)

        # --- 3) Roman numerals riêng lẻ (ALL-UPPER, không phải unit) ---
        rx_roman = re.compile(r'\b([IVXLCDM]{1,7})\b')
        def _rep_roman(m: re.Match) -> str:
            tok = m.group(1)
            if tok == tok.upper() and not self.unit_base_mapping.has_mapping_of(tok.lower()):
                dec = conv.roman_to_decimal(tok)
                if dec.isdigit():
                    return conv.convert_number(dec)
            return tok
        result = rx_roman.sub(_rep_roman, result)

        # --- 4) Plain numbers với dấu phẩy phân cách hàng nghìn ---
        rx_grouped_plain = re.compile(r'\b(\d{1,3}(?:,\d{3})+)\b')
        def _rep_grouped_plain(m: re.Match) -> str:
            raw = m.group(1)
            # Chỉ loại bỏ dấu phẩy (không phải dấu chấm)
            num = raw.replace(',', '')
            return conv.convert_number(num)
        result = rx_grouped_plain.sub(_rep_grouped_plain, result)
        
        # --- 5) Plain numbers (số thuần túy không có đơn vị, không có dấu phẩy) ---
        rx_plain = re.compile(r'\b(\d+)\b')
        def _rep_plain_number(m: re.Match) -> str:
            num = m.group(1)
            return conv.convert_number(num)
        result = rx_plain.sub(_rep_plain_number, result)
        
        # --- 6) Khôi phục các chuỗi mã đã bảo vệ ---
        def restore_code(match: re.Match) -> str:
            placeholder = match.group(0)
            return protected.get(placeholder, placeholder)
        
        result = re.sub(r'__PROTECTED_\d+__', restore_code, result)
        
        # --- 7) Dọn khoảng trắng thừa ---
        result = re.sub(r'\s+', ' ', result).strip()

        return result

    def _string_for_replace(self, category: int, m: re.Match, pattern_idx: int) -> str:
        if category == Math.ROMAN_NUMBER:
            return self._regex_roman_number(m.group(0))
        elif category in (Math.MEASUREMENT, Math.MEASUREMENT_1):
            # cả hai category đều dùng unit_base_mapping
            return self._local_handle_measurement(m, pattern_idx)
        elif category == Math.NORMAL_NUMBER:
            return self._regex_normal_number(m, pattern_idx)
        else:
            return ""

    def _regex_roman_number(self, s: str) -> str:
        """
        Thay thế các token La Mã (I, IV, X,…) thành số chữ tiếng Việt,
        nhưng chỉ khi toàn bộ token là La Mã hợp lệ.
        Ví dụ: “IV” → 4 → “bốn”; “LG” sẽ không match và giữ nguyên.
        """
        conv = ConvertingNumber()
        # Regex chỉ match những token nguyên khối hoàn toàn là La Mã, 1–7 ký tự
        roman_prog = re.compile(r'\b(?P<R>[IVXLCDM]{1,7})\b', re.IGNORECASE)
        def _to_word(m: re.Match) -> str:
            tok = m.group('R')
            # Kiểm tra token có hoàn toàn là La Mã (fullmatch)
            if not re.fullmatch(r'[IVXLCDM]+', tok, re.IGNORECASE):
                return tok
            # Chuyển La Mã sang số
            dec = conv.roman_to_decimal(tok)
            # Nếu output không phải digits (chuyển thất bại), trả về nguyên token
            if not str(dec).isdigit():
                return tok
            # Cuối cùng chuyển số thập phân thành chữ tiếng Việt
            return conv.convert_number(dec)
        return roman_prog.sub(_to_word, s)

    def _regex_normal_number(self, m: re.Match, pattern_idx: int) -> str:
        """
        Đọc số thường; nếu group(1) là '-' thì thêm tiền tố 'trừ '.
        pattern_idx quyết định phần thập phân (point).
        """
        whole = m.group(0)
        sign = ""
        if m.groups() and m.group(1).strip() == "-":
            sign = "đến "
        point = 0 if pattern_idx in (0, 2) else 1
        return sign + read_number(whole, point)

    def _local_handle_measurement(self, m: re.Match, pattern_idx: int) -> str:
        """
        Xử lý đo lường với unit_base_mapping:
        1) Range "A-B unit" → "A đến B đơn vị"
        2) Single "Aunit" hoặc "A unit" → "A đơn vị"
        2bis) Plain number "12345" → đọc nguyên (một hai ba bốn năm)
        """
        text = m.group(0).strip()
        conv = ConvertingNumber()

        # 1) Range: "3-5 cm" hoặc "3-5cm"
        rng = re.match(r"^(\d+)-(\d+)\s*([A-Za-z]+)$", text)
        if rng:
            a, b, unit = rng.groups()
            a_txt = conv.convert_number(a)
            b_txt = conv.convert_number(b)
            if not self.unit_base_mapping.has_mapping_of(unit):
                return ""
            u_txt = self.unit_base_mapping.mapping_of(unit)
            return f"{a_txt} đến {b_txt} {u_txt}"

        # 2) Single: "10km" hoặc "10 km"
        single = re.match(r"^(\d+)(?:[,.](\d+))?([A-Za-z€]+)$", text)
        if single:
            print("DEBUG: single check")
            integer_part, decimal_part, unit = single.groups()
            # Chuyển phần nguyên thành chữ
            num_txt = self.conv.convert_number(integer_part)
            # Xử lý phần thập phân nếu có
            if decimal_part:
                decimal_txt = " phẩy " + " ".join(self.conv.convert_number(d) for d in decimal_part)
                num_txt += decimal_txt
            # Kiểm tra và lấy đơn vị
            if not self.unit_base_mapping.has_mapping_of(unit):
                return ""
            u_txt = self.unit_base_mapping.mapping_of(unit)
            return f"{num_txt} {u_txt}"

        # 2bis) Plain number: "45000", "1234567" → đọc nguyên
        plain = re.match(r"^(\d+)$", text)
        if plain:
            return conv.convert_number(plain.group(1))

        # 3) Không khớp → giữ nguyên (trả về chuỗi rỗng để pipeline tiếp tục)
        return ""
    
