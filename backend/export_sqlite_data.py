#!/usr/bin/env python3
"""
Export SQLite data to SQL file that can be imported to PostgreSQL
"""
import sqlite3
import json

def export_sqlite_to_sql():
    """Export SQLite database to SQL INSERT statements"""
    
    db_path = "officer_priya_multi.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    output_file = "database_export.sql"
    
    with open(output_file, 'w') as f:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Exporting {len(tables)} tables...")
        
        for table in tables:
            print(f"   Exporting {table}...")
            
            # Get all data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                continue
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Write INSERT statements
            for row in rows:
                values = []
                for val in row:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, str):
                        # Escape single quotes
                        escaped = val.replace("'", "''")
                        values.append(f"'{escaped}'")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        values.append(f"'{val}'")
                
                columns_str = ', '.join(columns)
                values_str = ', '.join(values)
                f.write(f"INSERT INTO {table} ({columns_str}) VALUES ({values_str}) ON CONFLICT DO NOTHING;\n")
    
    conn.close()
    
    print(f"\n✅ Data exported to {output_file}")
    print(f"📊 Summary:")
    
    # Show summary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   {table}: {count} rows")
    conn.close()

if __name__ == "__main__":
    export_sqlite_to_sql()
