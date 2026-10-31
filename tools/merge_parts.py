#!/usr/bin/env python3
"""Ghép bài học từ nhiều phần (dùng khi bài dài, soạn từng phần một).

Dùng:  python3 merge_parts.py header.json part_01.json part_02.json ... -o lesson.json
  header.json : object gồm id, title, topic, source, sections (không có questions)
  part_XX.json: mảng các câu hỏi
"""
import argparse
import json
import pathlib

ap = argparse.ArgumentParser()
ap.add_argument("header")
ap.add_argument("parts", nargs="+")
ap.add_argument("-o", "--out", required=True)
a = ap.parse_args()

data = json.loads(pathlib.Path(a.header).read_text(encoding="utf-8"))
qs = []
for p in a.parts:
    part = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    if isinstance(part, dict):
        part = part.get("questions", [])
    qs.extend(part)
for i, q in enumerate(qs, 1):
    q["id"] = f"q{i:03d}"
data["questions"] = qs
pathlib.Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Đã ghép {len(qs)} câu vào {a.out}")
