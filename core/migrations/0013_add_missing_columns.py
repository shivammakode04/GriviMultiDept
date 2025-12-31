# Generated migration to add missing columns

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_badge_department_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE core_user ADD COLUMN IF NOT EXISTS last_activity DATETIME DEFAULT CURRENT_TIMESTAMP",
            reverse_sql="",  # Don't drop, just mark as applied
        ),
    ]
