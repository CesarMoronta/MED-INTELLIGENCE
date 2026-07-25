with open("static/js/main.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
for idx, line in enumerate(lines):
    if "function loadWaitingRoom" in line:
        found = True
        start = idx
        end = min(len(lines), idx+80)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].rstrip()}")
        break

if not found:
    print("Function loadWaitingRoom not found with exact signature")
