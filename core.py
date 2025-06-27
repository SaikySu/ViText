import os
import re
from .utils import (
    number2words, year2words, replace_full_date,
    replace_word_number, spell_unknown, is_vietnamese_word,
    load_multi_dict_from_folder, replace_number_unit,
    protect_patterns, unprotect_patterns, replace_number_unit_regex, 
    remove_thousand_sep, number2words, SPELL_MAP
)

VNORM_UNITS = {"m", "cm", "dm", "nm", "mm", "mg", "kg", "g", "ml", "dl", "cl"}

def is_code_token(token):
    # Nhận diện token là mã code: phải có số và chữ, không chứa dấu cách, có thể có ký tự đặc biệt nhưng không chứa khoảng trắng
    return bool(re.match(r"(?i)(\b|^)[^\s]*\d[^\s]*\b", token))

class Vinorm:
    def __init__(self, dict_dir=None):
        if dict_dir is None:
            dict_dir = os.path.join(os.path.dirname(__file__), "dicts")
        self.special_dict = load_multi_dict_from_folder(dict_dir)
        self.unit_dict = {}
        self.abbr_dict = {}
        for key, val in self.special_dict.items():
            if len(key) <= 3:
                self.unit_dict[key] = val
            else:
                self.abbr_dict[key] = val

    def _replace_special(self, text):
        for key, val in self.unit_dict.items():
            text = re.sub(rf"(?<=\d)\s*{re.escape(key)}\b", f" {val}", text)
        for key, val in self.abbr_dict.items():
            text = re.sub(rf"\b{re.escape(key)}\b", val, text)
        return text

    def _replace_number(self, text):
        def repl(m):
            num = int(m.group(0))
            return number2words(num)
        return re.sub(r"(?<![\w%])\d+(?![\w%])", repl, text)

    def _replace_float_number(self, text):
        # Xử lý số thực dạng 3.14, 123.456 (không dính chữ, không dính số phía sau)
        def repl(m):
            int_part, dec_part = m.group(1), m.group(2)
            int_words = number2words(int(int_part))
            dec_words = " ".join([number2words(int(d)) for d in dec_part])
            return f"{int_words} phẩy {dec_words}"
        # Sửa regex cho nhận diện đúng mọi TH: đầu, giữa, cuối câu
        return re.sub(r'(?<!\d)(\d+)\.(\d+)(?!\d|\w)', repl, text)

    def normalize(self, text, lower=False, unknown=False, punc=True, rule=False):
        # Email, phone, web: Trả về nguyên token đặc biệt (không chuyển đổi).
        text, emails, phones, webs = protect_patterns(text)
        # Loại bỏ dấu ",", "." trong số
        text = remove_thousand_sep(text)
        # Xử lý số thực
        text = self._replace_float_number(text)   
        # Loại bỏ dấu ngoặc đơn 
        text = text.replace("(", "").replace(")", "")
        # Xử lý ngày tháng
        text = replace_full_date(text)
        # Chuyển số dạng chữ (one, two, three...)
        text = replace_word_number(text)
        # Xử lý các cặp số + đơn vị bằng regex
        text = replace_number_unit_regex(text, self.unit_dict)
        # Xử lý các cặp số + đơn vị bằng dict
        text = replace_number_unit(text, self.special_dict)
        # Chuyển đổi số
        text = self._replace_number(text)
        # Xử lý các trường hợp đặc biệt
        text = self._replace_special(text)

        # Tokenization, tách chuỗi thành các token đặc biệt (email, phone, web), Từ tiếng Việt, Số + ký tự (như 1m, 100$...), Dấu câu, ký tự lẻ.
        tokens = re.findall(
            r'__\w+__\d+|[a-zA-ZÀ-ỹà-ỹĐđ]+|\d+%|\d+\w+|\w+|[^\w\s]',
            text,
            re.UNICODE
        )
        
        def token_proc(w):  
 
            # Nếu có nhận được là "emai", "Phone", "Web" thì trả về giữ nguyên và đánh vần theo từng chữ
            if w.startswith("__EMAIL__") or w.startswith("__PHONE__") or w.startswith("__WEB__"):
                return w
            
            # Nếu trong VNORM_UNITS thì đánh vần
            if w in VNORM_UNITS:
                return spell_unknown(w)
                
            # Nếu token có cả số và chữ liền nhau → đánh vần từng ký tự (KHÔNG tra unit_dict)
            if any(c.isdigit() for c in w) and any(c.isalpha() for c in w):
                return " ".join([SPELL_MAP.get(c.lower(), c.lower()) for c in w if c.isalnum()])

            # Nếu là dãy số
            if w.isdigit():
                return " ".join([SPELL_MAP.get(c, c) for c in w])

            # Xử lý ký tự đơn lẻ là chữ cái: chỉ đánh vần, KHÔNG tra unit_dict, KHÔNG tra abbr_dict
            if len(w) == 1 and w.isalpha():
                return spell_unknown(w)

            # Xử lý các ký tự in hoa toàn bộ (vd: VTV, LG)
            if all(c.isalnum() for c in w) and w.isupper():
                return " ".join([SPELL_MAP.get(c.lower(), c.lower()) for c in w])

            # KIỂM TRA XEM TỪ ĐÃ ĐƯỢC NORMALIZE CHƯA (đã có trong values của dict)
            # Nếu từ này đã là kết quả của quá trình normalize trước đó thì giữ nguyên
            if w in self.unit_dict.values() or w in self.abbr_dict.values() or w in self.special_dict.values():
                return w

            if w in self.special_dict:
                return self.special_dict[w]
    
            if w in self.abbr_dict:
                return self.abbr_dict[w]

            if w in self.unit_dict:
                return self.unit_dict[w]

            if w.isupper() and len(w) <= 4:
                return spell_unknown(w)

            if w.endswith('%') and w[:-1].isdigit():
                return number2words(int(w[:-1])) + " phần trăm"

            if w.isalpha():
                if is_vietnamese_word(w, self.abbr_dict, self.unit_dict):
                    return w
                else:
                    return spell_unknown(w)

            # Loại bỏ các ký tự không cần thiết
            if w in {"(", ")", "-", "_"}:
                return ""

            # Giữ dấu câu hợp lệ
            if w in {",", ".", ";", ":", "...", "?", "!", "'", '"'}:
                return w

            return spell_unknown(w)

        # Ghép lại các chuỗi đã xử lý
        output = [token_proc(w) for w in tokens]

        text = ""
        for i, token in enumerate(output):
            if not token:
                continue
            if i > 0 and token not in {",", ".", ";", ":", "...", "?", "!", "'", '"'}:
                text += " "
            text += token

        if lower:
            text = text.lower()
        text = unprotect_patterns(text, emails, phones, webs)
        return text.strip()