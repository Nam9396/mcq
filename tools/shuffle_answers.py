#!/usr/bin/env python3
"""Trộn vị trí đáp án đúng trong file bài học (options và why_wrong trộn cùng thứ tự).

Dùng:  python3 shuffle_answers.py bai.json            (ghi đè file)
       python3 shuffle_answers.py bai.json -o ra.json
Trộn theo seed tạo từ nội dung câu, nên chạy lại trên cùng file gốc cho cùng kết quả.
Chỉ chạy một lần trên bản nháp, trước validate/publish.
"""
import argparse
import hashlib
import json
import pathlib
import random


def shuffle_question(q):
    seed = int(hashlib.sha1((q.get("stem", "") + q["lead"]).encode("utf-8")).hexdigest()[:8], 16)
    order = list(range(len(q["options"])))
    random.Random(seed).shuffle(order)
    q["options"] = [q["options"][k] for k in order]
    ww = q.get("why_wrong")
    if isinstance(ww, list) and len(ww) == len(order):
        q["why_wrong"] = [ww[k] for k in order]
    q["answer"] = order.index(q["answer"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    src = pathlib.Path(a.lesson)
    data = json.loads(src.read_text(encoding="utf-8"))
    for q in data["questions"]:
        shuffle_question(q)
    out = pathlib.Path(a.out) if a.out else src
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pos = [q["answer"] for q in data["questions"]]
    print(f"Đã trộn {len(pos)} câu. Phân bố vị trí đáp án đúng: " +
          ", ".join(f"{'ABCD'[i]}={pos.count(i)}" for i in range(4)))


if __name__ == "__main__":
    main()
