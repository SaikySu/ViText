import re
import os
import chardet

# ======= PATTERNS BẢO VỆ =======
EMAIL_REGEX = r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
WEBSITE_REGEX = r"(?i)\b((https?:\/\/|ftp:\/\/|sftp:\/\/|www\.)[^\s,]+)"
SDT_REGEXES = [
    r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{1,3}[-\s.]?\d{3}[-\s.]?\d{4}\b",
    r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{2,3}[-\s.]?\d{2}[- .]?\d{2}[- .]?\d{2}\b",
    r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{1,3}[-\s.]?\d{1,2}[-\s.]?\d{2,3}[-\s.]?\d{3}\b",
    r"\b1[89]00[\s\.]?[\d\s\.]{4,8}\b"
]

# ===== PHIÊN ÂM (SPELL) EMAIL, WEB, PHONE =====
SPELL_MAP = {
    'a': 'ai', 'b': 'bê', 'c': 'xê', 'd': 'dê', 'e': 'e', 'f': 'ép', 'g': 'giy', 'h': 'hát', 'i': 'i',
    'j': 'giây', 'k': 'ca', 'l': 'eo', 'm': 'em', 'n': 'en', 'o': 'o', 'p': 'pê', 'q': 'quy', 'r': 'rờ',
    's': 'ét', 't': 'ti', 'u': 'u', 'v': 'vê', 'w': 'đắp liu', 'x': 'ích', 'y': 'i', 'z': 'giét',
    'A': 'ai', 'B': 'bê', 'C': 'xê', 'D': 'dê', 'E': 'e', 'F': 'ép', 'G': 'giy', 'H': 'hát', 'I': 'i',
    'J': 'giây', 'K': 'ca', 'L': 'eo', 'M': 'em', 'N': 'en', 'O': 'o', 'P': 'pê', 'Q': 'quy', 'R': 'rờ',
    'S': 'ét', 'T': 'ti', 'U': 'u', 'V': 'vê', 'W': 'đắp liu', 'X': 'ích', 'Y': 'i', 'Z': 'giét',
    '0': 'không', '1': 'một', '2': 'hai', '3': 'ba', '4': 'bốn', '5': 'năm', '6': 'sáu', '7': 'bảy', '8': 'tám', '9': 'chín',
    '.': 'chấm', ',': 'phẩy', '@': 'a còng', '-': 'gạch', '_': 'gạch', '/': 'xẹt', ':': 'hai chấm', '+': 'cộng'
}

# ====== PATTERN SỐ + ĐƠN VỊ ======
NUMBER_UNIT_PATTERNS = [
    r"(?i)(?:\b|^)(\d+(?:\.\d{3})+(?:,\d+)?)[ ]?(\%|\$|\฿|\₱|\₭|\₩|\¥|\€|\£|\Ω)(?=\s|-|$|[.,;:])",
    r"(?i)(?:\b|^)(\d+(?:,\d{3})+(?:\.\d+)?)[ ]?(\%|\$|\฿|\₱|\₭|\₩|\¥|\€|\£|\Ω)(?=\s|-|$|[.,;:])",
    r"(?i)(?:\b|^)(\d+(?:,\d+))[ ]?(\%|\$|\฿|\₱|\₭|\₩|\¥|\€|\£|\Ω)(?=\s|-|$|[.,;:])",
    r"(?i)(?:\b|^)(\d+(?:\.\d+)?)[ ]?(\%|\$|\฿|\₱|\₭|\₩|\¥|\€|\£|\Ω)(?=\s|-|$|[.,;:])"
]

# ===== ĐƠN VỊ KÝ HIỆU (dùng cho số + ký hiệu) =====
UNIT_MAP = {
    "₫": "đồng",
    "%": "phần trăm",
    "$": "đô la",
    "€": "ê rô",
    "£": "bảng anh",
    "¥": "yên",
    "₩": "uôn",
    "₭": "kíp",
    "₱": "pê sô",
    "฿": "bạt",
    "Ω": "ôm"
}

# Bảo vệ các token đặc biệt như email, sdt và web
def protect_patterns(text):
    def mask(pattern, text, mask_str):
        found = []
        def repl(m):
            found.append(m.group(0))
            return f" {mask_str}{len(found)-1} "
        text = re.sub(pattern, repl, text)
        return text, found
    text, emails = mask(EMAIL_REGEX, text, "__EMAIL__")
    phones = []
    for phone_pat in SDT_REGEXES:
        text, found_phones = mask(phone_pat, text, "__PHONE__")
        phones.extend(found_phones)
    text, webs = mask(WEBSITE_REGEX, text, "__WEB__")
    return text, emails, phones, webs


def number_unit2words(number_str, unit, unit_dict=None):
    number_str = number_str.replace(" ", "")
    # Châu Âu: 1.000.000,50 => 1000000.50
    if "." in number_str and "," in number_str:
        number_str = number_str.replace(".", "").replace(",", ".")
    elif "," in number_str and "." in number_str:
        if number_str.find(",") < number_str.find("."):
            number_str = number_str.replace(",", "")
        else:
            number_str = number_str.replace(".", "").replace(",", ".")
    elif "." in number_str:
        if number_str.count(".") == 1 and len(number_str.split(".")[1]) <= 2:
            pass
        else:
            number_str = number_str.replace(".", "")
    elif "," in number_str:
        if number_str.count(",") == 1 and len(number_str.split(",")[1]) <= 2:
            number_str = number_str.replace(",", ".")
        else:
            number_str = number_str.replace(",", "")
    try:
        if "." in number_str:
            n, decimal_part = number_str.split(".")
            n_words = number2words(int(n))
            decimal_words = " ".join([number2words(int(ch)) for ch in decimal_part])
            res = f"{n_words} phẩy {decimal_words}"
        else:
            res = number2words(int(number_str))
    except Exception as e:
        res = number_str
    # Ưu tiên lấy từ unit_dict nếu có, nếu không thì mới đến UNIT_MAP
    if unit_dict:
        unit_txt = unit_dict.get(unit, UNIT_MAP.get(unit, unit))
    else:
        unit_txt = UNIT_MAP.get(unit, unit)
    return f"{res} {unit_txt}"

def remove_thousand_sep(text):
    """
    Tìm tất cả số có >=2 dấu chấm hoặc phẩy liên tiếp,
    bỏ hết dấu '.' hoặc ',' trong số đó (giữ nguyên các phần khác).
    """
    def repl(match):
        s = match.group(0)
        s_norm = s.replace(".", "").replace(",", "")
        return s_norm

    # Số có 2 dấu chấm hoặc 2 dấu phẩy hoặc trộn cả hai, ví dụ: 1.234.567 hoặc 1,234,567 hoặc 1,234.567
    pattern = r'\d{1,3}([.,]\d{3}){2,}'

    return re.sub(pattern, repl, text)

def replace_number_unit_regex(text, unit_dict=None):

    # Ưu tiên bắt số thập phân kèm đơn vị
    text = re.sub(
        r"(?<!\w)(\d+)[,.](\d+)\s*([a-zA-Z₫đ%$€£¥₩₭₱฿Ω]{1,4}|\₫)",
        lambda m: number_unit2words(f"{m.group(1)}.{m.group(2)}", m.group(3), unit_dict),
        text
    )

    # Sau đó xử lý số lớn có dấu phẩy hoặc dấu chấm nhiều lần (hàng nghìn)
    text = re.sub(
        r'\d{1,3}([.,]\d{3}){2,}',
        lambda m: m.group(0).replace('.', '').replace(',', ''),
        text
    )

    # Các pattern số nguyên + đơn vị
    text = re.sub(
        r"(?<!\w)(\d+)\s*([A-Za-zÀ-ỹà-ỹĐđ%$€£¥₩₭₱฿Ω]{1,10}|\₫)",
        lambda m: number_unit2words(m.group(1), m.group(2), unit_dict),
        text
    )
    return text

def spell_text(text):
    return " ".join([SPELL_MAP.get(c, c) for c in text])

def spell_email(email):
    return spell_text(email)

def spell_phone(phone):
    phone = phone.replace(" ", "").replace("-", "").replace("_", "")
    return " ".join([SPELL_MAP.get(c, c) for c in phone if c in SPELL_MAP])

def spell_web(web):
    web = re.sub(r'^(https?|ftp|sftp):\/\/', '', web, flags=re.I)
    return spell_text(web)

def unprotect_patterns(text, emails, phones, webs):
    for i, email in enumerate(emails):
        spoken = spell_email(email)
        text = text.replace(f"__EMAIL__{i}", f"{spoken}")
    for i, phone in enumerate(phones):
        spoken = spell_phone(phone)
        text = text.replace(f"__PHONE__{i}", f"{spoken}")
    for i, web in enumerate(webs):
        spoken = spell_web(web)
        text = text.replace(f"__WEB__{i}", f"{spoken}")
    return text

# ===== XỬ LÝ SỐ =====
def number2words(num):
    mapping = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    units = ["", " nghìn", " triệu", " tỉ", " nghìn tỉ"]

    if num == 0:
        return mapping[0]

    # Chia số thành các nhóm 3 chữ số từ phải sang trái
    groups = []
    while num > 0:
        groups.insert(0, num % 1000)
        num //= 1000

    n_groups = len(groups)
    result = []

    for idx, n in enumerate(groups):
        if n == 0:
            continue
        
        unit = units[n_groups - idx - 1]
        s = ""

        tram = n // 100
        chuc = (n % 100) // 10
        donvi = n % 10

        is_first_group = (idx == 0)

        if is_first_group:
            # Nhóm đầu tiên (bên trái nhất)
            if tram > 0:
                s += mapping[tram] + " trăm"
            if chuc > 1:
                if s: s += " "
                s += mapping[chuc] + " mươi"
                if donvi == 1:
                    s += " mốt"
                elif donvi == 5:
                    s += " lăm"
                elif donvi > 0:
                    s += " " + mapping[donvi]
            elif chuc == 1:
                if s: s += " "
                s += "mười"
                if donvi == 1:
                    s += " một"
                elif donvi == 5:
                    s += " lăm"
                elif donvi > 0:
                    s += " " + mapping[donvi]
            elif chuc == 0:
                if donvi > 0:
                    if tram != 0:
                        s += " linh " + mapping[donvi]
                    else:
                        s += mapping[donvi]
        else:
            # Các nhóm sau: luôn đủ ba chữ số
            if tram > 0:
                s += mapping[tram] + " trăm"
            else:
                s += "không trăm"
            if chuc > 1:
                s += " " + mapping[chuc] + " mươi"
                if donvi == 1:
                    s += " mốt"
                elif donvi == 5:
                    s += " lăm"
                elif donvi > 0:
                    s += " " + mapping[donvi]
            elif chuc == 1:
                s += " mười"
                if donvi == 1:
                    s += " một"
                elif donvi == 5:
                    s += " lăm"
                elif donvi > 0:
                    s += " " + mapping[donvi]
            elif chuc == 0:
                if donvi > 0:
                    s += " linh " + mapping[donvi]
        s = s.strip()
        if s:
            result.append(f"{s}{unit}")

    return " ".join(result).replace("  ", " ").strip()


def year2words(year):
    year = int(year)
    if not (1000 <= year <= 9999):
        # Không hợp lệ, trả về số thường
        return number2words(year)
    num = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    hang_nghin = year // 1000
    hang_tram = (year % 1000) // 100
    last_two = year % 100
    words = [num[hang_nghin], "nghìn", num[hang_tram], "trăm"]
    if last_two != 0:
        if last_two < 10:
            words.append("linh " + number2words(last_two))
        else:
            words.append(number2words(last_two))
    return " ".join(words)

def replace_full_date(text):
    def repl_ddmmyyyy(m):
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        day_txt = number2words(day)
        month_txt = number2words(month)
        year_txt = year2words(year)
        return f"{day_txt} tháng {month_txt} năm {year_txt}"
    
    def repl_mmyyyy(m):
        month = int(m.group(1))
        year = int(m.group(2))
        month_txt = number2words(month)
        year_txt = year2words(year)
        return f"tháng {month_txt} năm {year_txt}"
    
    def repl_ddmm(m):
        day = int(m.group(1))
        month = int(m.group(2))
        day_txt = number2words(day)
        month_txt = number2words(month)
        return f"{day_txt} tháng {month_txt}"
    
    def repl_year(m):
        year = int(m.group(1))
        year_txt = year2words(year)
        return year_txt
    
    text = re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", repl_ddmmyyyy, text)
    text = re.sub(r"\btháng[ ]*(\d{1,2})/(\d{4})\b", repl_mmyyyy, text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d{1,2})/(\d{4})\b", repl_mmyyyy, text)
    text = re.sub(r"\b(\d{1,2})/(\d{1,2})\b", repl_ddmm, text)
    text = re.sub(r"(?<![A-Za-z0-9])(\d{4})(?![%$€£¥₩₭₱฿ΩA-Za-z0-9])", repl_year, text)
    return text

def replace_word_number(text):
    def repl(m):
        word = m.group(1)
        num = int(m.group(2))
        num_txt = number2words(num)
        return f"{word} {num_txt}"
    return re.sub(r"([A-Za-zÀ-ỹà-ỹĐđ]+)-(\d+)", repl, text)

def is_vietnamese_word(word, abbr_dict=None, unit_dict=None):
    if abbr_dict and word in abbr_dict:
        return True
    if unit_dict and word in unit_dict:
        return True
    if len(word) == 1:
        return False
    if re.fullmatch(r"[a-zA-ZÀ-ỹà-ỹĐđ]+", word, re.UNICODE):
        if re.search(r"[aeiouáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ]", word, re.IGNORECASE):
            return True
    if word.isdigit():
        return True
    return False

def spell_unknown(word):
    if word.isalpha():
        return " ".join([SPELL_MAP.get(c, c) for c in word])
    return " ".join([SPELL_MAP.get(c, c) for c in word if c in SPELL_MAP])

def read_text_file(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    enc = chardet.detect(raw)['encoding']
    if not enc:
        enc = 'utf-8'
    text = raw.decode(enc)
    return text

def load_multi_dict_from_folder(folder_path):
    d = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    if "#" in line:
                        parts = line.split("#")
                    else:
                        parts = line.split("\t")
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        d[key] = val
    return d

def replace_number_unit(text, unit_dict):
    pattern = r"(\d+)\s*([%$\€£¥₩₭₱฿Ω])"
    def repl(m):
        num = int(m.group(1))
        unit = m.group(2)
        num_txt = number2words(num)
        unit_txt = unit_dict.get(unit, unit)
        return f"{num_txt} {unit_txt}"
    return re.sub(pattern, repl, text)