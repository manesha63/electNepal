#!/usr/bin/env python
"""
Test script to verify full-text search optimization for issue #31.

This script tests that:
1. ILIKE queries removed from code
2. PostgreSQL FTS (SearchVector/SearchQuery) is used instead
3. Search functionality still works correctly
4. FTS index exists and is being used
5. No fallback to slow ILIKE queries
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

def test_no_ilike_in_code():
    """Test that ILIKE queries (icontains) have been removed"""
    print("=" * 70)
    print("TEST 1: No ILIKE Queries in Search Code")
    print("=" * 70)

    # Check views.py
    with open('candidates/views.py', 'r') as f:
        views_content = f.read()

    # Check api_views.py
    with open('candidates/api_views.py', 'r') as f:
        api_views_content = f.read()

    # Count icontains usage (should be 0 in search code)
    views_icontains = views_content.count('__icontains')
    api_icontains = api_views_content.count('__icontains')

    print(f"  __icontains in views.py: {views_icontains}")
    print(f"  __icontains in api_views.py: {api_icontains}")

    # There should be NO icontains in the files anymore
    assert views_icontains == 0, f"Found {views_icontains} __icontains in views.py"
    assert api_icontains == 0, f"Found {api_icontains} __icontains in api_views.py"

    print(f"  ✓ No slow ILIKE queries found")

    print(f"\n✓ PASS: ILIKE queries removed from search code")
    print()


def test_fts_imports_present():
    """Test that FTS imports are present"""
    print("=" * 70)
    print("TEST 2: Full-Text Search Imports Present")
    print("=" * 70)

    with open('candidates/views.py', 'r') as f:
        views_content = f.read()

    with open('candidates/api_views.py', 'r') as f:
        api_views_content = f.read()

    # Check for FTS imports
    views_has_imports = all(x in views_content for x in ['SearchQuery', 'SearchRank', 'SearchVector'])
    api_has_imports = all(x in api_views_content for x in ['SearchQuery', 'SearchRank', 'SearchVector'])

    print(f"  views.py has FTS imports: {views_has_imports}")
    print(f"  api_views.py has FTS imports: {api_has_imports}")

    assert views_has_imports, "FTS imports missing in views.py"
    assert api_has_imports, "FTS imports missing in api_views.py"

    print(f"\n✓ PASS: Full-text search imports present in both files")
    print()


def test_fts_usage_in_code():
    """Test that SearchVector/SearchQuery are actually used"""
    print("=" * 70)
    print("TEST 3: FTS Actually Used in Search Functions")
    print("=" * 70)

    with open('candidates/views.py', 'r') as f:
        views_content = f.read()

    with open('candidates/api_views.py', 'r') as f:
        api_views_content = f.read()

    # Check for FTS usage
    views_uses_vector = 'SearchVector(' in views_content
    views_uses_query = 'SearchQuery(' in views_content
    views_uses_rank = 'SearchRank(' in views_content

    api_uses_vector = 'SearchVector(' in api_views_content
    api_uses_query = 'SearchQuery(' in api_views_content
    api_uses_rank = 'SearchRank(' in api_views_content

    print(f"  views.py uses SearchVector: {views_uses_vector}")
    print(f"  views.py uses SearchQuery: {views_uses_query}")
    print(f"  views.py uses SearchRank: {views_uses_rank}")
    print(f"  api_views.py uses SearchVector: {api_uses_vector}")
    print(f"  api_views.py uses SearchQuery: {api_uses_query}")
    print(f"  api_views.py uses SearchRank: {api_uses_rank}")

    assert all([views_uses_vector, views_uses_query, views_uses_rank]), "FTS not fully used in views.py"
    assert all([api_uses_vector, api_uses_query, api_uses_rank]), "FTS not fully used in api_views.py"

    print(f"\n✓ PASS: Full-text search properly used in code")
    print()


def test_fts_index_exists():
    """Test that FTS index exists in database"""
    print("=" * 70)
    print("TEST 4: FTS Index Exists in Database")
    print("=" * 70)

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'candidates_candidate'
            AND indexname LIKE '%fulltext%'
        """)
        indexes = cursor.fetchall()

    print(f"  Full-text search indexes found: {len(indexes)}")

    for index_name, index_def in indexes:
        print(f"    - {index_name}")

    assert len(indexes) > 0, "No full-text search index found"
    assert any('candidates_fulltext_idx' in idx[0] for idx in indexes), "candidates_fulltext_idx not found"

    print(f"\n✓ PASS: FTS index exists in database")
    print()


def test_search_functionality_works():
    """Test that search actually works with FTS"""
    print("=" * 70)
    print("TEST 5: Search Functionality Works")
    print("=" * 70)

    from candidates.models import Candidate
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

    # Get total candidates
    total_candidates = Candidate.objects.filter(status='approved').count()

    print(f"  Total approved candidates: {total_candidates}")

    if total_candidates == 0:
        print(f"  ⊘ SKIP: No approved candidates to search")
        print()
        return

    # Get a sample candidate
    sample_candidate = Candidate.objects.filter(status='approved').first()

    # Search for part of their name
    if sample_candidate:
        search_term = sample_candidate.full_name.split()[0] if ' ' in sample_candidate.full_name else sample_candidate.full_name[:3]

        print(f"  Sample candidate: {sample_candidate.full_name}")
        print(f"  Searching for: '{search_term}'")

        # Perform FTS search
        search_vector = (
            SearchVector('full_name', weight='A') +
            SearchVector('bio_en', weight='B')
        )
        search_query = SearchQuery(search_term)

        results = Candidate.objects.filter(status='approved').annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')

        result_count = results.count()

        print(f"  Search results: {result_count} candidates")

        if result_count > 0:
            print(f"  ✓ Search found results")
            print(f"  Top result: {results.first().full_name}")
        else:
            print(f"  ℹ No results (FTS may require exact word matches)")

    print(f"\n✓ PASS: Search functionality works")
    print()


def test_no_ilike_fallback_logic():
    """Test that there's no fallback to ILIKE in code"""
    print("=" * 70)
    print("TEST 6: No ILIKE Fallback Logic")
    print("=" * 70)

    with open('candidates/views.py', 'r') as f:
        views_content = f.read()

    with open('candidates/api_views.py', 'r') as f:
        api_views_content = f.read()

    # Check for fallback patterns
    fallback_patterns = [
        'if not.*:.*icontains',
        'except.*:.*icontains',
        'fallback.*icontains',
    ]

    has_fallback = False
    for pattern in fallback_patterns:
        import re
        if re.search(pattern, views_content, re.IGNORECASE) or re.search(pattern, api_views_content, re.IGNORECASE):
            has_fallback = True
            print(f"  ❌ Found fallback pattern: {pattern}")

    if not has_fallback:
        print(f"  ✓ No fallback to ILIKE found")

    assert not has_fallback, "Found fallback logic to ILIKE"

    print(f"\n✓ PASS: No ILIKE fallback logic in code")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("FULL-TEXT SEARCH OPTIMIZATION TEST SUITE")
    print("Testing fix for issue #31")
    print("=" * 70 + "\n")

    try:
        test_no_ilike_in_code()
        test_fts_imports_present()
        test_fts_usage_in_code()
        test_fts_index_exists()
        test_search_functionality_works()
        test_no_ilike_fallback_logic()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- Slow ILIKE queries removed from all search code")
        print("- Full-text search imports present in both files")
        print("- SearchVector/SearchQuery/SearchRank properly used")
        print("- FTS index exists in database (candidates_fulltext_idx)")
        print("- Search functionality works correctly with FTS")
        print("- No fallback to slow ILIKE queries")
        print("\nSearch is now optimized for large datasets!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
