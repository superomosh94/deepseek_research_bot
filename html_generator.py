import os
import json
from datetime import datetime

class HTMLGenerator:
    """
    Generates a premium, interactive HTML report for research findings
    """
    
    @staticmethod
    def generate(research_data, output_path):
        """
        research_data structure:
        {
            'initial_query': str,
            'responses': list,
            'research_prompts': list,
            'final_report': str,
            'quality_history': list
        }
        """
        
        # Prepare data for JS
        js_data = {
            'topic': research_data['initial_query'],
            'date': datetime.now().strftime("%B %d, %Y at %H:%M"),
            'iterations': []
        }
        
        for i in range(len(research_data['responses'])):
            js_data['iterations'].append({
                'id': i + 1,
                'prompt': research_data['research_prompts'][i] if i < len(research_data['research_prompts']) else "",
                'content': research_data['responses'][i],
                'quality': research_data.get('quality_history', [])[i]['quality'] if i < len(research_data.get('quality_history', [])) else 0.8
            })
            
        js_data['final_report'] = research_data['final_report']
        js_data['quality_history'] = research_data.get('quality_history', [])
        
        # HTML Template
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research: {js_data['topic']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #00e5ff;
            --secondary: #0081ff;
            --bg: #050a14;
            --card-bg: rgba(255, 255, 255, 0.05); /* Increased slightly for contrast */
            --border: rgba(255, 255, 255, 0.12); /* Sharper borders */
            --text: #ffffff; /* pure white for better visibility */
            --text-dim: #cbd5e1; /* lighter dim text */
            --accent: #ff007b;
            --glass: rgba(255, 255, 255, 0.02);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.8; /* Increased line height for legibility */
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(0, 229, 255, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(0, 129, 255, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
        }}

        .nav-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 15px 0;
            margin-bottom: 40px;
            background: rgba(5, 10, 20, 0.7);
        }}

        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .back-btn {{
            color: var(--text-dim);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: color 0.3s ease;
        }}

        .back-btn:hover {{ color: var(--primary); }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 20px 80px;
        }}

        header {{
            text-align: center;
            margin-bottom: 60px;
            animation: fadeInDown 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        .badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 30px;
            background: rgba(0, 229, 255, 0.1);
            color: var(--primary);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 229, 255, 0.2);
        }}

        h1 {{
            font-size: 3.5rem; /* Slightly larger */
            font-weight: 800; /* Bolder */
            margin-bottom: 20px;
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1.5px;
            text-shadow: 0 10px 30px rgba(0,0,0,0.5); /* Lift off background */
        }}

        .meta {{
            font-size: 0.95rem;
            color: var(--text-dim);
            display: flex;
            justify-content: center;
            gap: 25px;
        }}

        .dashboard-layout {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 40px;
        }}

        .sidebar {{
            position: sticky;
            top: 100px;
            height: fit-content;
        }}

        .glass-card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }}

        .glass-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(to right, transparent, var(--border), transparent);
        }}

        .nav-btn {{
            width: 100%;
            padding: 14px 18px;
            margin-bottom: 10px;
            border-radius: 14px;
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-dim);
            text-align: left;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 1rem;
            font-weight: 500;
        }}

        .nav-btn:hover {{
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            transform: translateX(4px);
        }}

        .nav-btn.active {{
            background: linear-gradient(90deg, rgba(0, 229, 255, 0.15) 0%, transparent 100%);
            border-left: 3px solid var(--primary);
            color: var(--primary);
            padding-left: 20px;
        }}

        .panel {{
            display: none;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .panel.active {{
            display: block;
            opacity: 1;
            transform: translateY(0);
        }}

        .markdown-content {{
            font-size: 1.15rem; /* Larger body text */
            color: #f1f5f9; /* Near white body */
            font-weight: 400;
        }}
        
        .markdown-content strong {{
            color: var(--primary); /* highlight strong text */
            font-weight: 700;
        }}

        .markdown-content h1, .markdown-content h2, .markdown-content h3 {{
            color: #ffffff;
            margin: 2.5rem 0 1.5rem;
            font-weight: 700; /* Max weight for headings */
            letter-spacing: -0.5px;
            line-height: 1.3;
        }}
        
        .markdown-content h2 {{ font-size: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
        .markdown-content h3 {{ font-size: 1.6rem; color: var(--primary); }}

        .markdown-content p {{ margin-bottom: 1.2rem; }}
        
        .markdown-content blockquote {{
            border-left: 4px solid var(--primary);
            padding: 15px 25px;
            background: rgba(0, 229, 255, 0.03);
            border-radius: 0 16px 16px 0;
            margin: 2rem 0;
            font-style: italic;
            color: var(--text);
        }}

        .chart-box {{
            height: 200px;
            margin-bottom: 30px;
        }}

        .iter-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }}

        .prompt-reveal {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }}

        .prompt-reveal summary {{
            cursor: pointer;
            color: var(--primary);
            font-weight: 600;
            user-select: none;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .prompt-reveal summary::before {{
            content: '\\f054';
            font-family: 'Font Awesome 6 Free';
            font-weight: 900;
            font-size: 0.8rem;
            transition: transform 0.3s ease;
        }}

        .prompt-reveal[open] summary::before {{
            transform: rotate(90deg);
        }}

        footer {{
            margin-top: 100px;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 900px) {{
            .dashboard-layout {{ grid-template-columns: 1fr; }}
            .sidebar {{ position: static; }}
            h1 {{ font-size: 2.2rem; }}
        }}
    </style>
</head>
<body>
    <nav class="nav-header">
        <div class="nav-container">
            <a href="../dashboard.html" class="back-btn">
                <i class="fas fa-arrow-left"></i> Hub
            </a>
            <div style="font-weight: 600; font-size: 0.9rem; color: #fff;">RESEARCH INSIGHT</div>
            <div style="width: 50px;"></div>
        </div>
    </nav>

    <div class="container">
        <header>
            <div class="badge">Intelligence Report</div>
            <h1>{js_data['topic']}</h1>
            <div class="meta">
                <span><i class="far fa-calendar-alt"></i> {js_data['date']}</span>
                <span><i class="fas fa-bolt" style="color: var(--primary);"></i> Enhanced by DeepSeek</span>
            </div>
        </header>

        <div class="dashboard-layout">
            <div class="sidebar">
                <div class="glass-card">
                    <h3 style="margin-bottom: 20px; font-size: 0.9rem; letter-spacing: 1px; color: #fff; text-transform: uppercase;">Analysis Center</h3>
                    <button class="nav-btn active" onclick="showPanel('final')">
                        <i class="fas fa-brain"></i> Synthesis
                    </button>
                    <button class="nav-btn" onclick="showPanel('stats')">
                        <i class="fas fa-chart-line"></i> Analytics
                    </button>
                    
                    <div style="margin: 30px 0 15px; font-size: 0.7rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">Data Nodes</div>
                    <div id="iter-nav"></div>
                </div>
            </div>

            <div class="main-content">
                <!-- Final Synthesis -->
                <div id="panel-final" class="panel active glass-card">
                    <h2 style="font-size: 1.8rem; margin-bottom: 30px; display: flex; align-items: center; gap: 15px;">
                        <span style="width: 40px; height: 40px; background: rgba(0, 229, 255, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-star" style="color: var(--primary); font-size: 1rem;"></i>
                        </span>
                        Synthesis Report
                    </h2>
                    <div id="synthesis-md" class="markdown-content"></div>
                </div>

                <!-- Stats/Analytics -->
                <div id="panel-stats" class="panel glass-card">
                    <h2 style="font-size: 1.8rem; margin-bottom: 20px;">Quality Evolution</h2>
                    <p style="color: var(--text-dim); margin-bottom: 30px;">Metric analysis of AI response depth and relevance over the research cycle.</p>
                    <div class="chart-box">
                        <canvas id="qualityChart"></canvas>
                    </div>
                </div>

                <!-- Iteration Panels -->
                <div id="iter-panels"></div>
            </div>
        </div>

        <footer>
            PROPRIETARY RESEARCH ENGINE &bull; DEEPSEEK v2.0 &bull; 2026
        </footer>
    </div>

    <script>
        const rawData = {json.dumps(js_data)};

        function init() {{
            // Render Synthesis
            document.getElementById('synthesis-md').innerHTML = marked.parse(rawData.final_report);

            // Create Iteration Elements
            const nav = document.getElementById('iter-nav');
            const panels = document.getElementById('iter-panels');

            rawData.iterations.forEach(iter => {{
                // Nav
                const btn = document.createElement('button');
                btn.className = 'nav-btn';
                btn.onclick = () => showPanel(`iter-${{iter.id}}`);
                btn.innerHTML = `<i class="fas fa-microscope"></i> Node ${{iter.id}}`;
                nav.appendChild(btn);

                // Panel
                const panel = document.createElement('div');
                panel.id = `panel-iter-${{iter.id}}`;
                panel.className = 'panel glass-card';
                panel.innerHTML = `
                    <div class="iter-meta">
                        <h2 style="font-size: 1.5rem;">Node ${{iter.id}} Findings</h2>
                        <span class="badge" style="margin: 0;">Iteration ${{iter.id}}</span>
                    </div>
                    ${{iter.prompt ? `
                        <details class="prompt-reveal">
                            <summary>View Neural Prompt</summary>
                            <div style="margin-top: 15px; color: var(--text-dim); font-family: 'JetBrains Mono'; line-height: 1.4;">
                                ${{iter.prompt}}
                            </div>
                        </details>
                    ` : ''}}
                    <div class="markdown-content">${{marked.parse(iter.content)}}</div>
                `;
                panels.appendChild(panel);
            }});

            initChart();
        }}

        function showPanel(id) {{
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            
            const targetP = document.getElementById(`panel-${{id}}`);
            if (targetP) targetP.classList.add('active');

            const btn = Array.from(document.querySelectorAll('.nav-btn')).find(b => 
                b.getAttribute('onclick')?.includes(id)
            );
            if (btn) btn.classList.add('active');
            
            window.scrollTo({{ top: document.querySelector('.main-content').offsetTop - 120, behavior: 'smooth' }});
        }}

        function initChart() {{
            const ctx = document.getElementById('qualityChart').getContext('2d');
            const qData = rawData.iterations.map(i => i.quality * 100);
            const labels = rawData.iterations.map(i => `Iter ${{i.id}}`);

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Quality Score %',
                        data: qData,
                        borderColor: '#00e5ff',
                        backgroundColor: 'rgba(0, 229, 255, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#00e5ff',
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ 
                            beginAtZero: true, 
                            max: 100,
                            grid: {{ color: 'rgba(255,255,255,0.05)' }},
                            ticks: {{ color: '#808080' }}
                        }},
                        x: {{ grid: {{ display: false }}, ticks: {{ color: '#808080' }} }}
                    }}
                }}
            }});
        }}

        window.onload = init;
    </script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        return output_path
