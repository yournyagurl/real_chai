import sqlite3
import datetime
import pytz

def initialize_database():
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stats(
        MemberId INTEGER PRIMARY KEY,
        Cash INTEGER DEFAULT 0,
        Bank INTEGER DEFAULT 0,
        Xp INTEGER DEFAULT 0,
        Level INTEGER DEFAULT 0        
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Income (
        MemberId INTEGER,
        Cash INTEGER DEFAULT 0,
        LastDailyClaim TEXT,
        LastWeeklyClaim TEXT,
        FOREIGN KEY (MemberId) REFERENCES Stats(MemberId)
    )
''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Shop(
        ItemId INTEGER PRIMARY KEY,
        ItemName TEXT,
        ItemPrice INTEGER,
        ItemConsumable BOOLEAN,
        RoleAssigned INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Inventory(
        MemberId INTEGER,
        ItemId INTEGER,
        Quantity INTEGER DEFAULT 1,
        FOREIGN KEY (MemberId) REFERENCES Stats(MemberId),
        FOREIGN KEY (ItemId) REFERENCES Shop(ItemId)
    )''')

    connection.commit()
    cursor.close()
    connection.close()

def add_member(member_id):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO Stats (MemberId)
    VALUES (?)''', (member_id,))

    connection.commit()
    cursor.close()
    connection.close()

def add_cash(member_id, amount):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute(''' 
    UPDATE Stats
    SET Cash = Cash + ?
    WHERE MemberId = ?''', (amount, member_id))

    connection.commit()
    cursor.close()
    connection.close()

def add_xp(member_id, lvl):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    UPDATE Stats
    SET Xp = Xp + ?
    WHERE MemberId = ?''', (lvl, member_id))

    connection.commit()
    cursor.close()
    connection.close()

def reset_xp(member_id, new_xp):
    try:
        connection = sqlite3.connect("eli.db")
        cursor = connection.cursor()
        cursor.execute('''UPDATE stats SET Xp = ? WHERE MemberId = ?''', (new_xp, member_id))
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def remove_xp(member_id, lvl):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    UPDATE Stats
    SET Xp = Xp - ?
    WHERE MemberId = ?''', (lvl, member_id))

    connection.commit()
    cursor.close()
    connection.close()

def remove_cash(member_id, amount):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    UPDATE Stats
    SET Cash = Cash - ?
    WHERE MemberId = ?''', (amount, member_id))

    connection.commit()
    cursor.close()
    connection.close()


def reset_cash(member_id, new_cash):
    try:
        connection = sqlite3.connect("eli.db")
        cursor = connection.cursor()
        cursor.execute('''UPDATE stats SET Xp = ? WHERE MemberId = ?''', (new_cash, member_id))
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_xp(member_id):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    SELECT Xp 
    FROM Stats
    WHERE MemberId = ?''', (member_id,))

    result = cursor.fetchone()
    xp = result[0] if result else 0

    cursor.close()
    connection.close()

    return xp

def get_cash(member_id):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    SELECT Cash
    FROM Stats
    WHERE MemberId = ?''', (member_id,))
    
    result = cursor.fetchone()
    cash = result[0] if result else 0

    cursor.close()
    connection.close()

    return cash

def get_xp_leaderboard():
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    cursor.execute('''
    SELECT MemberId, Xp 
    FROM Stats
    ORDER BY Xp DESC
    LIMIT 10''')
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def get_cash_leaderboard():
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    cursor.execute('''
    SELECT MemberId, Cash 
    FROM Stats
    ORDER BY Cash DESC
    LIMIT 10''')
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def deposit(member_id, amount=None):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('SELECT Cash FROM Stats WHERE MemberId = ?', (member_id,))
    result = cursor.fetchone()
    cash = result[0] if result else 0

    if amount is None or amount > cash:
        amount = cash

    cursor.execute('''
    UPDATE Stats
    SET Cash = Cash - ?, Bank = Bank + ?
    WHERE MemberId = ?''', (amount, amount, member_id))

    connection.commit()
    cursor.close()
    connection.close()


def withdraw(member_id, amount=None):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('SELECT Bank FROM Stats WHERE MemberId = ?', (member_id,))
    result = cursor.fetchone()
    bank = result[0] if result else 0

    if amount is None or amount > bank:
        amount = bank

    cursor.execute('''
    UPDATE Stats
    SET Cash = Cash + ?, Bank = Bank - ?
    WHERE MemberId = ?''', (amount, amount, member_id))

    connection.commit()
    cursor.close()
    connection.close()

def get_bank_balance(member_id):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    SELECT Bank 
    FROM Stats
    WHERE MemberId = ?''', (member_id,))

    result = cursor.fetchone()
    bank_balance = result[0] if result else 0

    cursor.close()
    connection.close()

    return bank_balance

def get_inventory(member_id):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    SELECT s.ItemName, i.Quantity
    FROM Inventory i
    JOIN Shop s ON i.ItemId = s.ItemId
    WHERE i.MemberId = ?''', (member_id,))
    
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

def get_shop_items():
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    cursor.execute('''
    SELECT ItemName, ItemPrice
    FROM Shop''')
    
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

# Function to add a new item to the shop
def add_shop_item(name, price, consumable, role_assigned=None):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO Shop (ItemName, ItemPrice, ItemConsumable, RoleAssigned)
        VALUES (?, ?, ?, ?)
    ''', (name, price, consumable, role_assigned))
    connection.commit()
    connection.close()

# Function to delete an item from the shop
def delete_shop_item(item_name):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    cursor.execute('''
        DELETE FROM Shop
        WHERE ItemName = ?
    ''', (item_name,))
    connection.commit()
    connection.close()

# Function to edit the details of an item in the shop
def edit_shop_item(item_id, name=None, price=None, consumable=None, role_assigned=None):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    
    # Prepare the SQL query based on the provided parameters
    query = 'UPDATE Shop SET '
    if name:
        query += 'ItemName = ?, '
    if price:
        query += 'ItemPrice = ?, '
    if consumable is not None:
        query += 'ItemConsumable = ?, '
    if role_assigned is not None:
        query += 'RoleAssigned = ?, '
    query = query.rstrip(', ') + ' WHERE ItemId = ?'
    
    # Prepare the values to be updated
    values = []
    if name:
        values.append(name)
    if price:
        values.append(price)
    if consumable is not None:
        values.append(consumable)
    if role_assigned is not None:
        values.append(role_assigned)
    values.append(item_id)
    
    # Execute the query
    cursor.execute(query, values)
    connection.commit()
    connection.close()

def add_inventory_item(member_id, item_name):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    # Get the item ID from the Shop table
    cursor.execute('''
    SELECT ItemId
    FROM Shop
    WHERE ItemName = ?''', (item_name,))
    result = cursor.fetchone()
    if not result:
        # If the item doesn't exist in the shop, do nothing
        return

    item_id = result[0]

    # Check if the member already has the item in their inventory
    cursor.execute('''
    SELECT COUNT(*)
    FROM Inventory
    WHERE MemberId = ? AND ItemId = ?''', (member_id, item_id))
    result = cursor.fetchone()
    if result and result[0] > 0:
        # If the member already has the item, increase the quantity by 1
        cursor.execute('''
        UPDATE Inventory
        SET Quantity = Quantity + 1
        WHERE MemberId = ? AND ItemId = ?''', (member_id, item_id))
    else:
        # Otherwise, add a new row to the Inventory table with quantity 1
        cursor.execute('''
        INSERT INTO Inventory (MemberId, ItemId)
        VALUES (?, ?)''', (member_id, item_id))

    connection.commit()
    cursor.close()
    connection.close()

def use_inventory_item(member_id, item_name):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()

    # Get the item ID and effects from the Shop table
    cursor.execute('''
    SELECT ItemId, ItemConsumable, RoleAssigned
    FROM Shop
    WHERE ItemName = ?''', (item_name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError("Item not found in shop.")
    
    item_id, consumable, role_assigned = result

    # Check if the user has the item in their inventory
    cursor.execute('''
    SELECT Quantity
    FROM Inventory
    WHERE MemberId = ? AND ItemId = ?''', (member_id, item_id))
    result = cursor.fetchone()
    if not result or result[0] <= 0:
        raise ValueError("Item not found in inventory or quantity is zero.")
    
    quantity = result[0]

    # If the item is consumable, decrease its quantity
    if consumable:
        new_quantity = quantity - 1
        if new_quantity <= 0:
            cursor.execute('''
            DELETE FROM Inventory
            WHERE MemberId = ? AND ItemId = ?''', (member_id, item_id))
        else:
            cursor.execute('''
            UPDATE Inventory
            SET Quantity = ?
            WHERE MemberId = ? AND ItemId = ?''', (new_quantity, member_id, item_id))

    connection.commit()
    cursor.close()
    connection.close()
    return True

def get_last_claim_times(member_id, claim_type):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    column = 'LastDailyClaim' if claim_type == 'daily' else 'LastWeeklyClaim'
    cursor.execute(f'SELECT {column} FROM Income WHERE MemberId = ?', (member_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else None

# Function to update the last claim times
def update_last_claim_times(member_id, claim_type, time):
    connection = sqlite3.connect("eli.db")
    cursor = connection.cursor()
    column = 'LastDailyClaim' if claim_type == 'daily' else 'LastWeeklyClaim'
    
    # Check if the record already exists
    cursor.execute(f'SELECT 1 FROM Income WHERE MemberId = ?', (member_id,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Update the existing record
        cursor.execute(f'''
            UPDATE Income 
            SET {column} = ?
            WHERE MemberId = ?
        ''', (time, member_id))
    else:
        # Insert a new record
        cursor.execute(f'''
            INSERT INTO Income (MemberId, {column}) 
            VALUES (?, ?)
        ''', (member_id, time))
    
    connection.commit()
    cursor.close()
    connection.close()
