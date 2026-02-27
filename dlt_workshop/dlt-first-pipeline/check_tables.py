import duckdb
import time

time.sleep(1)

try:
    conn = duckdb.connect('open_library_pipeline.duckdb', read_only=True)
    
    print("\n=== Tables in open_library_data ===")
    tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='open_library_data' ORDER BY table_name").fetchall()
    
    if tables:
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM open_library_data.{table[0]}").fetchone()[0]
            print(f"  • {table[0]}: {count} rows")
    else:
        print("  No tables found")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
