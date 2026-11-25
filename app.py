import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NYC Airbnb Pricing", layout="wide")


@st.cache_data
def load_data():
  if os.path.exists("data/clean.csv"):
    return pd.read_csv("data/clean.csv")
  return pd.read_csv("clean.csv")


df = load_data()

st.title("تسعير الليلة في شقق نيويورك (NYC Airbnb)")
st.caption(
    "لوحة تحليل وأداة تسعير لمساعدة المضيفين على تحديد سعر منطقي وتنافسي."
)

neigh_col = (
    "neighbourhood_group"
    if "neighbourhood_group" in df.columns
    else df.select_dtypes(include="object").columns[0]
)
room_col = (
    "room_type"
    if "room_type" in df.columns
    else df.select_dtypes(include="object").columns[1]
)
price_col = (
    "price"
    if "price" in df.columns
    else df.select_dtypes(include="number").columns[0]
)

st.sidebar.header("الفلاتر")
all_neighs = sorted(df[neigh_col].dropna().unique())
all_rooms = sorted(df[room_col].dropna().unique())

selected_neigh = st.sidebar.multiselect(
    "الحي الرئيسي",
    options=all_neighs,
    default=all_neighs,
)
selected_room = st.sidebar.multiselect(
    "نوع الغرفة",
    options=all_rooms,
    default=all_rooms,
)

filtered_df = df[
    df[neigh_col].isin(selected_neigh) & df[room_col].isin(selected_room)
]
if filtered_df.empty:
  filtered_df = df

tab1, tab2, tab3 = st.tabs(["1. نظرة عامة", "2. الاكتشافات", "3. المنتج"])

with tab1:
  c1, c2, c3 = st.columns(3)
  c1.metric("عدد الإعلانات", f"{len(filtered_df):,}")
  c2.metric("متوسط السعر", f"${filtered_df[price_col].mean():.2f}")
  c3.metric("وسيط السعر", f"${filtered_df[price_col].median():.2f}")

  st.subheader("عينة من البيانات المفلترة")
  st.dataframe(filtered_df.head(15), use_container_width=True)

with tab2:
  st.subheader("رسومات بيانية من البيانات")

  col_a, col_b = st.columns(2)

  with col_a:
    neigh_med = (
        filtered_df.groupby(neigh_col)[price_col]
        .median()
        .sort_values(ascending=False)
    )
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(neigh_med.index.astype(str), neigh_med.values)
    ax1.set_title("Median Price by Neighbourhood Group")
    ax1.set_ylabel("Price ($)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    st.pyplot(fig1)

    top_n = neigh_med.index[0]
    top_v = neigh_med.iloc[0]
    st.write(
        f"أعلى وسيط سعر يظهر في *{top_n}* بقيمة *${top_v:.2f}* لليلة."
    )

  with col_b:
    room_med = (
        filtered_df.groupby(room_col)[price_col]
        .median()
        .sort_values(ascending=False)
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(room_med.index.astype(str), room_med.values)
    ax2.set_title("Median Price by Room Type")
    ax2.set_ylabel("Price ($)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    st.pyplot(fig2)

    top_r = room_med.index[0]
    top_rv = room_med.iloc[0]
    st.write(
        f"فئة *{top_r}* تتصدر بوسيط سعر يبلغ *${top_rv:.2f}* مقارنة بباقي"
        " الفئات."
    )

  st.markdown("### أهم الاكتشافات والتوصيات")
  st.write(
      "- يختلف السعر بشكل واضح باختلاف نوع الغرفة والحي، مما يجعل الاعتماد"
      " على الوسيط أدق من المتوسط عند وجود أسعار مرتفعة جداً."
  )
  st.write(
      "- التوصية 1: تسعير الوحدات الكاملة في الأحياء عالية الطلب بناءً على"
      " وسيط الحي ونوع الغرفة لتجنب التسعير المبالغ فيه أو الخسارة."
  )
  st.write(
      "- التوصية 2: في الأحياء الأقل سعراً، الاعتماد على سعر تنافسي قريب من"
      " وسيط الفئة لرفع فرص الحجز."
  )
  st.write(
      "- التوصية 3: استخدام البيانات كمرجع أولي مع مراعاة عوامل غير مرصودة"
      " مثل جودة الصور والتقييمات (الارتباط لا يعني السببية)."
  )

with tab3:
  st.subheader("أداة تقدير السعر المقترح للمضيف")

  u_neigh = st.selectbox("اختر الحي الرئيسي", all_neighs)
  u_room = st.selectbox("اختر نوع الغرفة", all_rooms)

  similar = df[(df[neigh_col] == u_neigh) & (df[room_col] == u_room)][
      price_col
  ]
  if similar.empty:
    similar = df[df[room_col] == u_room][price_col]

  est_price = similar.median()
  st.success(
      f"السعر المقترح لليلة: *${est_price:.2f}* (بناءً على"
      f" {len(similar):,} إعلان مشابه)"
  )
  st.caption(
      "كيف وصلنا للنتيجة؟ حسبنا وسيط أسعار الإعلانات المطابقة للحي ونوع"
      " الغرفة المختارين من البيانات المنظفة لأنه يمثل القيمة النموذجية"
      " دون تأثر بالقيم الشاذة."
  )