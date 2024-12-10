from flask_mysqldb import MySQL

mysql = MySQL()

def get_histories_by_user_id(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT age, hypertension, heart_disease, body_mass_index, HbA1c_level, 
               blood_glucose_level, gender, smoking_history, diabetes_category, check_date
        FROM histories WHERE user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    return rows

def find_user_by_email(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    cursor.close()
    return row

def create_user(name, email, password):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
    """, (name, email, password))
    mysql.connection.commit()
    cursor.close()

def find_user_by_id(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    return row

def find_user_by_name(name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE name = %s", (name,))
    row = cursor.fetchone()
    cursor.close()
    return row



def update_user_profile(user_id, name, password):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE users 
        SET name = COALESCE(%s, name), password = COALESCE(%s, password) 
        WHERE id = %s
    """, (name, password, user_id))
    mysql.connection.commit()
    cursor.close()
    return True  # Kembalikan True jika update berhasil

