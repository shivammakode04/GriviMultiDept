# Add missing notification_type column

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_add_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE core_notification ADD COLUMN notification_type VARCHAR(50) DEFAULT 'complaint_filed'",
            reverse_sql="",
        ),
    ]
