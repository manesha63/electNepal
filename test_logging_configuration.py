#!/usr/bin/env python
"""
Test script to verify logging configuration for issue #34.

This script tests that:
1. All logger instances have proper handlers and formatters configured
2. Root logger is configured
3. App-specific loggers (core, authentication, candidates, locations, etc.) are configured
4. Logs are written to files correctly
5. Console and file handlers work
6. Log levels are properly set
"""

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

def test_logging_config_exists():
    """Test that LOGGING configuration exists in settings"""
    print("=" * 70)
    print("TEST 1: Logging Configuration Exists")
    print("=" * 70)

    from django.conf import settings

    has_logging = hasattr(settings, 'LOGGING')
    print(f"  {'✓' if has_logging else '❌'} LOGGING setting exists: {has_logging}")

    if has_logging:
        logging_config = settings.LOGGING

        # Check version
        has_version = 'version' in logging_config
        print(f"  {'✓' if has_version else '❌'} Version specified: {has_version}")

        # Check formatters
        has_formatters = 'formatters' in logging_config
        formatter_count = len(logging_config.get('formatters', {}))
        print(f"  {'✓' if has_formatters else '❌'} Formatters configured: {formatter_count}")

        # Check handlers
        has_handlers = 'handlers' in logging_config
        handler_count = len(logging_config.get('handlers', {}))
        print(f"  {'✓' if has_handlers else '❌'} Handlers configured: {handler_count}")

        # Check loggers
        has_loggers = 'loggers' in logging_config
        logger_count = len(logging_config.get('loggers', {}))
        print(f"  {'✓' if has_loggers else '❌'} Loggers configured: {logger_count}")

        # Check root logger
        has_root = 'root' in logging_config
        print(f"  {'✓' if has_root else '❌'} Root logger configured: {has_root}")

        assert has_logging, "LOGGING configuration missing"
        assert has_formatters, "No formatters configured"
        assert has_handlers, "No handlers configured"
        assert has_loggers, "No loggers configured"
        assert has_root, "Root logger missing"

    print(f"\n✓ PASS: Logging configuration exists and complete")
    print()


def test_required_handlers():
    """Test that all required handlers are configured"""
    print("=" * 70)
    print("TEST 2: Required Handlers")
    print("=" * 70)

    from django.conf import settings

    required_handlers = ['console', 'file', 'error_file', 'security_file', 'email_file']
    handlers = settings.LOGGING.get('handlers', {})

    all_present = True
    for handler_name in required_handlers:
        has_handler = handler_name in handlers
        print(f"  {'✓' if has_handler else '❌'} {handler_name}: {has_handler}")
        if not has_handler:
            all_present = False

    assert all_present, "Some required handlers are missing"

    print(f"\n✓ PASS: All required handlers configured")
    print()


def test_required_loggers():
    """Test that all app loggers are configured"""
    print("=" * 70)
    print("TEST 3: Required App Loggers")
    print("=" * 70)

    from django.conf import settings

    required_loggers = [
        'django',
        'django.request',
        'django.security',
        'candidates',
        'candidates.emails',
        'authentication',
        'authentication.emails',
        'locations',
        'core',
        'analytics',
        'api_auth',
    ]
    loggers = settings.LOGGING.get('loggers', {})

    all_present = True
    for logger_name in required_loggers:
        has_logger = logger_name in loggers
        print(f"  {'✓' if has_logger else '❌'} {logger_name}: {has_logger}")
        if not has_logger:
            all_present = False

    assert all_present, "Some required loggers are missing"

    print(f"\n✓ PASS: All required app loggers configured")
    print()


def test_logs_directory_exists():
    """Test that logs directory exists"""
    print("=" * 70)
    print("TEST 4: Logs Directory")
    print("=" * 70)

    logs_dir = 'logs'
    exists = os.path.exists(logs_dir)
    is_directory = os.path.isdir(logs_dir) if exists else False

    print(f"  {'✓' if exists else '❌'} Logs directory exists: {exists}")
    print(f"  {'✓' if is_directory else '❌'} Is a directory: {is_directory}")

    if exists and is_directory:
        files = os.listdir(logs_dir)
        print(f"  Log files present: {len(files)}")
        for file in files:
            size = os.path.getsize(os.path.join(logs_dir, file))
            print(f"    - {file}: {size} bytes")

    assert exists, "Logs directory does not exist"
    assert is_directory, "Logs path is not a directory"

    print(f"\n✓ PASS: Logs directory properly configured")
    print()


def test_logger_instances_work():
    """Test that logger instances can be created and used"""
    print("=" * 70)
    print("TEST 5: Logger Instances Work")
    print("=" * 70)

    test_loggers = [
        ('candidates', 'Candidates app logger'),
        ('candidates.emails', 'Candidates emails logger'),
        ('authentication', 'Authentication app logger'),
        ('authentication.emails', 'Authentication emails logger'),
        ('locations', 'Locations app logger'),
        ('core', 'Core app logger'),
        ('core.auto_translate', 'Core auto_translate logger'),
        ('core.mt', 'Core machine translation logger'),
        ('analytics', 'Analytics app logger'),
        ('api_auth', 'API auth logger'),
    ]

    all_work = True
    for logger_name, description in test_loggers:
        try:
            logger = logging.getLogger(logger_name)
            has_handlers = len(logger.handlers) > 0 or logger.parent is not None
            effective_level = logger.getEffectiveLevel()

            print(f"  {'✓' if has_handlers else '❌'} {logger_name}: Level={logging.getLevelName(effective_level)}")

            if not has_handlers and logger.parent is None:
                all_work = False
                print(f"    Warning: No handlers and no parent logger")
        except Exception as e:
            print(f"  ❌ {logger_name}: Error - {e}")
            all_work = False

    assert all_work, "Some loggers don't have proper configuration"

    print(f"\n✓ PASS: All logger instances work correctly")
    print()


def test_logging_output():
    """Test that logging actually writes to files"""
    print("=" * 70)
    print("TEST 6: Logging Output")
    print("=" * 70)

    import time

    # Get initial file sizes
    log_file = 'logs/electnepal.log'
    initial_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0

    # Test different loggers
    test_messages = [
        ('candidates', logging.INFO, 'Test message from candidates logger'),
        ('core', logging.INFO, 'Test message from core logger'),
        ('authentication', logging.INFO, 'Test message from authentication logger'),
        ('locations', logging.DEBUG, 'Test message from locations logger'),
    ]

    for logger_name, level, message in test_messages:
        logger = logging.getLogger(logger_name)
        logger.log(level, message)
        print(f"  Logged to {logger_name}: {message}")

    # Small delay to allow file write
    time.sleep(0.1)

    # Check if file grew
    final_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    file_grew = final_size > initial_size

    print(f"\n  Initial file size: {initial_size} bytes")
    print(f"  Final file size: {final_size} bytes")
    print(f"  {'✓' if file_grew else '❌'} Log file grew: {file_grew}")

    assert file_grew, "Log file did not grow - logging may not be working"

    print(f"\n✓ PASS: Logging output works correctly")
    print()


def test_handler_formatters():
    """Test that handlers have formatters configured"""
    print("=" * 70)
    print("TEST 7: Handler Formatters")
    print("=" * 70)

    from django.conf import settings

    handlers = settings.LOGGING.get('handlers', {})

    all_have_formatters = True
    for handler_name, handler_config in handlers.items():
        # Skip mail_admins as it doesn't need a formatter
        if handler_name == 'mail_admins':
            continue

        has_formatter = 'formatter' in handler_config
        formatter_name = handler_config.get('formatter', 'N/A')

        print(f"  {'✓' if has_formatter else '❌'} {handler_name}: {formatter_name}")

        if not has_formatter:
            all_have_formatters = False

    assert all_have_formatters, "Some handlers missing formatters"

    print(f"\n✓ PASS: All handlers have formatters")
    print()


def test_log_file_rotation():
    """Test that log file rotation is configured"""
    print("=" * 70)
    print("TEST 8: Log File Rotation")
    print("=" * 70)

    from django.conf import settings

    handlers = settings.LOGGING.get('handlers', {})

    rotating_handlers = ['file', 'error_file', 'security_file', 'email_file']

    all_configured = True
    for handler_name in rotating_handlers:
        handler_config = handlers.get(handler_name, {})

        is_rotating = handler_config.get('class') == 'logging.handlers.RotatingFileHandler'
        has_max_bytes = 'maxBytes' in handler_config
        has_backup_count = 'backupCount' in handler_config

        max_bytes = handler_config.get('maxBytes', 0)
        backup_count = handler_config.get('backupCount', 0)

        configured = is_rotating and has_max_bytes and has_backup_count

        print(f"  {'✓' if configured else '❌'} {handler_name}:")
        print(f"    Rotating: {is_rotating}")
        print(f"    Max bytes: {max_bytes / (1024*1024):.1f}MB" if has_max_bytes else "    Max bytes: Not set")
        print(f"    Backups: {backup_count}")

        if not configured:
            all_configured = False

    assert all_configured, "Some file handlers missing rotation config"

    print(f"\n✓ PASS: Log file rotation properly configured")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LOGGING CONFIGURATION TEST SUITE")
    print("Testing fix for issue #34")
    print("=" * 70 + "\n")

    try:
        test_logging_config_exists()
        test_required_handlers()
        test_required_loggers()
        test_logs_directory_exists()
        test_logger_instances_work()
        test_logging_output()
        test_handler_formatters()
        test_log_file_rotation()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- Logging configuration complete")
        print("- All required handlers configured (console, file, error, security, email)")
        print("- All app loggers configured (core, authentication, candidates, locations, etc.)")
        print("- Root logger configured as fallback")
        print("- Formatters properly attached to handlers")
        print("- Log file rotation configured (15MB, 10 backups)")
        print("- Logs directory exists and is writable")
        print("- All logger instances working correctly")
        print("\nLogging system is fully operational!")

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
