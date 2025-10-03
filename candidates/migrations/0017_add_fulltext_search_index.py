# Generated migration to add full-text search index
from django.db import migrations
from django.contrib.postgres.operations import BtreeGinExtension
from django.contrib.postgres.indexes import GinIndex


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0016_candidate_office_alter_candidate_position_level'),
    ]

    operations = [
        # Install the btree_gin extension if not already installed
        BtreeGinExtension(),

        # Add GIN index for full-text search on text fields
        # This significantly improves search performance
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS candidates_fulltext_idx
            ON candidates_candidate
            USING GIN ((
                to_tsvector('english', COALESCE(full_name, '')) ||
                to_tsvector('english', COALESCE(bio_en, '')) ||
                to_tsvector('english', COALESCE(bio_ne, '')) ||
                to_tsvector('english', COALESCE(education_en, '')) ||
                to_tsvector('english', COALESCE(education_ne, '')) ||
                to_tsvector('english', COALESCE(experience_en, '')) ||
                to_tsvector('english', COALESCE(experience_ne, '')) ||
                to_tsvector('english', COALESCE(manifesto_en, '')) ||
                to_tsvector('english', COALESCE(manifesto_ne, ''))
            ));
            """,
            reverse_sql="DROP INDEX IF EXISTS candidates_fulltext_idx;",
        ),
    ]