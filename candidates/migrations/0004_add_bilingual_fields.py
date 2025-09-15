# Generated manually for bilingual support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0003_remove_candidate_unique_user_candidate_and_more'),
    ]

    operations = [
        # Add bilingual fields to CandidatePost
        migrations.RenameField(
            model_name='candidatepost',
            old_name='title',
            new_name='title_en',
        ),
        migrations.RenameField(
            model_name='candidatepost',
            old_name='content',
            new_name='content_en',
        ),
        migrations.AddField(
            model_name='candidatepost',
            name='title_ne',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='candidatepost',
            name='content_ne',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='candidatepost',
            name='is_mt_title_ne',
            field=models.BooleanField(default=False, help_text='True if title_ne is machine translated'),
        ),
        migrations.AddField(
            model_name='candidatepost',
            name='is_mt_content_ne',
            field=models.BooleanField(default=False, help_text='True if content_ne is machine translated'),
        ),

        # Add bilingual fields to CandidateEvent
        migrations.RenameField(
            model_name='candidateevent',
            old_name='title',
            new_name='title_en',
        ),
        migrations.RenameField(
            model_name='candidateevent',
            old_name='description',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='candidateevent',
            old_name='location',
            new_name='location_en',
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='title_ne',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='description_ne',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='location_ne',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='is_mt_title_ne',
            field=models.BooleanField(default=False, help_text='True if title_ne is machine translated'),
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='is_mt_description_ne',
            field=models.BooleanField(default=False, help_text='True if description_ne is machine translated'),
        ),
        migrations.AddField(
            model_name='candidateevent',
            name='is_mt_location_ne',
            field=models.BooleanField(default=False, help_text='True if location_ne is machine translated'),
        ),
    ]