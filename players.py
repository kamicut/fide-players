import sqlite3
import xml.etree.ElementTree as ET
from tqdm import tqdm

def convert_to_none(value):
    return value if value else None

def create_database(db_file):
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()

        # Create players table
        c.execute('''CREATE TABLE IF NOT EXISTS players (
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
                )''')

        # Create the FTS5 virtual table
        c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS players_fts USING fts5(
                    name, 
                    content='players', 
                    content_rowid='fideid'
                )''')

        # Set up triggers to keep the FTS table in sync with the original table
        c.executescript('''
            CREATE TRIGGER IF NOT EXISTS players_ai AFTER INSERT ON players BEGIN
              INSERT INTO players_fts(rowid, name) VALUES (new.fideid, new.name);
            END;
            
            CREATE TRIGGER IF NOT EXISTS players_ad AFTER DELETE ON players BEGIN
              DELETE FROM players_fts WHERE rowid=old.fideid;
            END;
            
            CREATE TRIGGER IF NOT EXISTS players_au AFTER UPDATE ON players BEGIN
              UPDATE players_fts SET name = new.name WHERE rowid=old.fideid;
            END;
        ''')

def parse_xml_to_sqlite(xml_file, db_file, batch_size=1000):
    create_database(db_file)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()
        
        # Disable synchronous writes and journal for faster inserts
        c.execute('PRAGMA synchronous = OFF')
        c.execute('PRAGMA journal_mode = MEMORY')
        
        # Prepare the insert statement
        insert_stmt = '''
            INSERT OR IGNORE INTO players (
                fideid, name, country, sex, title, w_title, o_title, foa_title,
                rating, games, k, rapid_rating, rapid_games, rapid_k,
                blitz_rating, blitz_games, blitz_k, birthday, flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        players = []
        for player in tqdm(root.findall('player'), desc="Processing players"):
            fideid = int(player.find('fideid').text)
            name = player.find('name').text
            country = player.find('country').text
            sex = player.find('sex').text
            title = convert_to_none(player.find('title').text)
            w_title = convert_to_none(player.find('w_title').text)
            o_title = convert_to_none(player.find('o_title').text)
            foa_title = convert_to_none(player.find('foa_title').text)
            rating = int(player.find('rating').text) if player.find('rating').text else None
            games = int(player.find('games').text) if player.find('games').text else None
            k = int(player.find('k').text) if player.find('k').text else None
            rapid_rating = int(player.find('rapid_rating').text) if player.find('rapid_rating').text else None
            rapid_games = int(player.find('rapid_games').text) if player.find('rapid_games').text else None
            rapid_k = int(player.find('rapid_k').text) if player.find('rapid_k').text else None
            blitz_rating = int(player.find('blitz_rating').text) if player.find('blitz_rating').text else None
            blitz_games = int(player.find('blitz_games').text) if player.find('blitz_games').text else None
            blitz_k = int(player.find('blitz_k').text) if player.find('blitz_k').text else None
            birthday = int(player.find('birthday').text) if player.find('birthday').text else None
            flag = convert_to_none(player.find('flag').text)
            
            players.append((
                fideid, name, country, sex, title, w_title, o_title, foa_title,
                rating, games, k, rapid_rating, rapid_games, rapid_k,
                blitz_rating, blitz_games, blitz_k, birthday, flag
            ))
            
            # Process in batches to avoid memory issues
            if len(players) >= batch_size:
                c.executemany(insert_stmt, players)
                players = []
                conn.commit()
        
        # Insert remaining players
        if players:
            c.executemany(insert_stmt, players)
            conn.commit()
        
        # Create indices after data insertion for better performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_country ON players (country)')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse XML and store data into SQLite.')
    parser.add_argument('xml_file', help='Path to the XML file to parse.')
    parser.add_argument('db_file', help='Path to the SQLite database file.')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for database inserts')

    args = parser.parse_args()
    parse_xml_to_sqlite(args.xml_file, args.db_file, args.batch_size)
