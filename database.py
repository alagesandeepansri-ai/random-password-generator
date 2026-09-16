import sqlite3


def create_database():

    conn = sqlite3.connect("password_generator.db")

    cursor = conn.cursor()


    # User table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE,

            mobile TEXT UNIQUE,

            dob TEXT NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # Password history table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            password TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id)

        )
    """)


    # Admin table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # Default admin account

    cursor.execute("""
        INSERT OR IGNORE INTO admin (username, password)
        VALUES ('admin', 'admin123')
    """)


    conn.commit()

    conn.close()


if __name__ == "__main__":
    create_database()

    print("Database created successfully!")