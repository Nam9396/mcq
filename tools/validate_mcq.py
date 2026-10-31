#!/usr/bin/env python3
"""Kiểm tra file bài học JSON cho app Ôn trắc nghiệm.

Dùng:  python3 validate_mcq.py lesson.json
Thoát mã 1 nếu có LỖI (phải sửa). CẢNH BÁO thì nên xem lại nhưng không chặn.
"""
import json
import re
import sys
from collections import Counter, defaultdict

MAX_Q = 100
TYPES = {"nho", "lam-sang"}
FORBIDDEN_OPTION = re.compile(
    r"(tất cả (các )?(đều|câu|ý|đáp án)|cả [abcd] (và|lẫn) [abcd]|[abcd] (và|,) ?[abcd] (đều )?đúng|"
    r"không (có )?(câu|ý|đáp án) nào|cả hai|cả ba|các câu trên|các ý trên|all of the above|none of the above)",
    re.IGNORECASE,
)
LETTER_PREFIX = re.compile(r"^\s*[A-Da-d][\.\)]\s")
NUMBER_IN_TEXT = re.compile(r"^\s*\**\s*câu\s*\d+", re.IGNORECASE)
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(data):
    """Trả về (errors, warnings, report). report là dict thống kê."""
    E, W = [], []

    def err(where, msg):
        E.append(f"{where}: {msg}")

    def warn(where, msg):
        W.append(f"{where}: {msg}")

    if not isinstance(data, dict):
        return ["Gốc file phải là một object JSON."], [], {}

    for f in ("id", "title", "topic", "sections", "questions"):
        if f not in data:
            err("bài học", f"thiếu trường '{f}'")
    if E:
        return E, W, {}

    if not SLUG.match(str(data["id"])):
        err("id", f"'{data['id']}' phải là chữ thường không dấu, nối bằng '-'")
    if data.get("updated") and not DATE.match(str(data["updated"])):
        err("updated", "phải có dạng YYYY-MM-DD")

    sections = data["sections"]
    if not isinstance(sections, list) or not sections or not all(isinstance(s, str) and s.strip() for s in sections):
        err("sections", "phải là danh sách tên phần, không rỗng")
        sections = []
    if len(set(sections)) != len(sections):
        err("sections", "có tên phần bị trùng")

    qs = data["questions"]
    if not isinstance(qs, list) or not qs:
        err("questions", "phải là danh sách không rỗng")
        return E, W, {}
    if len(qs) > MAX_Q:
        err("questions", f"có {len(qs)} câu, vượt giới hạn {MAX_Q}")

    ids = Counter()
    leads = Counter()
    per_section = defaultdict(Counter)
    longest_is_correct = 0
    answer_pos = Counter()
    negatives = 0

    for i, q in enumerate(qs, 1):
        w = f"câu #{i} ({q.get('id', '?')})" if isinstance(q, dict) else f"câu #{i}"
        if not isinstance(q, dict):
            err(w, "phải là object")
            continue
        for f in ("id", "type", "section", "stem", "lead", "options", "answer", "explanation"):
            if f not in q:
                err(w, f"thiếu trường '{f}'")
        if any(f not in q for f in ("type", "lead", "options", "answer")):
            continue

        ids[q.get("id")] += 1
        leads[str(q["lead"]).strip().lower()] += 1

        t = q["type"]
        if t not in TYPES:
            err(w, f"type '{t}' không hợp lệ (dùng 'nho' hoặc 'lam-sang')")
        sec = q.get("section")
        if sections and sec not in sections:
            err(w, f"section '{sec}' không có trong danh sách sections")
        per_section[sec][t] += 1

        stem = str(q.get("stem") or "")
        lead = str(q["lead"] or "")
        if not lead.strip():
            err(w, "lead (câu hỏi dẫn) rỗng")
        if NUMBER_IN_TEXT.match(stem) or NUMBER_IN_TEXT.match(lead):
            err(w, "không ghi 'Câu x' trong nội dung, app tự đánh số")
        if t == "lam-sang":
            if len(stem.strip()) < 60:
                err(w, "câu lâm sàng cần tình huống trong 'stem'")
            elif len(stem) > 700:
                warn(w, f"tình huống dài {len(stem)} ký tự (nên ≤ 700)")
        if t == "nho" and len(lead) > 220:
            warn(w, f"câu ghi nhớ dài {len(lead)} ký tự, nên rút gọn")
        if re.search(r"\b(KHÔNG|NGOẠI TRỪ|SAI)\b", lead):
            negatives += 1

        opts = q["options"]
        if not isinstance(opts, list) or len(opts) != 4:
            err(w, "phải có đúng 4 lựa chọn")
            continue
        if not all(isinstance(o, str) and o.strip() for o in opts):
            err(w, "có lựa chọn rỗng")
            continue
        if len({o.strip().lower() for o in opts}) != 4:
            err(w, "có lựa chọn trùng nhau")
        for k, o in enumerate(opts):
            if LETTER_PREFIX.match(o):
                err(w, f"lựa chọn {k + 1} có chữ cái đầu ('{o[:4]}'), app tự gắn chữ cái")
            if FORBIDDEN_OPTION.search(o):
                err(w, f"lựa chọn {k + 1} dạng 'tất cả / cả A và B' sẽ hỏng khi trộn: '{o}'")

        a = q["answer"]
        if not isinstance(a, int) or not 0 <= a <= 3:
            err(w, "answer phải là số nguyên 0–3")
            continue
        answer_pos[a] += 1

        if not str(q.get("explanation") or "").strip():
            err(w, "thiếu giải thích")
        ww = q.get("why_wrong")
        if ww is not None:
            if not isinstance(ww, list) or len(ww) != 4:
                err(w, "why_wrong phải là mảng 4 phần tử")
            else:
                for k in range(4):
                    if k != a and not (isinstance(ww[k], str) and ww[k].strip()):
                        warn(w, f"why_wrong thiếu lý do cho lựa chọn {k + 1}")

        lens = [len(o.strip()) for o in opts]
        mx, mn = max(lens), min(lens)
        if mn and mx / mn > 1.6 and mx - mn > 15:
            warn(w, f"độ dài lựa chọn chênh lệch nhiều ({mn}–{mx} ký tự)")
        others = sorted(lens[:a] + lens[a + 1:])
        if lens[a] == mx and lens[a] > others[-1] * 1.15 and lens[a] - others[-1] >= 6:
            longest_is_correct += 1
            warn(w, "đáp án đúng dài hơn hẳn các lựa chọn khác (dễ đoán)")

    for qid, c in ids.items():
        if c > 1:
            err("id", f"'{qid}' bị trùng {c} lần")
    for ld, c in leads.items():
        if c > 1 and ld:
            warn("trùng lặp", f"{c} câu có cùng câu dẫn: '{ld[:60]}…'")

    n = len(qs)
    for s in sections:
        if sum(per_section[s].values()) == 0:
            err("bao phủ", f"phần '{s}' chưa có câu hỏi nào")

    n_case = sum(c["lam-sang"] for c in per_section.values())
    share_case = n_case / n if n else 0
    if n >= 10 and not 0.38 <= share_case <= 0.52:
        warn("tỷ lệ", f"câu lâm sàng chiếm {share_case:.0%} (mục tiêu khoảng 45%, chấp nhận 40–50%)")
    if n >= 10 and longest_is_correct / n > 0.25:
        warn("độ dài", f"{longest_is_correct}/{n} câu có đáp án đúng dài nhất rõ rệt, người làm dễ đoán mò")
    if n and negatives / n > 0.10:
        warn("phủ định", f"{negatives} câu dùng KHÔNG/NGOẠI TRỪ/SAI (nên ≤ 10%)")

    report = {
        "n": n,
        "n_case": n_case,
        "n_recall": n - n_case,
        "per_section": {s: dict(per_section[s]) for s in sections},
        "answer_pos": dict(answer_pos),
    }
    return E, W, report


def print_report(data, E, W, R):
    print(f"Bài: {data.get('title')} ({data.get('id')})")
    if R:
        print(f"Tổng {R['n']} câu: {R['n_recall']} ghi nhớ, {R['n_case']} lâm sàng "
              f"({R['n_case'] / R['n']:.0%} lâm sàng)")
        print("\nPhân bổ theo phần:")
        width = max((len(s) for s in R["per_section"]), default=10)
        print(f"  {'Phần'.ljust(width)}  Nhớ  LS  Tổng")
        for s, c in R["per_section"].items():
            a, b = c.get("nho", 0), c.get("lam-sang", 0)
            print(f"  {s.ljust(width)}  {a:>3}  {b:>2}  {a + b:>4}")
    if W:
        print(f"\nCẢNH BÁO ({len(W)}):")
        for x in W:
            print("  - " + x)
    if E:
        print(f"\nLỖI ({len(E)}) — phải sửa:")
        for x in E:
            print("  - " + x)
    else:
        print("\nKhông có lỗi.")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    E, W, R = validate(data)
    print_report(data, E, W, R)
    sys.exit(1 if E else 0)


if __name__ == "__main__":
    main()
