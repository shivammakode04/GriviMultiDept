# Add all missing columns to notification table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_add_notification_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE core_notification ADD COLUMN complaint_id BIGINT NULL",
            reverse_sql="",
        ),
    ]
