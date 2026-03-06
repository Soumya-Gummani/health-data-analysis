import sqlite3 as sql

# Connect to the database (creates stroke.db if it doesn't exist)
conn = sql.connect('stroke.db')
print("Opened database successfully")

# Create 'signup' table
conn.execute('''
CREATE TABLE IF NOT EXISTS signup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uname TEXT NOT NULL,
    uphone TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    upassword TEXT NOT NULL
)
''')

# Create 'adminlogin' table
conn.execute('''
CREATE TABLE IF NOT EXISTS adminlogin (
    ausername TEXT PRIMARY KEY,
    apassword TEXT NOT NULL
)
''')

# Create 'patient' table
conn.execute('''
CREATE TABLE IF NOT EXISTS patient (
    ausername TEXT PRIMARY KEY,
    apassword TEXT NOT NULL
)
''')

# Create 'appointment' table
conn.execute('''
CREATE TABLE IF NOT EXISTS appointment (
    pname TEXT,
    pnumber TEXT,
    specialist TEXT
)
''')

# Create 'predict' table
conn.execute('''
CREATE TABLE IF NOT EXISTS predict (
    gender TEXT,
    age TEXT,
    hypertension TEXT,
    heart_disease TEXT,
    work_type TEXT,
    Residence_type TEXT,
    avg_glucose_level TEXT,
    bmi TEXT,
    smoking_status TEXT
)
''')

# Insert test user if not exists
cursor = conn.cursor()
cursor.execute("SELECT * FROM signup WHERE username = ?", ('soumya@example.com',))
if cursor.fetchone() is None:
    conn.execute("INSERT INTO signup (uname, uphone, username, upassword) VALUES (?, ?, ?, ?)",
                 ('Soumya S', '9876543210', 'soumya@example.com', '1234'))
    print("Test user inserted")

# Insert test admin if not exists
cursor.execute("SELECT * FROM adminlogin WHERE ausername = ?", ('admin@example.com',))
if cursor.fetchone() is None:
    conn.execute("INSERT INTO adminlogin (ausername, apassword) VALUES (?, ?)",
                 ('admin@example.com', 'admin123'))
    print("Test admin inserted")

# Insert test patient if not exists
cursor.execute("SELECT * FROM patient WHERE ausername = ?", ('patient@example.com',))
if cursor.fetchone() is None:
    conn.execute("INSERT INTO patient (ausername, apassword) VALUES (?, ?)",
                 ('patient@example.com', 'patient123'))
    print("Test patient inserted")

conn.commit()
conn.close()
print("Database setup completed successfully.")
