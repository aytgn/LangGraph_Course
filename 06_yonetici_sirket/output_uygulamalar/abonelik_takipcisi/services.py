import pandas as pd
import plotly.express as px
from datetime import datetime

def get_df(data):
    return pd.DataFrame(data, columns=['id', 'name', 'amount', 'category', 'renewal_date'])

def calculate_monthly_total(df):
    return df['amount'].sum() if not df.empty else 0.0

def calculate_yearly_total(df):
    return df['amount'].sum() * 12 if not df.empty else 0.0

def get_category_distribution(df):
    if df.empty: return None
    return px.pie(df, values='amount', names='category', title='Kategori Bazlı Dağılım')

def get_upcoming_payments(df):
    if df.empty: return df
    df['renewal_date'] = pd.to_datetime(df['renewal_date'])
    return df.sort_values(by='renewal_date').head(5)