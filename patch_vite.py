import os

pkg_path = "c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\new_dashboard_temp\\package.json"
with open(pkg_path, "r", encoding="utf-8") as f:
    pkg = f.read()

pkg = pkg.replace('"dev": "vite --port=3000 --host=0.0.0.0"', '"dev": "vite --port=3001 --host=0.0.0.0"')

with open(pkg_path, "w", encoding="utf-8") as f:
    f.write(pkg)

print("Updated package.json to port 3001")
