with open("database.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "def " in line and ("appointment" in line or "patient" in line or "doctor" in line):
        print(f"Line {idx+1}: {line.strip()}")
