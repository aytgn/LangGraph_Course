import streamlit as st
import pandas as pd
from database import init_db, add_subscription, get_all_subscriptions_raw, delete_subscription, update_subscription
from services import get_df, calculate_monthly_total, calculate_yearly_total, get_category_distribution, get_upcoming_payments

init_db()
st.set_page_config(page_title='Abonelik Takipçisi', layout='wide')
st.title('Abonelik ve Gider Takipçisi')

raw_data = get_all_subscriptions_raw()
df = get_df(raw_data)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader('Yeni Abonelik Ekle')
    with st.form('add_sub'):
        name = st.text_input('Abonelik Adı')
        amount = st.number_input('Tutar', min_value=0.0)
        category = st.selectbox('Kategori', ['Eğlence', 'Bulut', 'Yazılım', 'Diğer'])
        date = st.date_input('Yenilenme Tarihi')
        if st.form_submit_button('Kaydet'):
            add_subscription((name, amount, category, str(date)))
            st.rerun()

with col2:
    m1, m2 = st.columns(2)
    m1.metric('Aylık Toplam', f'{calculate_monthly_total(df):.2f} TL')
    m2.metric('Yıllık Toplam', f'{calculate_yearly_total(df):.2f} TL')
    st.dataframe(df, use_container_width=True)

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    st.subheader('Yaklaşan Ödemeler')
    st.table(get_upcoming_payments(df)[['name', 'renewal_date', 'amount']])
with col_b:
    st.plotly_chart(get_category_distribution(df), use_container_width=True)

st.divider()
with st.expander('Abonelik Yönetimi (Sil/Güncelle)'):
    sub_id = st.number_input('İşlem Yapılacak ID', min_value=1, step=1)
    if st.button('Sil'):
        delete_subscription(sub_id)
        st.rerun()