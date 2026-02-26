import os
import json
import webbrowser
from pathlib import Path
from html_generator import HTMLGenerator
from rich.console import Console
from rich.table import Table

console = Console()

def list_past_research():
    output_dir = Path("research_output")
    if not output_dir.exists():
        console.print("[red]No research output directory found.[/red]")
        return []
        
    data_files = list(output_dir.glob("research_data_*.txt"))
    data_files.sort(reverse=True)
    
    if not data_files:
        console.print("[yellow]No past research found.[/yellow]")
        return []
        
    return data_files

def parse_txt_to_data(filepath):
    """Simple parser for the .txt logs back into raw data for the HTML generator"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    topic_match = re.search(r"Topic: (.+)", content)
    topic = topic_match.group(1) if topic_match else "Unknown Topic"
    
    # Extract iterations
    iterations = []
    # This is a bit complex for a regex, lets try a simple split
    parts = content.split("ITERATION ")
    for part in parts[1:]:
        # Split into prompt and findings
        # Iteration 1\n========\n\nRESEARCH PROMPT:\n...\n\nFINDINGS:\n...
        lines = part.split("\n")
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
        synthesis = content[syn_start + 23 + 40 + 2:].strip()
        
    return {
        'initial_query': topic,
        'responses': [i['response'] for i in iterations],
        'research_prompts': [i['prompt'] for i in iterations],
        'final_report': synthesis
    }

import re

def main():
    console.rule("[bold cyan]DeepSeek Research Viewer[/bold cyan]")
    files = list_past_research()
    
    if not files:
        return

    table = Table(title="Select a report to view", show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="center", style="dim")
    table.add_column("Date/Time", style="cyan")
    table.add_column("Topic", style="green")
    
    for i, f in enumerate(files):
        # research_data_20260226_085552.txt
        timestamp = f.stem.replace("research_data_", "")
        date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}"
        
        # Peek at topic
        with open(f, "r", encoding="utf-8") as peek:
            line = peek.readline()
            line = peek.readline() # report
            line = peek.readline() # topic
            topic = line.replace("Topic: ", "").strip()
            
        table.add_row(str(i+1), date_str, topic[:60] + "..." if len(topic) > 60 else topic)
        
    console.print(table)
    
    choice = input("\nEnter ID to open (or 'q' to quit): ")
    if choice.lower() == 'q':
        return
        
    try:
        idx = int(choice) - 1
        selected_file = files[idx]
        
        console.print(f"[yellow]Loading research from {selected_file.name}...[/yellow]")
        data = parse_txt_to_data(selected_file)
        
        html_path = selected_file.parent / selected_file.name.replace(".txt", ".html").replace("research_data_", "report_")
        HTMLGenerator.generate(data, html_path)
        
        console.print(f"[green]DONE: Report generated:[/green] {html_path.name}")
        console.print("[cyan]Opening in browser...[/cyan]")
        webbrowser.open(f"file:///{html_path.absolute()}")
        
    except (ValueError, IndexError):
        console.print("[red]Invalid choice.[/red]")

if __name__ == "__main__":
    main()
