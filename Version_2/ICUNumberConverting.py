import re
from typing import List, Optional

class ConvertingNumber:
    def __init__(self):
        # Vietnamese number words
        self.CHU_SO = [
            "không", "một", "hai", "ba", "bốn", 
            "năm", "sáu", "bảy", "tám", "chín"
        ]
        
        # Vietnamese number units
        self.MUOI_F = "mười"
        self.MUOI = "mươi"
        self.HUNDRED = "trăm"
        self.THOUSAND = "nghìn"
        self.MILLION = "triệu"
        self.BILLION = "tỷ"
        self.MOTS = "mốt"
        self.TUW = "tư"
        self.LAWM = "lăm"
        self.LINH = "linh"
        self.SPACE = " "
        self.COMMA = ", "
        self.NGHIN = "nghìn"
        self.TRIEU = "triệu"
    
    def convert_number_lt_hundred(self, num: str) -> str:
        """Convert numbers less than 100 to Vietnamese"""
        if not num or not num.isdigit():
            return ""
        
        # Less than 10
        if len(num) == 1:
            return self.CHU_SO[int(num)]
        
        result = ""
        first_digit = int(num[0])
        second_digit = int(num[1])
        
        # Between 10 and 19
        if first_digit == 1:
            result = self.MUOI_F
        # Between 20 and 99
        else:
            result = self.CHU_SO[first_digit] + self.SPACE + self.MUOI
        
        # num is 10, 20, 30, ...
        if second_digit == 0:
            return result
        
        result += self.SPACE
        
        # Special cases for Vietnamese pronunciation
        if second_digit == 1 and first_digit != 1:
            result += self.MOTS
        elif second_digit == 4 and first_digit != 1:
            result += self.TUW
        elif second_digit == 5:
            result += self.LAWM
        else:
            result += self.CHU_SO[second_digit]
        
        return result
    
    def convert_number_lt_thousand(self, num: str) -> str:
        """Convert numbers less than 1000 to Vietnamese"""
        if not num or not num.isdigit():
            return ""
        
        if len(num) < 3:
            return self.convert_number_lt_hundred(num)
        
        result = ""
        first_digit = int(num[0])
        second_digit = int(num[1])
        third_digit = int(num[2])
        
        result += self.CHU_SO[first_digit] + self.SPACE + self.HUNDRED
        
        # 000, 100, 200, ..., 900
        if second_digit == 0 and third_digit == 0:
            if first_digit == 0:
                return ""
            else:
                return result
        
        # [1-9]0[1-9] (e.g., 101, 202, 303)
        if second_digit == 0:
            return result + self.SPACE + self.LINH + self.SPACE + self.CHU_SO[third_digit]
        
        # Normal case
        return result + self.SPACE + self.convert_number_lt_hundred(num[1:])
    
    def convert_number_lt_million(self, num: str) -> str:
        """Convert numbers less than 1 million to Vietnamese"""
        if not num or not num.isdigit():
            return ""
        
        if len(num) < 4:
            return self.convert_number_lt_thousand(num)
        
        split_index = len(num) % 3
        if split_index == 0:
            split_index = 3
        
        left = self.convert_number_lt_million(num[:split_index])
        right = self.convert_number_lt_million(num[split_index:])
        
        if not left and not right:
            return ""
        
        hang_index = (len(num) - split_index) // 3 - 1
        hang = self.NGHIN if hang_index == 0 else self.TRIEU
        
        if not left:
            return self.CHU_SO[0] + self.SPACE + hang + self.SPACE + right
        if not right:
            return left + self.SPACE + hang
        
        return left + self.SPACE + hang + self.SPACE + right
    
    def convert_number_arbitrary(self, num: str) -> str:
        """Convert arbitrarily large numbers to Vietnamese"""
        if not num or not num.isdigit():
            return ""
        
        if len(num) < 10:
            return self.convert_number_lt_million(num)
        
        split_index = len(num) % 9
        if split_index == 0:
            split_index = 9
        
        left = self.convert_number_lt_million(num[:split_index])
        right = self.convert_number_arbitrary(num[split_index:])
        
        if not left:
            return right
        
        hang = self.BILLION
        for i in range((len(num) - split_index) // 9 - 1):
            hang += self.SPACE + self.BILLION
        
        if not right:
            return left + self.SPACE + hang
        
        return left + self.SPACE + hang + self.COMMA + right
    
    def strip_zeros(self, num: str, z: int = 0) -> str:
        """Remove leading zeros from number string"""
        while z < len(num) and num[z] == '0':
            z += 1
        
        if z > 0 and z < len(num):
            return num[z:]
        elif z == len(num):
            return ""
        else:
            return num
    
    def convert_number(self, num: str) -> str:
        """Main function to convert number to Vietnamese words"""
        if not num:
            return ""
        
        if num == "0":
            return "không"
        
        # Check if num contains only digits
        if not num.isdigit():
            return ""
        
        result = self.strip_zeros(num)
        
        # Handle very long numbers (more than 15 digits)
        if len(result) > 15:
            long_result = ""
            for char in result:
                long_result += " " + self.convert_number(char)
            return long_result.strip()
        
        if not result:
            return ""
        
        result = self.convert_number_arbitrary(result)
        
        # Clean up the result
        result = result.replace("không nghìn ", "")
        result = result.replace("không triệu ", "")
        
        if len(result) < 60:
            result = result.replace("tỷ,", "tỷ")
        
        return result
    
    def decimal_to_roman(self, number: int) -> str:
        """Convert decimal number to Roman numerals"""
        if number <= 0:
            return ""
        
        result = ""
        decimal = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        symbol = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        
        i = 0
        while number > 0:
            while number // decimal[i] > 0:
                result += symbol[i]
                number -= decimal[i]
            i += 1
        
        return result
    
    def roman_to_decimal(self, roman: str) -> str:
        """Convert Roman numerals to decimal string"""
        if not roman:
            return roman
        
        # Convert to uppercase for processing
        roman_upper = roman.upper()
        
        # Map Roman characters to values
        roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        
        # Convert Roman to decimal
        values = []
        for char in roman_upper:
            if char in roman_values:
                values.append(roman_values[char])
            else:
                return roman  # Invalid Roman numeral
        
        if not values:
            return roman
        
        # Calculate decimal value
        total = values[-1]  # Start with the last value
        
        for i in range(len(values) - 2, -1, -1):
            if values[i] < values[i + 1]:
                total -= values[i]
            else:
                total += values[i]
        
        # Verify if the conversion is correct by converting back
        if roman_upper == self.decimal_to_roman(total):
            return str(total)
        else:
            return roman  # Return original if conversion doesn't match
    
    def unit_test(self):
        """Unit test for the conversion functions"""
        test_cases = [
            ("0", "không"),
            ("1", "một"),
            ("12", "mười hai"),
            ("25", "hai mươi lăm"),
            ("101", "một trăm linh một"),
            ("1000", "một nghìn"),
            ("1234", "một nghìn hai trăm ba mươi tư"),
            ("1000000", "một triệu"),
        ]
        
        print("Running unit tests for number conversion:")
        for number, expected in test_cases:
            result = self.convert_number(number)
            status = "✓" if result == expected else "✗"
            print(f"{status} {number} -> {result} (expected: {expected})")
        
        # Test Roman numeral conversion
        print("\nTesting Roman numeral conversion:")
        roman_tests = [
            ("IV", "4"),
            ("IX", "9"),
            ("XL", "40"),
            ("XC", "90"),
            ("CD", "400"),
            ("CM", "900"),
            ("MCMXC", "1990"),
        ]
        
        for roman, expected in roman_tests:
            result = self.roman_to_decimal(roman)
            status = "✓" if result == expected else "✗"
            print(f"{status} {roman} -> {result} (expected: {expected})")