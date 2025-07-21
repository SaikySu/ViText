import re
import os
from typing import Dict, List
from enum import IntEnum
from ICUHelper import is_number_literal, read_number
from ICUConstant import REGEX_FOLDER

class DateTimeCategory(IntEnum):
    TIME = 0
    DATE_1 = 1
    DATE_FROM_TO_1 = 2
    DATE_FROM_TO_2 = 3
    MONTH = 4
    DATE_3 = 5
    DATE_2 = 6

class ConvertingNumber:
    """Placeholder for number conversion functionality"""
    def convert_number(self, number_str: str) -> str:
        # This would contain the actual number conversion logic
        return number_str
    
    def roman_to_decimal(self, roman: str) -> str:
        # This would contain roman numeral conversion logic
        return roman

class DateTime:
    def __init__(self, regex_folder: str = REGEX_FOLDER):
        self.REGEX_FOLDER = regex_folder
        
        # File mappings
        self.pattern_files = {
            DateTimeCategory.TIME: "Time.txt",
            DateTimeCategory.DATE_1: "Date_1.txt", 
            DateTimeCategory.DATE_FROM_TO_1: "Date_From_To_1.txt",
            DateTimeCategory.DATE_FROM_TO_2: "Date_From_To_2.txt",
            DateTimeCategory.MONTH: "Month.txt",
            DateTimeCategory.DATE_3: "Date_3.txt",
            DateTimeCategory.DATE_2: "Date_2.txt"
        }
        
        # Store patterns for each category
        self.patterns: Dict[int, List[str]] = {}
        
        # Load all patterns
        self._load_all_patterns()
        
        # Number converter
        self.converter = ConvertingNumber()
    
    def _load_all_patterns(self):
        """Load all pattern files"""
        if not os.path.exists(self.REGEX_FOLDER):
            print(f"[INFO] Err load folder: {self.REGEX_FOLDER}")
        
        for category, filename in self.pattern_files.items():
            self.load_patterns(category, filename)
    
    def load_patterns(self, category: int, filename: str):
        """Load regex patterns from file"""
        filepath = os.path.join(self.REGEX_FOLDER, filename)
        
        if category not in self.patterns:
            self.patterns[category] = []
        
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                print(f"[E] Pattern file not found: {filepath}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        self.patterns[category].append(line)
            
            # print(f"[INFO] Loaded {len(self.patterns[category])} patterns from {filename}")
            
        except FileNotFoundError:
            print(f"[E] Error reading pattern file: {filename}")
        except Exception as e:
            print(f"[E] Error reading pattern file {filename}: {str(e)}")
    
    def normalize_text(self, input_text: str) -> str:
        """Normalize text using loaded patterns"""
        if not input_text:
            return ""
        
        result = ""
        pre_result = input_text
        
        # Define order of categories to ensure correct pattern matching
        category_order = [
            DateTimeCategory.DATE_FROM_TO_1,
            DateTimeCategory.DATE_FROM_TO_2,
            DateTimeCategory.DATE_1,
            DateTimeCategory.DATE_2,
            DateTimeCategory.DATE_3,
            DateTimeCategory.MONTH,
            DateTimeCategory.TIME
        ]
        
        for category in category_order:
            if category not in self.patterns or not self.patterns[category]:
                continue
                
            for pattern in self.patterns[category]:
                try:
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    
                    def replace_func(match):
                        return " " + self.string_for_replace(category, match) + " "
                    
                    result = compiled_pattern.sub(replace_func, pre_result)
                    pre_result = result
                    result = ""
                    
                except re.error as e:
                    print(f"[E] Error in regex pattern: {pattern}, Error: {e}")
                    continue
        
        return pre_result.strip()
    
    def string_for_replace(self, category: int, match: re.Match) -> str:
        """Router function to call appropriate regex handler"""
        if category == DateTimeCategory.TIME:
            return self.regex_time(match)
        elif category == DateTimeCategory.DATE_1:
            return self.regex_date1(match)
        elif category == DateTimeCategory.DATE_FROM_TO_1:
            return self.regex_date_from_to_1(match)
        elif category == DateTimeCategory.DATE_FROM_TO_2:
            return self.regex_date_from_to_2(match)
        elif category == DateTimeCategory.MONTH:
            return self.regex_month(match)
        elif category == DateTimeCategory.DATE_3:
            return self.regex_date3(match)
        elif category == DateTimeCategory.DATE_2:
            return self.regex_date2(match)
        else:
            print(f"[E] Invalid category: {category}")
            return ""
    
    def regex_time(self, match: re.Match) -> str:
        """Handle time regex matches"""
        match_text = match.group(0).lower()
        next_part = match.group(1).strip() if match.lastindex and match.lastindex >= 1 else ""
        
        result = ""
        number = ""
        continuous_digits = False
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['h', 'g', ':']:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number) + " "
                    number = ""
                result += "giờ "
            elif char == 'a':
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number) + " "
                    number = ""
                result += "ây em "
            elif char == 'p':
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number) + " "
                    number = ""
                result += "bi em "
            elif char == 'm':
                pass  # Skip 'm' character
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number) + " "
                    number = ""
                result += char
        
        if number:
            result += " " + self.converter.convert_number(number) + " "
        
        if next_part == "-":
            result += "đến "
        
        return result
    
    def regex_date1(self, match: re.Match) -> str:
        """Handle date format 1 regex matches"""
        match_text = match.group(0).lower()
        result = ""
        number = ""
        continuous_digits = False
        check_date = 1
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['/', '.', '-']:
                if check_date == 1:
                    check_date += 1
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                elif check_date == 2:
                    result += " tháng "
                    check_date += 1
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                result += char
        
        result += " năm " + self.converter.convert_number(number)
        return result
    
    def regex_date_from_to_1(self, match: re.Match) -> str:
        """Handle date from-to format 1 regex matches"""
        match_text = match.group(0).lower()
        result = ""
        number = ""
        continuous_digits = False
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['/', '.']:
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " tháng "
                number = ""
            elif char == '-':
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " đến "
                number = ""
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                result += char
        
        result += self.converter.convert_number(number)
        return result
    
    def regex_date_from_to_2(self, match: re.Match) -> str:
        """Handle date from-to format 2 regex matches"""
        match_text = match.group(0).lower()
        result = ""
        number = ""
        continuous_digits = False
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['/', '.']:
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " năm "
                number = ""
            elif char == '-':
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " đến tháng "
                number = ""
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                result += char
        
        result += self.converter.convert_number(number)
        return result
    
    def regex_month(self, match: re.Match) -> str:
        """Handle month regex matches"""
        match_text = match.group(0).lower()
        result = ""
        number = ""
        continuous_digits = False
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['/', '.', '-']:
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " năm "
                number = ""
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                result += char
        
        result += self.converter.convert_number(number)
        return result
    
    def regex_date3(self, match: re.Match) -> str:
        """Handle date format 3 regex matches"""
        match_text = match.group(0).lower()
        result = ""
        number = ""
        continuous_digits = False
        
        for char in match_text:
            if char.isdigit():
                if continuous_digits:
                    number += char
                else:
                    number = char
                    continuous_digits = True
            elif char in ['/', '.', '-']:
                continuous_digits = False
                result += self.converter.convert_number(number)
                result += " tháng "
                number = ""
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += self.converter.convert_number(number)
                    number = ""
                result += char
        
        result += self.converter.convert_number(number)
        return result
    
    def regex_date2(self, match: re.Match) -> str:
        """Handle date format 2 regex matches (Roman numerals)"""
        match_text = match.group(0)
        roman_part = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
        year_part = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
        
        result = ""
        check_roman = self.converter.roman_to_decimal(roman_part)
        
        if check_roman != roman_part and is_number_literal(check_roman):
            result += " " + read_number(check_roman, 0) + " "
        
        return result + "năm " + self.converter.convert_number(year_part)