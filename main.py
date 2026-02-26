from config import Config
from browser_controller import BrowserController
from prompt_engine import PromptEngine
from research_bot import DeepSeekResearchBot
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
import sys
import time

console = Console()

def print_banner():
    """Display beautiful banner"""
    banner = r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🚀 DEEPSEEK SELF-IMPROVING RESEARCH BOT v2.0                ║
║                                                                  ║
║     I will take your simple query, ask DeepSeek to refine it,   ║
║     research with the improved prompt, evaluate quality, and    ║
║     keep refining until I get comprehensive results!            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold cyan"))

def print_how_it_works():
    """Explain how the bot works"""
    steps = """
[bold yellow]How This Bot Works:[/bold yellow]

1. [green]INPUT[/green] → You provide a simple query (e.g., "Tell me about AI")
2. [green]REFINE[/green] → Bot asks DeepSeek: "How can I improve this query?"
3. [green]RESEARCH[/green] → Bot uses improved prompt to research
4. [green]EVALUATE[/green] → Bot checks if response is comprehensive
5. [green]REPEAT[/green] → If quality is low, repeat steps 2-4 with deeper questions
6. [green]SYNTHESIZE[/green] → All findings combined into final report

[dim]The bot will automatically pause if it encounters CAPTCHAs,
wait for you to solve them, then continue.[/dim]
    """
    console.print(Panel(steps, title="How It Works", border_style="blue"))

def check_ollama_warning():
    """Show warning about not using Ollama"""
    console.print("[yellow]⚠️  Note: This bot uses the DEEPSEEK WEBSITE directly[/yellow]")
    console.print("   It will open Chrome and navigate to chat.deepseek.com")
    console.print("   Make sure you're logged into DeepSeek in your browser\n")

def main():
    print_banner()
    print_how_it_works()
    check_ollama_warning()
    
    # Get confirmation
    if not Confirm.ask("\n[bold]Ready to start?[/bold]"):
        console.print("[yellow]Research cancelled.[/yellow]")
        return
    
    # Get initial query
    console.print("\n[bold yellow]📝 What would you like me to research?[/bold yellow]")
    console.print("[dim](Start simple - I'll refine it automatically)[/dim]")
    
    initial_query = Prompt.ask("\n[bold cyan]Your query[/bold cyan]")
    
    if not initial_query:
        console.print("[red]No query entered. Exiting.[/red]")
        return
    
    # Show configuration
    console.print(f"\n[bold]Research Configuration:[/bold]")
    console.print(f"  • Topic: {initial_query}")
    console.print(f"  • Max iterations: {Config.MAX_ITERATIONS}")
    console.print(f"  • Quality target: {Config.MIN_QUALITY_SCORE:.0%}")
    console.print(f"  • Browser: {'Visible' if not Config.HEADLESS else 'Headless'}")
    
    if not Confirm.ask("\n[bold]Proceed with research?[/bold]"):
        console.print("[yellow]Research cancelled.[/yellow]")
        return
    
    # Initialize components
    console.print("\n[bold]Initializing research system...[/bold]")
    config = Config()
    
    # Browser Detection and Selection
    from browser_utils import detect_installed_browsers
    available_browsers = detect_installed_browsers()
    
    selected_browser_type = "chrome" # Default
    
    if available_browsers:
        console.print("\n[bold cyan]Found compatible browsers on your PC:[/bold cyan]")
        for i, b in enumerate(available_browsers, 1):
            console.print(f"  {i}. [green]{b['name']}[/green] ({b['path']})")
        
        choice = Prompt.ask(
            "\n[bold]Select a browser to use[/bold]", 
            choices=[str(i) for i in range(1, len(available_browsers) + 1)],
            default="1"
        )
        browser_info = available_browsers[int(choice) - 1]
        selected_browser_type = browser_info['type']
        console.print(f"Using: [bold green]{browser_info['name']}[/bold green]")
        
        # Update config dynamically
        config.BROWSER = selected_browser_type
        config.BROWSER_PATH = browser_info['path']
    else:
        console.print("[yellow]No specific browsers detected, defaulting to Chrome...[/yellow]")

    browser = BrowserController(config)
    prompt_engine = PromptEngine()
    bot = DeepSeekResearchBot(browser, prompt_engine, config)
    
    try:
        # Start browser
        console.print("\n[bold]Step 1: Starting browser...[/bold]")
        browser.start()
        
        # Manual Login Step
        browser.wait_for_login()
        
        # Run research cycle
        console.print("\n[bold]Step 2: Beginning research cycle...[/bold]")
        bot.run_research_cycle(initial_query)
        
        # Show summary
        console.print("\n[bold]Step 3: Research complete! Generating summary...[/bold]")
        bot.show_summary()
        
        # Save results
        console.print("\n[bold]Step 4: Saving results...[/bold]")
        bot.save_results()
        
        # Final message
        console.print("\n[bold green]✅ RESEARCH COMPLETE![/bold green]")
        console.print(Panel(
            f"[green]Your research on '{initial_query}' is complete.\n"
            f"Check the 'research_output' folder for:\n"
            f"  • Full research data (TXT)\n"
            f"  • Final report (Markdown)\n"
            f"  • Summary statistics (JSON)[/green]",
            title="Success",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Research interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        console.print("\n[bold]Cleaning up...[/bold]")
        browser.close()
        console.print("[cyan]👋 Goodbye![/cyan]")

if __name__ == "__main__":
    main()
