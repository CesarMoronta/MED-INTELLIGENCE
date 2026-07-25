with open("database.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "list_users" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # Print lines around it
        start = max(0, idx-5)
        end = min(len(lines), idx+20)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].rstrip()}")
        break
