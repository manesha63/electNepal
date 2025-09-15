#!/bin/bash

# Simple SQLite backup script for ElectNepal

BACKUP_DIR="$HOME/electNepal/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="$HOME/electNepal/db.sqlite3"
BACKUP_FILE="$BACKUP_DIR/electnepal_backup_$DATE.sqlite3"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup using SQLite's backup command (ensures consistency)
sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

# Compress the backup
gzip "$BACKUP_FILE"

echo "✅ Database backed up to: $BACKUP_FILE.gz"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "*.sqlite3.gz" -mtime +30 -delete

# Optional: Copy to cloud storage
# rclone copy "$BACKUP_FILE.gz" gdrive:electnepal-backups/