#!/usr/bin/env python3
"""Tạo trang HTML độc lập để duyệt đề (mở trực tiếp bằng trình duyệt, không cần server).

Dùng:  python3 render_review.py lesson.json -o duyet_de.html
"""
import argparse
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate_mcq import validate  # noqa: E402

LETTERS = "ABCD"


def inline(s):
    s = html.escape(str(s or ""))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(^|[^*])\*([^*\n]+)\*", r"\1<em>\2</em>", s)
    return s


def md(text):
    if not text:
        return ""
    lines = re.sub(r"</?br\s*/?>", "\n", str(text), flags=re.I).split("\n")
    out, in_list = [], False
    for raw in lines:
        line = raw.rstrip()
        m = re.match(r"^\s*[-•]\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)


def with_number(h, n):
    label = f'<strong class="qnum">Câu {n}.</strong> '
    return h.replace("<p>", "<p>" + label, 1) if h.startswith("<p>") else f"<p>{label}</p>{h}"


CSS = """
:root{--bg:#f6f5f1;--surface:#fff;--surface-2:#efede7;--ink:#1c2321;--muted:#6a736f;--line:#e2dfd7;
--accent:#0f6e64;--accent-soft:#e2f0ed;--ok:#1d7a44;--ok-soft:#e4f3e9;--bad:#b3372e;--bad-soft:#fbe8e5;
--warn:#8a5a00;--warn-soft:#fbf1dc;--case:#7a4fb0;--case-soft:#efe8f8}
@media (prefers-color-scheme:dark){:root{--bg:#111514;--surface:#1a1f1e;--surface-2:#232928;--ink:#e7ebe9;
--muted:#98a29e;--line:#2c3331;--accent:#4fb3a6;--accent-soft:#163330;--ok:#5fc58b;--ok-soft:#15301f;
--bad:#f0877d;--bad-soft:#3a1d1a;--warn:#e8b65a;--warn-soft:#3a2e14;--case:#b896e6;--case-soft:#2a2238}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:820px;margin:0 auto;padding:20px 16px 48px}
h1{font-size:1.5rem;margin:4px 0}h2{font-size:1.1rem;margin:28px 0 10px}
p{margin:0}p+p{margin-top:.3em}ul{margin:.3em 0;padding-left:1.2em}.muted{color:var(--muted)}
.box{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin-top:14px}
table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}tfoot td{font-weight:700;border-bottom:0}
.warn{background:var(--warn-soft);border-color:transparent}.warn li{margin:2px 0}
.q{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:12px;break-inside:avoid}
.qnum{color:var(--accent)}.lead{margin-top:10px;padding-top:10px;border-top:1px dashed var(--line);font-weight:600}
.lead.only{margin-top:0;padding-top:0;border-top:0}
.tag{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:999px;margin-bottom:8px}
.t-nho{background:var(--accent-soft);color:var(--accent)}.t-ls{background:var(--case-soft);color:var(--case)}
.opts{list-style:none;padding:0;margin:12px 0 0;display:flex;flex-direction:column;gap:6px}
.opts li{display:flex;gap:10px;padding:8px 10px;border-radius:10px;border:1px solid var(--line);font-size:.95rem}
.opts li.ok{background:var(--ok-soft);border-color:transparent}
.L{flex:none;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--surface-2);font-weight:700;font-size:.8rem}
.ok .L{background:var(--ok);color:#fff}.why{display:block;color:var(--muted);font-size:.85rem;margin-top:2px}
.ex{background:var(--surface-2);border-radius:10px;padding:10px 12px;margin-top:10px;font-size:.94rem}
.lbl{display:block;font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:2px}
.qid{float:right;color:var(--muted);font-size:.75rem;font-family:ui-monospace,monospace}
@media print{body{background:#fff}.q,.box{border-color:#ccc}}
"""


def render(data):
    E, W, R = validate(data)
    sections = data.get("sections") or sorted({q.get("section", "Khác") for q in data["questions"]})
    rows = []
    for s in sections:
        c = R.get("per_section", {}).get(s, {})
        a, b = c.get("nho", 0), c.get("lam-sang", 0)
        rows.append(f"<tr><td>{inline(s)}</td><td class=n>{a}</td><td class=n>{b}</td><td class=n>{a + b}</td></tr>")
    n = R.get("n", len(data["questions"]))
    summary = (
        "<div class=box><table><thead><tr><th>Phần</th><th class=n>Ghi nhớ</th><th class=n>Lâm sàng</th><th class=n>Tổng</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody><tfoot><tr><td>Tổng</td><td class=n>{R.get('n_recall', '')}</td>"
        f"<td class=n>{R.get('n_case', '')}</td><td class=n>{n}</td></tr></tfoot></table></div>"
    )
    issues = ""
    if E or W:
        items = "".join(f"<li><b>Lỗi:</b> {html.escape(x)}</li>" for x in E) + "".join(f"<li>{html.escape(x)}</li>" for x in W)
        issues = f"<div class='box warn'><b>Kiểm tra tự động ({len(E)} lỗi, {len(W)} cảnh báo)</b><ul>{items}</ul></div>"

    body, k = [], 0
    for s in sections:
        qs = [q for q in data["questions"] if q.get("section") == s]
        if not qs:
            continue
        body.append(f"<h2>{inline(s)} <span class=muted>· {len(qs)} câu</span></h2>")
        for q in qs:
            k += 1
            stem, lead = md(q.get("stem")), md(q.get("lead"))
            qhtml = (f"<div class=stem>{with_number(stem, k)}</div><div class=lead>{lead}</div>"
                     if stem else f"<div class='lead only'>{with_number(lead, k)}</div>")
            ww = q.get("why_wrong") or [None] * 4
            opts = "".join(
                f"<li class='{'ok' if i == q['answer'] else ''}'><span class=L>{LETTERS[i]}</span><span>{inline(o)}"
                + (f"<span class=why>{inline(ww[i])}</span>" if i < len(ww) and ww[i] else "")
                + "</span></li>"
                for i, o in enumerate(q["options"])
            )
            tag = "<span class='tag t-ls'>Lâm sàng</span>" if q.get("type") == "lam-sang" else "<span class='tag t-nho'>Ghi nhớ</span>"
            body.append(
                f"<article class=q><span class=qid>{html.escape(str(q.get('id', '')))}</span>{tag}{qhtml}"
                f"<ul class=opts>{opts}</ul><div class=ex><span class=lbl>Giải thích</span>{md(q.get('explanation'))}</div></article>"
            )

    title = html.escape(data.get("title", ""))
    meta = " · ".join(x for x in [html.escape(data.get("topic", "")), f"{n} câu",
                                  html.escape(data.get("source", "")) and "Nguồn: " + html.escape(data.get("source", ""))] if x)
    return (f"<!doctype html><html lang=vi><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>Duyệt đề · {title}</title><style>{CSS}</style></head><body><main>"
            f"<p class=muted>Bản duyệt đề</p><h1>{title}</h1><p class=muted>{meta}</p>{summary}{issues}{''.join(body)}</main></body></html>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    data = json.loads(pathlib.Path(a.lesson).read_text(encoding="utf-8"))
    out = pathlib.Path(a.out or f"duyet_{data.get('id', 'de')}.html")
    out.write_text(render(data), encoding="utf-8")
    print(f"Đã tạo {out}")


if __name__ == "__main__":
    main()
