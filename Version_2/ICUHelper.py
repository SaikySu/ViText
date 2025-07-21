import re
from ICUNumberConverting import ConvertingNumber
from ICUMapping import ICUMapping
from ICUConstant import MAPPING_FOLDER, F_UNIT_MAPPING_BASE, F_PREFIX_UNIT

def remove_noise_symbols(s: str, space_replace: bool) -> str:
    # 1) Loại bỏ ngoặc, dấu “…” v.v. (không xóa '-')
    noisy1 = r'[“”\.{3}\"{}\[\]]'
    s = re.sub(noisy1, ' ' if space_replace else '', s)

    # 2) Xóa '-' chỉ nếu trước hoặc sau nó không phải letter/digit
    if space_replace:
        s = re.sub(r'(?<![\w\d])\-|-(?![\w\d])', ' ', s)
    else:
        s = re.sub(r'(?<![\w\d])\-|-(?![\w\d])', '', s)

    # 3) Gộp multi-space & trim
    return re.sub(r'\s+', ' ', s).strip()


def remove_extra_whitespace(s: str) -> str:
    """
    Collapse multiple whitespace characters into a single space,
    and trim leading/trailing whitespace.
    """
    return re.sub(r'\s+', ' ', s).strip()

def is_number_literal(s: str) -> bool:
    """Return True if the string consists solely of digits."""
    return bool(s) and all(ch.isdigit() for ch in s)

def split_fraction_unit(unit: str) -> list[str]:
    """Split on '/' to separate numerator/denominator."""
    if '/' in unit:
        num, den = unit.split('/', 1)
        return [num, den]
    return [unit]

def split_composite_unit(unit: str) -> str:
    """
    Handle composite units:
    - Load base-unit and prefix-unit mappings
    - Decompose the unit string into known sub-units or numeric superscripts.
    """

    base_mapper = ICUMapping()
    base_mapper.load_mapping_file(f"{MAPPING_FOLDER}/{F_UNIT_MAPPING_BASE}")
    prefix_mapper = ICUMapping()
    prefix_mapper.load_mapping_file(f"{MAPPING_FOLDER}/{F_PREFIX_UNIT}")

    # Direct mapping if short or known
    if len(unit) < 2 or base_mapper.has_mapping_of(unit):
        return f" {base_mapper.mapping_of(unit)} "

    # Detect prefix (1-2 chars)
    prefix_len = 2 if prefix_mapper.has_mapping_of(unit[:2]) else (1 if prefix_mapper.has_mapping_of(unit[:1]) else 0)
    normalized = ""
    if prefix_len:
        pref = unit[:prefix_len]
        normalized += prefix_mapper.mapping_of(pref) + " "
        main_unit = unit[prefix_len:]
    else:
        main_unit = unit

    conv = ConvertingNumber()
    start = 0
    end = 0
    parts = []
    while start < len(main_unit):
        end = start + 1
        while end <= len(main_unit):
            part = main_unit[start:end]
            if base_mapper.has_mapping_of(part) or part.isdigit():
                if part.isdigit():
                    if part == "2":
                        parts.append("vuông")
                    elif part == "3":
                        parts.append("khối")
                    else:
                        parts.append("mũ " + conv.convert_number(part))
                else:
                    parts.append(base_mapper.mapping_of(part))
                start = end
                break
            end += 1
        else:
            # No match, output raw char
            parts.append(main_unit[start])
            start += 1

    return " " + normalized + " ".join(parts) + " "

def normalize_unit(unit: str) -> str:
    """
    Normalize a unit string, handling fractions and composite units.
    """
    parts = split_fraction_unit(unit)
    normalized = ""
    for i, part in enumerate(parts):
        normalized += split_composite_unit(part)
        if i != len(parts) - 1:
            normalized += " trên "
    return remove_extra_whitespace(normalized)

def read_number(literal_number: str, point: int) -> str:
    """
    Convert a numeric literal to its Vietnamese spoken form.
    - point=0: decimal separator is ','
    - point=1: decimal separator is '.'
    - else: detect either ',', '.'
    """
    idx = -1
    if point == 0:
        idx = literal_number.find(',')
    elif point == 1:
        idx = literal_number.find('.')
    else:
        for i, c in enumerate(literal_number):
            if c in ',.':
                idx = i
                break

    conv = ConvertingNumber()
    if idx == -1:
        # integer only
        digits = ''.join(ch for ch in literal_number if ch.isdigit())
        return f" {conv.convert_number(digits)} "
    else:
        int_part = ''.join(ch for ch in literal_number[:idx] if ch.isdigit())
        frac_part = ''.join(ch for ch in literal_number[idx+1:] if ch.isdigit())
        # handle leading zeros
        zero_frac = ""
        started = False
        for ch in literal_number[idx+1:]:
            if ch == '0' and not started:
                zero_frac += " không "
            elif ch.isdigit():
                started = True
        return f" {conv.convert_number(int_part)} phẩy {zero_frac}{conv.convert_number(frac_part)} "

