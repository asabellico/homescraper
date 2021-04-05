import sqlalchemy
import dataclasses_sql

from homescraper.datatypes import Apartment

class ApartmentDb:
    def __init__(self, db_path):
        self.engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        self.metadata = sqlalchemy.MetaData(self.engine)
        self.metadata.reflect()

    def add_apartment(self, apartment):
        return dataclasses_sql.insert(self.metadata, apartment, check_exists=True)