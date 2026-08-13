import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from routes.pdf_routes import generate_database_sql_dump

try:
    dump = generate_database_sql_dump()
    print("Dump total length (chars):", len(dump))
    print("Dump line count:", len(dump.splitlines()))
    
    # Check if INSERT INTO is in dump
    insert_count = dump.count("INSERT INTO")
    print("Number of INSERT INTO statements:", insert_count)

    # Print first 20 lines and last 30 lines
    lines = dump.splitlines()
    print("\n--- FIRST 20 LINES ---")
    print("\n".join(lines[:20]))
    print("\n--- LAST 30 LINES ---")
    print("\n".join(lines[-30:]))

except Exception as e:
    import traceback
    print("ERROR DURING DUMP:")
    traceback.print_exc()
