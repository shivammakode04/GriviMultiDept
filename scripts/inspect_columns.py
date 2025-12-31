from django.conf import settings
import django
django.setup()
from django.db import connection

db = settings.DATABASES['default']['NAME']
tbl = 'core_complaint'
cur = connection.cursor()
cur.execute("SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", [db, tbl])
rows = cur.fetchall()
print('TABLE:', tbl, 'DB:', db)
for name, data_type, column_type, is_nullable, col_default in rows:
    if is_nullable == 'NO' and col_default is None:
        print(name, data_type, column_type, is_nullable, col_default)
