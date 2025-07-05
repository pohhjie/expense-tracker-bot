from datetime import datetime
import logging
import sqlite3
from typing import Any

# Get a logger instance specifically for this module.
# The __name__ variable will be 'string_utils' when this module is imported.
logger = logging.getLogger(__name__)

# TODO!
# Refactor this DatabaseManager into an Abstract Base Class (IDatabaseManager)
# and a concrete implementation (SQLiteDatabaseManager) for better
# interface definition and reusability across different database types.

class DatabaseManager:

  """
  Manages the SQLite database connection and provides methods
  for interacting with the expenses table.
  """

  def __init__(self, db_name: str):
    """
    Initializes the DatabaseManager, establishing a connection
    to the specified SQLite database.
    """
    self.db_name = db_name
    self.conn = None # Initialize connection to None
    self.cursor = None # Initialize cursor to None
    self._connect() # Establish connection upon initialization


  def _connect(self):
    """Establishes the database connection."""
    try:
      self.conn = sqlite3.connect(self.db_name)

      # Configure the connection to return rows as sqlite3.Row objects 
      # (which behave like dicts). This allows accessing columns by name
      # (e.g., row['column_name']) instead of by index (row[0]),
      # making the code more readable and robust to schema changes.
      self.conn.row_factory = sqlite3.Row

      self.cursor = self.conn.cursor()
      logger.info(f"Connected to database: {self.db_name}")
    except sqlite3.Error as e:
      logger.error(f"Error connecting to database: {e}")
      # You might want to raise the exception or handle it differently in a real app


  def close(self):
    """Closes the database connection."""
    if self.conn:
      self.conn.commit() # Ensure all pending transactions are saved
      self.conn.close()
      logger.info(f"Disconnected from database: {self.db_name}")

    self.conn = None
    self.cursor = None


  def init_db(self):
    """
    Initializes the database by creating the 'expenses' table
    if it does not already exist.
    """
    if (not self.conn):
        self._connect() # Reconnect if somehow disconnected

    try:
      self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          amount REAL NOT NULL,
          description TEXT,
          category TEXT,
          date TEXT NOT NULL -- Store dates as ISO8601 strings (YYYY-MM-DD HH:MM:SS)
        )
      ''')
      self.conn.commit()
      logger.info("Expenses table checked/created successfully.")

    except sqlite3.Error as e:
        logger.error(f"Error creating table: {e}")
        # Consider raising or handling this more robustly

    finally:
      # For init_db, it's common to ensure it's self-contained.
      # In a long-running app, you might not close here.
      # For simplicity, keeping it self-contained for now as per original func.
      # If called only once at startup, closing here is fine.
      pass # Keep connection open for subsequent operations



  def insert_expense(self, user_id: int, amount: float, description: str, category: str, date: str) -> int:
    """
    Inserts a new expense record into the database.
    Returns the ID of the newly inserted expense.
    """
    # Ensure connection is active before performing operation
    if not self.conn:
      self._connect()

    logger.info(f"Attempting to insert expense for user {user_id}...")
    try:
      # List column names in the INSERT statement
      self.cursor.execute(
        "INSERT INTO expenses (user_id, amount, description, category, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, description, category, date)
      )
      self.conn.commit()
      
      # Get the ID of the last inserted row using .lastrowid
      expense_id = self.cursor.lastrowid
      logger.info(f"Successfully inserted expense with ID: {expense_id}")
      return expense_id
    
    except sqlite3.Error as e:
      logger.error(f"Database error during insert for user {user_id}: {e}")
      self.conn.rollback() # Rollback changes if an error occurs
      raise # Re-raise the exception after logging and rollback
    
    except Exception as e:
      logger.error(f"An unexpected error occurred during insert for user {user_id}: {e}")
      self.conn.rollback() # Rollback on unexpected errors too
      raise # Re-raise the exception


  def get_expenses_by_user_and_date(self, user_id: int, date: str) -> list[Any]:
    # Ensure connection is active before performing operation
    if not self.conn:
      self._connect()

    self.cursor.execute(
        "SELECT * from expenses where user_id = ? AND strftime('%Y-%m', date) = ? ORDER BY date(date) DESC",
        (user_id, date)
    )
    return self.cursor.fetchall()

  def get_expenses_by_user(self, user_id: int, month):
    """
    Retrieves recent expenses for a given user.
    """
    print(f"Attempting to retrieve expenses for user {user_id}...")
    # Example:
    # self.cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit))
    # return self.cursor.fetchall()
    return [] # Placeholder
    