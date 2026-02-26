from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
from rich.console import Console
from rich.panel import Panel
import os

console = Console()

class BrowserController:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.last_response = ""
        
    def start(self):
        """Start the browser and navigate to DeepSeek"""
        browser_name = self.config.BROWSER.title()
        console.print(f"[bold green]🚀 Starting {browser_name} browser...[/bold green]")
        
        try:
            if self.config.BROWSER == "edge":
                console.print(f"[dim]Initialzing Edge with path: {self.config.BROWSER_PATH}[/dim]")
                from selenium.webdriver.edge.service import Service as EdgeService
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                from selenium.webdriver.edge.options import Options as EdgeOptions
                
                options = EdgeOptions()
                if self.config.BROWSER_PATH:
                    options.binary_location = self.config.BROWSER_PATH
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                
                self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
            
            elif self.config.BROWSER in ["chrome", "brave"]:
                if self.config.USE_UNDETECTED:
                    import threading
                    
                    console.print(f"[dim]Initializing Undetected {browser_name} (Stall fallback active)...[/dim]")
                    
                    self.driver = None
                    init_error = None
                    
                    def init_uc():
                        nonlocal self, init_error
                        try:
                            kwargs = {}
                            if self.config.BROWSER_PATH:
                                kwargs["browser_executable_path"] = self.config.BROWSER_PATH
                            self.driver = uc.Chrome(**kwargs)
                        except Exception as e:
                            init_error = e

                    thread = threading.Thread(target=init_uc, daemon=True)
                    thread.start()
                    thread.join(timeout=20) # 20 second timeout for stealth mode

                    if thread.is_alive() or not self.driver:
                        console.print(f"[yellow]⚠️ Undetected {browser_name} is taking too long or failed.[/yellow]")
                        console.print("[yellow]Switching to Standard compatibility mode for reliability...[/yellow]")
                        self.start_standard_chrome()
                    elif init_error:
                        console.print(f"[yellow]⚠️ Stealth mode error: {init_error}[/yellow]")
                        self.start_standard_chrome()
                else:
                    self.start_standard_chrome()
            else:
                console.print(f"[red]Unsupported browser type: {self.config.BROWSER}[/red]")
                self.start_standard_chrome()

            if not self.driver:
                raise Exception("Failed to initialize any browser driver.")

            # Navigate to DeepSeek
            console.print(f"[cyan]🌐 Navigating to {self.config.DEEPSEEK_URL}...[/cyan]")
            self.driver.get(self.config.DEEPSEEK_URL)
            time.sleep(self.config.PAGE_LOAD_WAIT)
            
            # Check for CAPTCHA
            self.check_for_captcha()
            
            console.print("[green]✓ Browser ready![/green]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Critical Error starting browser: {e}[/bold red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise

    def start_standard_chrome(self):
        """Fallback to standard Selenium Chrome driver using built-in Selenium Manager"""
        try:
            console.print("[dim]Accessing standard browser engine...[/dim]")
            options = webdriver.ChromeOptions()
            if self.config.BROWSER_PATH:
                console.print(f"[dim]Setting binary path: {self.config.BROWSER_PATH}[/dim]")
                options.binary_location = self.config.BROWSER_PATH
            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Selenium 4.6.0+ has a built-in Selenium Manager that handles driver discovery automatically.
            # We don't need ChromeDriverManager().install() which often has connection issues.
            console.print("[dim]Connecting to browser (using Selenium Manager)...[/dim]")
            self.driver = webdriver.Chrome(options=options)
            console.print("[dim]Browser engine connected.[/dim]")
        except Exception as e:
            console.print(f"[red]Failed standard fallback: {e}[/red]")
            console.print("[yellow]Attempting one last legacy method...[/yellow]")
            try:
                # Last resort: try to use ChromeDriverManager but skip SSL if possible
                import os
                os.environ['WDM_SSL_VERIFY'] = '0'
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e2:
                raise Exception(f"All browser startup methods failed. Error: {e2}")

    def wait_for_login(self):
        """Wait for user to login manually"""
        console.print(Panel(
            "Please log in to your DeepSeek account in the browser window.\n"
            "Once you are logged in and see the chat interface, come back here.",
            title="Manual Login Required",
            style="yellow"
        ))
        input("Press ENTER here AFTER you have logged in to continue...")
        console.print("[green]✓ Login confirmed. Stabilizing...[/green]")
        
        # Wait for the main UI to be ready rather than a fixed sleep
        self.wait_for_element(self.config.SELECTORS["chat_input"], timeout=20)
        
        # Scroll to ensure elements are in view and trigger any lazy loads
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            pass
        time.sleep(1) # Minimal settle time
    
    def check_for_captcha(self):
        """Check for CAPTCHA and pause if found"""
        try:
            # First, check if input box is present. If it is, we are likely NOT in a captcha
            input_exists = self.driver.find_elements(By.CSS_SELECTOR, self.config.SELECTORS["chat_input"])
            if input_exists and input_exists[0].is_displayed():
                return False

            # Check for specific Captcha/Cloudflare indicators
            # These are much more reliable than scanning all text
            captcha_selectors = [
                "iframe[src*='captcha']",
                "iframe[src*='challenges']",
                ".g-recaptcha",
                "#cf-challenge",
                "#turnstile-wrapper",
                "div[id*='captcha']"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(e.is_displayed() for e in elements):
                    self.trigger_manual_captcha_pause()
                    return True

            # If no specific selectors found, do a PRECISE keyword scan
            # only if we don't see the chat input
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            captcha_keywords = [
                "recaptcha", "i am not a robot", 
                "verify you are human", "security check",
                "robot verification", "human verification"
            ]
            
            # Note: "captcha" and "challenge" removed as they are too common in page text/scripts
            
            for keyword in captcha_keywords:
                if keyword in page_text:
                    self.trigger_manual_captcha_pause()
                    return True
            
            return False
            
        except Exception as e:
            console.print(f"[dim]CAPTCHA check error: {e}[/dim]")
            return False

    def trigger_manual_captcha_pause(self):
        """Standard prompt for manual captcha resolution"""
        console.print("[bold red]🔴 CAPTCHA DETECTED![/bold red]")
        console.print(Panel(
            "Please solve the CAPTCHA manually in the browser window.\n"
            "The script will wait for you to complete it.",
            title="Manual Intervention Required",
            style="yellow"
        ))
        input("Press ENTER here AFTER you've solved the CAPTCHA to continue...")
        time.sleep(2)
    
    def wait_for_element(self, selector, timeout=10):
        """Wait for element to be present and visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except:
            return None

    def safe_interact(self, selector, action="click", value=None, timeout=10):
        """Perform an action with retry for stale elements or interceptions. Returns the element on success."""
        for attempt in range(3):
            try:
                # Always clear modals before interacting
                self.close_modals()
                
                element = self.wait_for_element(selector, timeout)
                if not element:
                    if attempt < 2: continue
                    return None

                if action == "click":
                    try:
                        element.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", element)
                elif action == "type":
                    if value is not None:
                        # Clear first
                        try:
                            element.clear()
                        except:
                            element.send_keys(Keys.CONTROL + "a")
                            element.send_keys(Keys.BACKSPACE)
                        
                        # Optimization for speed and reliability:
                        # Use JS to set the value directly for longer strings
                        if len(value) > 20:
                             # ADVANCED: Use the "native value setter" trick to bypass React/Vue state management
                             # This is the most reliable way to paste large amounts of text into modern web apps
                             self.driver.execute_script("""
                                var el = arguments[0];
                                var text = arguments[1];
                                el.focus();
                                
                                // Try to find the native setter for the 'value' property 
                                // (Works for React, Vue, and plain JS)
                                var nativeSetter = Object.getOwnPropertyDescriptor(
                                    window.HTMLTextAreaElement.prototype, 'value'
                                ).set;
                                
                                if (nativeSetter) {
                                    nativeSetter.call(el, text);
                                } else {
                                    el.value = text;
                                }
                                
                                // Trigger standard events
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('blur', { bubbles: true }));
                             """, element, value)
                             time.sleep(0.5)
                        else:
                            # Short strings: Standard typing
                            element.send_keys(value)
                return element
            except Exception as e:
                if attempt < 2:
                    console.print(f"[dim]Note: Element state updated, retrying interaction ({attempt+1})...[/dim]")
                    time.sleep(1)
                else:
                    console.print(f"[red]Interaction failure: {e}[/red]")
        return None
    
    def send_message(self, message):
        """Send a message to DeepSeek and return response"""
        console.print(f"[yellow]💬 Sending message ({len(message)} chars)...[/yellow]")
        
        # 1. Type the message
        input_box = self.safe_interact(self.config.SELECTORS["chat_input"], action="type", value=message)
        
        if input_box:
            try:
                # Small breathe time for UI to register
                time.sleep(0.5)
                
                # Verification: Ensure input content is actually there
                actual_val = self.driver.execute_script("return arguments[0].value;", input_box)
                if not actual_val or len(actual_val.strip()) == 0:
                    console.print("[yellow]⚠️ Paste verification failed. Falling back to char-by-char typing...[/yellow]")
                    input_box.clear()
                    for char in message:
                        input_box.send_keys(char)
                        if len(message) > 500: # Very slow for very long ones
                            time.sleep(0.01)
                    time.sleep(1)
                
                # 2. Try to click the send button first (more reliable in some 2026 UI versions)
                send_btns = self.driver.find_elements(By.CSS_SELECTOR, self.config.SELECTORS["send_button"])
                sent = False
                
                if send_btns and any(b.is_displayed() for b in send_btns):
                    for btn in send_btns:
                        if btn.is_displayed():
                            try:
                                btn.click()
                                sent = True
                                break
                            except:
                                self.driver.execute_script("arguments[0].click();", btn)
                                sent = True
                                break
                
                # 3. Fallback to Enter key on the original input box if button click failed/missing
                if not sent:
                    try:
                        input_box.send_keys(Keys.RETURN)
                    except:
                        # Re-find as last resort
                        self.driver.find_element(By.CSS_SELECTOR, self.config.SELECTORS["chat_input"]).send_keys(Keys.RETURN)
                
                console.print("[dim]Message sent, waiting for response...[/dim]")
                
                # Before waiting, capture the current state as a "baseline" 
                # to avoid returning old responses when reusing chats
                baseline_text = self.get_last_response()
                
                # Wait for response to start
                time.sleep(2)
                
                # Wait for response to complete, passing the baseline
                return self.wait_for_response(baseline=baseline_text)
            except Exception as e:
                console.print(f"[red]Failed to finalize message send: {e}[/red]")
        else:
            console.print("[red]❌ Could not find chat input to send message.[/red]")
        
        return ""
    
    def wait_for_response(self, timeout=300, baseline=None): # Increased total timeout but faster polling
        """Wait for DeepSeek to complete its response with adaptive speed"""
        console.print("[dim]Waiting for DeepSeek to respond...[/dim]")
        
        start_time = time.time()
        last_length = 0
        stable_count = 0
        poll_interval = 0.5 # Default fast polling
        
        # If we have a baseline, we are looking for a DIFFERENT response or a NEW one
        has_baseline = baseline is not None and len(baseline.strip()) > 0
        
        while time.time() - start_time < timeout:
            try:
                # Detect current state from UI
                # Stop button usually means it's still generating
                stop_btns = self.driver.find_elements(By.CSS_SELECTOR, self.config.SELECTORS["stop_button"])
                is_thinking = any(btn.is_displayed() for btn in stop_btns)
                
                # Regenerate button usually means it's finished
                regen_btns = self.driver.find_elements(By.CSS_SELECTOR, self.config.SELECTORS["regenerate_button"])
                is_done = any(btn.is_displayed() for btn in regen_btns)
                
                # Get current response text
                current_response = self.get_last_response()
                
                # If we have a baseline and the current response is the same as the baseline,
                # it means the AI hasn't started its NEW response yet.
                if has_baseline and current_response == baseline:
                    # If we find a stop button, it probably means it HAS started 
                    # but the text hasn't changed yet (or we are in a new block)
                    if not is_thinking:
                        # Logic: stay in loop as if no response found yet
                        current_response = None
                
                if current_response and len(current_response.strip()) > 0:
                    current_length = len(current_response)
                    
                    # If regenerate button appears and stop button is gone, we are 100% finished
                    if is_done and not is_thinking:
                        # One final verification: if we have a baseline, the response MUST be different 
                        # or significantly longer (unless AI just said "Okay" or something)
                        if has_baseline and current_response == baseline:
                             # Old response found, still waiting for new one
                             pass
                        else:
                            console.print(f"[green]✓ AI finished processing ({current_length} chars)[/green]")
                            return current_response

                    # Fallback to stability check: if length hasn't changed in several fast checks
                    if current_length == last_length and not is_thinking:
                        stable_count += 1
                        # If AI isn't "thinking" (stop button gone) and text is stable for 3 seconds (6 polls)
                        if stable_count > 6:  
                            if has_baseline and current_response == baseline:
                                # This is still the old response, don't return it!
                                stable_count = 0
                            else:
                                console.print(f"[green]✓ Response stable ({current_length} chars)[/green]")
                                return current_response
                    else:
                        stable_count = 0
                        # If AI is thinking or text is changing, keep polling fast
                        poll_interval = 0.5
                    
                    last_length = current_length
                
                # Dynamic polling: if we haven't seen any NEW output yet, wait slightly longer
                if not current_response or (has_baseline and current_response == baseline):
                    poll_interval = 1.0
                
                # Check for CAPTCHA during response
                self.check_for_captcha()
                
                time.sleep(poll_interval)
                
            except Exception as e:
                # Silently catch minor browser hiccups, but log major ones
                if "Read timed out" in str(e):
                    console.print("[red]❌ Browser engine hung. Retrying...[/red]")
                    raise e
                time.sleep(1)
        
        console.print("[yellow]⚠️ Response timeout - returning captured text[/yellow]")
        return self.get_last_response()
    
    def get_last_response(self):
        """Get DeepSeek's last response using advanced JS extraction"""
        try:
            # JavaScript approach is more robust than CSS selectors alone
            # It finds the last markdown block associated with a copy button
            js_script = """
            const copyButtons = Array.from(document.querySelectorAll("button")).filter(b => 
                b.innerText.includes("Copy") || 
                b.getAttribute("title")?.includes("Copy") ||
                b.innerHTML.includes("copy")
            );
            
            if (copyButtons.length > 0) {
                // Get the last copy button (most recent response)
                const lastBtn = copyButtons[copyButtons.length - 1];
                
                // Usually the markdown is a sibling or in a parent container nearby
                let container = lastBtn.closest('.message-container') || 
                                lastBtn.closest('.ds-message') || 
                                lastBtn.parentElement;
                
                const markdown = container.querySelector('.ds-markdown, .markdown');
                if (markdown) return markdown.innerText;
            }
            
            // Fallback to standard selector hunt if JS copy-button logic fails
            const selectors = [
                ".ds-markdown.ds-markdown--block",
                ".ds-markdown",
                "div.markdown",
                ".assistant-message"
            ];
            
            for (let s of selectors) {
                const elements = document.querySelectorAll(s);
                if (elements.length > 0) {
                    return elements[elements.length - 1].innerText;
                }
            }
            return null;
            """
            
            result = self.driver.execute_script(js_script)
            if result and len(result.strip()) > 10:
                self.last_response = result.strip()
                return self.last_response
                
        except Exception as e:
            console.print(f"[dim]JS Extraction Error: {e}[/dim]")
            
        # Last-resort Python fallback
        try:
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, self.config.SELECTORS["last_response"])
            if response_elements:
                text = response_elements[-1].text
                if text and len(text.strip()) > 10:
                    self.last_response = text
                    return self.last_response
        except:
            pass
            
        return self.last_response
    
    def close_modals(self):
        """Find and close any blocking modals or overlays with minimal impact"""
        modal_selectors = [
            ".ds-modal-wrapper",
            ".ds-dialog__close",
            "button[aria-label='Close']",
            ".ds-icon--close"
        ]
        
        found_any = False
        for selector in modal_selectors:
            try:
                modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for modal in modals:
                    if modal.is_displayed():
                        if not found_any:
                            console.print(f"[dim]Attempting to clear overlays...[/dim]")
                            found_any = True
                        
                        try:
                            # Use JS click for speed and to avoid "element not interactable"
                            self.driver.execute_script("arguments[0].click();", modal)
                        except:
                            pass
            except:
                pass
        
        if found_any:
            time.sleep(0.5) # Short wait for UI to update

    def start_new_chat(self):
        """Start a fresh conversation"""
        console.print("[cyan]🔄 Starting new conversation...[/cyan]")
        self.close_modals()
        
        try:
            # Try multiple selectors for new chat
            selectors = [
                self.config.SELECTORS["new_chat_button"],
                "a[href='/']",
                "[data-testid='new-chat-button']",
                ".ds-icon--plus",
                "div[title='New Chat']"
            ]
            
            button_found = False
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    try:
                        elements[0].click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elements[0])
                    button_found = True
                    time.sleep(3)
                    break
            
            if not button_found:
                # Alternative: refresh the page
                console.print("[yellow]New chat button not found, refreshing page...[/yellow]")
                self.driver.get(self.config.DEEPSEEK_URL)
                time.sleep(self.config.PAGE_LOAD_WAIT)
            
            # CRITICAL: Wait for input to be ready after new chat/refresh
            console.print("[dim]Waiting for chat interface to ready...[/dim]")
            if not self.wait_for_element(self.config.SELECTORS["chat_input"], timeout=15):
                console.print("[yellow]⚠️ Warning: Chat input didn't appear in 15s. Retrying navigation...[/yellow]")
                self.driver.get(self.config.DEEPSEEK_URL)
                self.wait_for_element(self.config.SELECTORS["chat_input"], timeout=15)
            
        except Exception as e:
            console.print(f"[red]Error starting new chat: {e}[/red]")
            # Fallback: just refresh
            self.driver.refresh()
            time.sleep(5)
    
    def take_screenshot(self, filename):
        """Take screenshot for debugging"""
        try:
            self.driver.save_screenshot(filename)
            console.print(f"[dim]Screenshot saved: {filename}[/dim]")
        except:
            pass
    
    def close(self):
        """Close the browser gracefully"""
        if self.driver:
            try:
                console.print("[dim]Closing browser...[/dim]")
                self.driver.quit()
                console.print("[green]✓ Browser closed[/green]")
            except (OSError, Exception) as e:
                # Catch WinError 6 and other shutdown artifacts
                console.print(f"[dim]Note: Browser cleanup finished with minor system artifact: {e}[/dim]")
            finally:
                self.driver = None
