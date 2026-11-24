import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NYC Airbnb Pricing Dashboard", layout="wide")


@st.cache_data
def load_data():
  try:
    return pd.read_csv("data/clean.csv")
  except FileNotFoundError:
    return pd.read_csv("clean.csv")


df = load_data()

st.title("لوحة تحكم تسعير شقق نيويورك (NYC Airbnb)")
st.caption("النسخة الأولى — تتغير المؤشرات والرسومات تلقائياً حسب الفلاتر")

# --- Sidebar Filters ---
st.sidebar.header("الفلاتر (Filters)")

neigh_options = sorted(df["neighbourhood_group"].dropna().unique())
selected_neigh = st.sidebar.multiselect(
    "الحي (neighbourhood_group)", options=neigh_options, default=neigh_options
)

room_options = sorted(df["room_type"].dropna().unique())
selected_room = st.sidebar.multiselect(
    "نوع الغرفة (room_type)", options=room_options, default=room_options
)

min_p, max_p = int(df["price"].min()), int(df["price"].max())
selected_price = st.sidebar.slider(
    "نطاق السعر ($)",
    min_value=min_p,
    max_value=max_p,
    value=(min_p, max_p),
)

filtered_df = df[
    (df["neighbourhood_group"].isin(selected_neigh))
    & (df["room_type"].isin(selected_room))
    & (df["price"] >= selected_price[0])
    & (df["price"] <= selected_price[1])
]

# --- 4 KPIs (st.metric) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric("عدد الإعلانات", f"{len(filtered_df):,}")
with col2:
  mean_price = filtered_df["price"].mean() if len(filtered_df) > 0 else 0
  st.metric("متوسط السعر ($)", f"{mean_price:,.2f}")
with col3:
  median_price = filtered_df["price"].median() if len(filtered_df) > 0 else 0
  st.metric("وسيط السعر ($)", f"{median_price:,.1f}")
with col4:
  avg_reviews = (
      filtered_df["number_of_reviews"].mean() if len(filtered_df) > 0 else 0
  )
  st.metric("متوسط التقييمات", f"{avg_reviews:,.1f}")

st.divider()

# --- 3 Charts ---
if len(filtered_df) > 0:
  c1, c2 = st.columns(2)

  with c1:
    st.subheader("1. متوسط السعر حسب الحي")
    neigh_mean = (
        filtered_df.groupby("neighbourhood_group")["price"]
        .mean()
        .sort_values(ascending=False)
    )
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(neigh_mean.index, neigh_mean.values)
    ax1.set_title("Average Price by Neighbourhood Group")
    ax1.set_xlabel("Neighbourhood Group")
    ax1.set_ylabel("Average Price ($)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    st.pyplot(fig1)

  with c2:
    st.subheader("2. متوسط السعر حسب نوع الغرفة")
    room_mean = (
        filtered_df.groupby("room_type")["price"]
        .mean()
        .sort_values(ascending=False)
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(room_mean.index, room_mean.values)
    ax2.set_title("Average Price by Room Type")
    ax2.set_xlabel("Room Type")
    ax2.set_ylabel("Average Price ($)")
    plt.tight_layout()
    st.pyplot(fig2)

  st.subheader("3. عدد الإعلانات حسب الحي")
  neigh_count = filtered_df["neighbourhood_group"].value_counts()
  fig3, ax3 = plt.subplots(figsize=(8, 3.8))
  ax3.bar(neigh_count.index, neigh_count.values)
  ax3.set_title("Number of Listings by Neighbourhood Group")
  ax3.set_xlabel("Neighbourhood Group")
  ax3.set_ylabel("Number of Listings")
  plt.tight_layout()
  st.pyplot(fig3)
else:
  st.warning("لا توجد بيانات مطابقة للفلاتر المختارة حالياً.")