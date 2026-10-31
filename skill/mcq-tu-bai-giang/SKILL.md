---
name: mcq-tu-bai-giang
description: Soạn bộ câu hỏi trắc nghiệm ôn tập từ file bài giảng (pdf, docx, pptx, md) và xuất thành file JSON cho app Ôn trắc nghiệm (PWA trên GitHub Pages). Dùng khi người dùng gửi bài giảng và muốn tạo MCQ để tự ôn, hoặc gọi /mcq-tu-bai-giang.
---

# Soạn trắc nghiệm từ bài giảng cho app Ôn trắc nghiệm

Kết quả: **một file JSON cho mỗi bài giảng**, ghi vào `data/lessons/<id>.json` của repo app trên máy người dùng, kèm `data/catalog.json` dựng lại. Người dùng tự `git push`. Skill **không** viết hay sửa code app; app tự trộn câu, trộn đáp án, chấm điểm và cho làm lại câu sai.

Làm **một mạch** từ đầu đến cuối, không dừng hỏi giữa chừng. Người dùng duyệt sau qua file duyệt đề.

**Nhận diện repo app**: thư mục có `index.html`, `app.js`, `data/catalog.json`, `data/lessons/` và `tools/validate_mcq.py`. Tên thư mục tuỳ người dùng.

Các script kiểm tra nằm trong repo, thư mục `tools/`:
- `validate_mcq.py <bai.json>` — kiểm tra; thoát mã 1 nếu có LỖI.
- `publish.py <bai.json> --repo <repo>` — kiểm tra, đổi id câu thành mã ổn định, điền ngày, ghi vào `data/lessons/`, dựng lại `catalog.json`. `--out <dir>` để chỉ xuất file.
- `render_review.py <bai.json> -o duyet_<id>.html` — trang HTML duyệt đề, mở trực tiếp.
- `merge_parts.py header.json part_*.json -o <id>.json` — ghép bài dài soạn theo phần.

---

## Quy trình

### Bước 1. Đọc bài giảng
- Đọc toàn bộ file bài giảng (dùng skill đọc file theo định dạng). Mỗi file là một bài học; nhiều file thì làm lần lượt.
- Xác định `title`, `topic` (chuyên đề để nhóm bài trong danh mục; nếu danh mục đã có chuyên đề phù hợp thì dùng lại đúng tên đó), `id` (chữ thường không dấu, nối bằng `-`), `sections` (theo đề mục bài giảng, khoảng 4–10 phần).

### Bước 2. Lấy script và danh mục từ repo
- Nếu chat nối được với máy người dùng: tìm repo app trong các thư mục đã kết nối theo dấu hiệu nhận diện ở trên (xin quyền truy cập nếu chưa có; hỏi đường dẫn nếu không tìm thấy). Chép `tools/*.py`, `data/catalog.json` và `data/lessons/*.json` về một bản sao trong workspace, ví dụ `repo/`.
- Nếu không truy cập được máy: soạn tiếp bình thường, kiểm tra thủ công theo mục "Quy tắc" bên dưới, và ở Bước 6 dùng phương án B.

### Bước 3. Lập blueprint (nội bộ, không hỏi người dùng)
- Quyết định tổng số câu (tối đa 100) và số câu ghi nhớ / lâm sàng cho từng phần theo mục "Phân bổ".
- Liệt kê các ý cần hỏi cho từng phần để tránh trùng và bỏ sót.

### Bước 4. Soạn và tự rà soát
- Viết theo mục "Quy tắc", "Mẫu tình huống", đúng "Định dạng JSON".
- Bài trên 40 câu: soạn `parts/header.json` (không có questions) và `parts/part_01.json`, `part_02.json`… (mỗi part là mảng câu hỏi), rồi ghép bằng `merge_parts.py`.
- Đọc lại toàn bộ theo checklist "Tự rà soát" trước khi chạy validator.

### Bước 5. Kiểm tra tự động
```
python3 repo/tools/validate_mcq.py <id>.json
```
- **LỖI**: sửa hết, chạy lại.
- **CẢNH BÁO**: sửa nếu hợp lý (nhất là "đáp án đúng dài hơn hẳn", "độ dài chênh lệch", "tỷ lệ"). Cảnh báo nào giữ nguyên thì ghi lý do trong báo cáo.

### Bước 6. Ghi vào repo
**A. Truy cập được máy**
1. `python3 repo/tools/publish.py <id>.json --repo repo`
2. Ghi trở lại máy đúng 2 file: `data/lessons/<id>.json` và `data/catalog.json`.
3. Nếu đã có bài cùng `id`: coi là bản cập nhật của cùng bài giảng, ghi đè. Nếu là bài giảng khác trùng tên, đặt `id` khác.

**B. Không truy cập được máy**
Gửi file `<id>.json` cho người dùng, kèm hướng dẫn: chép vào `data/lessons/` của repo, chạy `python3 tools/publish.py data/lessons/<id>.json` ở thư mục gốc repo (script sẽ kiểm tra và cập nhật danh mục), rồi push.

### Bước 7. File duyệt đề và báo cáo
- Tạo `duyet_<id>.html` bằng `render_review.py` (phương án B không có script thì bỏ qua, người dùng duyệt trong app ở mục "Xem toàn bộ đề và đáp án").
- Gửi file duyệt cho người dùng. Báo cáo ngắn:
  - Tên bài, tổng số câu, số câu ghi nhớ / lâm sàng.
  - File đã ghi ở đâu, lệnh git:
    ```
    cd <repo>
    git add data
    git commit -m "Thêm bài: <title>"
    git push
    ```
  - **Điểm cần xem lại**: chỗ bài giảng có vẻ mâu thuẫn hoặc lỗi thời, câu mà đáp án phụ thuộc cách hiểu, cảnh báo validator còn giữ.
  - Mời góp ý theo số câu trong file duyệt (ví dụ "câu 12 mồi nhử yếu"). Khi sửa: chỉnh JSON, chạy lại bước 5–7.

---

## Quy tắc ra đề

### Hai loại câu
**Câu ghi nhớ** (`"type": "nho"`)
- Hỏi trực tiếp một ý trong bài: định nghĩa, tác nhân, cơ chế, tiêu chuẩn, ngưỡng, liều, chỉ định, chống chỉ định.
- `stem` để `""`, toàn bộ câu hỏi nằm trong `lead`. Ngắn, khoảng 30 từ trở xuống.
- Hạn chế câu phủ định; nếu dùng, viết **KHÔNG** in đậm, không quá 10% tổng số câu.

**Câu lâm sàng** (`"type": "lam-sang"`)
- Tình huống theo "Mẫu tình huống". Được tự do sáng tạo bệnh cảnh, nhưng đáp án phải khớp bài giảng.
- Đòi hỏi phân tích hoặc áp dụng: chẩn đoán, phân độ, đọc cận lâm sàng, xử trí bước tiếp theo, chọn thuốc/liều, nhận diện biến chứng.
- Phép thử "che tình huống": nếu che `stem` mà vẫn trả lời được `lead` thì đó là câu ghi nhớ trá hình, viết lại.
- Mỗi câu độc lập. Không viết chuỗi câu dùng chung tình huống, vì app trộn thứ tự.
- Bài giảng không thuộc lĩnh vực lâm sàng (khoa học cơ bản, quản lý…): vẫn dùng `type: "lam-sang"` cho câu tình huống ứng dụng, viết tình huống thực tế phù hợp lĩnh vực thay cho bệnh án.

### Phân bổ
- Mỗi phần trong `sections` có ít nhất 1 câu.
- Tỷ lệ chung khoảng **55% ghi nhớ / 45% lâm sàng** (chấp nhận 50–60% ghi nhớ).
- Định nghĩa, dịch tễ, bệnh sinh: chủ yếu ghi nhớ. Chẩn đoán, phân độ, điều trị, biến chứng: ưu tiên lâm sàng.
- Phần trọng tâm được nhiều câu hơn. Một ý tối đa 2 câu, hỏi từ hai góc khác nhau.
- Số câu theo độ dài bài, tối đa 100. Gợi ý: bài ngắn 20–30, trung bình 40–60, dài 70–100.

### Đáp án và mồi nhử
- Đúng 4 lựa chọn, 1 đáp án đúng nhất.
- Mồi nhử phải là thứ người chưa vững bài thật sự có thể chọn: sai lầm hay gặp, khái niệm/bệnh gần, con số gần đúng cùng đơn vị, hành động đúng nhưng sai thời điểm hoặc không phải ưu tiên.
- Đồng nhất: cùng loại (cùng là thuốc, cùng là xét nghiệm…), cùng cấu trúc câu, cùng mức độ cụ thể, độ dài chênh không quá khoảng 50%. Đáp án đúng không được dài nhất, chi tiết nhất hay nhiều điều kiện nhất một cách nổi bật.
- Cấm: "Tất cả đều đúng/sai", "Cả A và B", "Không câu nào đúng"; ghi chữ cái "A." hay "Câu 1" trong nội dung (app tự gắn); đáp án đúng lặp từ khoá của câu dẫn; từ tuyệt đối ("luôn luôn", "không bao giờ", "chỉ") chỉ xuất hiện ở mồi nhử.
- Không cần sắp vị trí đáp án đúng; app trộn mỗi lần làm.

### Giải thích
- `explanation`: 1–3 câu, vì sao đáp án đúng, bám bài giảng. Câu lâm sàng thì chỉ ra dữ kiện nào dẫn đến đáp án.
- `why_wrong`: mảng 4 phần tử theo thứ tự `options`, mỗi mồi nhử 1 câu ngắn nói vì sao sai, `null` ở vị trí đáp án đúng.

### Bám nguồn
- Đáp án, con số, ngưỡng, liều lấy từ bài giảng. Kiến thức nội tại chỉ dùng để dựng tình huống và viết mồi nhử.
- Bài giảng khác kiến thức nội tại hoặc có vẻ lỗi thời: vẫn theo bài giảng và ghi vào "Điểm cần xem lại".
- Không ra câu về nội dung không có trong bài giảng.

### Văn phong
Viết theo ngôn ngữ của bài giảng (mặc định tiếng Việt), thuật ngữ chuẩn của chuyên ngành, câu ngắn, dễ đọc trên điện thoại. Viết tắt phổ biến (Hct, CRP, SpO₂, HA, CRT, BC). Không bẫy câu chữ, không phủ định kép.

### Tự rà soát
1. Câu này kiểm tra ý nào? Ý đó đã hỏi ở câu khác chưa?
2. Người chưa học có đoán được nhờ độ dài, độ cụ thể hay từ khoá không?
3. Mỗi mồi nhử có người chưa vững bài sẽ chọn không?
4. Câu lâm sàng có qua phép thử "che tình huống" không?
5. Đáp án có khớp bài giảng không?

---

## Mẫu tình huống lâm sàng

```
Bệnh nhân [nam/nữ], [tuổi], [cân nặng] kg (nếu liên quan), [nhập viện / đến khám] vì [lý do], [ngày bệnh thứ n].
- N1–N2: [sự kiện]
- N3: [sự kiện]
- N4: [sự kiện dẫn đến nhập viện]
Tiền căn: [chỉ ghi nếu liên quan]
Điều trị trước đó: [nếu có]
Khám: [tri giác]. Mạch …, HA …, nhịp thở …, nhiệt độ …, SpO₂ …, CRT …. [dấu hiệu chính].
Cận lâm sàng: [kết quả cần cho câu hỏi, kèm giá trị so sánh nếu cần].
```
- `stem` khoảng 60–120 từ, không quá 700 ký tự. Mỗi dòng một sự kiện theo dòng thời gian, đầu dòng `- ` để app hiển thị gạch đầu dòng.
- Chỉ đưa dữ kiện cần cho câu hỏi, cộng 1–2 dữ kiện nhiễu hợp lý. Bỏ các dòng không dùng (tiền căn, điều trị trước).
- Sinh hiệu, cân nặng hợp lý theo tuổi. Trẻ em ghi cân nặng; sơ sinh ghi ngày tuổi, tuổi thai, cân nặng lúc sinh khi cần.
- Không tiết lộ đáp án trong tình huống.
- `lead` một câu, hỏi một việc: "Chẩn đoán phù hợp nhất là gì?", "Xử trí tiếp theo phù hợp nhất là gì?".

**Ví dụ tốt**
- stem: "Bệnh nhân nam, 7 tuổi, 22 kg, nhập viện vì sốt ngày 5.\n- N1–N3: sốt cao 39–40 °C, đau đầu, đau cơ.\n- N4: giảm sốt, đau bụng, nôn 3 lần.\n- N5: lừ đừ, tay chân lạnh.\nKhám: tỉnh, lừ đừ. Mạch 130 lần/phút, nhẹ. HA 100/85 mmHg. CRT 3 giây. Gan 3 cm dưới bờ sườn.\nCận lâm sàng: Hct 48% (N2: 38%), tiểu cầu 40.000/mm³."
- lead: "Chẩn đoán phân độ phù hợp nhất là gì?"
- options: "Sốt xuất huyết Dengue có dấu hiệu cảnh báo" / "Sốc sốt xuất huyết Dengue" (đúng) / "Sốc sốt xuất huyết Dengue nặng" / "Sốt xuất huyết Dengue nặng do xuất huyết"
- Vì sao tốt: 4 lựa chọn cùng loại, độ dài tương đương; mồi nhử là các mức độ liền kề; phải đọc sinh hiệu mới trả lời được.

---

## Định dạng JSON

```json
{
  "id": "viem-mang-nao-vi-khuan",
  "title": "Viêm màng não vi khuẩn",
  "topic": "Truyền nhiễm",
  "updated": "2026-10-31",
  "source": "ten_file_bai_giang.pdf",
  "sections": ["Dịch tễ", "Lâm sàng", "Chẩn đoán", "Điều trị", "Biến chứng"],
  "questions": [
    {
      "id": "q001",
      "type": "nho",
      "section": "Dịch tễ",
      "stem": "",
      "lead": "…?",
      "options": ["…", "…", "…", "…"],
      "answer": 0,
      "explanation": "…",
      "why_wrong": [null, "…", "…", "…"]
    }
  ]
}
```
- `id` bài = tên file. `section` của câu phải trùng một mục trong `sections`.
- `type`: `"nho"` hoặc `"lam-sang"`. `answer`: chỉ số 0–3 trong `options`.
- `stem`, `lead`, `explanation` hỗ trợ `\n`, dòng bắt đầu `- `, `**đậm**`, `*nghiêng*`.
- `publish.py` tự đổi `id` câu thành mã băm từ nội dung (giữ đúng lịch sử câu sai trên điện thoại khi bài được cập nhật) và tự điền `updated`.

## Ràng buộc
- Không quá 100 câu một bài; mỗi câu đúng 4 lựa chọn, 1 đáp án, có giải thích.
- Không sửa code app (`index.html`, `app.js`, `styles.css`, `sw.js`) trừ khi người dùng yêu cầu riêng.
- Không tự `git push`.
