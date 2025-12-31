# Add missing title and other columns to notification

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_add_notification_type'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE core_notification ADD COLUMN title VARCHAR(255) DEFAULT 'Notification'",
            reverse_sql="",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE core_notification ADD COLUMN is_sent BOOLEAN DEFAULT 1",
            reverse_sql="",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE core_notification ADD COLUMN read_at DATETIME NULL",
            reverse_sql="",
        ),
    ]
