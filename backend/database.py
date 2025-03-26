import sqlite3


class SupplyChainDB:
    def __init__(self, db_path="supply_chain.db"):
        # Initialize the database connection
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()
        self._populate_initial_data()

    def _create_table(self):
        try:
            # Create the supply_chain table if it doesn't exist
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS supply_chain (
                    product_name TEXT PRIMARY KEY,
                    stock_quantity INTEGER,
                    order_id INTEGER,
                    order_status TEXT,
                    current_price REAL,
                    old_price REAL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def _populate_initial_data(self):
        try:
            # Check if the table is empty
            cursor = self.conn.execute("SELECT COUNT(*) FROM supply_chain")
            if cursor.fetchone()[0] == 0:
                sample_data = [
                    ("ProductX", 50, 123, "Shipped", 10.99, 9.99),
                    ("ProductY", 0, 456, "Pending", 5.99, 5.99),
                    ("ProductZ", 100, 789, "Pending", 15.50, 14.99),
                ]
                self.conn.executemany("""
                    INSERT INTO supply_chain (product_name, stock_quantity, order_id, order_status, current_price, old_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, sample_data)
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error populating initial data: {e}")

    def check_stock(self, product: str) -> str:
        try:
            print(f"Querying stock for product: {product}")  # Debug log
            result = self.conn.execute("SELECT stock_quantity FROM supply_chain WHERE LOWER(product_name) = ?", (product.lower(),)).fetchone()
            if result:
                qty = result[0]
                print(f"Stock quantity found: {qty}")  # Debug log
                return f"{product} has {qty} units in stock." if qty > 0 else f"{product} is out of stock."
            print(f"No data found for product: {product}")  # Debug log
            return f"No data available for {product}."
        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Debug log
            return f"Database error: {e}"

    def check_order_status(self, order_id: int) -> str:
        try:
            result = self.conn.execute("SELECT order_status FROM supply_chain WHERE order_id = ?", (order_id,)).fetchone()
            if result:
                return result[0]
            return f"Order #{order_id} not found."
        except sqlite3.Error as e:
            return f"Database error: {e}"

    def check_price(self, product: str) -> str:
        try:
            result = self.conn.execute("SELECT current_price, old_price FROM supply_chain WHERE LOWER(product_name) = ?", (product.lower(),)).fetchone()
            if result:
                current, old = result[0], result[1]
                if current != old:
                    return f"The price of {product} has changed from ${old} to ${current}."
                return f"The price of {product} is ${current} (no recent changes)."
            return f"No pricing data for {product}."
        except sqlite3.Error as e:
            return f"Database error: {e}"

    def close(self):
        """Explicitly close the database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Destructor to ensure the connection is closed."""
        self.close()