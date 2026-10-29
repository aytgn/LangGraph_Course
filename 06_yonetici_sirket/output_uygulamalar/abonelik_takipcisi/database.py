import sqlite3

def get_connection():
    return sqlite3.connect('subscriptions.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, category TEXT, renewal_date DATE)''')
    cursor.execute('SELECT count(*) FROM subscriptions')
    if cursor.fetchone()[0] == 0:
        seed_data = [('Netflix', 150.0, 'Eğlence', '2023-11-15'), ('Spotify', 40.0, 'Eğlence', '2023-11-20'), ('Google One', 30.0, 'Bulut', '2023-12-01'), ('GitHub Pro', 120.0, 'Yazılım', '2023-11-25')]
        cursor.executemany('INSERT INTO subscriptions (name, amount, category, renewal_date) VALUES (?,?,?,?)', seed_data)
        conn.commit()
    conn.close()

def add_subscription(data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subscriptions (name, amount, category, renewal_date) VALUES (?,?,?,?)', data)
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f'Veritabanı ekleme hatası: {e}')

def get_all_subscriptions_raw():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscriptions')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_subscription(sub_id, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE subscriptions SET name=?, amount=?, category=?, renewal_date=? WHERE id=?', (*data, sub_id))
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f'Güncelleme hatası: {e}')

def delete_subscription(sub_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE id = ?', (sub_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f'Silme hatası: {e}')