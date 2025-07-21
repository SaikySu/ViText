import os
import re
from ICUConstant import (
    DICT_FOLDER, F_ACRONYMS, F_LETTER_SOUND_EN, F_LETTER_SOUND_VN,
    F_POPULAR, F_SYMBOL, F_TEENCODE, MAPPING_FOLDER
)
from ICUHelper import remove_extra_whitespace, remove_noise_symbols
from ICUMapping import ICUMapping
from ICUDictionary import ICUDictionary
from SpecialCase import SpecialCase
from Address import Address
from Math import Math
from DateTime import DateTime
from ICUNumberConverting import ConvertingNumber

def normalize_line(line, options=None):
    # Default options
    if options is None:
        options = {"punc": False, "unknown": False, "lower": False, "rule": False}

    special_case = SpecialCase()
    address = Address()
    math_mod = Math()
    date_time = DateTime()

    acronym = ICUMapping()
    acronym.load_mapping_file(os.path.join(MAPPING_FOLDER, F_ACRONYMS))
    teen_code = ICUMapping()
    teen_code.load_mapping_file(os.path.join(MAPPING_FOLDER, F_TEENCODE))
    symbol = ICUMapping()
    symbol.load_mapping_file(os.path.join(MAPPING_FOLDER, F_SYMBOL))
    letterVN = ICUMapping()
    letterVN.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_VN))
    letterEN = ICUMapping()
    letterEN.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_EN))

    popular = ICUDictionary()
    popular.load_dict_file(os.path.join(DICT_FOLDER, F_POPULAR))

    def tokenize_symbol(s: str) -> str:
        s = re.sub(r'([^\w\s])', r' \1 ', s)
        s = s.replace('-', ' ')
        return s.strip()
    
    def read_letter_by_letter(word: str, mapper: ICUMapping) -> str:
        return ' '.join(mapper.mapping_of(c) for c in word.lower())

    def is_uppercase_word(word: str) -> bool:
        return word.isupper() and word.isalpha()

    def contains_only_letter(word: str, mapper: ICUMapping) -> bool:
        return all(mapper.has_mapping_of(c) for c in word.lower())

    def contains_vowel(word: str) -> bool:
        vowels = "aàảãáạăằẳẵâầẩẫấậeèẻẽéẹêềểễếệiìỉĩíịoòỏõóọôồổỗốộơỡớợuùủũúụưừửữứựyỳỷỹýỵ"
        return any(c in vowels for c in word.lower())

    def split_token_punct(token: str, keep_punc: bool) -> tuple[str, str]:
        m = re.match(r'^(.*?)([;:!\?,\.]?)$', token)
        base, p = m.group(1), m.group(2)
        if not keep_punc and p in '.!?:':
            p = '.'
        if not keep_punc and p in ',;':
            p = ','
        return base, p

    text = remove_extra_whitespace(line)
    text = special_case.normalize_text(text)
    text = date_time.normalize_text(text)
    text = math_mod.normalize_text(text)
    # Gộp các chuỗi số bị ngắt bởi khoảng trắng
    text = re.sub(r'(\d+)\s+(\d+)', r'\1\2', text)
    text = address.normalize_text(text)
    text = tokenize_symbol(text)
    text = remove_noise_symbols(text, space_replace=False)
    text = remove_extra_whitespace(text)

    if options["rule"]:
        return text

    tokens = re.findall(r'\S+', text)
    result = ""
    for tok in tokens:
        base_tok, tm_punc = split_token_punct(tok, options["punc"])
        word = base_tok.strip()
        out_tok = None
        if not word:
            out_tok = base_tok
        elif popular.has_word(word):
            out_tok = word
        elif acronym.has_mapping_of(word):
            out_tok = acronym.mapping_of(word)
        elif teen_code.has_mapping_of(word):
            out_tok = teen_code.mapping_of(word)
        else:
            tmp = remove_noise_symbols(base_tok, space_replace=True)
            tmp = tokenize_symbol(tmp)
            subtoks = re.findall(r'\S+', tmp)
            assemble = ""
            for st in subtoks:
                if popular.has_word(st):
                    assemble += f" {st} "
                elif acronym.has_mapping_of(st):
                    assemble += f" {acronym.mapping_of(st)} "
                elif teen_code.has_mapping_of(st):
                    assemble += f" {teen_code.mapping_of(st)} "
                elif st in '.!?:,;/':
                    if not options["punc"]:
                        if st in '.!?:':
                            assemble += " . "
                        else:
                            assemble += " , "
                    else:
                        assemble += f" {st} "
                elif symbol.has_mapping_of(st):
                    assemble += f" {symbol.mapping_of(st)} "
                elif contains_only_letter(st, letterVN):
                    if is_uppercase_word(st):
                        if re.fullmatch(r'[IVXLCDM]+', st) and len(st) <= 7:
                            roman = ConvertingNumber().roman_to_decimal(st)
                            if roman != st and roman.isdigit():
                                assemble += f" {roman} "
                            elif options["unknown"]:
                                assemble += f" {st} "
                            else:
                                assemble += f" {read_letter_by_letter(st, letterEN)} "
                        elif options["unknown"]:
                            assemble += f" {st} "
                        else:
                            assemble += f" {read_letter_by_letter(st, letterEN)} "
                    else:
                        if not options["unknown"]:
                            if not contains_vowel(st):
                                assemble += f" {read_letter_by_letter(st, letterVN)} "
                            else:
                                assemble += f" {st} "
                        else:
                            assemble += f" {st} "
                else:
                    assemble += f" {st} "
            out_tok = assemble.strip()
            if not out_tok:
                out_tok = word

        if tm_punc:
            if options["punc"]:
                out_tok += f" {tm_punc} "
            else:
                out_tok += " . " if tm_punc in '.!?:' else " , "
        result += " " + out_tok + " "

    if options["lower"]:
        result = result.lower()
    result = remove_noise_symbols(result, space_replace=False)
    result = remove_extra_whitespace(result)
    result = result.rstrip()
    if not result.endswith("."):
        result += "."
    return result