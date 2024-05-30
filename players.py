import sqlite3
import xml.etree.ElementTree as ET
from tqdm import tqdm

# Function to parse the XML file and insert data into the SQLite database
def parse_xml_to_sqlite(xml_file, db_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist, with nullable fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        fideid INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        sex TEXT,
        title TEXT,
        w_title TEXT,
        o_title TEXT,
        foa_title TEXT,
        rating INTEGER,
        games INTEGER,
        k INTEGER,
        rapid_rating INTEGER,
        rapid_games INTEGER,
        rapid_k INTEGER,
        blitz_rating INTEGER,
        blitz_games INTEGER,
        blitz_k INTEGER,
        birthday INTEGER,
        flag TEXT
    )
    ''')

    # Function to convert text to integer, returning None if the text is empty
    def to_int(value):
        return int(value) if value and value.isdigit() else None

    # Function to return the text of an element or None if the element is missing
    def maybe(element):
        return element.text if element is not None else None

    # Get the list of players
    players = root.findall('player')
    
    # Iterate over each player in the XML and insert into the database with a progress bar
    for player in tqdm(players, desc="Processing players"):
        try:
            fideid = to_int(maybe(player.find('fideid')))
            name = maybe(player.find('name'))
            country = maybe(player.find('country'))
            sex = maybe(player.find('sex'))
            title = maybe(player.find('title'))
            w_title = maybe(player.find('w_title'))
            o_title = maybe(player.find('o_title'))
            foa_title = maybe(player.find('foa_title'))

            rating = to_int(maybe(player.find('rating')))
            games = to_int(maybe(player.find('games')))
            k = to_int(maybe(player.find('k')))
            rapid_rating = to_int(maybe(player.find('rapid_rating')))
            rapid_games = to_int(maybe(player.find('rapid_games')))
            rapid_k = to_int(maybe(player.find('rapid_k')))
            blitz_rating = to_int(maybe(player.find('blitz_rating')))
            blitz_games = to_int(maybe(player.find('blitz_games')))
            blitz_k = to_int(maybe(player.find('blitz_k')))
            birthday = to_int(maybe(player.find('birthday')))
            flag = maybe(player.find('flag'))

            cursor.execute('''
            INSERT OR REPLACE INTO players (
                fideid, name, country, sex, title, w_title, o_title, foa_title,
                rating, games, k, rapid_rating, rapid_games, rapid_k, blitz_rating,
                blitz_games, blitz_k, birthday, flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fideid, name, country, sex, title, w_title, o_title, foa_title,
                rating, games, k, rapid_rating, rapid_games, rapid_k, blitz_rating,
                blitz_games, blitz_k, birthday, flag
            ))

        except Exception as e:
            print(f"Error processing player: {ET.tostring(player, encoding='unicode')}")
            print(f"Error details: {e}")
            break

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print("Data has been successfully imported into the SQLite database.")

# Example usage
xml_file = 'players.xml'
db_file = 'players.db'
parse_xml_to_sqlite(xml_file, db_file)
