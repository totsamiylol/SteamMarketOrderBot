import sqlite3

def get_data(account_id, type_, rarity, wear=None, stat_trak=None):
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    if type_ == "Case Skins":
        c.execute(f"SELECT * FROM all_data WHERE id=? AND type=? AND rarity=? AND wear=? AND stat_trak=?", (account_id, type_, rarity, wear, stat_trak))
    elif type_ == "Op Skins":
        c.execute(f"SELECT * FROM all_data WHERE id=? AND type=? AND rarity=? AND wear=?", (account_id, type_, rarity, wear))
    else:
        c.execute(f"SELECT * FROM all_data WHERE id=? AND type=? AND rarity=?", (account_id, type_, rarity))
    data = c.fetchone()

    # Close the database connection
    conn.close()
    return data

def get_all_data():
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Query the skin table
    c.execute(f"SELECT * FROM all_data")
    data = c.fetchall()

    # Close the database connection
    conn.close()
    return data

def check_existence(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS all_data (
            id INTEGER,
            type TEXT,
            rarity TEXT,
            wear TEXT,
            stat_trak TEXT,
            price REAL,
            quantity INTEGER
        )""")


def add_data(account_id, type_, rarity, wear=None, stat_trak=None, price=0, quantity=0):
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Create database if not exists
    check_existence(c)

    c.execute("""
            SELECT COUNT(*) FROM all_data
            WHERE id=? AND type=? AND rarity=? AND wear=? AND stat_trak=?
            """, (account_id, type_, rarity, wear, stat_trak))
    exists = c.fetchone()[0]
    if exists:
        return False

    if type_ == "Case Skins":
        c.execute("""
                    SELECT COUNT(*) FROM all_data
                    WHERE id=? AND type=? AND rarity=? AND wear=? AND stat_trak=?
                    """, (account_id, type_, rarity, wear, stat_trak))
        exists = c.fetchone()[0]
        if exists:
            return False
        else:
            c.execute(f"INSERT INTO all_data (id, type, rarity, wear, stat_trak, price, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (account_id, type_, rarity, wear, stat_trak, price, quantity))

    elif type_ == "Op Skins":
        c.execute("""
                    SELECT COUNT(*) FROM all_data
                    WHERE id=? AND type=? AND rarity=? AND wear=?
                    """, (account_id, type_, rarity, wear))
        exists = c.fetchone()[0]
        if exists:
            return False
        else:
            c.execute(f"INSERT INTO all_data (id, type, rarity, wear, price, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                      (account_id, type_, rarity, wear, price, quantity))

    else:
        c.execute("""
                    SELECT COUNT(*) FROM all_data
                    WHERE id=? AND type=? AND rarity=?
                    """, (account_id, type_, rarity))
        exists = c.fetchone()[0]
        if exists:
            return False
        else:
            c.execute(f"INSERT INTO all_data (id, type, rarity, price, quantity) VALUES (?, ?, ?, ?, ?)",
                      (account_id, type_, rarity, price, quantity))

    # Commit changes and close the database connection
    conn.commit()
    conn.close()
    return True

def delete_all_data():
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Delete skin data
    c.execute(f"DELETE FROM all_data")

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

def delete_data(account_id, type_, rarity, wear=None, stat_trak=None):
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Delete skin data
    if type_ == "Case Skins":
        c.execute(f"DELETE FROM all_data WHERE id=? AND type=? AND rarity=? AND wear=? AND stat_trak=?", (account_id, type_, rarity, wear, stat_trak))
    elif type_ == "Op Skins":
        c.execute(f"DELETE FROM all_data WHERE id=? AND type=? AND rarity=? AND wear=?", (account_id, type_, rarity, wear))
    else:
        c.execute(f"DELETE FROM all_data WHERE id=? AND type=? AND rarity=?", (account_id, type_, rarity))

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    # Create database if not exists
    check_existence(c)

    print(get_data("25068251", "Case Skins", "Mil-Spec Grade", "Factory New", "No"))
    print(get_data("25068251", "Case Skins", "Restricted", "Minimal Wear", "Yes"))
    print(get_data("25068251", "Op Skins", "Industrial Grade", "Field-Tested", "None"))

    # Commit changes and close the database connection
    conn.commit()
    conn.close()
