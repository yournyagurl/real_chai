import sqlite3

def initialize_database():
    try:
        connection = sqlite3.connect("eli.db")
        cursor = connection.cursor()

        # Drop the old Pets table if it exists
        cursor.execute('''DROP TABLE IF EXISTS Pets''')

        # Create a new table with the desired schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pets (
                PetId INTEGER PRIMARY KEY,
                MemberId INTEGER UNIQUE NOT NULL,
                PetName TEXT NOT NULL,
                LastFedDate TEXT,  -- Allow NULL values for LastFedDate
                image_url TEXT,
                AdoptionDate TEXT,
                Level TEXT DEFAULT 'newborn',
                FOREIGN KEY (MemberId) REFERENCES Stats(MemberId)
            )
        ''')

        connection.commit()
        cursor.close()
        connection.close()

        print("Tables initialized successfully: Pets created.")

    except sqlite3.Error as error:
        print("Error initializing database:", error)

# Call the function to initialize the database
initialize_database()
