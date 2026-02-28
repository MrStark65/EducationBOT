"""Run all database migrations"""

import sqlite3
import os
from pathlib import Path

def run_migrations(db_path="officer_priya_multi.db"):
    """Run all migrations in order"""
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print("No migrations directory found")
        return
    
    # Get all migration files
    migration_files = sorted([f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"])
    
    print(f"Found {len(migration_files)} migration files")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    for migration_file in migration_files:
        print(f"\nRunning migration: {migration_file.name}")
        
        try:
            # Import and run the migration
            import importlib.util
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            
            if hasattr(migration, 'upgrade'):
                migration.upgrade(conn)
                print(f"✅ {migration_file.name} completed")
            else:
                print(f"⚠️  {migration_file.name} has no upgrade function")
                
        except Exception as e:
            print(f"❌ {migration_file.name} failed: {e}")
            # Continue with other migrations
    
    conn.close()
    print("\n✅ All migrations completed")

if __name__ == "__main__":
    run_migrations()
