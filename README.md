# Ôn trắc nghiệm

App ôn bài bằng câu hỏi trắc nghiệm (MCQ), chạy trên điện thoại dạng PWA: cài lên màn hình chính, dùng được khi không có mạng. Không cần máy chủ, không cần build, host miễn phí bằng GitHub Pages.

- Mỗi bài giảng là một file JSON trong `data/lessons/`.
- Mỗi lần làm bài, app trộn thứ tự câu và đáp án, chấm điểm, hiện đáp án đúng và lý do cho câu sai, và cho **làm lại các câu sai**.
- Điểm và danh sách câu sai lưu trên chính thiết bị (không đồng bộ giữa các máy).
- Đi kèm skill **`mcq-tu-bai-giang`** cho Claude: gửi file bài giảng, Claude soạn đề và ghi file JSON vào thư mục này.

## Cấu trúc

```
├── index.html, app.js, styles.css   # giao diện (không cần sửa khi thêm bài)
├── manifest.webmanifest, sw.js       # PWA: cài lên màn hình chính, chạy offline
├── icons/
├── data/
│   ├── catalog.json                  # danh mục bài, dựng tự động
│   └── lessons/<id>.json             # mỗi bài một file
└── tools/                            # script Python 3, không cần cài thêm thư viện
    ├── validate_mcq.py               # kiểm tra file bài học
    ├── publish.py                    # kiểm tra + chuẩn hoá + ghi vào data/ + dựng danh mục
    ├── render_review.py              # tạo trang HTML duyệt đề
    ├── merge_parts.py                # ghép bài dài soạn theo từng phần
    └── build_catalog.py              # dựng lại data/catalog.json
└── skill/mcq-tu-bai-giang/SKILL.md   # skill cho Claude, để chia sẻ cùng app
```

## Cài đặt lần đầu

1. Tạo một repo **public** trên GitHub (tên tuỳ ý, ví dụ `mcq`), đưa toàn bộ thư mục này lên.
2. Trên GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, chọn nhánh `main`, thư mục `/ (root)`, bấm **Save**.
3. Sau 1–2 phút, app có địa chỉ `https://<tên-tài-khoản>.github.io/<tên-repo>/`.
4. Cài lên điện thoại:
   - **iPhone (Safari)**: mở địa chỉ trên → nút Chia sẻ → *Thêm vào MH chính*.
   - **Android (Chrome)**: mở địa chỉ trên → menu ⋮ → *Cài đặt ứng dụng* / *Thêm vào màn hình chính*.

Đổi tên app hiển thị trên trang chủ: sửa trường `"title"` trong `data/catalog.json`.

## Cài skill vào Claude

File `skill/mcq-tu-bai-giang/SKILL.md` chứa toàn bộ quy trình và quy tắc ra đề. Thêm skill này vào phần Skills trong Claude của bạn (tải lên thư mục `mcq-tu-bai-giang`, hoặc nhờ Claude tạo skill từ nội dung file). Các script kiểm tra nằm ở `tools/` của repo, skill tự tìm khi được gắn thư mục repo.

## Thêm hoặc cập nhật bài

**Cách 1: dùng skill `mcq-tu-bai-giang` trong Claude**
1. Gắn thư mục này vào Claude (nếu dùng Claude desktop) và gửi file bài giảng kèm lệnh gọi skill.
2. Claude ghi `data/lessons/<id>.json` và cập nhật `data/catalog.json`. Nếu Claude không truy cập được thư mục, Claude gửi file JSON; chép vào `data/lessons/` rồi chạy:
   ```
   python3 tools/publish.py data/lessons/<id>.json
   ```
3. Đưa lên GitHub:
   ```
   git add data
   git commit -m "Thêm bài: <tên bài>"
   git push
   ```
4. Mở app khi có mạng là thấy bài mới.

**Cách 2: tự viết file JSON** theo định dạng ở mục dưới, rồi chạy `python3 tools/publish.py <file>.json` để kiểm tra và đưa vào repo.

**Xoá bài**: xoá file trong `data/lessons/`, chạy `python3 tools/build_catalog.py`, rồi push. Bài mẫu `demo-dengue.json` có thể xoá khi đã có bài thật.

## Định dạng file bài học

```json
{
  "id": "ten-bai-khong-dau",
  "title": "Tên bài",
  "topic": "Chuyên đề",
  "updated": "2026-10-31",
  "sections": ["Phần 1", "Phần 2"],
  "questions": [
    {
      "id": "q001",
      "type": "nho",
      "section": "Phần 1",
      "stem": "",
      "lead": "Câu hỏi?",
      "options": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
      "answer": 0,
      "explanation": "Vì sao đáp án đúng.",
      "why_wrong": [null, "Vì sao sai", "Vì sao sai", "Vì sao sai"]
    }
  ]
}
```

- `type`: `"nho"` (câu ghi nhớ) hoặc `"lam-sang"` (câu tình huống, nội dung tình huống đặt trong `stem`).
- `answer`: vị trí đáp án đúng trong `options` (0–3). Không ghi chữ A/B/C/D hay "Câu x" trong nội dung, app tự gắn.
- `stem`, `lead`, `explanation` hỗ trợ xuống dòng `\n`, dòng bắt đầu bằng `- `, `**đậm**`, `*nghiêng*`.
- `publish.py` tự đổi `id` câu thành mã tạo từ nội dung, để lịch sử câu sai không bị lệch khi bài được cập nhật.

## Chạy thử trên máy tính

Không mở `index.html` trực tiếp (trình duyệt chặn đọc file JSON). Chạy trong thư mục này:

```
python3 -m http.server 8000
```

rồi mở `http://localhost:8000`.

## Cập nhật giao diện

Sau khi sửa `app.js` / `styles.css`, thiết bị sẽ nhận bản mới ở lần mở thứ hai. Nếu đổi danh sách file giao diện, tăng `CACHE` trong `sw.js` (ví dụ `mcq-v2`).
