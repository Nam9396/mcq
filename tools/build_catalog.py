#!/usr/bin/env python3
"""Dựng lại data/catalog.json từ toàn bộ file trong data/lessons/.

Chạy từ thư mục gốc của repo:  python3 tools/build_catalog.py
Chạy lại mỗi khi thêm, sửa hoặc xoá một bài học.
"""
import json
import pathlib
import sys
import unicodedata
from datetime import date

DEFAULT_TITLE = "Ôn trắc nghiệm"


def sort_key(s):
    s = unicodedata.normalize("NFD", str(s)).replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").casefold()


def build(repo):
    repo = pathlib.Path(repo)
    lessons_dir = repo / "data" / "lessons"
    cat_path = repo / "data" / "catalog.json"
    title = DEFAULT_TITLE
    if cat_path.exists():
        try:
            title = json.loads(cat_path.read_text(encoding="utf-8")).get("title") or DEFAULT_TITLE
        except Exception:
            pass
    items = []
    for p in sorted(lessons_dir.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Bỏ qua {p.name}: không đọc được JSON ({e})", file=sys.stderr)
            continue
        if d.get("id") != p.stem:
            print(f"Cảnh báo: {p.name} có id '{d.get('id')}' khác tên file", file=sys.stderr)
        items.append({
            "id": p.stem,
            "title": d.get("title", p.stem),
            "topic": d.get("topic", "Khác"),
            "count": len(d.get("questions", [])),
            "updated": d.get("updated", ""),
        })
    items.sort(key=lambda x: (sort_key(x["topic"]), sort_key(x["title"])))
    cat = {"title": title, "updated": date.today().isoformat(), "lessons": items}
    cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cat


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    cat = build(root)
    print(f"Đã cập nhật catalog.json: {len(cat['lessons'])} bài học")
    for l in cat["lessons"]:
        print(f"  [{l['topic']}] {l['title']} — {l['count']} câu")
