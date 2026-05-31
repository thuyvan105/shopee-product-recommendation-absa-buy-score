import json
import time
import itertools
import os

import pandas as pd
import requests
import websocket


OUTPUT_FILE = "shopee_products.csv"

SHOP_URLS = [
    "https://shopee.vn/xiaomiofficialstore",
    "https://shopee.vn/apple_flagship_store",
    "https://shopee.vn/viettel_store_aar",
    "https://shopee.vn/samsung_official_store",
    "https://shopee.vn/tecno_official_store",
    "https://shopee.vn/huawei_flagship_store",
    "https://shopee.vn/vivo_vietnam",
    "https://shopee.vn/oppo_official_store_vn",
    "https://shopee.vn/shopdunk_official_store",
    "https://shopee.vn/minhtuanmobile.official",
    "https://shopee.vn/didongviet.official",
    "https://shopee.vn/realmevietnam"
]


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


def parse_products(data, shop_name):
    rows = []

    cards = (
        data.get("data", {})
        .get("centralize_item_card", {})
        .get("item_cards", [])
    )

    for item in cards:
        itemid = item.get("itemid")
        shopid = item.get("shopid")

        if not itemid or not shopid:
            continue

        price_info = item.get("item_card_display_price", {})

        current_price = price_info.get("price", 0) / 100000
        original_price = price_info.get("original_price", 0) / 100000

        discount_percent = 0

        if original_price > 0:
            discount_percent = round(
                (original_price - current_price)
                / original_price * 100
            )

        rows.append({
            "shop": shop_name,
            "shop_id": shopid,
            "item_id": itemid,
            "product_name": item.get("item_card_displayed_asset", {}).get("name"),
            "current_price": current_price,
            "original_price": original_price,
            "discount_percent": discount_percent,
            "rating": item.get("item_rating", {}).get("rating_star"),
            "rating_count": item.get("item_rating", {}).get("rating_count"),
            "sold_count": item.get(
                "item_card_display_sold_count", {}
            ).get("historical_sold_count_text"),
            "monthly_sold": item.get(
                "item_card_display_sold_count", {}
            ).get("monthly_sold_count_text"),
            "liked_count": item.get("liked_count"),
            "brand": item.get("global_brand", {}).get("display_name"),
            "product_url": f"https://shopee.vn/product/{shopid}/{itemid}"
        })

    return rows


def save_products(rows):
    if not rows:
        return

    new_df = pd.DataFrame(rows)

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)

        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df

    df = df.drop_duplicates(
        subset=["shop_id", "item_id"]
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Đã lưu:", len(df), "products")


def main():
    ws, send = cdp_connect()

    send("Network.enable")
    send("Page.enable")

    all_rows = []

    for shop_url in SHOP_URLS:
        print("\n====================")
        print("SHOP:", shop_url)

        shop_name = shop_url.split("/")[-1]

        send("Page.navigate", {
            "url": shop_url
        })

        time.sleep(8)

        for _ in range(15):
            send("Runtime.evaluate", {
                "expression": "window.scrollBy(0, 1500);"
            })

            time.sleep(1)

        found = False

        start = time.time()

        while time.time() - start < 20:
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

            if "rcmd_items" not in url:
                continue

            request_id = params.get("requestId")

            try:
                body = get_response_body(ws, send, request_id)

                data = json.loads(body)

                rows = parse_products(data, shop_name)

                if rows:
                    all_rows.extend(rows)

                    print("Lấy được:", len(rows), "products")

                    found = True
                    break

            except Exception as e:
                print("Lỗi:", e)

        if not found:
            print("Không bắt được product API.")

    ws.close()

    save_products(all_rows)

    print("\nHoàn tất")


if __name__ == "__main__":
    main()