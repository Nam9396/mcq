#!/usr/bin/env python3
"""Đưa một file bài học vào repo app và dựng lại danh mục.

Dùng (từ thư mục gốc repo):
  python3 tools/publish.py duong/dan/bai.json            -> ghi vào data/lessons/ của repo này
  python3 tools/publish.py bai.json --repo /duong/dan/repo
  python3 tools/publish.py bai.json --out ./xuat         -> chỉ xuất file đã chuẩn hoá

Các bước:
  1. Kiểm tra bằng validate_mcq (có LỖI thì dừng).
  2. Đổi id câu hỏi thành mã ổn định băm từ nội dung (giữ đúng lịch sử câu sai trên điện thoại).
  3. Điền ngày cập nhật.
  4. Ghi vào <repo>/data/lessons/<id>.json và dựng lại <repo>/data/catalog.json.
"""
import argparse
import hashlib
import json
import pathlib
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate_mcq import validate, print_report  # noqa: E402
from build_catalog import build as build_catalog  # noqa: E402

def stable_ids(data):
    seen = set()
    for q in data["questions"]:
        basis = (q.get("stem", "") + "\n" + q["lead"] + "\n" + q["options"][q["answer"]]).strip().lower()
        h = "h" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:8]
        while h in seen:
            h = "h" + hashlib.sha1((h + basis).encode("utf-8")).hexdigest()[:8]
        seen.add(h)
        q["id"] = h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--repo", help="thư mục gốc repo app (mặc định: thư mục cha của tools/)")
    g.add_argument("--out", help="chỉ xuất file đã chuẩn hoá, không ghi vào repo")
    args = ap.parse_args()
    if not args.out and not args.repo:
        args.repo = str(pathlib.Path(__file__).resolve().parent.parent)

    data = json.loads(pathlib.Path(args.lesson).read_text(encoding="utf-8"))
    E, W, R = validate(data)
    print_report(data, E, W, R)
    if E:
        print("\nDừng: sửa hết LỖI rồi chạy lại.")
        sys.exit(1)

    stable_ids(data)
    data["updated"] = date.today().isoformat()
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    if args.repo:
        repo = pathlib.Path(args.repo)
        lessons_dir = repo / "data" / "lessons"
        if not lessons_dir.is_dir():
            print(f"Không thấy {lessons_dir}. Kiểm tra lại đường dẫn repo.")
            sys.exit(1)
        target = lessons_dir / f"{data['id']}.json"
        existed = target.exists()
        target.write_text(text, encoding="utf-8")
        cat = build_catalog(repo)
        print(f"\n{'Đã cập nhật' if existed else 'Đã thêm'} {target}")
        print(f"Danh mục hiện có {len(cat['lessons'])} bài.")
        print("\nĐể đưa lên GitHub:")
        print(f'  cd "{repo}"')
        print("  git add data")
        print(f'  git commit -m "{"Cập nhật" if existed else "Thêm"} bài: {data["title"]}"')
        print("  git push")
    else:
        out = pathlib.Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        target = out / f"{data['id']}.json"
        target.write_text(text, encoding="utf-8")
        print(f"\nĐã xuất {target}")
        print("Chép file vào data/lessons/ của repo, rồi chạy: python3 tools/build_catalog.py")


if __name__ == "__main__":
    main()
