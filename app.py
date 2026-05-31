# app.py — Shopee Recommendation Dashboard + Chat Advisor
# Run: streamlit run app.py

import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Shopee Recommendation Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"
PRODUCT_FILE = os.path.join(DATA_DIR, "shopee_products_processed.csv")
ABSA_FILE = os.path.join(DATA_DIR, "product_absa_score.csv")
ASPECT_FILE = os.path.join(DATA_DIR, "product_aspect_summary.csv")
RANKED_OUT = os.path.join(DATA_DIR, "ranked_products_final.csv")
COMPARE_OUT = os.path.join(DATA_DIR, "same_product_shop_comparison.csv")

ASPECTS = [
    "GENERAL", "PRICE", "PERFORMANCE", "BATTERY", "SCREEN",
    "CAMERA", "DESIGN", "FEATURES", "STORAGE", "SERANDACC"
]
ASPECT_LABELS = {
    "GENERAL": "Tổng quan", "PRICE": "Giá", "PERFORMANCE": "Hiệu năng",
    "BATTERY": "Pin", "SCREEN": "Màn hình", "CAMERA": "Camera",
    "DESIGN": "Thiết kế", "FEATURES": "Tính năng", "STORAGE": "Dung lượng",
    "SERANDACC": "Dịch vụ"
}

def svg_icon(name, size=18):
    icons = {
        "home": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 10.5 9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></svg>',
        "trophy": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0Z"/></svg>',
        "chat": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/></svg>',
        "compare": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16V4"/><path d="M17 20V8"/><path d="M3 12h8"/><path d="M13 16h8"/></svg>',
        "chart": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 16v-5"/><path d="M12 16V7"/><path d="M17 16v-8"/></svg>',
        "package": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.3 9 5.2"/><path d="M21 8v8a2 2 0 0 1-1 1.7l-7 4a2 2 0 0 1-2 0l-7-4A2 2 0 0 1 3 16V8a2 2 0 0 1 1-1.7l7-4a2 2 0 0 1 2 0l7 4A2 2 0 0 1 21 8Z"/></svg>',
        "settings": '<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 10v6M4.22 4.22l4.24 4.24m7.08 7.08 4.24 4.24M1 12h6m10 0h6"/></svg>',
    }
    return icons.get(name, icons["home"]).format(s=size)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(180deg,#F7FAFC 0%,#EFF4FB 100%);color:#0F172A;}
[data-testid="stHeader"]{background:rgba(255,255,255,.84);backdrop-filter:blur(12px);}
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1500px;}
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#F8FBFF 0%,#EDF4FF 100%);
    border-right:1px solid #D9E3F2;
}
[data-testid="stSidebar"] .block-container{padding-top:1rem;padding-left:1rem;padding-right:1rem;}
.sidebar-brand{padding:10px 8px 14px 8px;border-bottom:1px solid #E2E8F0;margin-bottom:14px;}
.sidebar-kicker{font-size:11px;font-weight:900;color:#2563EB;letter-spacing:.18em;text-transform:uppercase;margin-bottom:8px;}
.sidebar-title{font-size:26px;font-weight:900;line-height:1.08;color:#0F172A;}
.sidebar-desc{font-size:12px;line-height:1.55;color:#64748B;margin-top:8px;}
.sidebar-section{margin-top:16px;margin-bottom:8px;font-size:12px;font-weight:900;color:#64748B;text-transform:uppercase;letter-spacing:.08em;}
.hero{border:1px solid #D8E3F4;border-radius:26px;padding:28px 32px;margin-bottom:14px;background:radial-gradient(circle at 92% 10%,rgba(37,99,235,.16),transparent 28%),radial-gradient(circle at 16% 8%,rgba(124,58,237,.10),transparent 28%),linear-gradient(135deg,#FFFFFF 0%,#F7FAFF 55%,#EEF4FF 100%);box-shadow:0 18px 45px rgba(15,23,42,.06);}
.eyebrow{color:#2563EB;font-size:12px;font-weight:900;letter-spacing:.18em;text-transform:uppercase;margin-bottom:12px;}
.hero-title{font-size:36px;line-height:1.08;font-weight:900;letter-spacing:-.045em;color:#0F172A;margin-bottom:10px;}
.hero-desc{font-size:15px;line-height:1.65;color:#475569;max-width:920px;}
.card{border:1px solid #D8E3F4;background:#FFFFFF;border-radius:22px;box-shadow:0 14px 34px rgba(15,23,42,.05);padding:20px;}
.soft-card{border:1px solid #E2E8F0;background:#F8FAFC;border-radius:18px;padding:16px;}
.metric-card{min-height:118px;display:flex;flex-direction:column;justify-content:center;}
.metric-label{color:#64748B;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.04em;}
.metric-value{color:#0F172A;font-size:30px;font-weight:900;letter-spacing:-.03em;margin-top:6px;}
.metric-note{color:#64748B;font-size:12px;font-weight:700;margin-top:4px;}
.section-title{color:#0F172A;font-weight:900;font-size:18px;letter-spacing:-.02em;margin-bottom:4px;}
.section-subtitle{color:#64748B;font-size:12px;margin-bottom:14px;}
.badge{display:inline-flex;align-items:center;justify-content:center;padding:6px 10px;border-radius:999px;font-size:11px;font-weight:900;white-space:nowrap;}
.badge-green{background:#DCFCE7;color:#166534}.badge-yellow{background:#FEF3C7;color:#92400E}.badge-blue{background:#DBEAFE;color:#1D4ED8}.badge-red{background:#FEE2E2;color:#B91C1C}.badge-gray{background:#E2E8F0;color:#475569}
.chat-user{background:#EEF4FF;border:1px solid #BFDBFE;border-radius:18px;padding:14px;margin:8px 0;color:#1E3A8A;}
.chat-bot{background:#FFFFFF;border:1px solid #D8E3F4;border-radius:18px;padding:14px;margin:8px 0;box-shadow:0 8px 20px rgba(15,23,42,.05);}
.small-muted{color:#64748B;font-size:12px;}
[data-testid="stDataFrame"]{border:1px solid #E2E8F0;border-radius:18px;overflow:hidden;}
.stTextInput input,.stSelectbox div[data-baseweb="select"]>div,.stNumberInput input{border-radius:13px!important;border:1px solid #CBD5E1!important;background:#FFFFFF!important;color:#0F172A!important;}
.stButton button{border-radius:13px!important;border:1px solid #CBD5E1!important;background:#FFFFFF!important;color:#0F172A!important;font-weight:800!important;}
.stButton button:hover{border-color:#2563EB!important;color:#2563EB!important;}
.stDownloadButton button{border-radius:13px!important;border:1px solid #CBD5E1!important;background:#FFFFFF!important;color:#0F172A!important;font-weight:800!important;}
[data-testid="stExpander"]{background:#FFFFFF;border:1px solid #D8E3F4;border-radius:18px;box-shadow:0 10px 24px rgba(15,23,42,.04);}
div[role="radiogroup"] label{margin-bottom:6px!important;}

/* POLISHED SIDEBAR MENU */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#F8FBFF 0%,#EEF5FF 100%) !important;
    border-right:1px solid #D8E3F4;
}
[data-testid="stSidebar"] .block-container{padding-top:1rem;padding-left:1rem;padding-right:1rem;}
.sidebar-nav-active{
    display:flex;
    align-items:center;
    gap:10px;
    width:100%;
    min-height:42px;
    padding:0 14px;
    margin:5px 0;
    border-radius:14px;
    color:#FFFFFF;
    background:linear-gradient(135deg,#2563EB,#7C3AED);
    box-shadow:0 12px 24px rgba(37,99,235,.22);
    font-size:14px;
    font-weight:900;
}
[data-testid="stSidebar"] .stButton > button{
    width:100%;
    min-height:42px;
    justify-content:flex-start;
    text-align:left;
    padding:0 14px!important;
    margin:2px 0;
    border-radius:14px!important;
    border:1px solid transparent!important;
    background:transparent!important;
    color:#334155!important;
    font-size:14px!important;
    font-weight:800!important;
    box-shadow:none!important;
}
[data-testid="stSidebar"] .stButton > button:hover{
    background:#EAF2FF!important;
    border:1px solid #C7D7F2!important;
    color:#1D4ED8!important;
}

</style>

<style>
.insight-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:10px 0 18px;}
.insight-card{background:#FFFFFF;border:1px solid #D8E3F4;border-radius:22px;padding:18px 20px;box-shadow:0 14px 32px rgba(15,23,42,.05);}
.insight-title{font-size:12px;font-weight:900;color:#64748B;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px;}
.insight-main{font-size:20px;font-weight:900;color:#0F172A;line-height:1.25;}
.insight-sub{font-size:12px;color:#64748B;line-height:1.55;margin-top:8px;}
.good-box{border-left:5px solid #22C55E;background:#F0FDF4;}
.warn-box{border-left:5px solid #F59E0B;background:#FFFBEB;}
.info-box{border-left:5px solid #3B82F6;background:#EFF6FF;}
.analysis-note{border-radius:18px;padding:14px 16px;margin:10px 0 16px;border:1px solid #D8E3F4;color:#334155;font-size:14px;line-height:1.6;}
[data-testid="stSidebar"] .stButton > button p{font-weight:800!important;}
</style>

""", unsafe_allow_html=True)

# Helpers

def numeric(df, col, default=0):
    if col not in df.columns:
        df[col] = default
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)
    return df

def fmt_price(x):
    try:
        x = float(x)
        if np.isnan(x) or x <= 0:
            return "N/A"
        return f"{x:,.0f}đ"
    except Exception:
        return "N/A"

def fmt_int(x):
    try:
        return f"{int(float(x)):,}"
    except Exception:
        return "0"

def minmax_scale(series):
    s = pd.to_numeric(series, errors="coerce").fillna(0).astype(float)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([0.5] * len(s), index=s.index)
    return (s - mn) / (mx - mn)

def minmax_scale_group(x):
    s = pd.to_numeric(x, errors="coerce").fillna(0).astype(float)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([0.5] * len(s), index=s.index)
    return (s - mn) / (mx - mn)

def rec_label(score):
    if score >= 80: return "Đáng mua"
    if score >= 65: return "Đáng cân nhắc"
    if score >= 50: return "Trung bình"
    return "Cần cân nhắc"

def rec_badge(label):
    cls = {"Đáng mua":"badge-green", "Đáng cân nhắc":"badge-yellow", "Trung bình":"badge-blue", "Cần cân nhắc":"badge-red"}.get(str(label), "badge-gray")
    return f"<span class='badge {cls}'>{label}</span>"

def short_name(x, n=70):
    x = str(x)
    return x if len(x) <= n else x[:n-3] + "..."

def clean_filter_value(x):
    x = str(x).strip()
    if x.lower() in ["nan", "none", "unknown", "", "n/a"]:
        return "Không xác định"
    return x

def safe_unique_options(series):
    vals = [clean_filter_value(x) for x in series.dropna().tolist()]
    vals = sorted(set([v for v in vals if v != "Không xác định"]))
    return ["Tất cả"] + vals

def plot_layout(fig, height=420, showlegend=True):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", family="Inter", size=12),
        margin=dict(l=10, r=10, t=42, b=10), showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#CBD5E1")
    return fig


def add_price_band(df):
    d = df.copy()
    price = pd.to_numeric(d["current_price"], errors="coerce").fillna(0)
    bins = [0, 1_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000, 10**12]
    labels = ["<1tr", "1-3tr", "3-5tr", "5-10tr", "10-20tr", ">20tr"]
    d["price_band"] = pd.cut(price, bins=bins, labels=labels, include_lowest=True)
    return d

def insight_text(df):
    if df.empty:
        return "Không có dữ liệu phù hợp với bộ lọc."
    best = df.sort_values("buy_score_100", ascending=False).iloc[0]
    cheap_good = df[(df["price_score"] >= 0.7) & (df["absa_score"] >= 70)].sort_values("buy_score_100", ascending=False)
    msg = f"Sản phẩm đang dẫn đầu là **{short_name(best['product_name'], 80)}** với Buy Score **{best['buy_score_100']:.1f}**."
    if not cheap_good.empty:
        cg = cheap_good.iloc[0]
        msg += f" Nhóm đáng chú ý là sản phẩm **giá tốt nhưng review ổn**, ví dụ **{short_name(cg['product_name'], 70)}**."
    return msg

def component_contribution_df(df, n=10):
    d = df.sort_values("buy_score_100", ascending=False).head(n).copy()
    d["Sản phẩm"] = d["product_name"].apply(lambda x: short_name(x, 36))
    return pd.DataFrame({
        "Sản phẩm": d["Sản phẩm"],
        "ABSA": d["absa_score_norm"] * 30,
        "Giá": d["price_score"] * 25,
        "Rating": d["rating_score"] * 20,
        "Lượt bán": d["sold_score"] * 15,
        "Độ tin cậy": d["review_confidence_score"] * 10,
    })

def aspect_heatmap_top(df, n=12):
    top = df.sort_values("buy_score_100", ascending=False).head(n).copy()
    rows = []
    for _, r in top.iterrows():
        row = {"Sản phẩm": short_name(r["product_name"], 34)}
        for a in ASPECTS:
            row[ASPECT_LABELS.get(a, a)] = float(r.get(f"{a}_positive_rate", 0)) * 100
        rows.append(row)
    return pd.DataFrame(rows)

def best_value_candidates(df):
    d = df.copy()
    d["value_signal"] = (
        d["price_score"] * 0.40 +
        d["absa_score_norm"] * 0.35 +
        d["rating_score"] * 0.15 +
        d["review_confidence_score"] * 0.10
    ) * 100
    return d.sort_values("value_signal", ascending=False)


def section(title, subtitle=""):
    st.markdown(f"<div class='section-title'>{title}</div><div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

def require_files():
    missing = [p for p in [PRODUCT_FILE, ABSA_FILE] if not os.path.exists(p)]
    if missing:
        st.error("Thiếu file dữ liệu đầu vào trong thư mục data/.")
        st.markdown("""
Cần copy các file output từ Kaggle vào thư mục `data/`:

```text
shopee_products_processed.csv
product_absa_score.csv
product_aspect_summary.csv  # nếu có thì dashboard phân tích khía cạnh chi tiết hơn
```

Sau đó chạy lại:

```bash
streamlit run app.py
```
""")
        st.stop()

@st.cache_data(show_spinner="Đang đọc dữ liệu và tính Buy Score...")
def load_data():
    require_files()
    products = pd.read_csv(PRODUCT_FILE)
    absa = pd.read_csv(ABSA_FILE)
    for c in ["shop", "brand", "product_type", "product_name", "product_url", "canonical_product_name", "canonical_product_id"]:
        if c not in products.columns:
            products[c] = "Unknown"
    for c in ["current_price", "original_price", "discount_percent", "rating", "rating_count", "sold_count_num", "monthly_sold_num"]:
        products = numeric(products, c, 0)

    # Làm sạch các cột dùng cho bộ lọc, tránh hiện nan/None/Unknown trên dashboard
    for c in ["shop", "brand", "product_type", "canonical_product_name"]:
        products[c] = products[c].apply(clean_filter_value)

    for c in ["absa_score", "total_aspect_mentions", "avg_positive_rate", "avg_negative_rate"]:
        absa = numeric(absa, c, 0)

    df = products.merge(absa, on=["shop_id", "item_id"], how="left")
    df["absa_score"] = df["absa_score"].fillna(50).clip(0, 100)
    df["total_aspect_mentions"] = df["total_aspect_mentions"].fillna(0)
    df["avg_positive_rate"] = df["avg_positive_rate"].fillna(0)
    df["avg_negative_rate"] = df["avg_negative_rate"].fillna(0)

    if os.path.exists(ASPECT_FILE):
        asp = pd.read_csv(ASPECT_FILE)
        for c in ["positive_rate", "negative_rate", "neutral_rate", "total_mentions"]:
            if c not in asp.columns: asp[c] = 0
            asp[c] = pd.to_numeric(asp[c], errors="coerce").fillna(0)
        if "aspect" in asp.columns:
            idx = ["shop_id", "item_id"]
            for val in ["positive_rate", "negative_rate", "neutral_rate", "total_mentions"]:
                pv = asp.pivot_table(index=idx, columns="aspect", values=val, aggfunc="mean", fill_value=0).reset_index()
                pv.columns = [c if c in idx else f"{c}_{val}" for c in pv.columns]
                df = df.merge(pv, on=idx, how="left")
    for a in ASPECTS:
        for suffix in ["positive_rate", "negative_rate", "neutral_rate", "total_mentions"]:
            col = f"{a}_{suffix}"
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["canonical_product_id"] = df["canonical_product_id"].fillna(df["product_name"].astype(str))
    df["price_score"] = df.groupby("canonical_product_id")["current_price"].transform(lambda x: 1 - minmax_scale_group(x))
    df["rating_score"] = (df["rating"] / 5).clip(0, 1)
    df["sold_score"] = minmax_scale(np.log1p(df["sold_count_num"].fillna(0)))
    df["review_confidence_score"] = minmax_scale(np.log1p(df["total_aspect_mentions"].fillna(0)))
    df["absa_score_norm"] = (df["absa_score"] / 100).clip(0, 1)

    df["buy_score_100"] = (
        df["absa_score_norm"] * 0.30 +
        df["price_score"] * 0.25 +
        df["rating_score"] * 0.20 +
        df["sold_score"] * 0.15 +
        df["review_confidence_score"] * 0.10
    ) * 100
    df["recommendation_label"] = df["buy_score_100"].apply(rec_label)
    df = df.sort_values("buy_score_100", ascending=False).copy()
    df["rank"] = range(1, len(df) + 1)

    shop_count = df.groupby("canonical_product_id")["shop_id"].nunique().reset_index(name="num_shops") if "shop_id" in df.columns else pd.DataFrame()
    compare = df.merge(shop_count, on="canonical_product_id", how="left") if not shop_count.empty else df.copy()
    if "num_shops" not in compare.columns: compare["num_shops"] = 1
    compare = compare[compare["num_shops"] >= 2].copy()
    if not compare.empty:
        compare["price_advantage_score"] = compare.groupby("canonical_product_id")["current_price"].transform(lambda x: 1 - minmax_scale_group(x))
        compare["absa_compare_score"] = compare.groupby("canonical_product_id")["absa_score"].transform(minmax_scale_group)
        compare["rating_compare_score"] = compare.groupby("canonical_product_id")["rating"].transform(minmax_scale_group)
        compare["sold_compare_score"] = compare.groupby("canonical_product_id")["sold_count_num"].transform(lambda x: minmax_scale_group(np.log1p(x)))
        compare["review_trust_score"] = compare.groupby("canonical_product_id")["total_aspect_mentions"].transform(lambda x: minmax_scale_group(np.log1p(x)))
        compare["same_product_buy_score"] = (
            compare["price_advantage_score"] * 0.30 + compare["absa_compare_score"] * 0.30 +
            compare["rating_compare_score"] * 0.15 + compare["sold_compare_score"] * 0.15 + compare["review_trust_score"] * 0.10
        ) * 100
        compare = compare.sort_values(["canonical_product_id", "same_product_buy_score"], ascending=[True, False])
        compare["rank_in_same_product"] = compare.groupby("canonical_product_id").cumcount() + 1

    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(RANKED_OUT, index=False, encoding="utf-8-sig")
    compare.to_csv(COMPARE_OUT, index=False, encoding="utf-8-sig")
    return df, compare

ranked, same_compare = load_data()

# Filters helper

def filter_df(df, shop, ptype, rec, keyword, score_range, price_range):
    out = df.copy()
    if shop != "Tất cả":
        out = out[out["shop"].astype(str) == shop]
    if ptype != "Tất cả":
        out = out[out["product_type"].astype(str) == ptype]
    if rec != "Tất cả":
        out = out[out["recommendation_label"] == rec]
    if keyword:
        out = out[out["product_name"].astype(str).str.lower().str.contains(keyword.lower(), na=False)]
    out = out[(out["buy_score_100"] >= score_range[0]) & (out["buy_score_100"] <= score_range[1])]
    if price_range[1] > 0:
        out = out[(out["current_price"] >= price_range[0]) & (out["current_price"] <= price_range[1])]
    return out.sort_values("buy_score_100", ascending=False)

# Chat recommendation

def parse_budget(text):
    t = text.lower().replace(",", ".")
    m = re.search(r"(?:dưới|duoi|<=|<|tối đa|max|không quá|khong qua)\s*(\d+(?:\.\d+)?)\s*(triệu|tr|m|k|nghìn|ngàn)?", t)
    if not m:
        m = re.search(r"(?:khoảng|tầm|tam|cỡ|co)\s*(\d+(?:\.\d+)?)\s*(triệu|tr|m)?", t)
    if m:
        val = float(m.group(1)); unit = m.group(2) or ""
        if unit in ["triệu", "tr", "m"] or val < 200:
            return val * 1_000_000
        if unit in ["k", "nghìn", "ngàn"]:
            return val * 1_000
        return val
    return None

def parse_need(text):
    t = text.lower()
    aspects = []
    if any(k in t for k in ["pin", "battery", "lâu", "trâu"]): aspects.append("BATTERY")
    if any(k in t for k in ["camera", "chụp", "ảnh", "quay"]): aspects.append("CAMERA")
    if any(k in t for k in ["game", "gaming", "mượt", "hiệu năng", "performance", "chip", "chơi game"]): aspects.append("PERFORMANCE")
    if any(k in t for k in ["màn", "màn hình", "screen", "hiển thị"]): aspects.append("SCREEN")
    if any(k in t for k in ["giá", "rẻ", "sinh viên", "tiết kiệm"]): aspects.append("PRICE")
    if any(k in t for k in ["đẹp", "thiết kế", "mỏng", "nhẹ"]): aspects.append("DESIGN")
    if any(k in t for k in ["dung lượng", "bộ nhớ", "storage", "128", "256", "512"]): aspects.append("STORAGE")

    ptype = None
    allowed_types = None

    # Từ khóa sản phẩm rõ ràng
    if any(k in t for k in ["điện thoại", "phone", "iphone", "samsung", "xiaomi", "oppo", "vivo"]):
        ptype = "phone"
    elif any(k in t for k in ["tablet", "ipad", "máy tính bảng"]):
        ptype = "tablet"
    elif any(k in t for k in ["tai nghe", "earphone", "airpods", "buds"]):
        ptype = "earphone"
    elif any(k in t for k in ["đồng hồ", "watch", "smartwatch"]):
        ptype = "smartwatch"

    # Nếu hỏi chơi game/mượt nhưng không nói loại sản phẩm,
    # mặc định chỉ lấy thiết bị có thể chơi game, không lấy sạc/cáp/tai nghe.
    if any(k in t for k in ["game", "gaming", "chơi game", "mượt", "hiệu năng"]):
        if ptype is None:
            allowed_types = ["phone", "tablet"]

    # Nếu hỏi camera/pin/màn hình mà không nói loại,
    # cũng ưu tiên điện thoại/tablet thay vì phụ kiện.
    if any(k in t for k in ["camera", "chụp", "ảnh", "pin", "màn hình", "màn"]):
        if ptype is None:
            allowed_types = ["phone", "tablet"]

    brand = None
    for b in ranked["brand"].dropna().astype(str).unique():
        if b and b.lower() != "unknown" and b.lower() in t:
            brand = b
            break

    return aspects, ptype, brand, allowed_types

def filter_by_product_intent(data, ptype=None, allowed_types=None):
    out = data.copy()
    product_type = out["product_type"].astype(str).str.lower()
    product_name = out["product_name"].astype(str).str.lower()

    if ptype:
        mask = product_type.str.contains(ptype, na=False) | product_name.str.contains(ptype, na=False)
        if mask.sum() > 0:
            return out[mask]

    if allowed_types:
        pattern = "|".join(allowed_types)
        mask = product_type.str.contains(pattern, na=False)

        # fallback theo tên nếu product_type trong file chưa chuẩn
        name_keywords = {
            "phone": ["điện thoại", "iphone", "samsung galaxy", "xiaomi", "redmi", "oppo", "vivo", "tecno"],
            "tablet": ["ipad", "tablet", "máy tính bảng", "galaxy tab", "matepad"],
        }
        name_mask = pd.Series(False, index=out.index)
        for t in allowed_types:
            for kw in name_keywords.get(t, []):
                name_mask = name_mask | product_name.str.contains(kw, na=False)

        mask = mask | name_mask

        # loại phụ kiện rõ ràng
        accessory_keywords = [
            "sạc", "adapter", "cáp", "cable", "tai nghe", "airpods", "buds",
            "ốp", "case", "miếng dán", "kính cường lực", "chuột", "bàn phím"
        ]
        accessory_mask = pd.Series(False, index=out.index)
        for kw in accessory_keywords:
            accessory_mask = accessory_mask | product_name.str.contains(kw, na=False)

        final_mask = mask & (~accessory_mask)
        if final_mask.sum() > 0:
            return out[final_mask]

    return out

def recommend_from_query(query, n=5):
    q = str(query)
    budget = parse_budget(q)
    aspects, ptype, brand, allowed_types = parse_need(q)

    data = ranked.copy()

    if budget:
        data = data[data["current_price"] <= budget]

    data = filter_by_product_intent(data, ptype=ptype, allowed_types=allowed_types)

    if brand:
        data = data[data["brand"].astype(str).str.lower() == brand.lower()]

    if data.empty:
        return data, "Không tìm thấy sản phẩm phù hợp với điều kiện. Hãy thử nới ngân sách hoặc bỏ bớt yêu cầu."

    data = data.copy()

    # Điểm chat ưu tiên Buy Score nhưng tăng điểm theo aspect đúng nhu cầu
    data["chat_score"] = data["buy_score_100"] * 0.60

    if aspects:
        aspect_bonus = pd.Series(0, index=data.index, dtype=float)
        for a in aspects:
            aspect_bonus += data.get(f"{a}_positive_rate", 0) * 100
        aspect_bonus = aspect_bonus / len(aspects)
        data["chat_score"] += aspect_bonus * 0.30

    if "PRICE" in aspects or budget:
        data["chat_score"] += data["price_score"] * 10

    # Với nhu cầu game/hiệu năng, cộng thêm rating và loại thiết bị phù hợp
    if "PERFORMANCE" in aspects:
        data["chat_score"] += data["rating_score"] * 5

    data = data.sort_values("chat_score", ascending=False).head(n)

    intent = []
    if budget: intent.append(f"ngân sách khoảng {fmt_price(budget)}")
    if ptype: intent.append(f"loại sản phẩm: {ptype}")
    if allowed_types: intent.append("loại sản phẩm phù hợp: điện thoại/tablet")
    if aspects: intent.append("ưu tiên " + ", ".join([ASPECT_LABELS.get(a,a) for a in aspects]))

    reason = "Hệ thống đã lọc theo " + "; ".join(intent) + ", sau đó xếp hạng bằng Buy Score kết hợp với khía cạnh người dùng quan tâm." if intent else "Hệ thống xếp hạng theo Buy Score tổng thể."
    return data, reason

def display_product_table(df, columns="default", height=440):
    show = df.copy()
    show["Giá"] = show["current_price"].apply(fmt_price)
    show["Buy Score"] = show["buy_score_100"].round(1)
    show["ABSA"] = show["absa_score"].round(1)
    show["Rating"] = show["rating"].round(2)
    show["Lượt bán"] = show["sold_count_num"].apply(fmt_int)
    base = ["rank", "product_name", "shop", "brand", "Giá", "Rating", "ABSA", "Buy Score", "recommendation_label"]
    if columns == "compare":
        base = ["rank_in_same_product", "product_name", "shop", "Giá", "Rating", "ABSA", "same_product_buy_score", "recommendation_label"]
        rename = {"rank_in_same_product":"Rank", "product_name":"Sản phẩm", "shop":"Shop", "same_product_buy_score":"Điểm so sánh", "recommendation_label":"Gợi ý"}
    else:
        rename = {"rank":"Rank", "product_name":"Sản phẩm", "shop":"Shop", "brand":"Brand", "recommendation_label":"Gợi ý"}
    available = [c for c in base if c in show.columns]
    st.dataframe(show[available].rename(columns=rename), use_container_width=True, hide_index=True, height=height)

# Sidebar menu + filters
pages = ["Tổng quan", "Gợi ý sản phẩm", "So sánh cùng sản phẩm", "Phân tích khía cạnh", "Đánh giá kết quả", "Chi tiết sản phẩm"]
with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>
      <div class='sidebar-title'>Shopee · ABSA · Buy Score</div>
      <div class='sidebar-desc'>Dashboard gợi ý sản phẩm đáng mua dựa trên ABSA, giá bán, rating và lượt bán.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>Điều hướng</div>", unsafe_allow_html=True)

    nav_icons = {
        "Tổng quan": "home",
        "Gợi ý sản phẩm": "trophy",
        "So sánh cùng sản phẩm": "compare",
        "Phân tích khía cạnh": "chart",
        "Đánh giá kết quả": "chart",
        "Chi tiết sản phẩm": "package",
        "Phương pháp": "settings",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Tổng quan"

    for nav_name in pages:
        icon = svg_icon(nav_icons.get(nav_name, "home"), 17)
        if st.session_state.page == nav_name:
            st.markdown(
                f"<div class='sidebar-nav-active'>{icon}<span>{nav_name}</span></div>",
                unsafe_allow_html=True
            )
        else:
            if st.button(nav_name, key=f"nav_{nav_name}", use_container_width=True):
                st.session_state.page = nav_name
                st.rerun()

    page = st.session_state.page

    st.markdown("<div class='sidebar-section'>Bộ lọc chung</div>", unsafe_allow_html=True)

    shop = st.selectbox(
        "Shop",
        safe_unique_options(ranked["shop"])
    )

    ptype = st.selectbox(
        "Loại sản phẩm",
        safe_unique_options(ranked["product_type"])
    )

    rec = st.selectbox(
        "Nhóm gợi ý",
        ["Tất cả", "Đáng mua", "Đáng cân nhắc", "Trung bình", "Cần cân nhắc"]
    )

    keyword = st.text_input(
        "Tìm theo tên sản phẩm",
        placeholder="iphone, samsung, tai nghe..."
    )

    prices = ranked.loc[ranked["current_price"] > 0, "current_price"]
    if len(prices) > 0:
        price_range = st.slider(
            "Khoảng giá bán",
            int(prices.min()),
            int(prices.max()),
            (int(prices.min()), int(prices.max())),
            step=10000,
            format="%dđ"
        )
    else:
        price_range = (0, 0)

    score_range = st.slider("Khoảng Buy Score", 0, 100, (0, 100))

filtered = filter_df(ranked, shop, ptype, rec, keyword, score_range, price_range)
if filtered.empty:
    st.warning("Không có sản phẩm phù hợp với bộ lọc hiện tại.")
    st.stop()



# =========================
# V3 analytical helpers
# =========================
def top_summary_cards(df):
    best = df.sort_values("buy_score_100", ascending=False).iloc[0]
    best_shop = (
        df.groupby("shop")
        .agg(buy_score_tb=("buy_score_100", "mean"), so_sp=("product_name", "count"))
        .reset_index()
        .sort_values("buy_score_tb", ascending=False)
        .iloc[0]
    )
    value = df[(df["price_score"] >= 0.65) & (df["absa_score"] >= 70)].sort_values("buy_score_100", ascending=False)
    value_name = short_name(value.iloc[0]["product_name"], 60) if not value.empty else "Chưa có sản phẩm nổi bật"
    value_note = f"Giá tốt + ABSA {value.iloc[0]['absa_score']:.1f}" if not value.empty else "Cần nới bộ lọc để thấy rõ hơn"

    st.markdown(f"""
    <div class="insight-grid">
      <div class="insight-card good-box">
        <div class="insight-title">Sản phẩm nổi bật nhất</div>
        <div class="insight-main">{short_name(best['product_name'], 60)}</div>
        <div class="insight-sub">Buy Score: <b>{best['buy_score_100']:.1f}</b> · Giá: <b>{fmt_price(best['current_price'])}</b> · Shop: {best['shop']}</div>
      </div>
      <div class="insight-card info-box">
        <div class="insight-title">Shop có điểm trung bình tốt</div>
        <div class="insight-main">{short_name(best_shop['shop'], 60)}</div>
        <div class="insight-sub">Buy Score TB: <b>{best_shop['buy_score_tb']:.1f}</b> · Số sản phẩm: <b>{int(best_shop['so_sp'])}</b></div>
      </div>
      <div class="insight-card warn-box">
        <div class="insight-title">Ứng viên best value</div>
        <div class="insight-main">{value_name}</div>
        <div class="insight-sub">{value_note}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def make_price_band(df):
    d = df.copy()
    bins = [0, 1_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000, 10**12]
    labels = ["<1tr", "1-3tr", "3-5tr", "5-10tr", "10-20tr", ">20tr"]
    d["price_band"] = pd.cut(d["current_price"], bins=bins, labels=labels, include_lowest=True)
    return d

def score_contribution(df, n=8):
    d = df.sort_values("buy_score_100", ascending=False).head(n).copy()
    d["Sản phẩm"] = d["product_name"].apply(lambda x: short_name(x, 34))
    comp = pd.DataFrame({
        "Sản phẩm": d["Sản phẩm"],
        "ABSA review": d["absa_score_norm"] * 30,
        "Giá tốt": d["price_score"] * 25,
        "Rating": d["rating_score"] * 20,
        "Lượt bán": d["sold_score"] * 15,
        "Độ tin cậy": d["review_confidence_score"] * 10,
    })
    return comp.melt(id_vars="Sản phẩm", var_name="Thành phần", value_name="Điểm đóng góp")

def quadrant_chart(df):
    d = df.head(350).copy()
    fig = px.scatter(
        d, x="price_score", y="absa_score", size="sold_count_num",
        color="recommendation_label", hover_name="product_name",
        hover_data={"current_price":":,.0f", "rating":":.2f", "buy_score_100":":.1f"},
        labels={"price_score":"Điểm giá tốt", "absa_score":"ABSA Score", "recommendation_label":"Nhóm gợi ý"}
    )
    fig.add_vline(x=0.5, line_dash="dash", line_color="#94A3B8")
    fig.add_hline(y=70, line_dash="dash", line_color="#94A3B8")
    fig.add_annotation(x=0.82, y=96, text="<b>NÊN ƯU TIÊN</b><br>Giá tốt + review tốt", showarrow=False, font=dict(color="#166534", size=12))
    fig.add_annotation(x=0.18, y=96, text="<b>CHẤT LƯỢNG ỔN</b><br>nhưng giá chưa tốt", showarrow=False, font=dict(color="#92400E", size=12))
    fig.add_annotation(x=0.82, y=45, text="<b>GIÁ RẺ</b><br>nhưng cần xem review", showarrow=False, font=dict(color="#B91C1C", size=12))
    return plot_layout(fig, 500)

def aspect_heatmap(df, n=10):
    d = df.sort_values("buy_score_100", ascending=False).head(n).copy()
    rows = []
    for _, r in d.iterrows():
        row = {"Sản phẩm": short_name(r["product_name"], 32)}
        for a in ASPECTS:
            row[ASPECT_LABELS.get(a, a)] = float(r.get(f"{a}_positive_rate", 0)) * 100
        rows.append(row)
    h = pd.DataFrame(rows)
    if h.empty:
        return None
    z = h.drop(columns=["Sản phẩm"]).values
    fig = go.Figure(data=go.Heatmap(
        z=z, x=h.drop(columns=["Sản phẩm"]).columns, y=h["Sản phẩm"],
        colorscale=[[0, "#EFF6FF"], [0.5, "#60A5FA"], [1, "#1D4ED8"]],
        colorbar=dict(title="Positive %"),
        text=np.round(z, 0), texttemplate="%{text}%",
        hovertemplate="Sản phẩm: %{y}<br>Khía cạnh: %{x}<br>Tích cực: %{z:.1f}%<extra></extra>"
    ))
    fig.update_yaxes(autorange="reversed")
    return plot_layout(fig, 520, False)

def product_table_compact(df, height=420):
    show = df.copy()
    show["Giá"] = show["current_price"].apply(fmt_price)
    show["Buy Score"] = show["buy_score_100"].round(1)
    show["ABSA"] = show["absa_score"].round(1)
    show["Rating"] = show["rating"].round(2)
    cols = ["rank", "product_name", "shop", "Giá", "Rating", "ABSA", "Buy Score", "recommendation_label"]
    rename = {"rank":"Rank", "product_name":"Sản phẩm", "shop":"Shop", "recommendation_label":"Gợi ý"}
    st.dataframe(show[[c for c in cols if c in show.columns]].rename(columns=rename), use_container_width=True, hide_index=True, height=height)



def top_rating_vs_buy_tables(df, n=10):
    top_rating = df.sort_values(["rating", "sold_count_num"], ascending=False).head(n).copy()
    top_buy = df.sort_values("buy_score_100", ascending=False).head(n).copy()
    return top_rating, top_buy

def sensitivity_analysis(df, n=10):
    d = df.copy()

    scenarios = {
        "Cân bằng hiện tại": {
            "ABSA": 0.30, "Price": 0.25, "Rating": 0.20, "Sold": 0.15, "Confidence": 0.10
        },
        "Ưu tiên review ABSA": {
            "ABSA": 0.45, "Price": 0.20, "Rating": 0.15, "Sold": 0.10, "Confidence": 0.10
        },
        "Ưu tiên giá tốt": {
            "ABSA": 0.25, "Price": 0.40, "Rating": 0.15, "Sold": 0.10, "Confidence": 0.10
        },
        "Ưu tiên độ phổ biến": {
            "ABSA": 0.25, "Price": 0.20, "Rating": 0.20, "Sold": 0.25, "Confidence": 0.10
        },
    }

    base_top = set(d.sort_values("buy_score_100", ascending=False).head(n)["item_id"].astype(str))
    rows = []

    for name, w in scenarios.items():
        score = (
            d["absa_score_norm"] * w["ABSA"] +
            d["price_score"] * w["Price"] +
            d["rating_score"] * w["Rating"] +
            d["sold_score"] * w["Sold"] +
            d["review_confidence_score"] * w["Confidence"]
        ) * 100
        col = f"score_{name}"
        d[col] = score
        top_ids = set(d.sort_values(col, ascending=False).head(n)["item_id"].astype(str))
        overlap = len(base_top.intersection(top_ids))
        rows.append({
            "Kịch bản": name,
            "ABSA": w["ABSA"],
            "Giá": w["Price"],
            "Rating": w["Rating"],
            "Lượt bán": w["Sold"],
            "Độ tin cậy": w["Confidence"],
            f"Trùng Top {n} với hiện tại": overlap,
            "Tỷ lệ ổn định": overlap / n * 100
        })

    return pd.DataFrame(rows), d

def find_case_studies(df):
    d = df.copy()
    cases = {}

    cases["Sản phẩm đáng mua nhất"] = d.sort_values("buy_score_100", ascending=False).head(1)

    # Rating cao nhưng Buy Score không quá cao: dùng percentile để có case study
    high_rating = d[d["rating"] >= d["rating"].quantile(0.80)].copy()
    if not high_rating.empty:
        cases["Rating cao nhưng Buy Score chưa nổi bật"] = high_rating.sort_values("buy_score_100", ascending=True).head(1)
    else:
        cases["Rating cao nhưng Buy Score chưa nổi bật"] = d.sort_values(["rating", "buy_score_100"], ascending=[False, True]).head(1)

    # Giá tốt + ABSA tốt
    best_value = d[(d["price_score"] >= 0.65) & (d["absa_score"] >= 70)].copy()
    if not best_value.empty:
        cases["Giá tốt và review tích cực"] = best_value.sort_values("buy_score_100", ascending=False).head(1)
    else:
        cases["Giá tốt và review tích cực"] = d.sort_values(["price_score", "absa_score"], ascending=False).head(1)

    return cases

def case_card(title, row):
    if row.empty:
        return
    r = row.iloc[0]
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">{title}</div>
        <div class="insight-main">{short_name(r['product_name'], 85)}</div>
        <div class="insight-sub">
            Shop: <b>{r['shop']}</b> · Giá: <b>{fmt_price(r['current_price'])}</b><br>
            Rating: <b>{r['rating']:.2f}</b> · ABSA: <b>{r['absa_score']:.1f}</b> · Buy Score: <b>{r['buy_score_100']:.1f}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# Main header
# =========================
st.markdown("""
<div class="hero">
  <div class="eyebrow">Shopee · ABSA · Buy Score · Recommendation</div>
  <div class="hero-title">Hệ thống đề xuất sản phẩm đáng mua</div>
  <div class="hero-desc">Dashboard phân tích giá bán, rating, lượt bán và cảm xúc review theo khía cạnh để tìm sản phẩm đáng mua và so sánh shop bán cùng sản phẩm.</div>
</div>
""", unsafe_allow_html=True)

if page == "Tổng quan":
    k1,k2,k3,k4,k5 = st.columns(5)
    metrics = [
        ("Tổng sản phẩm", fmt_int(len(filtered)), "theo bộ lọc"),
        ("Buy Score TB", f"{filtered['buy_score_100'].mean():.1f}", "điểm đề xuất"),
        ("ABSA Score TB", f"{filtered['absa_score'].mean():.1f}", "cảm xúc review"),
        ("Rating TB", f"{filtered['rating'].mean():.2f}", "trên thang 5"),
        ("Tổng lượt bán", fmt_int(filtered['sold_count_num'].sum()), "sold_count_num"),
    ]
    for col, (label, val, note) in zip([k1,k2,k3,k4,k5], metrics):
        with col:
            st.markdown(f"<div class='card metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)

    top_summary_cards(filtered)

    c1, c2 = st.columns([1.35, 1])
    with c1:
        with st.container(border=True):
            section("Ma trận giá trị sản phẩm", "Xác định nhóm sản phẩm vừa giá tốt vừa được khách hàng đánh giá tích cực")
            st.plotly_chart(quadrant_chart(filtered), use_container_width=True)
    with c2:
        with st.container(border=True):
            section("Cơ cấu nhóm gợi ý", "Tỷ lệ sản phẩm theo nhãn recommendation")
            rec_count = filtered["recommendation_label"].value_counts().reset_index()
            rec_count.columns = ["Nhóm", "Số lượng"]
            fig = px.pie(rec_count, values="Số lượng", names="Nhóm", hole=.62)
            st.plotly_chart(plot_layout(fig, 500), use_container_width=True)

    with st.container(border=True):
        section("Top 10 sản phẩm đáng mua", "Danh sách rút gọn theo Buy Score")
        product_table_compact(filtered.head(10), height=340)

elif page == "Gợi ý sản phẩm":
    section("Gợi ý sản phẩm", "Trang này tập trung trả lời: sản phẩm nào đáng mua và vì sao đáng mua")

    with st.container(border=True):
        st.markdown("#### Hỏi nhanh nhu cầu")
        q1, q2 = st.columns([3, 1])
        with q1:
            quick_query = st.text_input("Nhập nhu cầu", placeholder="Ví dụ: Cần điện thoại chơi game mượt dưới 8 triệu", label_visibility="collapsed")
        with q2:
            run_query = st.button("Gợi ý", use_container_width=True)
        if run_query and quick_query.strip():
            result, reason = recommend_from_query(quick_query, n=8)
            st.info(reason)
            if result.empty:
                st.warning("Không tìm thấy sản phẩm phù hợp. Hãy thử tăng ngân sách hoặc ghi rõ loại sản phẩm.")
            else:
                product_table_compact(result, height=300)

    with st.container(border=True):
        section("Vì sao top sản phẩm được gợi ý?", "Biểu đồ cho thấy Buy Score đến từ ABSA review, giá, rating, lượt bán hay độ tin cậy")
        comp_long = score_contribution(filtered, n=10)
        fig = px.bar(comp_long, x="Điểm đóng góp", y="Sản phẩm", color="Thành phần", orientation="h")
        fig.update_layout(barmode="stack")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(plot_layout(fig, 560), use_container_width=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        with st.container(border=True):
            section("Khoảng giá nào đáng mua?", "So sánh Buy Score trung bình theo khoảng giá")
            band = make_price_band(filtered)
            band_sum = band.dropna(subset=["price_band"]).groupby("price_band", observed=False).agg(
                buy_score_tb=("buy_score_100", "mean"),
                so_san_pham=("product_name", "count")
            ).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=band_sum["price_band"].astype(str), y=band_sum["buy_score_tb"], name="Buy Score TB", text=[f"{x:.1f}" for x in band_sum["buy_score_tb"]], textposition="outside"))
            fig.add_trace(go.Scatter(x=band_sum["price_band"].astype(str), y=band_sum["so_san_pham"], name="Số sản phẩm", mode="lines+markers", yaxis="y2"))
            fig.update_layout(yaxis=dict(title="Buy Score TB"), yaxis2=dict(title="Số sản phẩm", overlaying="y", side="right", showgrid=False))
            st.plotly_chart(plot_layout(fig, 430), use_container_width=True)
    with c2:
        with st.container(border=True):
            section("Shop nào có sản phẩm đáng mua?", "Kích thước điểm thể hiện số sản phẩm, màu thể hiện ABSA trung bình")
            shop_score = filtered.groupby("shop").agg(
                buy_score_tb=("buy_score_100", "mean"),
                so_san_pham=("product_name", "count"),
                absa_tb=("absa_score", "mean"),
                rating_tb=("rating", "mean")
            ).reset_index().sort_values("buy_score_tb", ascending=False).head(10)
            fig = px.scatter(shop_score, x="rating_tb", y="buy_score_tb", size="so_san_pham", color="absa_tb", hover_name="shop",
                             labels={"rating_tb":"Rating TB", "buy_score_tb":"Buy Score TB", "so_san_pham":"Số sản phẩm", "absa_tb":"ABSA TB"})
            st.plotly_chart(plot_layout(fig, 430), use_container_width=True)

    with st.container(border=True):
        section("Top sản phẩm mạnh ở khía cạnh nào?", "Heatmap giúp biết sản phẩm được khen về giá, pin, camera, hiệu năng hay dịch vụ")
        fig = aspect_heatmap(filtered, n=12)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        section("Bảng xếp hạng chi tiết", "Bảng nằm cuối trang để kiểm tra và tải kết quả")
        product_table_compact(filtered, height=520)
        st.download_button("Tải ranked_products_final.csv", filtered.to_csv(index=False, encoding="utf-8-sig"), file_name="ranked_products_final.csv", mime="text/csv")

elif page == "So sánh cùng sản phẩm":
    section("So sánh cùng một sản phẩm giữa nhiều shop", "Dùng canonical_product_id để so sánh giá và review của cùng một sản phẩm")
    if same_compare.empty:
        st.info("Hiện chưa có nhóm sản phẩm nào được bán bởi từ 2 shop trở lên.")
    else:
        options = same_compare["canonical_product_name"].dropna().astype(str).sort_values().unique().tolist()
        selected = st.selectbox("Chọn sản phẩm chuẩn", options)
        view = same_compare[same_compare["canonical_product_name"].astype(str) == selected].sort_values("same_product_buy_score", ascending=False)
        c1, c2 = st.columns([1.1, 1])
        with c1:
            with st.container(border=True):
                section("Giá vs ABSA giữa các shop", "Góc trái trên là giá thấp hơn nhưng review vẫn tốt")
                fig = px.scatter(view, x="current_price", y="absa_score", size="sold_count_num", color="shop", hover_name="product_name",
                                 labels={"current_price":"Giá bán", "absa_score":"ABSA Score", "sold_count_num":"Lượt bán"})
                st.plotly_chart(plot_layout(fig, 440), use_container_width=True)
        with c2:
            with st.container(border=True):
                section("Điểm so sánh shop", "Same Product Buy Score dùng riêng cho cùng một sản phẩm")
                fig = px.bar(view.sort_values("same_product_buy_score"), x="same_product_buy_score", y="shop", orientation="h", text="same_product_buy_score",
                             labels={"same_product_buy_score":"Điểm so sánh", "shop":"Shop"})
                fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                st.plotly_chart(plot_layout(fig, 440, False), use_container_width=True)
        with st.container(border=True):
            display_product_table(view, columns="compare", height=360)

elif page == "Phân tích khía cạnh":
    section("Phân tích cảm xúc theo khía cạnh", "Xem khách hàng đang khen/chê sản phẩm ở điểm nào")
    aspect_summary = pd.DataFrame({
        "Aspect": [ASPECT_LABELS.get(a,a) for a in ASPECTS],
        "Positive": [filtered[f"{a}_positive_rate"].mean()*100 for a in ASPECTS],
        "Negative": [filtered[f"{a}_negative_rate"].mean()*100 for a in ASPECTS],
    })
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            section("Khía cạnh được khen nhiều", "Positive rate trung bình")
            fig = px.bar(aspect_summary.sort_values("Positive"), x="Positive", y="Aspect", orientation="h", text="Positive")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(plot_layout(fig, 450, False), use_container_width=True)
    with c2:
        with st.container(border=True):
            section("Khía cạnh có rủi ro tiêu cực", "Negative rate trung bình")
            fig = px.bar(aspect_summary.sort_values("Negative"), x="Negative", y="Aspect", orientation="h", text="Negative")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(plot_layout(fig, 450, False), use_container_width=True)

    with st.container(border=True):
        aspect = st.selectbox("Chọn khía cạnh để xem top sản phẩm", ASPECTS, format_func=lambda x: ASPECT_LABELS.get(x,x))
        top = filtered.sort_values(f"{aspect}_positive_rate", ascending=False).head(15)
        product_table_compact(top, height=420)

elif page == "Đánh giá kết quả":


    # 1. Rating vs Buy Score
    with st.container(border=True):
        section("Rating cao có luôn đáng mua không?", "So sánh rating và Buy Score để thấy hệ thống không chỉ phụ thuộc vào điểm sao")
        fig = px.scatter(
            filtered.head(350),
            x="rating",
            y="buy_score_100",
            size="sold_count_num",
            color="absa_score",
            hover_name="product_name",
            labels={
                "rating": "Rating",
                "buy_score_100": "Buy Score",
                "sold_count_num": "Lượt bán",
                "absa_score": "ABSA Score",
            }
        )
        fig.add_hline(y=65, line_dash="dash", line_color="#94A3B8")
        fig.add_vline(x=4.7, line_dash="dash", line_color="#94A3B8")
        st.plotly_chart(plot_layout(fig, 500), use_container_width=True)

    # 2. Top Rating vs Top Buy Score
    c1, c2 = st.columns(2)
    top_rating, top_buy = top_rating_vs_buy_tables(filtered, n=10)

    with c1:
        with st.container(border=True):
            section("Top 10 nếu chỉ xếp theo Rating", "Cách xếp hạng truyền thống, dễ thiếu yếu tố giá và nội dung review")
            product_table_compact(top_rating, height=360)

    with c2:
        with st.container(border=True):
            section("Top 10 theo Buy Score", "Cách xếp hạng của hệ thống, kết hợp nhiều tín hiệu hơn")
            product_table_compact(top_buy, height=360)

    # 3. Sensitivity Analysis
    with st.container(border=True):
        section("Sensitivity Analysis: thay đổi trọng số có làm kết quả đảo lộn không?", "Kiểm tra độ ổn định của hệ thống khi ưu tiên ABSA, giá hoặc độ phổ biến")
        sens, sens_data = sensitivity_analysis(filtered, n=10)

        c3, c4 = st.columns([1.1, 1])
        with c3:
            fig = px.bar(
                sens,
                x="Kịch bản",
                y="Tỷ lệ ổn định",
                text="Tỷ lệ ổn định",
                labels={"Tỷ lệ ổn định": "Tỷ lệ trùng Top 10 với công thức hiện tại (%)"}
            )
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig.update_yaxes(range=[0, 110])
            st.plotly_chart(plot_layout(fig, 380, False), use_container_width=True)

        with c4:
            st.dataframe(
                sens.round(2),
                use_container_width=True,
                hide_index=True,
                height=380
            )

elif page == "Chi tiết sản phẩm":
    selected = st.selectbox("Chọn sản phẩm", filtered["product_name"].astype(str).tolist())
    row = filtered[filtered["product_name"].astype(str) == selected].iloc[0]
    c1, c2 = st.columns([.9,1.1])
    with c1:
        st.markdown(f"""
        <div class='soft-card'>
        <div class='section-title'>{short_name(row['product_name'], 90)}</div>
        <div class='small-muted'>Shop: {row['shop']} · Brand: {row['brand']} · Loại: {row['product_type']}</div><br>
        Giá: <b>{fmt_price(row['current_price'])}</b><br>
        Rating: <b>{row['rating']:.2f}</b><br>
        Lượt bán: <b>{fmt_int(row['sold_count_num'])}</b><br>
        Buy Score: <b>{row['buy_score_100']:.1f}</b><br>
        ABSA Score: <b>{row['absa_score']:.1f}</b><br><br>
        {rec_badge(row['recommendation_label'])}
        </div>
        """, unsafe_allow_html=True)
        if str(row.get("product_url", "")) not in ["", "nan", "N/A", "Unknown"]:
            st.link_button("Mở sản phẩm trên Shopee", str(row["product_url"]))
    with c2:
        score_df = pd.DataFrame({
            "Thành phần": ["ABSA", "Giá", "Rating", "Lượt bán", "Độ tin cậy"],
            "Điểm": [row["absa_score_norm"]*100, row["price_score"]*100, row["rating_score"]*100, row["sold_score"]*100, row["review_confidence_score"]*100]
        })
        fig = px.bar(score_df, x="Thành phần", y="Điểm", text="Điểm", title="Thành phần tạo nên Buy Score")
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(plot_layout(fig, 380, False), use_container_width=True)
    aspect_df = pd.DataFrame({"Aspect":[ASPECT_LABELS.get(a,a) for a in ASPECTS], "Positive":[row[f"{a}_positive_rate"]*100 for a in ASPECTS], "Negative":[row[f"{a}_negative_rate"]*100 for a in ASPECTS]})
    fig = px.bar(aspect_df, x="Aspect", y=["Positive", "Negative"], barmode="group", title="Cảm xúc theo khía cạnh")
    st.plotly_chart(plot_layout(fig, 420), use_container_width=True)