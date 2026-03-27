filepath = "c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\new_dashboard_temp\\src\\App.tsx"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("MOCK_LEADS", "leads")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Replaced MOCK_LEADS with leads in App.tsx.")
