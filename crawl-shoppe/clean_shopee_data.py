import re
import pandas as pd


PRODUCT_FILE = "shopee_products.csv"
REVIEW_FILE = "shopee_reviews.csv"

OUT_PRODUCT_FILE = "shopee_products_clean.csv"
OUT_REVIEW_FILE = "shopee_reviews_clean.csv"


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()

    # bỏ link
    text = re.sub(r"http\S+|www\S+", " ", text)

    # bỏ hashtag
    text = re.sub(r"#\S+", " ", text)

    # giữ chữ tiếng Việt, số, dấu câu cơ bản
    text = re.sub(r"[^a-zA-ZÀ-ỹ0-9\s.,!?%:/+-]", " ", text)

    # chuẩn hóa khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_price(x):
    if pd.isna(x):
        return None

    x = str(x)
    x = re.sub(r"[^\d.]", "", x)

    if x == "":
        return None

    return float(x)


def parse_sold_count(x):
    """
    Chuyển dạng:
    '889 đã bán' -> 889
    '5k+ đã bán' -> 5000
    '1k+ đã bán/tháng' -> 1000
    """
    if pd.isna(x):
        return 0

    x = str(x).lower().strip()

    if x == "" or x == "nan":
        return 0

    match = re.search(r"(\d+(\.\d+)?)\s*k", x)
    if match:
        return int(float(match.group(1)) * 1000)

    match = re.search(r"\d+", x)
    if match:
        return int(match.group())

    return 0


def star_to_sentiment(star):
    """
    Quy đổi sao sang sentiment tổng quan.
    Vẫn giữ cột review_star gốc 1-5.
    """
    if pd.isna(star):
        return "unknown"

    star = int(star)

    if star >= 4:
        return "positive"
    elif star == 3:
        return "neutral"
    else:
        return "negative"


def star_to_group(star):
    """
    Gom nhóm sao để trực quan hoá dễ hơn.
    """
    if pd.isna(star):
        return "unknown"

    star = int(star)

    if star == 5:
        return "5 sao"
    elif star == 4:
        return "4 sao"
    elif star == 3:
        return "3 sao"
    elif star == 2:
        return "2 sao"
    elif star == 1:
        return "1 sao"
    else:
        return "unknown"


def clean_products():
    df = pd.read_csv(PRODUCT_FILE)

    df = df.drop_duplicates(
        subset=["shop_id", "item_id"]
    )

    df["product_name_clean"] = df["product_name"].apply(clean_text)

    # chuyển các cột số
    for col in ["current_price", "original_price", "discount_percent", "rating", "liked_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # làm sạch sold_count và monthly_sold để vẽ biểu đồ được
    if "sold_count" in df.columns:
        df["sold_count_num"] = df["sold_count"].apply(parse_sold_count)

    if "monthly_sold" in df.columns:
        df["monthly_sold_num"] = df["monthly_sold"].apply(parse_sold_count)

    # bỏ sản phẩm không có tên
    df = df[df["product_name_clean"].str.len() > 0]

    df.to_csv(
        OUT_PRODUCT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Saved:", OUT_PRODUCT_FILE)
    print("Products:", df.shape)


def clean_reviews():
    df = pd.read_csv(REVIEW_FILE)

    df = df.drop_duplicates(
        subset=["shop_id", "item_id", "review_text"]
    )

    df["review_text_clean"] = df["review_text"].apply(clean_text)

    # bỏ review quá ngắn
    df = df[df["review_text_clean"].str.len() >= 10]

    # giữ review_star dạng số 1-5
    df["review_star"] = pd.to_numeric(
        df["review_star"],
        errors="coerce"
    )

    # bỏ dòng không có sao
    df = df.dropna(subset=["review_star"])

    df["review_star"] = df["review_star"].astype(int)

    # tạo thêm sentiment từ sao
    df["sentiment_by_star"] = df["review_star"].apply(star_to_sentiment)

    # tạo thêm nhóm sao để trực quan hoá
    df["review_star_group"] = df["review_star"].apply(star_to_group)

    # bỏ review spam chỉ toàn số
    df = df[~df["review_text_clean"].str.fullmatch(r"\d+")]

    df.to_csv(
        OUT_REVIEW_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Saved:", OUT_REVIEW_FILE)
    print("Reviews:", df.shape)

    print("\nSentiment by star:")
    print(df["sentiment_by_star"].value_counts())

    print("\nReview star:")
    print(df["review_star"].value_counts().sort_index())


def main():
    clean_products()
    clean_reviews()


if __name__ == "__main__":
    main()