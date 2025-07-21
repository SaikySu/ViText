import sys
import os

class ICUMapping:
    """
    Python port of the C++ ICUMapping:
    - load_mapping_file: đọc từng dòng có dạng "key#value" và lưu vào dict `mapping`
    - mapping_of: trả về value tương ứng hoặc chuỗi rỗng nếu không tìm thấy
    - has_mapping_of: kiểm tra key tồn tại (bao gồm kiểm thử với lower-case và special-case Teencode)
    - clear_mapping: xoá hết mapping
    - unit_test: in ra toàn bộ mapping
    """

    def __init__(self):
        self.mapping = {}
        self.mapping_name = ""

    def load_mapping_file(self, filepath: str) -> bool:
        """
        Đọc file mapping, mỗi dòng "unit#pronoun", thêm vào self.mapping.
        Trả về True nếu load thành công, False nếu lỗi I/O.
        """
        self.mapping_name = filepath
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or '#' not in line:
                        continue
                    unit, pronoun = line.split('#', 1)
                    unit = unit.strip()
                    pronoun = pronoun.strip()
                    if unit:
                        self.mapping[unit] = pronoun
            return True
        except Exception as e:
            print(f"[E] Cannot load file {filepath} for mapping: {e}", file=sys.stderr)
            return False

    def mapping_of(self, unit: str) -> str:
        """
        Trả về mapping của `unit`, hoặc:
         - Nếu unit rỗng → trả về unit gốc
         - Nếu mapping_name chỉ rõ Teencode và unit hoàn toàn viết hoa → trả về chuỗi rỗng
         - Cố gắng lookup nguyên bản rồi lookup lower-case
         - Nếu không tìm thấy → trả về chuỗi rỗng
        """
        u = unit.strip()
        if len(u) == 0:
            return unit

        # tìm nguyên bản
        if u in self.mapping:
            return self.mapping[u]

        # special-case Teencode: nếu file là Teencode.txt và unit toàn hoa, skip
        if os.path.basename(self.mapping_name) == "Teencode.txt" and u.upper() == u:
            return ""

        # thử lower-case
        ul = u.lower()
        if ul in self.mapping:
            return self.mapping[ul]

        # không tìm thấy
        return ""

    def has_mapping_of(self, input_word: str) -> bool:
        """
        Trả về True nếu tồn tại mapping cho input_word, theo cùng logic với mapping_of.
        """
        w = input_word.strip()
        if not w:
            return False

        if w in self.mapping:
            return True

        if os.path.basename(self.mapping_name) == "Teencode.txt" and w.upper() == w:
            return False

        if w.lower() in self.mapping:
            return True

        return False

    def clear_mapping(self) -> None:
        """Xoá hết các mapping đã load."""
        self.mapping.clear()

    def unit_test(self) -> None:
        """In ra toàn bộ cặp key→value đã load, theo thứ tự key."""
        for k in sorted(self.mapping):
            print(f"{k}  →  {self.mapping[k]}")
