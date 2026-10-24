import unittest
from engine.database import Database

class DatabaseTestcase(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.init_database()

        self.addCleanup(self.clean_database)

    def clean_database(self):
        try:
            self.db.conn.rollback()
        except:
            pass
        self.db.cursor.execute("""
            TRUNCATE TABLE items, injuries, talents, characters                                             
            RESTART IDENTITY CASCADE;   
        """)
        self.db.conn.commit()