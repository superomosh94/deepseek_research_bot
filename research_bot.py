from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import time
from datetime import datetime
import os
import webbrowser
from html_generator import HTMLGenerator
from dashboard_generator import DashboardGenerator

console = Console()

class DeepSeekResearchBot:
    def __init__(self, browser, prompt_engine, config):
        self.browser = browser
        self.prompt_engine = prompt_engine
        self.config = config
        self.research_data = {
            'initial_query': '',
            'refinement_prompts': [],
            'research_prompts': [],
            'responses': [],
            'final_report': '',
            'iterations': [],
            'messages_sent': 0  # Counter for current chat
        }
        
    def run_research_cycle(self, initial_query):
        """
        Main research loop: refine → research → evaluate → repeat
        """
        self.research_data['initial_query'] = initial_query
        
        # Display header
        console.rule("[bold cyan]Starting Self-Improving Research Cycle[/bold cyan]")
        console.print(Panel(
            f"[bold]Initial Query:[/bold]\n{initial_query}\n\n"
            f"[dim]I will now ask DeepSeek to refine this, research it, "
            f"evaluate the quality, and repeat until comprehensive results are achieved.[/dim]",
            title="Research Started",
            style="green"
        ))
        
        iteration = 1
        
        while iteration <= self.config.MAX_ITERATIONS:
            console.rule(f"[bold yellow]Iteration {iteration}/{self.config.MAX_ITERATIONS}[/bold yellow]")
            
            # Step 1: Get refined prompt from DeepSeek
            console.print("\n[bold]📝 Step 1: Getting refined research prompt...[/bold]")
            
            # Create refinement prompt
            refinement_prompt = self.prompt_engine.create_refinement_prompt(
                initial_query,
                self.research_data['responses'],
                iteration
            )
            
            # Send refinement request with retry logic
            refinement_response = ""
            for retry in range(3):
                refinement_response = self.browser.send_message(refinement_prompt)
                if refinement_response:
                    break
                
                console.print(f"[red]Failed to get refinement response (Attempt {retry+1}/3). Retrying...[/red]")
                if retry == 1:
                    console.print("[yellow]🔄 Attempting page refresh to recover UI state...[/yellow]")
                    self.browser.driver.refresh()
                    time.sleep(self.config.PAGE_LOAD_WAIT)
                time.sleep(5)
            
            if not refinement_response:
                console.print("[bold red]❌ Failed to get refinement after 3 attempts. Skipping to next step or stopping.[/bold red]")
                if iteration == 1:
                    # If first iteration fails, we can't really continue well
                    research_prompt = initial_query
                else:
                    iteration += 1
                    continue
            else:
                # Extract the actual research prompt
                research_prompt = self.prompt_engine.extract_research_prompt(refinement_response)
            
            # Store prompts
            self.research_data['refinement_prompts'].append(refinement_response)
            self.research_data['research_prompts'].append(research_prompt)
            
            # Display extracted prompt
            console.print(Panel(
                research_prompt[:500] + ("..." if len(research_prompt) > 500 else ""),
                title="[bold cyan]Research Prompt for this Iteration[/bold cyan]",
                border_style="cyan"
            ))
            
            # Step 2: Manage conversation state (Restart if necessary)
            self.research_data['messages_sent'] += 1 # Increment for the refinement prompt sent in Step 1
            
            should_new_chat = False
            was_reset = False
            if not self.config.REUSE_CHAT:
                should_new_chat = True
                reason_new = "Reusing chats is disabled"
            elif self.research_data['messages_sent'] >= self.config.MAX_MESSAGES_PER_CHAT:
                should_new_chat = True
                reason_new = f"Message limit ({self.config.MAX_MESSAGES_PER_CHAT}) reached"
            
            if should_new_chat:
                console.print(f"\n[bold]🔄 Step 2: Starting fresh conversation ({reason_new})...[/bold]")
                self.browser.start_new_chat()
                self.research_data['messages_sent'] = 0
                was_reset = True
            else:
                console.print("\n[bold]♻️  Step 2: Reusing current conversation...[/bold]")
                # Just a small delay to ensure UI is ready
                time.sleep(1)
            
            # Step 3: Send the refined prompt for research
            console.print("[bold]🔍 Step 3: Conducting research with refined prompt...[/bold]")
            
            # CONTEXT CARRYOVER: If we just started a new chat, carry over previous findings
            final_research_prompt = research_prompt
            if was_reset and self.research_data['responses']:
                 console.print("[dim]Prepending previous research findings for continuity...[/dim]")
                 context = f"Continuing research on: \"{initial_query}\"\n\nHere is what we have found so far across {len(self.research_data['responses'])} iterations:\n"
                 for i, resp in enumerate(self.research_data['responses']):
                     # Include a snippet of each previous finding
                     snippet = resp[:400].replace('\n', ' ')
                     context += f"- Iteration {i+1}: {snippet}...\n"
                 
                 final_research_prompt = f"{context}\n\n[OBJECTIVE] Based on the above, please proceed with this specific research goal:\n{research_prompt}"

            research_response = self.browser.send_message(final_research_prompt)
            self.research_data['messages_sent'] += 1
            
            if not research_response:
                console.print("[red]Failed to get research response. Skipping iteration.[/red]")
                continue
            
            # Store response
            self.research_data['responses'].append(research_response)
            
            # Display response preview
            console.print(Panel(
                research_response[:800] + ("..." if len(research_response) > 800 else ""),
                title=f"[bold green]Research Findings - Iteration {iteration}[/bold green]",
                border_style="green"
            ))
            
            # Step 4: Evaluate quality
            console.print("\n[bold]📊 Step 4: Evaluating response quality...[/bold]")
            quality_score, should_continue, reason = self.prompt_engine.evaluate_response_quality(
                research_response,
                initial_query
            )
            
            # Log iteration
            self.prompt_engine.log_iteration(
                iteration,
                refinement_prompt,
                research_response,
                quality_score,
                research_prompt
            )
            
            # Display quality metrics
            quality_table = Table(title="Quality Assessment", show_header=True, header_style="bold magenta")
            quality_table.add_column("Metric", style="cyan")
            quality_table.add_column("Value", style="yellow")
            quality_table.add_row("Quality Score", f"{quality_score:.1%}")
            quality_table.add_row("Decision", "Continue" if should_continue else "Stop")
            quality_table.add_row("Reason", reason)
            console.print(quality_table)
            
            if not should_continue:
                console.print("[bold green]✓ Research complete! Good quality achieved.[/bold green]")
                break
            
            # Prepare for next iteration
            iteration += 1
            console.print(f"\n[yellow]Preparing for iteration {iteration}...[/yellow]")
            time.sleep(3)
        
        # Generate final report
        self.generate_final_report()
        
    def generate_final_report(self):
        """Compile all research into a comprehensive report"""
        console.rule("[bold green]Generating Final Comprehensive Report[/bold green]")
        
        if not self.research_data['responses']:
            console.print("[red]No research data to generate report.[/red]")
            return
        
        # Prepare synthesis prompt
        synthesis_prompt = f"""I have conducted {len(self.research_data['responses'])} research iterations on: "{self.research_data['initial_query']}"

Here are ALL the responses I gathered:

"""
        
        for i, response in enumerate(self.research_data['responses'], 1):
            synthesis_prompt += f"\n--- ITERATION {i} ---\n{response[:8000]}\n"
        
        synthesis_prompt += """
Please synthesize ALL this information into a comprehensive, well-structured final report.

The report MUST include:

1. EXECUTIVE SUMMARY
   - Brief overview of the topic
   - Key findings at a glance

2. MAIN FINDINGS
   - Organized by theme/subtopic
   - Include specific details and examples
   - Cite which iteration provided what information

3. DETAILED ANALYSIS
   - Deeper exploration of important aspects
   - Connections between different findings
   - Implications and significance

4. KEY INSIGHTS
   - Most important takeaways
   - Unique or surprising findings
   - Practical applications

5. CONCLUSIONS
   - Summary of what we've learned
   - Answer to the original research question

6. FURTHER RESEARCH
   - What remains unexplored
   - Suggestions for deeper investigation

Make it thorough, well-organized, and valuable as a standalone research document.
"""
        
        console.print("[bold]🧠 Asking DeepSeek to synthesize findings...[/bold]")
        
        # Determine if we should start a new chat for synthesis
        # Often better for synthesis to have everything in context if possible, 
        # but if we've reached a limit, we better start fresh.
        if self.research_data['messages_sent'] > self.config.MAX_MESSAGES_PER_CHAT - 2:
            console.print("[dim]Starting new chat for synthesis due to message count...[/dim]")
            self.browser.start_new_chat()
            self.research_data['messages_sent'] = 0
        
        # No Progress bar here to avoid flickering with the console.print calls inside send_message
        final_report = self.browser.send_message(synthesis_prompt)
        
        self.research_data['final_report'] = final_report
        
        # Display report preview
        console.print(Panel(
            final_report[:1500] + ("..." if len(final_report) > 1500 else ""),
            title="[bold green]Final Report Preview[/bold green]",
            border_style="green",
            width=100
        ))
        
    def show_summary(self):
        """Display research summary"""
        console.rule("[bold blue]Research Summary[/bold blue]")
        
        # Main stats table
        stats_table = Table(title="Research Statistics", show_header=True, header_style="bold cyan")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Initial Query", self.research_data['initial_query'][:100])
        stats_table.add_row("Iterations Completed", str(len(self.research_data['responses'])))
        stats_table.add_row("Total Response Length", f"{sum(len(r) for r in self.research_data['responses']):,} chars")
        stats_table.add_row("Final Report Length", f"{len(self.research_data['final_report']):,} chars")
        
        if self.research_data['responses']:
            avg_quality = sum(e['quality_score'] for e in self.prompt_engine.iteration_history) / len(self.prompt_engine.iteration_history)
            stats_table.add_row("Average Quality", f"{avg_quality:.1%}")
        
        console.print(stats_table)
        
        # Iteration history table
        if self.prompt_engine.iteration_history:
            history_table = Table(title="Iteration History", show_header=True, header_style="bold magenta")
            history_table.add_column("Iteration", style="cyan", justify="center")
            history_table.add_column("Quality Score", style="yellow", justify="center")
            history_table.add_column("Response Length", style="green", justify="center")
            history_table.add_column("Research Prompt Preview", style="white")
            
            for entry in self.prompt_engine.iteration_history:
                history_table.add_row(
                    str(entry['iteration']),
                    f"{entry['quality_score']:.1%}",
                    str(entry['response_length']),
                    entry['research_prompt'][:50] + "..."
                )
            
            console.print(history_table)
    
    def save_results(self):
        """Save all research data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full research data
        filename1 = self.config.OUTPUT_DIR / f"research_data_{timestamp}.txt"
        with open(filename1, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"DEEPSEEK RESEARCH REPORT\n")
            f.write(f"Topic: {self.research_data['initial_query']}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Iterations: {len(self.research_data['responses'])}\n")
            f.write("=" * 80 + "\n\n")
            
            for i in range(len(self.research_data['responses'])):
                f.write(f"\n{'='*40}\n")
                f.write(f"ITERATION {i+1}\n")
                f.write(f"{'='*40}\n\n")
                
                if i < len(self.research_data['research_prompts']):
                    f.write(f"RESEARCH PROMPT:\n{self.research_data['research_prompts'][i]}\n\n")
                
                f.write(f"FINDINGS:\n{self.research_data['responses'][i]}\n")
                f.write("\n" + "-" * 40 + "\n")
            
            f.write(f"\n{'='*40}\n")
            f.write("FINAL SYNTHESIS REPORT\n")
            f.write(f"{'='*40}\n\n")
            f.write(self.research_data['final_report'])
        
        # Save just the final report as markdown
        filename2 = self.config.OUTPUT_DIR / f"final_report_{timestamp}.md"
        with open(filename2, "w", encoding="utf-8") as f:
            f.write(f"# Research Report: {self.research_data['initial_query']}\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(self.research_data['final_report'])
        
        # Save summary JSON
        import json
        filename3 = self.config.OUTPUT_DIR / f"summary_{timestamp}.json"
        summary = {
            'topic': self.research_data['initial_query'],
            'iterations': len(self.research_data['responses']),
            'quality_history': [
                {
                    'iteration': e['iteration'],
                    'quality': e['quality_score']
                } for e in self.prompt_engine.iteration_history
            ],
            'timestamp': datetime.now().isoformat()
        }
        with open(filename3, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        
        # Generate Modern HTML Report
        filename4 = self.config.OUTPUT_DIR / f"report_{timestamp}.html"
        try:
            HTMLGenerator.generate({
                'initial_query': self.research_data['initial_query'],
                'responses': self.research_data['responses'],
                'research_prompts': self.research_data['research_prompts'],
                'final_report': self.research_data['final_report']
            }, filename4)
            
            console.print(f"[green]✓ Modern dynamic report saved to:[/green] {filename4}")
            
            # Update Master Dashboard
            DashboardGenerator.generate()
            console.print("[green]✓ Master dashboard updated:[/green] dashboard.html")
            
            # Auto-open the report
            console.print("[cyan]🌐 Opening modern report in your browser...[/cyan]")
            webbrowser.open(f"file:///{filename4.absolute()}")
        except Exception as e:
            console.print(f"[red]Failed to generate modern report: {e}[/red]")
        
        console.print(f"\n[green]✓ Research data saved to:[/green] {filename1}")
        console.print(f"[green]✓ Final report saved to:[/green] {filename2}")
        console.print(f"[green]✓ Summary saved to:[/green] {filename3}")
