# database.py
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name="web_scraper.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # Drop existing tables to ensure schema consistency
        self.cursor.execute("DROP TABLE IF EXISTS scraped_data")
        self.cursor.execute("DROP TABLE IF EXISTS scrape_history")
        self.cursor.execute("DROP TABLE IF EXISTS product_data")
        self.create_tables()

    def create_tables(self):
        """Create necessary tables with expanded schema"""
        # Table for general scraped data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                emails TEXT,
                phone_numbers TEXT,
                social_links TEXT,
                meta_info TEXT,
                headers TEXT,
                main_content TEXT,
                contact_info TEXT,
                images TEXT,
                links TEXT,
                scrape_date TIMESTAMP,
                last_updated TIMESTAMP,
                UNIQUE(url)
            )
        ''')
        
        # Table for logging scrape attempts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                scrape_date TIMESTAMP,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        # Table for product-specific data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                price REAL,
                currency TEXT,
                rating REAL,
                reviews_count INTEGER,
                availability TEXT,
                image_url TEXT,
                seller TEXT,
                specifications TEXT,
                scrape_date TIMESTAMP,
                last_updated TIMESTAMP,
                UNIQUE(url)
            )
        ''')
        self.conn.commit()

    def log_scrape_attempt(self, url, status, error_message=None):
        """Log a scrape attempt into the scrape_history table."""
        current_time = datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO scrape_history (url, scrape_date, status, error_message)
            VALUES (?, ?, ?, ?)
        ''', (url, current_time, status, error_message))
        self.conn.commit()

    def insert_data(self, data):
        """Insert scraped data into the database with JSON serialization"""
        current_time = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO scraped_data (
                url, emails, phone_numbers, social_links, meta_info,
                headers, main_content, contact_info, images, links,
                scrape_date, last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["url"],
            json.dumps(data.get("emails", [])),
            json.dumps(data.get("phone_numbers", [])),
            json.dumps(data.get("social_links", [])),
            json.dumps(data.get("meta_info", {})),
            json.dumps(data.get("headers", {})),
            json.dumps(data.get("main_content", [])),
            json.dumps(data.get("contact_info", {})),
            json.dumps(data.get("images", [])),
            json.dumps(data.get("links", [])),
            current_time,
            current_time
        ))
        self.conn.commit()

    def update_data(self, url, data):
        """Update existing data with JSON serialization"""
        current_time = datetime.now().isoformat()
        
        self.cursor.execute('''
            UPDATE scraped_data
            SET emails = ?,
                phone_numbers = ?,
                social_links = ?,
                meta_info = ?,
                headers = ?,
                main_content = ?,
                contact_info = ?,
                images = ?,
                links = ?,
                last_updated = ?
            WHERE url = ?
        ''', (
            json.dumps(data.get("emails", [])),
            json.dumps(data.get("phone_numbers", [])),
            json.dumps(data.get("social_links", [])),
            json.dumps(data.get("meta_info", {})),
            json.dumps(data.get("headers", {})),
            json.dumps(data.get("main_content", [])),
            json.dumps(data.get("contact_info", {})),
            json.dumps(data.get("images", [])),
            json.dumps(data.get("links", [])),
            current_time,
            url
        ))
        self.conn.commit()

    def insert_product_data(self, product_data):
        """Insert product-specific data into the database."""
        current_time = datetime.now().isoformat()
        
        for product in product_data.get("products", []):
            self.cursor.execute('''
                INSERT INTO product_data (
                    url, title, price, currency, rating, reviews_count,
                    availability, image_url, seller, specifications,
                    scrape_date, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data["url"],
                product.get("title"),
                product.get("price"),
                product.get("currency"),
                product.get("rating"),
                product.get("reviews_count"),
                product.get("availability"),
                product.get("image_url"),
                product.get("seller"),
                json.dumps(product.get("specifications", {})),
                current_time,
                current_time
            ))
        self.conn.commit()

    def update_product_data(self, url, product_data):
        """Update product-specific data in the database."""
        current_time = datetime.now().isoformat()
        
        for product in product_data.get("products", []):
            self.cursor.execute('''
                UPDATE product_data
                SET title = ?,
                    price = ?,
                    currency = ?,
                    rating = ?,
                    reviews_count = ?,
                    availability = ?,
                    image_url = ?,
                    seller = ?,
                    specifications = ?,
                    last_updated = ?
                WHERE url = ?
            ''', (
                product.get("title"),
                product.get("price"),
                product.get("currency"),
                product.get("rating"),
                product.get("reviews_count"),
                product.get("availability"),
                product.get("image_url"),
                product.get("seller"),
                json.dumps(product.get("specifications", {})),
                current_time,
                url
            ))
        self.conn.commit()

    def fetch_data(self, url):
        """Fetch general scraped data for a specific URL with JSON deserialization"""
        self.cursor.execute('SELECT * FROM scraped_data WHERE url = ?', (url,))
        row = self.cursor.fetchone()
        if row:
            return self._deserialize_row(row)
        return None

    def fetch_product_data(self, url):
        """Fetch product-specific data for a specific URL."""
        self.cursor.execute('SELECT * FROM product_data WHERE url = ?', (url,))
        rows = self.cursor.fetchall()
        if rows:
            return [self._deserialize_product_row(row) for row in rows]
        return None

   # In database.py, modify the fetch methods:

    def fetch_all_data(self):
        """Fetch all general scraped data with JSON deserialization"""
        try:
            self.cursor.execute('SELECT * FROM scraped_data ORDER BY last_updated DESC')
            rows = self.cursor.fetchall()
            return [self._deserialize_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def fetch_all_product_data(self):
        """Fetch all product-specific data."""
        try:
            self.cursor.execute('SELECT * FROM product_data ORDER BY last_updated DESC')
            rows = self.cursor.fetchall()
            return [self._deserialize_product_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching product data: {e}")
            return []

    def _deserialize_row(self, row):
        """Helper method to deserialize JSON data from general scraped data row"""
        return {
            'id': row[0],
            'url': row[1],
            'emails': json.loads(row[2]) if row[2] else [],
            'phone_numbers': json.loads(row[3]) if row[3] else [],
            'social_links': json.loads(row[4]) if row[4] else [],
            'meta_info': json.loads(row[5]) if row[5] else {},
            'headers': json.loads(row[6]) if row[6] else {},
            'main_content': json.loads(row[7]) if row[7] else [],
            'contact_info': json.loads(row[8]) if row[8] else {},
            'images': json.loads(row[9]) if row[9] else [],
            'links': json.loads(row[10]) if row[10] else [],
            'scrape_date': row[11],
            'last_updated': row[12]
        }

    def _deserialize_product_row(self, row):
        """Helper method to deserialize product-specific data row"""
        return {
            'id': row[0],
            'url': row[1],
            'title': row[2],
            'price': row[3],
            'currency': row[4],
            'rating': row[5],
            'reviews_count': row[6],
            'availability': row[7],
            'image_url': row[8],
            'seller': row[9],
            'specifications': json.loads(row[10]) if row[10] else {},
            'scrape_date': row[11],
            'last_updated': row[12]
        }

    def close(self):
        """Close the database connection"""
        self.conn.close()