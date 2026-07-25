with open("static/js/main.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "api/notifications" in line or "setInterval" in line or "polling" in line:
        print(f"Line {idx+1}: {line.strip()}")
