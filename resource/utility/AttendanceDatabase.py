import sqlite3
import numpy as np


class AttendanceDatabase:
    """
    A class to manage attendance records in an SQLite database.
    """

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Create the attendance table if it does not exist."""
        self.cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS attendance (
                    "group" TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL
                )
            """
        )
        self.conn.commit()

    def add_data(self, group, name, date, time):
        """Insert a new attendance record."""
        try:
            self.cursor.execute(
                f'INSERT INTO attendance ("group", name, date, time) VALUES (?, ?, ?, ?)',
                (group, name, date, time),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def read_data(self, group, start_date, start_time, end_date, end_time):
        """
        Retrieve attendance records between start and end date/time.
        Returns a numpy array of results.
        """
        try:
            self.cursor.execute(
                f"""
                SELECT name, date, time FROM attendance
                WHERE "group" = ?
                  AND (
                    (date > ? OR (date = ? AND time >= ?))
                    AND (date < ? OR (date = ? AND time <= ?))
                  )
                LIMIT 1000
                """,
                (group, start_date, start_date, start_time, end_date, end_date, end_time),
            )
            return np.array(self.cursor.fetchall())
        except sqlite3.Error as e:
            print(f"Error reading data: {e}")
            return np.array([])

    def read_group(self):
        """Retrieve all unique groups from the attendance table."""
        try:
            self.cursor.execute('SELECT DISTINCT "group" FROM attendance')
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error reading groups: {e}")
            return []

    def close(self):
        """Close the database connection."""
        self.conn.close()
