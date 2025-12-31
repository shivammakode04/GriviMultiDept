import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
stmts = [
    "ALTER TABLE core_complaint MODIFY COLUMN title VARCHAR(200) NOT NULL DEFAULT 'General Issue'",
    "ALTER TABLE core_complaint MODIFY COLUMN category VARCHAR(50) NOT NULL DEFAULT 'Other'",
    "ALTER TABLE core_complaint MODIFY COLUMN is_escalated TINYINT NOT NULL DEFAULT 0",
    "ALTER TABLE core_complaint MODIFY COLUMN sla_breached TINYINT NOT NULL DEFAULT 0",
    "ALTER TABLE core_complaint MODIFY COLUMN is_public TINYINT NOT NULL DEFAULT 1",
    "ALTER TABLE core_complaint MODIFY COLUMN views_count INT NOT NULL DEFAULT 0",
    "ALTER TABLE core_complaint MODIFY COLUMN similar_complaints_count INT NOT NULL DEFAULT 0",
]

for stmt in stmts:
    try:
        cursor.execute(stmt)
        print(f"✅ {stmt.split()[0:5]}")
    except Exception as e:
        print(f"⚠️  {stmt[:50]}: {e}")

connection.commit()
print("\n✅ DB defaults updated!")
