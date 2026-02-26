import os
import json
from pathlib import Path
from datetime import datetime

class DashboardGenerator:
    """
    Generates a premium master dashboard.html to navigate all research reports
    """
    
    @staticmethod
    def generate(output_dir="research_output"):
        output_path = Path(output_dir)
        if not output_path.exists():
            return None
            
        reports = []
        summaries = list(output_path.glob("summary_*.json"))
        summaries.sort(reverse=True)
        
        for s_path in summaries:
            try:
                with open(s_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                
                timestamp = s_path.stem.replace("summary_", "")
                html_file = f"report_{timestamp}.html"
                
                if (output_path / html_file).exists():
                    reports.append({
                        'topic': meta.get('topic', 'Untitled Research'),
                        'date': meta.get('timestamp', ''),
                        'iterations': meta.get('iterations', 0),
                        'file': html_file,
                        'timestamp': timestamp,
                        'is_new': (datetime.now() - datetime.fromisoformat(meta.get('timestamp', ''))).days < 1
                    })
            except Exception as e:
                print(f"Error parsing {s_path}: {e}")

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #00e5ff;
            --secondary: #0081ff;
            --bg: #050a14;
            --card-bg: rgba(255, 255, 255, 0.04);
            --border: rgba(255, 255, 255, 0.12);
            --text: #ffffff;
            --text-dim: #cbd5e1;
            --accent: #ff007b;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Animated Blob Background */
        .blobs {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            filter: blur(80px);
            opacity: 0.4;
        }}

        .blob {{
            position: absolute;
            width: 500px; height: 500px;
            border-radius: 50%;
            animation: move 20s infinite alternate;
        }}

        .blob-1 {{ background: var(--primary); top: -100px; left: -100px; animation-duration: 25s; }}
        .blob-2 {{ background: var(--secondary); bottom: -100px; right: -100px; animation-duration: 30s; }}

        @keyframes move {{
            0% {{ transform: translate(0, 0) scale(1); }}
            100% {{ transform: translate(100px, 100px) scale(1.2); }}
        }}

        .container {{
            max-width: 1300px;
            margin: 0 auto;
            padding: 80px 24px;
        }}

        header {{
            text-align: center;
            margin-bottom: 80px;
        }}

        .logo-area {{
            display: inline-flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .logo-area i {{
            font-size: 3.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        h1 {{
            font-size: 4rem;
            font-weight: 800;
            letter-spacing: -2px;
            margin-bottom: 15px;
            color: #fff;
            text-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}

        .search-container {{
            max-width: 700px;
            margin: 0 auto 60px;
            position: relative;
        }}

        .search-bar {{
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            padding: 22px 30px 22px 65px;
            border-radius: 20px;
            color: #fff;
            font-size: 1.1rem;
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
        }}

        .search-bar:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.15);
            background: rgba(255, 255, 255, 0.05);
        }}

        .search-container i {{
            position: absolute;
            left: 25px; top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 1.2rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 30px;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 32px;
            padding: 40px;
            text-decoration: none;
            color: inherit;
            position: relative;
            backdrop-filter: blur(10px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .card:hover {{
            transform: translateY(-10px);
            border-color: var(--primary);
            background: rgba(255, 255, 255, 0.06);
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        }}

        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }}

        .new-tag {{
            background: linear-gradient(135deg, var(--accent), #ff5e00);
            color: #fff;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
        }}

        .cycles {{
            font-size: 0.8rem;
            color: var(--primary);
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}

        .card h3 {{
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 35px;
            color: #fff;
            letter-spacing: -0.5px;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 25px;
            border-top: 1px solid var(--border);
        }}

        .date-box {{
            color: var(--text-dim);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .arrow {{
            width: 40px; height: 40px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}

        .card:hover .arrow {{
            background: var(--primary);
            color: #000;
        }}
    </style>
</head>
<body>
    <div class="blobs">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
    </div>

    <div class="container">
        <header>
            <div class="logo-area">
                <i class="fas fa-atom"></i>
                <h1>Intelligence Hub</h1>
            </div>
            <p style="color: var(--text-dim); font-size: 1.1rem;">DeepSeek-powered research exploration engine</p>
        </header>

        <div class="search-container">
            <i class="fas fa-search"></i>
            <input type="text" class="search-bar" placeholder="Search research topics..." onkeyup="filter(this.value)">
        </div>

        <div class="grid" id="grid">
            {"".join([f'''
            <a href="{(output_path / r['file']).relative_to(Path('.')).as_posix()}" class="card" data-topic="{r['topic'].lower()}">
                <div class="card-top">
                    <span class="cycles">{r['iterations']} Research Cycles</span>
                    {f'<span class="new-tag">New</span>' if r['is_new'] else ''}
                </div>
                <h3>{r['topic']}</h3>
                <div class="card-footer">
                    <div class="date-box">
                        <i class="far fa-calendar-alt"></i>
                        {r['date'][:10]}
                    </div>
                    <div class="arrow">
                        <i class="fas fa-chevron-right"></i>
                    </div>
                </div>
            </a>
            ''' for r in reports])}
        </div>
    </div>

    <script>
        function filter(q) {{
            const cards = document.querySelectorAll('.card');
            q = q.toLowerCase();
            cards.forEach(c => {{
                if (c.dataset.topic.includes(q)) {{
                    c.style.display = 'flex';
                }} else {{
                    c.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
        with open("dashboard.html", "w", encoding="utf-8") as f:
            f.write(html_template)
        return "dashboard.html"

if __name__ == "__main__":
    DashboardGenerator.generate()
