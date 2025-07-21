import sys

class ICUReadFile:
    """
    Python port of the C++ ICUReadFile class:
    - read_file(): đọc file nhị phân, phát hiện BOM, decode về Unicode str
    - next_line(): cập nhật các con trỏ line_start, line_end, line_num dựa trên vị trí bắt đầu
    - getters: get_content_uchar, get_line_start, get_line_end, get_file_length
    """

    def __init__(self, filename: str = None):
        self.file_name   = filename
        self.content     = ""   # toàn bộ nội dung file sau decode
        self.line_start  = 0
        self.line_end    = 0
        self.line_num    = 0
        self.file_len    = 0    # chiều dài content

    def read_file(self) -> bool:
        """Đọc file nhị phân, detect BOM, decode sang Unicode, lưu vào self.content."""
        try:
            with open(self.file_name, 'rb') as f:
                raw = f.read()
        except Exception as e:
            print(f"[E] Could not open file \"{self.file_name}\": {e}", file=sys.stderr)
            return False

        # decode với BOM nếu có, ngược lại decode utf-8 và replace errors
        try:
            self.content = raw.decode('utf-8-sig')
        except:
            self.content = raw.decode('utf-8', errors='replace')

        self.file_len = len(self.content)
        # reset con trỏ dòng
        self.line_num   = 0
        self.line_start = 0
        self.line_end   = 0
        return True

    def next_line(self, start_pos: int):
        """
        Cập nhật line_start, line_end cho dòng tiếp theo bắt đầu từ start_pos.
        start_pos = 0 → dòng đầu tiên.
        """
        if start_pos == 0:
            self.line_num = 0
        else:
            self.line_num += 1

        self.line_start = start_pos
        self.line_end   = start_pos

        # tìm đến ký tự newline hoặc các dạng phân tách dòng Unicode
        while self.line_end < self.file_len:
            c = self.content[self.line_end]
            self.line_end += 1
            if c in ('\n', '\f', '\r', '\x85', '\u2028', '\u2029'):
                break

        # xử lý CR/LF sequence: nếu trước đó là '\r' và hiện tại là '\n', bao luôn '\n'
        if (self.line_end < self.file_len and
            self.content[self.line_end - 1] == '\r' and
            self.content[self.line_end] == '\n'):
            self.line_end += 1

    def get_content_uchar(self) -> str:
        """Trả về toàn bộ nội dung file đã decode (tương ứng UChar* trong C++)."""
        return self.content

    def get_line_start(self) -> int:
        return self.line_start

    def get_line_end(self) -> int:
        return self.line_end

    def get_file_length(self) -> int:
        return self.file_len
