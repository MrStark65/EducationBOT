#!/usr/bin/env python3
"""Database backup and recovery system"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import gzip
import json

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

DATABASE_FILE = "officer_priya_multi.db"


class BackupManager:
    """Manage database backups and recovery"""
    
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.backup_dir = BACKUP_DIR
    
    def create_backup(self, compress: bool = True) -> Optional[str]:
        """
        Create database backup
        
        Args:
            compress: Whether to compress the backup
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Compress if requested
            if compress:
                compressed_path = backup_path.with_suffix('.db.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                backup_path.unlink()
                backup_path = compressed_path
            
            # Create metadata
            metadata = {
                'timestamp': timestamp,
                'size': backup_path.stat().st_size,
                'compressed': compress,
                'original_db': self.db_path
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def list_backups(self) -> List[dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*.db*"), reverse=True):
            if backup_file.suffix == '.json':
                continue
            
            metadata_file = backup_file.with_suffix('.json')
            metadata = {}
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                'compressed': backup_file.suffix == '.gz',
                **metadata
            })
        
        return backups
    
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            target_path: Target database path (default: original db_path)
            
        Returns:
            Success status
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            target = target_path or self.db_path
            
            # Create backup of current database before restoring
            if Path(target).exists():
                current_backup = f"{target}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(target, current_backup)
                print(f"📦 Current database backed up to: {current_backup}")
            
            # Decompress if needed
            if backup_file.suffix == '.gz':
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(target, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_file, target)
            
            print(f"✅ Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup file"""
        try:
            backup_file = Path(backup_path)
            metadata_file = backup_file.with_suffix('.json')
            
            if backup_file.exists():
                backup_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            print(f"✅ Backup deleted: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Keep only the most recent N backups
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        deleted = 0
        for backup in backups[keep_count:]:
            if self.delete_backup(backup['path']):
                deleted += 1
        
        print(f"🧹 Cleaned up {deleted} old backups")
        return deleted
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity"""
        try:
            backup_file = Path(backup_path)
            
            # Decompress to temp file if needed
            if backup_file.suffix == '.gz':
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    with gzip.open(backup_file, 'rb') as f_in:
                        shutil.copyfileobj(f_in, tmp)
                    temp_path = tmp.name
            else:
                temp_path = backup_path
            
            # Try to open as SQLite database
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            conn.close()
            
            # Clean up temp file
            if backup_file.suffix == '.gz':
                os.unlink(temp_path)
            
            if result == 'ok':
                print(f"✅ Backup verified: {backup_path}")
                return True
            else:
                print(f"❌ Backup corrupted: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def auto_backup(self, compress: bool = True, keep_count: int = 10) -> Optional[str]:
        """
        Create backup and cleanup old ones
        
        Args:
            compress: Whether to compress backup
            keep_count: Number of backups to keep
            
        Returns:
            Path to new backup or None
        """
        backup_path = self.create_backup(compress=compress)
        
        if backup_path:
            self.cleanup_old_backups(keep_count=keep_count)
        
        return backup_path


# Singleton instance
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """Get or create backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
