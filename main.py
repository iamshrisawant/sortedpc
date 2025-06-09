from db import create_table, migrate_add_columns
from menu import manage_paths

if __name__ == "__main__":
    create_table()
    migrate_add_columns()
    watch_paths = manage_paths()
