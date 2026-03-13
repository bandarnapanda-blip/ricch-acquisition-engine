import os
import streamlit as st
import pandas as pd
from preview_engine import generate_preview_metadata

def generate_portfolio_html(leads_df):
    """Generates a premium Pinterest-style HTML portfolio from successful leads."""
    
    # Filter for interesting leads (or just take top 6 for demonstration)
    leads_to_show = leads_df.nlargest(9, 'opportunity_score')
    
    cards_html = ""
    for _, lead in leads_to_show.iterrows():
        meta = generate_preview_metadata(lead)
        if not meta:
            continue
            
        # Determine a color scheme based on the theme name (returned as string)
        theme_name = meta.get('theme_name', 'Modern Professional')
        theme_colors = {
            "Modern Professional": "linear-gradient(135deg, #1a1c2c, #4a192c)",
            "High-Ticket Luxury": "linear-gradient(135deg, #1c1c1c, #4d3d1a)",
            "Rugged Industrial": "linear-gradient(135deg, #1a2c1c, #194a2c)"
        }
        bg = theme_colors.get(theme_name, "linear-gradient(135deg, #1a1d28, #11131a)")
        txt_color = "#fff" if "Luxury" in theme_name or "Industrial" in theme_name or "Modern" in theme_name else "#333"
        
        cards_html += f"""
        <div class="portfolio-card" style="background:{bg}; color:{txt_color};">
            <div class="card-overlay"></div>
            <div class="card-content">
                <div class="badge">{meta['niche'].upper()}</div>
                <h3>{meta['business_name']}</h3>
                <p>Revived in {meta['city']}</p>
                <div class="features">
                    {" ".join([f"<span>• {f}</span>" for f in meta['features'][:3]])}
                </div>
                <a href="{meta['preview_url']}" class="view-btn">View Full Prototype</a>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ri2ch Growth Lab | Case Studies</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;700;900&display=swap');
            body {{
                background: #0a0b10;
                color: #fff;
                font-family: 'Outfit', sans-serif;
                margin: 0;
                padding: 40px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 60px;
            }}
            .header h1 {{
                font-size: 3rem;
                font-weight: 900;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #ff4d94, #00e5ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .portfolio-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 30px;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .portfolio-card {{
                height: 450px;
                border-radius: 30px;
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 30px;
                transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .portfolio-card:hover {{
                transform: translateY(-15px) scale(1.02);
                border-color: #ff4d94;
            }}
            .card-overlay {{
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background: linear-gradient(to bottom, transparent 30%, rgba(0,0,0,0.8));
                z-index: 1;
            }}
            .card-content {{
                position: relative;
                z-index: 2;
            }}
            .badge {{
                display: inline-block;
                padding: 6px 14px;
                background: rgba(255, 77, 148, 0.2);
                color: #ff4d94;
                border-radius: 20px;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 1px;
                margin-bottom: 15px;
            }}
            h3 {{ font-size: 1.8rem; margin: 0; font-weight: 900; }}
            p {{ margin: 5px 0 20px 0; color: rgba(255,255,255,0.6); font-size: 0.9rem; }}
            .features {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 25px;
            }}
            .features span {{
                font-size: 0.75rem;
                color: rgba(255,255,255,0.4);
            }}
            .view-btn {{
                display: inline-block;
                padding: 12px 25px;
                background: #fff;
                color: #000;
                text-decoration: none;
                border-radius: 15px;
                font-weight: 800;
                font-size: 0.85rem;
                text-align: center;
                transition: background 0.3s;
            }}
            .view-btn:hover {{
                background: #ff4d94;
                color: #fff;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RI2CH GROWTH LAB</h1>
            <p>High-Performance Technical Redesign Showcase</p>
        </div>
        <div class="portfolio-grid">
            {cards_html}
        </div>
    </body>
    </html>
    """
    return html

def save_portfolio(html, filename="showcase.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(filename)
