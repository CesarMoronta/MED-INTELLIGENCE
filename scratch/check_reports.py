import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/index.html', 'r', encoding='utf-8') as f:
    html_lines = f.readlines()

for i, line in enumerate(html_lines):
    if 'report' in line.lower():
        print(f"HTML L{i+1}: {line.strip()}")

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js_lines = f.readlines()

for i, line in enumerate(js_lines):
    if 'report' in line.lower():
        print(f"JS L{i+1}: {line.strip()}")
