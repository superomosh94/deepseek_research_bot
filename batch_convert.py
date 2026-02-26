import os
import re
from pathlib import Path
from html_generator import HTMLGenerator
from dashboard_generator import DashboardGenerator
from rich.console import Console

console = Console()

def parse_txt_to_data(filepath):
    """Parses .txt logs back into raw data for the HTML generator"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    topic_match = re.search(r"Topic: (.+)", content)
    topic = topic_match.group(1) if topic_match else "Unknown Topic"
    
    # Extract iterations
    iterations = []
    # Split by big iteration markers
    parts = re.split(r"={40}\nITERATION \d+\n={40}", content)
    
    # The first part is the header, subsequent parts are iterations
    for i, part in enumerate(parts[1:]):
        findings_match = re.search(r"FINDINGS:\n(.*?)(?:\n-{40}|$)", part, re.DOTALL)
        prompt_match = re.search(r"RESEARCH PROMPT:\n(.*?)(?:\n\nFINDINGS:|$)", part, re.DOTALL)
        
        prompt = prompt_match.group(1).strip() if prompt_match else "No prompt recorded."
        findings = findings_match.group(1).strip() if findings_match else "No findings recorded."
        
        # Try to find quality score in the part (if it was logged)
        # Note: older logs might not have it, so we estimate
        quality = 0.85 # Default
        quality_match = re.search(r"Quality Score: (\d+(?:\.\d+)?)%", part)
        if quality_match:
            quality = float(quality_match.group(1)) / 100.0
        else:
            # Estimate quality based on content length and structure
            word_count = len(findings.split())
            has_lists = '-' in findings or '*' in findings or '1.' in findings
            has_code = '```' in findings or '    ' in findings
            
            score = 0.5
            if word_count > 500: score += 0.2
            if has_lists: score += 0.1
            if has_code: score += 0.1
            quality = min(score, 0.95)

        iterations.append({
            'prompt': prompt,
            'response': findings,
            'quality': quality
        })
    
    # Extract final synthesis
    synthesis = ""
    syn_match = re.search(r"FINAL SYNTHESIS REPORT\n={40}\n\n(.*?)$", content, re.DOTALL)
    if syn_match:
        synthesis = syn_match.group(1).strip()
    else:
        # Fallback if the above fails
        syn_start = content.find("FINAL SYNTHESIS REPORT")
        if syn_start != -1:
            synthesis = content[syn_start:].split('='*40)[-1].strip()
        
    return {
        'initial_query': topic,
        'responses': [i['response'] for i in iterations],
        'research_prompts': [i['prompt'] for i in iterations],
        'quality_history': [{'iteration': i+1, 'quality': iter_data['quality']} for i, iter_data in enumerate(iterations)],
        'final_report': synthesis
    }

def batch_convert():
    console.rule("[bold cyan]DeepSeek Batch Report Converter[/bold cyan]")
    output_dir = Path("research_output")
    
    if not output_dir.exists():
        console.print("[red]No research output directory found.[/red]")
        return
        
    data_files = list(output_dir.glob("research_data_*.txt"))
    if not data_files:
        console.print("[yellow]No log files found to convert.[/yellow]")
        return
        
    console.print(f"Found {len(data_files)} reports to convert...")
    
    success_count = 0
    for f in data_files:
        html_path = output_dir / f.name.replace(".txt", ".html").replace("research_data_", "report_")
        
        # Skip if already exists unless user wants override (always override for this batch)
        try:
            data = parse_txt_to_data(f)
            HTMLGenerator.generate(data, html_path)
            console.print(f"[green]DONE:[/green] {f.name} -> {html_path.name}")
            success_count += 1
        except Exception as e:
            console.print(f"[red]FAIL:[/red] {f.name}: {e}")
            
    DashboardGenerator.generate()
    console.print(f"\n[bold green]Success![/bold green] Converted {success_count} reports.")
    console.print("[cyan]Master dashboard updated: dashboard.html[/cyan]")

if __name__ == "__main__":
    batch_convert()
