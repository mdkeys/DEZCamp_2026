import duckdb

conn = duckdb.connect('open_library_pipeline.duckdb', read_only=True)

# Query for Spanish books
result = conn.execute("""
    SELECT 
        value as language,
        COUNT(DISTINCT books__dlt_id) as num_books
    FROM open_library_data.books__language
    WHERE value LIKE '%es%' OR value LIKE '%Spanish%'
    GROUP BY value
    ORDER BY num_books DESC
""").fetchall()

print("Spanish books found:")
if result:
    for lang, count in result:
        print(f"  {lang}: {count} books")
else:
    print("  No Spanish books found")

# Also show top languages
print("\nTop 15 languages in dataset:")
all_langs = conn.execute("""
    SELECT 
        value as language,
        COUNT(DISTINCT books__dlt_id) as num_books
    FROM open_library_data.books__language
    GROUP BY value
    ORDER BY num_books DESC
    LIMIT 15
""").fetchall()

for lang, count in all_langs:
    print(f"  {lang}: {count} books")

conn.close()
