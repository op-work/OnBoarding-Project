import sys
try:
    import sqlite3
    import _sqlite3
except (ImportError, ModuleNotFoundError):
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
