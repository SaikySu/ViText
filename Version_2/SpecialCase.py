import re
import os
import sys
from ICUReadFile import ICUReadFile
from ICUMapping import ICUMapping
from ICUNumberConverting import ConvertingNumber
from ICUConstant import (
    REGEX_FOLDER, MAPPING_FOLDER,
    F_LETTER_SOUND_EN, F_LETTER_SOUND_VN,
    F_SYMBOL, F_NUMBER_SOUND,
    DIGIT_ZERO, PLUS_SIGN,
    FULL_STOP, SOLIDUS,
    COLON, HYPHEN_MINUS,
    LEFT_PARENTHESIS, RIGHT_PARENTHESIS,
    VERTICAL_LINE
)

class SpecialCase:

    PHONE_NUMBER     = 0
    FOOTBALL_UNDER   = 1
    FOOTBALL_OTHER   = 2
    EMAIL            = 3
    WEBSITE          = 4

    F_PHONE_NUMBER   = "PhoneNumber.txt"
    F_FOOTBALL_UNDER = "FootballUnder.txt"
    F_FOOTBALL_OTHER = "FootballOther.txt"
    F_WEBSITE        = "Website.txt"
    F_EMAIL          = "Email.txt"

    def __init__(self):
        self.patterns = {}
        self._load_patterns(SpecialCase.PHONE_NUMBER,     SpecialCase.F_PHONE_NUMBER)
        self._load_patterns(SpecialCase.FOOTBALL_UNDER,   SpecialCase.F_FOOTBALL_UNDER)
        self._load_patterns(SpecialCase.FOOTBALL_OTHER,   SpecialCase.F_FOOTBALL_OTHER)
        self._load_patterns(SpecialCase.WEBSITE,          SpecialCase.F_WEBSITE)
        self._load_patterns(SpecialCase.EMAIL,            SpecialCase.F_EMAIL)

    def _load_patterns(self, category: int, filename: str):
        """Load regex patterns from file into self.patterns[category]."""
        path = os.path.join(REGEX_FOLDER, filename)
        reader = ICUReadFile(path)
        if not reader.read_file():
            print(f"[E] Error reading pattern file: {filename}", file=sys.stderr)
            return
        pos = 0
        self.patterns.setdefault(category, [])
        while pos < reader.get_file_length():
            reader.next_line(pos)
            line = reader.get_content_uchar()[reader.get_line_start():reader.get_line_end()].strip()
            if line:
                self.patterns[category].append(line)
            pos = reader.get_line_end()

    def normalize_text(self, text: str) -> str:
        """Apply all special regex replacements to the input text."""
        text = re.sub(r'(?<=\d)\s+(?=\d)', '', text)
        result = text
        # 1) Handle emails first to avoid conflicts with websites
        for pattern in self.patterns.get(SpecialCase.EMAIL, []):
            prog = re.compile(pattern)
            result = prog.sub(lambda m: f" {self._replace(SpecialCase.EMAIL, m.group(0))} ", result)
        # 2) Handle other categories in fixed order
        for category in (
            SpecialCase.PHONE_NUMBER,
            SpecialCase.FOOTBALL_UNDER,
            SpecialCase.FOOTBALL_OTHER,
            SpecialCase.WEBSITE
        ):
            for pattern in self.patterns.get(category, []):
                prog = re.compile(pattern)
                result = prog.sub(lambda m: f" {self._replace(category, m.group(0))} ", result)
        return result

    def _replace(self, category: int, match_text: str) -> str:
        """Dispatch to the correct handler based on category."""
        if category == SpecialCase.PHONE_NUMBER:
            return self._regex_phone_number(match_text)
        if category == SpecialCase.FOOTBALL_UNDER:
            return self._regex_football_under(match_text)
        if category == SpecialCase.FOOTBALL_OTHER:
            return self._regex_football_other(match_text)
        if category == SpecialCase.WEBSITE:
            return self._regex_website(match_text)
        if category == SpecialCase.EMAIL:
            return self._regex_email(match_text)
        return ""

    def _regex_football_under(self, text: str) -> str:
        """Convert 'U12' style to 'u 12' + spoken number."""
        result = ""
        number = ""
        conv = ConvertingNumber()
        for c in text:
            if c.lower() == 'u':
                result += 'u'
            elif c.isdigit():
                number += c
        if number:
            result += " " + conv.convert_number(number)
        return result

    def _regex_football_other(self, text: str) -> str:
        """
        Convert scores like '1-2' or '1|2' and mixed text:
        separate continuous digits, map separators to space.
        """
        result = ""
        number = ""
        conv = ConvertingNumber()
        continuous = False
        for c in text:
            if c.isdigit():
                if continuous:
                    number += c
                else:
                    number = c
                    continuous = True
            elif c in (HYPHEN_MINUS, VERTICAL_LINE):
                if continuous:
                    result += conv.convert_number(number)
                    number = ""
                    continuous = False
                result += " "
            else:
                if continuous:
                    result += conv.convert_number(number)
                    number = ""
                    continuous = False
                result += c
        if number:
            result += conv.convert_number(number)
        return result

    def _regex_website(self, text: str) -> str:
        """
        Spell out website URLs, keeping 'com' intact,
        and say 'chấm' for '.', 'xuyệt' for '/'.
        """
        mapper = ICUMapping()
        mapper.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_VN))
        mapper.load_mapping_file(os.path.join(MAPPING_FOLDER, F_SYMBOL))

        lowered = text.lower()
        conv = ConvertingNumber()

        idx = lowered.find(".com")
        if idx != -1:
            skip_start, skip_end = idx + 1, idx + 1 + len("com")
        else:
            skip_start, skip_end = -1, -1

        result = ""
        for i, c in enumerate(lowered):
            if skip_start <= i < skip_end:
                result += c
            elif c.isdigit():
                result += f" {conv.convert_number(c)} "
            elif c == ".":
                result += " chấm "
            elif c == "/":
                result += " xuyệt "
            else:
                result += f" {mapper.mapping_of(c)} "
        return result.strip()

    def _regex_email(self, text: str) -> str:
        """
        Spell out an email address:
        - local part: letter-by-letter or digit-by-digit
        - '@' becomes 'a còng'
        - 'gmail.com' -> 'giy meo chấm com'
        - others: same as website
        """
        mapper = ICUMapping()
        mapper.load_mapping_file(os.path.join(MAPPING_FOLDER, F_LETTER_SOUND_EN))
        mapper.load_mapping_file(os.path.join(MAPPING_FOLDER, F_SYMBOL))
        conv = ConvertingNumber()

        lowered = text.lower()
        local, domain = (lowered.split("@", 1) + [""])[:2]

        parts = []
        for c in local:
            if c.isdigit():
                parts.append(conv.convert_number(c))
            else:
                parts.append(mapper.mapping_of(c))
        parts.extend(["a", "còng"]);
        if domain.startswith("gmail.com"):
            parts.extend(["giy", "meo", "chấm", "com"])
        else:
            for c in domain:
                if c.isdigit():
                    parts.append(conv.convert_number(c))
                elif c == ".":
                    parts.append("chấm")
                elif c == "/":
                    parts.append("xuyệt")
                else:
                    parts.append(mapper.mapping_of(c))
        return " ".join(parts).strip()

    def _regex_phone_number(self, text: str) -> str:
        """
        Spell out phone numbers: '+' -> 'cộng', digits via F_NUMBER_SOUND mapping,
        ignore punctuation.
        """
        mapper = ICUMapping()
        mapper.load_mapping_file(os.path.join(MAPPING_FOLDER, F_NUMBER_SOUND))
        result = ""
        for c in text:
            if c.isspace():
                continue
            if c == PLUS_SIGN:
                result += "cộng "
            elif c in (FULL_STOP, COLON, HYPHEN_MINUS, LEFT_PARENTHESIS, RIGHT_PARENTHESIS):
                continue
            elif c.isdigit():
                result += mapper.mapping_of(c) + " "
            else:
                result += c
        return result