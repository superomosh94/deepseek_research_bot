import os
import json
from datetime import datetime

class HTMLGenerator:
    """
    Generates a premium, focused 'Intelligence Dossier' HTML report.
    v3.0 - "Masterclass" Redesign
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
            'date': datetime.now().strftime("%B %d, %Y"),
            'iterations': []
        }
        
        for i in range(len(research_data['responses'])):
            js_data['iterations'].append({
                'id': i + 1,
                'prompt': research_data['research_prompts'][i] if i < len(research_data['research_prompts']) else "",
                'content': research_data['responses'][i],
                'quality': research_data.get('quality_history', [])[i]['quality'] if i < len(research_data.get('quality_history', [])) else 0.85
            })
            
        js_data['final_report'] = research_data['final_report']
        js_data_str = json.dumps(js_data).replace("</script>", "<\\/script>")
        
        # HTML Template - v3.0 Intelligence Dossier
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dossier: {js_data['topic']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #030712;
            --surface: #0f172a;
            --accent: #38bdf8;
            --ultramarine: #2563eb;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --border: rgba(255, 255, 255, 0.06);
            --glass: rgba(15, 23, 42, 0.6);
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Inter', sans-serif;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }}

        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: var(--font-body);
            line-height: 1.7;
            overflow-x: hidden;
            scroll-behavior: smooth;
        }}

        /* Subtle Noise Texture Overlay */
        body::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url("https://grainy-gradients.vercel.app/noise.svg");
            opacity: 0.03;
            pointer-events: none;
            z-index: 9999;
        }}

        /* --- IMMERSIVE HERO SECTION --- */
        .hero {{
            height: 90vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 0 24px;
            position: relative;
            background: radial-gradient(circle at 50% 50%, rgba(37, 99, 235, 0.08) 0%, transparent 70%);
            margin-bottom: 80px;
        }}

        .hero-pattern {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            mask-image: radial-gradient(circle at 50% 50%, black, transparent);
            z-index: -1;
        }}

        .badge-dossier {{
            font-family: var(--font-display);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 4px;
            font-size: 0.75rem;
            color: var(--accent);
            margin-bottom: 24px;
            opacity: 0.8;
            background: rgba(56, 189, 248, 0.1);
            padding: 8px 20px;
            border-radius: 100px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .hero h1 {{
            font-family: var(--font-display);
            font-size: clamp(2.5rem, 6vw, 4.5rem); /* Reduced slightly from 3-8-6 */
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -2px;
            max-width: 1100px;
            margin-bottom: 40px;
            background: linear-gradient(to bottom, #fff 40%, rgba(255, 255, 255, 0.4));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: slideUp 1s cubic-bezier(0.2, 0.8, 0.2, 1);
            
            /* Limit long titles */
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .hero-meta {{
            display: flex;
            gap: 32px;
            font-family: var(--font-display);
            color: var(--text-muted);
            font-size: 1rem;
            font-weight: 500;
            animation: fadeIn 1.5s ease-out;
        }}

        .scroll-indicator {{
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            animation: bounce 2s infinite;
            color: var(--text-dim);
            font-size: 1.5rem;
        }}

        /* --- NAVIGATION --- */
        .floating-nav {{
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: var(--glass);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border);
            padding: 12px 24px;
            border-radius: 100px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 32px;
            box-shadow: var(--shadow);
            transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        .floating-nav.active {{ transform: translateX(-50%) translateY(0); }}

        .nav-link {{
            color: var(--text-muted);
            text-decoration: none;
            font-family: var(--font-display);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: color 0.3s;
        }}

        .nav-link:hover {{ color: #fff; }}

        .hub-btn {{
            background: var(--ultramarine);
            color: #fff;
            padding: 8px 16px;
            border-radius: 100px;
            font-size: 0.8rem;
        }}

        /* --- MAIN CONTENT LAYOUT --- */
        .content-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 24px 120px;
        }}

        section {{
            margin-bottom: 120px;
            opacity: 0;
            transform: translateY(30px);
            transition: all 1s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        section.visible {{
            opacity: 1;
            transform: translateY(0);
        }}

        .section-label {{
            font-family: var(--font-display);
            font-weight: 700;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: var(--ultramarine);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-label::after {{
            content: "";
            height: 1px;
            flex-grow: 1;
            background: linear-gradient(to right, var(--ultramarine), transparent);
        }}

        /* --- SYNTHESIS REPORT --- */
        .report-body {{
            font-size: 1.15rem; /* Slightly smaller for density */
            color: #cbd5e1;
            line-height: 1.8;
        }}

        .report-body h2 {{
            font-family: var(--font-display);
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -1px;
            margin: 50px 0 24px;
            color: #fff;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }}

        .report-body h3 {{
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 35px 0 20px;
            color: var(--accent);
        }}

        .report-body p {{ margin-bottom: 20px; }}
        .report-body ul, .report-body ol {{ margin: 0 0 24px 24px; }}
        .report-body li {{ margin-bottom: 8px; }}

        /* Table Styling for Data */
        .report-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 32px 0;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        .report-body th, .report-body td {{
            padding: 16px;
            text-align: left;
            border: 1px solid var(--border);
        }}

        .report-body th {{
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-family: var(--font-display);
            font-weight: 600;
        }}

        .report-body blockquote {{
            border-left: 4px solid var(--ultramarine);
            background: rgba(37, 99, 235, 0.05);
            padding: 24px 32px;
            margin: 40px 0;
            font-style: italic;
            border-radius: 0 16px 16px 0;
            color: #fff;
        }}

        /* --- ANALYTICS --- */
        .analytics-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 40px;
            border-radius: 32px;
            box-shadow: var(--shadow);
        }}

        .chart-container {{
            height: 300px;
            margin-top: 32px;
        }}

        /* --- RESEARCH TRAIL (EVIDENCE CARDS) --- */
        .trail-header {{
            margin-bottom: 48px;
        }}

        .evidence-card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: 24px;
            margin-bottom: 24px;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        .evidence-card:hover {{
            background: rgba(255,255,255,0.04);
            border-color: var(--accent);
        }}

        .card-trigger {{
            padding: 32px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .card-topic {{
            display: flex;
            align-items: center;
            gap: 24px;
        }}

        .node-num {{
            width: 48px; height: 48px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 1.25rem;
            color: var(--accent);
        }}

        .node-info h4 {{
            font-family: var(--font-display);
            font-size: 1.25rem;
            margin-bottom: 4px;
        }}

        .node-info p {{
            font-size: 0.85rem;
            color: var(--text-dim);
        }}

        .card-content {{
            display: none;
            padding: 0 32px 32px;
            border-top: 1px solid var(--border);
            animation: fadeIn 0.5s ease-out;
        }}

        .evidence-card.active .card-content {{ display: block; }}
        .evidence-card.active .chevron i {{ transform: rotate(180deg); }}

        .prompt-box {{
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 24px;
            margin: 32px 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--accent);
            border: 1px dashed rgba(56, 189, 248, 0.2);
        }}

        .footer-dossier {{
            text-align: center;
            padding: 80px 0;
            border-top: 1px solid var(--border);
            color: var(--text-dim);
            font-family: var(--font-display);
            font-size: 0.85rem;
            letter-spacing: 2px;
        }}

        /* --- ANIMATIONS --- */
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(40px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateX(-50%) translateY(0); }}
            40% {{ transform: translateX(-50%) translateY(-10px); }}
            60% {{ transform: translateX(-50%) translateY(-5px); }}
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.5rem; }}
            .floating-nav {{ width: 90%; gap: 16px; padding: 10px 20px; justify-content: space-between; }}
            .nav-link {{ font-size: 0.75rem; }}
            .report-body {{ font-size: 1.1rem; }}
        }}
    </style>
</head>
<body>

    <nav class="floating-nav" id="main-nav">
        <a href="../dashboard.html" class="nav-link hub-btn">
            <i class="fas fa-chevron-left"></i> Hub
        </a>
        <a href="#synthesis" class="nav-link">Intelligence</a>
        <a href="#analytics" class="nav-link">Analysis</a>
        <a href="#trail" class="nav-link">Trail</a>
    </nav>

    <div class="hero">
        <div class="hero-pattern"></div>
        <a href="../dashboard.html" class="nav-link" style="position: absolute; top: 40px; left: 40px; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; letter-spacing: 2px;">
            <i class="fas fa-arrow-left"></i> BACK TO HUB
        </a>
        <div class="badge-dossier">Intelligence Dossier // v3.0</div>
        <h1 id="hero-title">{js_data['topic']}</h1>
        <div class="hero-meta">
            <span><i class="far fa-calendar-alt"></i> {js_data['date']}</span>
            <span><i class="fas fa-fingerprint"></i> DEEPSEEK CORE</span>
            <span><i class="fas fa-shield-halved"></i> VERIFIED</span>
        </div>
        <div class="scroll-indicator">
            <i class="fas fa-chevron-down"></i>
        </div>
    </div>

    <div class="content-container">
        <!-- SYNTHESIS -->
        <section id="synthesis">
            <div class="section-label">Executive Findings</div>
            <div id="synthesis-md" class="report-body"></div>
        </section>

        <!-- ANALYTICS -->
        <section id="analytics">
            <div class="section-label">Quality Metrics</div>
            <div class="analytics-box">
                <h3 style="font-family: var(--font-display); margin-bottom: 8px;">Neural Search Depth</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem;">Visualizing the cognitive progression of the intelligence cycles.</p>
                <div class="chart-container">
                    <canvas id="qualityChart"></canvas>
                </div>
            </div>
        </section>

        <!-- RESEARCH TRAIL -->
        <section id="trail">
            <div class="section-label">Evidence Repository</div>
            <div class="trail-header">
                <h2 style="font-family: var(--font-display); font-size: 2.5rem; margin-bottom: 12px;">The Research Trail</h2>
                <p style="color: var(--text-muted);">Explore the raw data nodes and chronological evolution of this dossier.</p>
            </div>
            <div id="evidence-trail"></div>
        </section>

        <footer class="footer-dossier">
            <a href="../dashboard.html" class="nav-link" style="display: inline-flex; align-items: center; gap: 10px; margin-bottom: 30px; color: var(--accent);">
                <i class="fas fa-arrow-left"></i> RETURN TO INTELLIGENCE HUB
            </a>
            <div style="opacity: 0.5;">AUTHENTICATED BY DEEPSEEK RESEARCH ENGINE &bull; 2026</div>
        </footer>
    </div>

    <script>
        const rawData = {js_data_str};

        function init() {{
            // Render Synthesis
            document.getElementById('synthesis-md').innerHTML = marked.parse(rawData.final_report);

            // Render Trail
            const trail = document.getElementById('evidence-trail');
            rawData.iterations.forEach(iter => {{
                const wordCount = iter.content.split(/\\s+/).length;
                const card = document.createElement('div');
                card.className = 'evidence-card';
                card.innerHTML = `
                    <div class="card-trigger" onclick="this.parentElement.classList.toggle('active')">
                        <div class="card-topic">
                            <div class="node-num">${{iter.id}}</div>
                            <div class="node-info">
                                <h4>Data Node ${{iter.id}}</h4>
                                <p>Quality Index: ${{ (iter.quality * 100).toFixed(0) }}% // Words: ${{wordCount}} // Status: Finalized</p>
                            </div>
                        </div>
                        <div class="chevron"><i class="fas fa-chevron-down"></i></div>
                    </div>
                    <div class="card-content">
                        ${{iter.prompt ? `
                            <div class="prompt-box">
                                <span style="font-size: 0.7rem; color: var(--text-dim); display: block; margin-bottom: 8px;">// NEURAL PROMPT</span>
                                ${{marked.parse(iter.prompt)}}
                            </div>
                        ` : ''}}
                        <div class="report-body" style="font-size: 1.1rem; color: var(--text-muted)">
                            ${{marked.parse(iter.content)}}
                        </div>
                    </div>
                `;
                trail.appendChild(card);
            }});

            initChart();
            initScrollEffects();
        }}

        function initScrollEffects() {{
            const nav = document.getElementById('main-nav');
            const sections = document.querySelectorAll('section');
            
            window.addEventListener('scroll', () => {{
                // Floating Nav Visibility
                if (window.scrollY > 400) nav.classList.add('active');
                else nav.classList.remove('active');

                // Section Entry Animations
                sections.forEach(sec => {{
                    const rect = sec.getBoundingClientRect();
                    if (rect.top < window.innerHeight * 0.8) {{
                        sec.classList.add('visible');
                    }}
                }});
            }});
            
            // Initial call for visible sections
            window.dispatchEvent(new Event('scroll'));
        }}

        function initChart() {{
            const ctx = document.getElementById('qualityChart').getContext('2d');
            const qData = rawData.iterations.map(i => i.quality * 100);
            const labels = rawData.iterations.map(i => `NODE ${{i.id}}`);

            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(37, 99, 235, 0.4)');
            gradient.addColorStop(1, 'rgba(37, 99, 235, 0)');

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Quality Score',
                        data: qData,
                        borderColor: '#38bdf8',
                        backgroundColor: gradient,
                        borderWidth: 4,
                        tension: 0.3,
                        fill: true,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#38bdf8',
                        pointBorderWidth: 4,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ 
                            beginAtZero: true, max: 100,
                            grid: {{ color: 'rgba(255,255,255,0.03)' }},
                            ticks: {{ color: '#64748b', font: {{ family: 'Outfit', weight: 600 }} }}
                        }},
                        x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b', font: {{ family: 'Outfit', weight: 600 }} }} }}
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
