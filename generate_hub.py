import os
import glob
from datetime import datetime

DEMO_DIR = 'demo'
OUTPUT_FILE = 'index.html'

def generate_hub():
    print("  [DALLAS STRATEGY] REBUILDING PERMANENT FLEET HUB...")
    
    # Get all HTML files in demo directory
    files = glob.glob(os.path.join(DEMO_DIR, "*.html"))
    files = [f for f in files if "index.html" not in f]
    
    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fleet Hub | RI2CH Agency OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #050505; color: white; font-family: 'Inter', sans-serif; }}
        .glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .neon-text {{ color: #00ffcc; text-shadow: 0 0 10px rgba(0, 255, 204, 0.5); }}
        .neon-border {{ border-color: #00ffcc; box-shadow: 0 0 15px rgba(0, 255, 204, 0.2); }}
        .card:hover {{ transform: translateY(-5px); border-color: #00ffcc; transition: all 0.3s ease; }}
    </style>
</head>
<body class="p-8 md:p-16">
    <header class="max-w-7xl mx-auto mb-16">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-5xl font-extrabold tracking-tighter mb-2">Fleet <span class="neon-text">Hub</span></h1>
                <p class="text-zinc-500 uppercase tracking-widest text-sm font-semibold">Active Shadow Site Network • {len(files)} Assets Live</p>
            </div>
            <div class="glass p-4 rounded-3xl text-right">
                <p class="text-[10px] text-zinc-500 uppercase font-bold tracking-tighter">Last Synchronized</p>
                <p class="text-lg font-mono text-white">{datetime.now().strftime('%H:%M:%S UTC')}</p>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
"""
    
    for file in files:
        filename = os.path.basename(file)
        # Convert slug back to Display Name
        display_name = filename.replace('.html', '').replace('-', ' ').title()
        
        html_content += f"""
        <a href="demo/{filename}" target="_blank" class="card glass p-8 rounded-[2rem] block group">
            <div class="flex justify-between items-start mb-6">
                <div class="w-10 h-10 rounded-xl bg-zinc-800 flex items-center justify-center text-[#00ffcc]">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                </div>
                <div class="bg-[#00ffcc]/10 text-[#00ffcc] text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-tighter">Dallas Prep</div>
            </div>
            <h3 class="text-xl font-bold mb-2 group-hover:text-[#00ffcc] transition-colors">{display_name}</h3>
            <p class="text-zinc-500 text-xs uppercase tracking-widest mb-6">Verified Shadow Instance</p>
            <div class="flex items-center gap-2 text-[#00ffcc] text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                Preview Asset <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
            </div>
        </a>
"""
        
    html_content += """
    </main>

    <footer class="max-w-7xl mx-auto mt-24 pt-8 border-t border-white/5 text-center">
        <p class="text-zinc-600 text-xs">RI2CH AGENCY OS • Dallas Strategy Acquisition Engine • v15.1.0</p>
    </footer>
</body>
</html>
"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[SUCCESS] Hub regenerated with {len(files)} assets: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_hub()
