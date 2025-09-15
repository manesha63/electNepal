# Generated manually for adding constraints

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='candidate',
            constraint=models.UniqueConstraint(
                fields=['user'],
                name='unique_user_candidate'
            ),
        ),
        migrations.AddConstraint(
            model_name='candidate',
            constraint=models.UniqueConstraint(
                fields=['province', 'district', 'municipality', 'ward_number', 'position_level'],
                condition=models.Q(ward_number__isnull=False),
                name='unique_ward_candidate'
            ),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='verification_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Verification'),
                    ('verified', 'Verified'),
                    ('rejected', 'Verification Rejected')
                ],
                db_index=True,
                default='pending',
                max_length=20
            ),
        ),
    ]