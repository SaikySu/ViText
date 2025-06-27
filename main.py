import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vinorm import Vinorm

def merge_output_file(filepath):
     TEXT = ""
     with open(filepath, mode="r", encoding="utf-8") as fr:
         text = fr.read()
     S = text.split("#line#")
     for s in S:
         if s.strip() == "":
             continue
         TEXT += s.strip() + ". "
     return TEXT.strip()

def main():
    vn = Vinorm()
    s = "Sunhouse Inverter 1 HP SHR-AW09IC650"
    results = [vn.normalize(s, unknown=False, lower=False, punc=False)]
    # Ghi ra file output.txt mỗi kết quả một dòng, dùng #line# phân cách
    A = "."  # thư mục hiện tại
    O = os.path.join(A, "output.txt")
    with open(O, mode="w", encoding="utf-8") as fw:
        for res in results:
            fw.write(res + "#line#")
    merged_text = merge_output_file(O)
    print(merged_text)

if __name__ == "__main__":
    main()


