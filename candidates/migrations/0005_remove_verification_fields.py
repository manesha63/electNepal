# Generated manually to remove verification fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0003_remove_candidate_unique_user_candidate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='verification_status',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='verification_document',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='verification_notes',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='verified_at',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='verified_by',
        ),
    ]