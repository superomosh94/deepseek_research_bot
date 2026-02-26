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
    parts = content.split("ITERATION ")
    for part in parts[1:]:
        findings_start = part.find("FINDINGS:\n")
        prompt_start = part.find("RESEARCH PROMPT:\n")
        
        prompt = ""
        if prompt_start != -1:
            end = findings_start if findings_start != -1 else len(part)
            prompt = part[prompt_start + 16:end].strip()
            
        findings = ""
        if findings_start != -1:
            end = part.find("-" * 40)
            if end == -1: end = part.find("=" * 40)
            if end == -1: end = len(part)
            findings = part[findings_start + 10:end].strip()
            
        iterations.append({
            'prompt': prompt,
            'response': findings
        })
    
    # Extract final synthesis
    synthesis = ""
    syn_start = content.find("FINAL SYNTHESIS REPORT\n")
    if syn_start != -1:
        # Skip the header lines
        syn_content = content[syn_start + 23:].strip()
        syn_lines = syn_content.split('\n')
        # Filter out the '====' separator line if it exists at the start
        if syn_lines and syn_lines[0].startswith('='):
            synthesis = '\n'.join(syn_lines[1:]).strip()
        else:
            synthesis = syn_content
        
    return {
        'initial_query': topic,
        'responses': [i['response'] for i in iterations],
        'research_prompts': [i['prompt'] for i in iterations],
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
