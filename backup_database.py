#!/usr/bin/env python
"""
Database Backup Script for RollCall
Run this script regularly to backup your database
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rollcall_project.settings')
import django
django.setup()

from django.core.management import call_command
from django.conf import settings

def create_backup():
    """Create a database backup"""
    # Create backups directory if it doesn't exist
    backup_dir = project_dir / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'db_backup_{timestamp}.json'
    
    print(f"Creating backup: {backup_file}")
    
    # Use Django's dumpdata command to backup database
    with open(backup_file, 'w') as f:
        call_command('dumpdata', 
                    '--natural-foreign', 
                    '--natural-primary',
                    '--indent', '2',
                    exclude=['contenttypes', 'auth.permission'],
                    stdout=f)
    
    print(f"✅ Backup created successfully: {backup_file}")
    print(f"Backup size: {backup_file.stat().st_size / 1024:.2f} KB")
    
    # Clean old backups (keep last 30 days)
    clean_old_backups(backup_dir, days=30)
    
    return backup_file

def clean_old_backups(backup_dir, days=30):
    """Remove backups older than specified days"""
    import time
    cutoff = time.time() - (days * 86400)
    
    cleaned = 0
    for backup_file in backup_dir.glob('db_backup_*.json'):
        if backup_file.stat().st_mtime < cutoff:
            backup_file.unlink()
            cleaned += 1
    
    if cleaned > 0:
        print(f"🗑️  Cleaned {cleaned} old backup(s)")

def restore_backup(backup_file):
    """Restore database from backup file"""
    if not Path(backup_file).exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"Restoring from backup: {backup_file}")
    
    # Confirm restoration
    confirm = input("⚠️  This will overwrite current data. Are you sure? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Restoration cancelled.")
        return False
    
    # Load data from backup
    call_command('loaddata', backup_file)
    
    print("✅ Backup restored successfully")
    return True

def list_backups():
    """List all available backups"""
    backup_dir = project_dir / 'backups'
    
    if not backup_dir.exists():
        print("No backups directory found.")
        return
    
    backups = sorted(backup_dir.glob('db_backup_*.json'), reverse=True)
    
    if not backups:
        print("No backups found.")
        return
    
    print("\n📦 Available Backups:")
    print("-" * 60)
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / 1024
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{i}. {backup.name}")
        print(f"   Size: {size:.2f} KB | Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='RollCall Database Backup Tool')
    parser.add_argument('action', choices=['backup', 'restore', 'list'],
                       help='Action to perform')
    parser.add_argument('--file', help='Backup file path (for restore)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        create_backup()
    elif args.action == 'list':
        list_backups()
    elif args.action == 'restore':
        if not args.file:
            print("Error: --file argument required for restore")
            sys.exit(1)
        restore_backup(args.file)
