import pytest
import tempfile
import os

from homescraper.datatypes import Apartment
from homescraper.db import ApartmentDb

def test_db_create():
    tmp_path = tempfile.mktemp()

    assert not os.path.exists(tmp_path)
    ApartmentDb(tmp_path)
    assert os.path.exists(tmp_path)

    os.unlink(tmp_path)

def test_db_in_memory():
    ApartmentDb(':memory:')

def test_insert():
    apt = Apartment(url='fake_url')
    apt2 = Apartment(url='fake_url2')

    db = ApartmentDb(':memory:')
    assert db.add_apartment(apt)
    assert not db.add_apartment(apt)
    assert db.add_apartment(apt2)