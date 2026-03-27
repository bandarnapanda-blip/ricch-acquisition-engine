with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\briefing.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("shadow_ready = db.get_count(\"leads\", {\"status\": \"in.(Demo Ready,Site Generated)\"})", 
                    "shadow_ready = db.get_count(\"leads\", {\"status\": \"in.(Demo Ready,Site Generated,Shadow Site Ready)\"})")

with open("c:\\Users\\razer\\.gemini\\antigravity\\playground\\static-armstrong\\briefing.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patched briefing.py to include Shadow Site Ready.")
