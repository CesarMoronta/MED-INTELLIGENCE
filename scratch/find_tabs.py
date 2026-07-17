with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'class="tab-panel' in line:
        print(f"L{i+1}: {line.strip()}")
