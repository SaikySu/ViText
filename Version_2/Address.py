import os
import re
import sys
# import logging

from ICUConstant import REGEX_FOLDER, MAPPING_FOLDER, DICT_FOLDER, F_LETTER_SOUND_EN, F_LETTER_SOUND_VN, F_SYMBOL, F_POPULAR
from ICUReadFile import ICUReadFile
from ICUMapping import ICUMapping
from ICUDictionary import ICUDictionary
from ICUNumberConverting import ConvertingNumber

# Thiết lập logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Address:
    POLITICAL_DIVISION = 0
    STREET = 1
    OFFICE = 2
    CODENUMBER = 3

    F_POLITICAL_DIVISION = "PoliticalDivision.txt"
    F_STREET = "Street.txt"
    F_OFFICE = "Office.txt"
    F_CODENUMBER = "Codenumber.txt"

    def __init__(self):
        self.patterns = {}
        self.popular = ICUDictionary()
        # Load popular.txt một lần trong __init__
        # logging.debug(f"Loading popular dictionary from {os.path.join(DICT_FOLDER, F_POPULAR)}")
        if not os.path.exists(os.path.join(DICT_FOLDER, F_POPULAR)):
            # logging.error(f"Popular dictionary file not found: {os.path.join(DICT_FOLDER, F_POPULAR)}")
            print(f"INFO: Erro load {os.path.join(DICT_FOLDER, F_POPULAR)}")
        self.popular.load_dict_file(os.path.join(DICT_FOLDER, F_POPULAR))
        self._load_patterns(Address.POLITICAL_DIVISION, Address.F_POLITICAL_DIVISION)
        self._load_patterns(Address.STREET, Address.F_STREET)
        self._load_patterns(Address.OFFICE, Address.F_OFFICE)
        self._load_patterns(Address.CODENUMBER, Address.F_CODENUMBER)

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

    def normalize_text(self, text: str) -> str:
        result = text
        for category, regex_list in self.patterns.items():
            for pattern in regex_list:
                prog = re.compile(pattern)
                def _repl(m: re.Match) -> str:
                    full = m.group(0)
                    if category == Address.CODENUMBER and not re.search(r'\d', full):
                        return full
                    return " " + self._string_for_replace(category, m) + " "
                result = prog.sub(_repl, result)
        return result

    def _string_for_replace(self, category: int, match: re.Match) -> str:
        if category == Address.POLITICAL_DIVISION:
            return self._regex_political_division(match)
        elif category == Address.STREET:
            return self._regex_street(match)
        elif category == Address.OFFICE:
            return self._regex_office(match)
        elif category == Address.CODENUMBER:
            return self._regex_codenumber(match)
        else:
            print(f"[E] Invalid category: {category}", file=sys.stderr)
            return ""

    def _regex_political_division(self, match: re.Match) -> str:
        full = match.group(0)
        prefix = match.group(1).lower()
        mapping = {
            "kp": "khu phố", "q": "quận", "p": "phường",
            "h": "huyện", "tx": "thị xã", "tp": "thành phố", "x": "xã"
        }
        exp = mapping.get(prefix)
        if not exp:
            print(f"[E] Invalid prefix to expand: {prefix}", file=sys.stderr)
            return full
        exp += " "
        idx = full.find('.')
        if idx != -1:
            return exp + full[idx+1:]
        else:
            return exp + full[len(prefix):]

    def _regex_street(self, match: re.Match) -> str:
        full = match.group(0)
        prefix = match.group(1)
        main = full[len(prefix):]
        parts = []
        conv = ConvertingNumber()
        letter_sound = ICUMapping()
        letter_sound.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_VN))
        continuous = False
        number = ""
        for c in main:
            if '0' <= c <= '9':
                if continuous:
                    number += c
                else:
                    if c == '0':
                        parts.append("không ")
                        number = ""
                        continuous = False
                    else:
                        number = c
                        continuous = True
            elif c == '/':
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append("xuyệt ")
            elif c == '-':
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append(", ")
            else:
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append(letter_sound.mapping_of(c) + " ")
        if continuous and number:
            parts.append(conv.convert_number(number))
        return prefix + " " + "".join(parts)

    def _regex_office(self, match: re.Match) -> str:
        full = match.group(0)
        prefix = match.group(1)
        main = full[len(prefix):]
        parts = []
        conv = ConvertingNumber()
        letter_sound = ICUMapping()
        letter_sound.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_VN))
        continuous = False
        number = ""
        for c in main:
            if '0' <= c <= '9':
                if continuous:
                    number += c
                else:
                    if c == '0':
                        parts.append("không ")
                        number = ""
                        continuous = False
                    else:
                        number = c
                        continuous = True
            elif c == '/':
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append(" ")
            elif c == '-':
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append(", ")
            else:
                if continuous:
                    parts.append(conv.convert_number(number) + " ")
                    number = ""
                    continuous = False
                parts.append(letter_sound.mapping_of(c) + " ")
        if continuous and number:
            parts.append(conv.convert_number(number))
        return prefix + " " + "".join(parts)

    def _regex_codenumber(self, match: re.Match) -> str:
        full = match.group(0)
        conv = ConvertingNumber()
        letter_vn = ICUMapping()
        letter_vn.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_VN))
        letter_vn.load_mapping_file(os.path.join(MAPPING_FOLDER, F_SYMBOL))
        letter_en = ICUMapping()
        letter_en.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_EN))

        # 1) Xử lý trường hợp chữ + số có dấu "-" hoặc không
        pm = re.match(r'^([A-Za-z]+)-?(\d+)$', full)
        if pm:
            prefix, numpart = pm.group(1), pm.group(2)
            if self.popular.has_word(prefix.lower()):
                result = prefix + ' '
            else:
                if prefix.isupper():
                    result = ''
                    for c in prefix:
                        if letter_vn.has_mapping_of(c.lower()):
                            result += letter_en.mapping_of(c.lower()) + ' '
                        else:
                            result += c + ' '
                else:
                    result = prefix + ' '
            # Xử lý số
            if len(numpart) <= 3:
                result += conv.convert_number(numpart)
            else:
                # Đọc từng chữ số nếu số dài hơn 3 chữ số hoặc bắt đầu bằng '0'
                for d in numpart:
                    result += conv.convert_number(d) + ' '
            return result.strip()

        # 2) Xử lý trường hợp chữ + số + chữ có dấu "-" hoặc không (ABC4-6362G2-XMZ)
        pm2 = re.match(r'^([A-Za-z]+)-(\d+)-([A-Za-z]+)$', full)
        if pm2:
            prefix, numpart, suffix = pm2.groups()
            parts = []
            # Đọc prefix
            for c in prefix:
                parts.append(letter_en.mapping_of(c.lower()))
            # Đọc từng chữ số của numpart
            for d in numpart:
                parts.append(conv.convert_number(d))
            # Đọc suffix
            for c in suffix:
                parts.append(letter_vn.mapping_of(c.lower()))
            return ' '.join(parts)

        # 3) Các trường hợp còn lại
        result = ''
        number = ''
        pop = ''
        continuous_digits = False
        continuous_pop = False

        for c in full:
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
                if continuous_pop:
                    continuous_pop = False
                    if self.popular.has_word(pop):
                        result += pop + ' '
                    else:
                        for ch in pop:
                            result += letter_en.mapping_of(ch) + ' '
                    pop = ''
            elif c == '/':
                if continuous_digits:
                    result += conv.convert_number(number) + ' '
                    number = ''
                    continuous_digits = False
                if continuous_pop:
                    continuous_pop = False
                    if self.popular.has_word(pop):
                        result += pop + ' '
                    else:
                        for ch in pop:
                            result += letter_en.mapping_of(ch) + ' '
                    pop = ''
                result += 'xuyệt '
            elif letter_vn.has_mapping_of(c.lower()):
                if continuous_digits:
                    result += conv.convert_number(number) + ' '
                    number = ''
                    continuous_digits = False
                if continuous_pop:
                    pop += c
                else:
                    pop = c
                    continuous_pop = True
            elif c == '.':
                if continuous_digits:
                    result += conv.convert_number(number) + ' '
                    number = ''
                    continuous_digits = False
                if continuous_pop:
                    continuous_pop = False
                    if self.popular.has_word(pop):
                        result += pop + ' '
                    else:
                        for ch in pop: #
                            result += letter_vn.mapping_of(ch) + ' '
                    pop = ''
                result += 'chấm '
            elif c == '-':
                if continuous_digits:
                    result += conv.convert_number(number) + ' '
                    number = ''
                    continuous_digits = False
                if continuous_pop:
                    continuous_pop = False
                    if self.popular.has_word(pop):
                        result += pop + ' '
                    else:
                        for ch in pop:
                            # Đọc phiên âm EN sau "-"
                            result += letter_en.mapping_of(ch) + ' '
                    pop = ''
                result += ' '
            else:
                if continuous_digits:
                    result += conv.convert_number(number) + ' '
                    number = ''
                    continuous_digits = False
                if continuous_pop:
                    continuous_pop = False
                    if self.popular.has_word(pop):
                        result += pop + ' '
                    else:   
                        for ch in pop:
                            result += letter_vn.mapping_of(ch) + ' '
                    pop = ''
                result += letter_vn.mapping_of(c) + ' '

        # Flush cuối
        if continuous_digits and number:
            result += conv.convert_number(number) + ' '
        if continuous_pop and pop:
            for ch in pop:
                result += letter_vn.mapping_of(ch) + ' '
        return result.strip()
    
# Tiếng việt mới đọc "/" thành "xuyệt" và đọc tên kí tự