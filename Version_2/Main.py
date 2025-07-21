import argparse
import re
import os

from ICUConstant import (
    DICT_FOLDER, F_ACRONYMS, F_INPUT, F_OUTPUT,
    F_LETTER_SOUND_EN, F_LETTER_SOUND_VN, F_POPULAR,
    F_SYMBOL, F_TEENCODE, MAPPING_FOLDER
)
from ICUHelper import remove_extra_whitespace, remove_noise_symbols
from ICUMapping import ICUMapping
from ICUDictionary import ICUDictionary
from SpecialCase import SpecialCase
from Address import Address
from Math import Math
from DateTime import DateTime
from ICUNumberConverting import ConvertingNumber

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-punc', action='store_true')
    parser.add_argument('-unknown', action='store_true')
    parser.add_argument('-lower', action='store_true')
    parser.add_argument('-rule', action='store_true')
    args = parser.parse_args()

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

    with open(F_INPUT, 'r', encoding='utf-8') as fin, \
         open(F_OUTPUT, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            text = remove_extra_whitespace(line)
            # print(f"After cleanup: {text}")
            text = special_case.normalize_text(text)
            # print(f"After special_case: {text}")
            text = date_time.normalize_text(text)
            # print(f"After date_time: {text}") 
            text = math_mod.normalize_text(text)
            # text = re.sub(r'(\d+)\s+(\d+)', r'\1\2', text)
            # print(f"After merge numbers: {text}")
            # text = re.sub(r'\b([A-Za-z]+)(\d+)\b', r'\1 \2', text)
            # print(f"Math_mod: {text}")  
            text = address.normalize_text(text)
            # print(f"Address: {text}")
            text = tokenize_symbol(text)
            # print(f"tokenize_symbol: {text}")
            text = remove_noise_symbols(text, space_replace=False)
            # print(f"remove_noise_symbols: {text}")
            text = remove_extra_whitespace(text)
            # print(f"remove_extra_whitespace: {text}")

            if args.rule:
                fout.write(text + "#line#")
                continue

            tokens = re.findall(r'\S+', text)
            result = ""
            for tok in tokens:
                base_tok, tm_punc = split_token_punct(tok, args.punc)
                word = base_tok.strip()

                out_tok = None
                if not word:
                    # Xử lý trường hợp token chỉ là dấu câu
                    if tm_punc:
                        out_tok = " . " if tm_punc in '.!?:' else " , "
                    else:
                        out_tok = ""
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
                            if not args.punc:
                                assemble += " . " if st in '.!?:' else " , "
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
                                    elif args.unknown:
                                        assemble += f" {st} "
                                    else:
                                        assemble += f" {read_letter_by_letter(st, letterEN)} "
                                elif args.unknown:
                                    assemble += f" {st} "
                                else:
                                    assemble += f" {read_letter_by_letter(st, letterEN)} "
                            else:
                                if not args.unknown:
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

                if tm_punc and out_tok != " . " and out_tok != " , ":
                    if args.punc:
                        out_tok += f" {tm_punc} "
                    else:
                        out_tok += " . " if tm_punc in '.!?:' else " , "

                result += " " + out_tok + " "
            if args.lower:
                result = result.lower()
                
            # print(f"Before noise sysbols {result}")
            result = remove_noise_symbols(result, space_replace=False)
            # print(f"A noise sysbols {result}")
            result = remove_extra_whitespace(result)
            result = result.rstrip()
            if not result.endswith('.'):
                result += '.'
            result = remove_extra_whitespace(result)
            fout.write(result + "#line#")
            print(result)

if __name__ == "__main__":
    main()