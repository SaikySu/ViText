import sys

class ICUDictionary:
    """
    Python port of the C++ ICUDictionary:
    - load_dict_file: đọc từng dòng từ file, thêm vào tập `words`
    - has_word: kiểm tra tồn tại, ưu tiên nguyên bản sau đó lower-case
    - clear_dict: xoá sạch tập từ
    - unit_test: in ra toàn bộ từ trong dict
    """

    def __init__(self):
        self.words = set()
        self.dict_name = ""

# ICUDictionary.py

    def load_dict_file(self, filepath: str) -> bool:
        self.dict_name = filepath
        try:
            # Đọc file nhị phân
            with open(filepath, 'rb') as f:
                raw = f.read()
            # Thử decode UTF-8 với BOM
            try:
                text = raw.decode('utf-8-sig')
            except:
                # Fallback: replace các ký tự lỗi
                text = raw.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"[E] Cannot load file {filepath} for dictionary: {e}", file=sys.stderr)
            return False

        # Now split lines on any newline and add
        for line in text.splitlines():
            w = line.strip()
            if w:
                self.words.add(w)
        return True

    def has_word(self, input_word: str) -> bool:
        """
        Kiểm tra xem `input_word` có trong dict hay không.
        Trả về True nếu có, False nếu không.
        So sánh cả bản gốc và lower-case.
        """
        w = input_word.strip()
        if w in self.words:
            return True
        lw = w.lower()
        if lw in self.words:
            return True
        return False

    def clear_dict(self) -> None:
        """Xoá hết từ trong dictionary."""
        self.words.clear()

    def unit_test(self) -> None:
        """In ra toàn bộ từ đã load (theo thứ tự chữ cái)."""
        for w in sorted(self.words):
            print(w)
