import json
import time
import itertools
import os

import pandas as pd
import requests
import websocket


PRODUCT_FILE = "shopee_products.csv"
OUTPUT_FILE = "shopee_reviews.csv"

TARGET_REVIEWS = 12000
MAX_PRODUCTS = 400

MAX_REVIEW_PAGES_PER_PRODUCT = 50
WAIT_EACH_REVIEW_PAGE = 8
NO_NEW_LIMIT = 2


def cdp_connect():
    tab = requests.put("http://localhost:9222/json/new").json()
    ws_url = tab["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url)

    counter = itertools.count(1)

    def send(method, params=None):
        msg_id = next(counter)
        ws.send(json.dumps({
            "id": msg_id,
            "method": method,
            "params": params or {}
        }))
        return msg_id

    return ws, send


def get_response_body(ws, send, request_id):
    body_id = send("Network.getResponseBody", {
        "requestId": request_id
    })

    while True:
        msg = json.loads(ws.recv())

        if msg.get("id") == body_id:
            return msg.get("result", {}).get("body", "")


def parse_reviews(data, product):
    rows = []
    ratings = data.get("data", {}).get("ratings", [])

    for r in ratings:
        comment = r.get("comment", "")

        if not comment:
            continue

        rows.append({
            "shop": product.get("shop", ""),
            "shop_id": product.get("shop_id", ""),
            "item_id": product.get("item_id", ""),
            "product_name": product.get("product_name", ""),
            "product_url": product.get("product_url", ""),
            "review_text": comment,
            "review_star": r.get("rating_star"),
            "author_username": r.get("author_username"),
            "ctime": r.get("ctime"),
            "model_name": r.get("product_items", [{}])[0].get("model_name") if r.get("product_items") else "",
            "liked_count": r.get("liked_count")
        })

    return rows


def save_reviews(rows):
    if not rows:
        return 0

    new_df = pd.DataFrame(rows)

    if os.path.exists(OUTPUT_FILE):
        try:
            old_df = pd.read_csv(OUTPUT_FILE)

            if old_df.empty:
                df = new_df
            else:
                df = pd.concat([old_df, new_df], ignore_index=True)

        except Exception:
            df = new_df
    else:
        df = new_df

    df = df.drop_duplicates(
        subset=["shop_id", "item_id", "review_text"]
    )

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    return len(df)


def scroll_to_review_area(send):
    for _ in range(10):
        send("Runtime.evaluate", {
            "expression": "window.scrollBy(0, 1200);"
        })
        time.sleep(1)


def click_next_review_page(send):
    expr = """
    (() => {
        const buttons = Array.from(document.querySelectorAll('button'));

        const candidates = buttons.filter(btn => {
            const cls = btn.className || '';
            const text = btn.innerText || '';
            const aria = btn.getAttribute('aria-label') || '';

            return (
                cls.includes('shopee-icon-button--right') ||
                text.includes('›') ||
                text.includes('>') ||
                aria.toLowerCase().includes('next')
            );
        });

        for (const btn of candidates) {
            if (!btn.disabled && btn.offsetParent !== null) {
                btn.click();
                return true;
            }
        }

        return false;
    })();
    """

    send("Runtime.evaluate", {
        "expression": expr
    })


def main():
    products = pd.read_csv(PRODUCT_FILE)

    products = products.dropna(
        subset=["product_url", "shop_id", "item_id"]
    )

    products = products.drop_duplicates(
        subset=["shop_id", "item_id"]
    )

    products = products.head(MAX_PRODUCTS)

    if os.path.exists(OUTPUT_FILE):
        old_reviews = pd.read_csv(OUTPUT_FILE)
        crawled_items = set(old_reviews["item_id"].astype(str).unique())
        products = products[~products["item_id"].astype(str).isin(crawled_items)]
        print("Số sản phẩm còn lại cần crawl review:", len(products))

    ws, send = cdp_connect()

    send("Network.enable")
    send("Page.enable")
    send("Runtime.enable")

    all_rows = []
    total_saved = 0

    for _, product in products.iterrows():
        product = product.to_dict()

        if total_saved >= TARGET_REVIEWS:
            break

        print("\n==============================")
        print("Product:", str(product["product_name"])[:90])
        print("URL:", product["product_url"])

        send("Page.navigate", {
            "url": product["product_url"]
        })

        time.sleep(6)

        scroll_to_review_area(send)

        captured_request_ids = set()
        no_new_count = 0

        for review_page in range(MAX_REVIEW_PAGES_PER_PRODUCT):
            before_count = total_saved

            print("Đang bắt review page:", review_page + 1)

            start = time.time()

            while time.time() - start < WAIT_EACH_REVIEW_PAGE:
                try:
                    msg = json.loads(ws.recv())
                except Exception:
                    continue

                method = msg.get("method")
                params = msg.get("params", {})

                if method != "Network.responseReceived":
                    continue

                response = params.get("response", {})
                url = response.get("url", "")

                if "get_ratings" not in url:
                    continue

                request_id = params.get("requestId")

                if request_id in captured_request_ids:
                    continue

                captured_request_ids.add(request_id)

                try:
                    body = get_response_body(ws, send, request_id)
                    data = json.loads(body)

                    if data.get("error"):
                        print("Shopee error:", data)
                        continue

                    rows = parse_reviews(data, product)

                    if rows:
                        all_rows.extend(rows)
                        total_saved = save_reviews(all_rows)

                        print("Bắt được review:", len(rows))
                        print("Tổng đã lưu:", total_saved)

                        if total_saved >= TARGET_REVIEWS:
                            print("Đã đủ target review.")
                            ws.close()
                            return

                except Exception as e:
                    print("Lỗi đọc response:", e)

            if total_saved == before_count:
                no_new_count += 1
                print("Không có review mới, count:", no_new_count)
            else:
                no_new_count = 0

            if no_new_count >= NO_NEW_LIMIT:
                print("Hết review hoặc không sang trang được, chuyển sản phẩm tiếp theo.")
                break

            click_next_review_page(send)
            time.sleep(3)

        time.sleep(3)

    ws.close()

    print("\nHoàn tất")
    print("Tổng review đã lưu:", total_saved)
    print("File:", OUTPUT_FILE)


if __name__ == "__main__":
    main()