with open("database.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "def create_notification" in line:
        start = idx
        end = min(len(lines), idx+20)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].rstrip()}")
        break
