import os
import pytest
from mydb import MyDB
from unittest.mock import call

todo = pytest.mark.skip(reason='todo: pending spec')

def describe_MyDB():

    @pytest.fixture(autouse=True, scope="session")
    def verify_filesystem_is_not_touched():
        yield
        assert not os.path.isfile("mydatabase.db")