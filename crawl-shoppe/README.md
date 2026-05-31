# Shopee Product Crawling & Dashboard

Dự án này dùng để cào dữ liệu sản phẩm, cào đánh giá Shopee, làm sạch dữ liệu và chạy dashboard phân tích/xếp hạng sản phẩm.

---

## 1. Cấu trúc thư mục

```text
crawl-shoppe/
│
├── .venv/
├── chrome_profile/
├── chrome_real_profile/
│
├── app.py
├── crawl_multi_shop_products.py
├── auto_capture_reviews.py
├── clean_shopee_data.py
│
├── shopee_products.csv
├── shopee_products_clean.csv
├── shopee_reviews.csv
├── shopee_reviews_clean.csv
├── ranked_products_final.csv
│
└── README.md
```

---

## 2. Cài đặt môi trường

Vào thư mục dự án:

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
```

Tạo môi trường ảo:

```bash
python3 -m venv .venv
```

Kích hoạt môi trường ảo:

```bash
source .venv/bin/activate
```

Cài thư viện cần thiết:

```bash
pip install pandas requests websocket-client streamlit plotly numpy scikit-learn matplotlib seaborn
```

---

## 3. Mở Chrome debug

Trước khi cào dữ liệu Shopee, cần mở Chrome bằng profile thật.

Chạy lệnh này ở Terminal 1:

```bash
cd /Users/nhuhong/Documents/crawl-shoppe

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
--remote-debugging-port=9222 \
'--remote-allow-origins=*' \
--user-data-dir="/Users/nhuhong/Documents/crawl-shoppe/chrome_real_profile"
```

Kiểm tra Chrome debug đã chạy chưa:

```bash
ps aux | grep "remote-debugging-port=9222"
```

Nếu thấy dòng có:

```text
--user-data-dir=/Users/nhuhong/Documents/crawl-shoppe/chrome_real_profile
--remote-debugging-port=9222
```

là đúng.

---

## 4. Cào dữ liệu sản phẩm

Chạy ở Terminal 2:

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python crawl_multi_shop_products.py
```

Dữ liệu sản phẩm sẽ được lưu vào:

```text
shopee_products.csv
```

---

## 5. Cào dữ liệu đánh giá

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python auto_capture_reviews.py
```

Dữ liệu đánh giá sẽ được lưu vào:

```text
shopee_reviews.csv
```

---

## 6. Làm sạch dữ liệu

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python clean_shopee_data.py
```

Sau khi chạy xong sẽ tạo ra các file:

```text
shopee_products_clean.csv
shopee_reviews_clean.csv
ranked_products_final.csv
```

---

## 7. Chạy dashboard

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
streamlit run app.py
```

Sau đó mở trình duyệt tại:

```text
http://localhost:8501
```

---

## 8. Chạy toàn bộ quy trình

Terminal 1: mở Chrome debug

```bash
cd /Users/nhuhong/Documents/crawl-shoppe

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
--remote-debugging-port=9222 \
--user-data-dir="/Users/nhuhong/Documents/crawl-shoppe/chrome_real_profile"
```

Terminal 2: chạy crawl, clean và dashboard

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate

python crawl_multi_shop_products.py
python auto_capture_reviews.py
python clean_shopee_data.py
streamlit run app.py
```

---

## 9. Chỉ chạy dashboard khi đã có dữ liệu

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
streamlit run app.py
```

---

## 10. Chỉ chạy lại phần cào sản phẩm

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python crawl_multi_shop_products.py
```

---

## 11. Chỉ chạy lại phần cào đánh giá

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python auto_capture_reviews.py
```

---

## 12. Chỉ chạy lại phần làm sạch dữ liệu

```bash
cd /Users/nhuhong/Documents/crawl-shoppe
source .venv/bin/activate
python clean_shopee_data.py
```