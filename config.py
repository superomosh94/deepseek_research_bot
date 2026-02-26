import os
from pathlib import Path

class Config:
    # DeepSeek website
    DEEPSEEK_URL = "https://chat.deepseek.com"
    
    # Browser settings
    HEADLESS = False  # Keep False so you can see and handle CAPTCHAs
    BROWSER = "chrome"
    BROWSER_PATH = None
    USE_UNDETECTED = True  # Avoid bot detection
    
    # Timing (seconds)
    PAGE_LOAD_WAIT = 5  # Initial wait before dynamic polling
    TYPING_DELAY = 0.03  # Slightly faster, more human-like "burst" speed
    BETWEEN_ACTIONS = 1
    SCROLL_DELAY = 0.5
    
    # Research settings
    MAX_ITERATIONS = 5  # Maximum refinement cycles
    MIN_QUALITY_SCORE = 0.8  # Stop when quality reaches this
    REUSE_CHAT = True  # Whether to reuse the same chat for multiple iterations
    MAX_MESSAGES_PER_CHAT = 15  # Limit messages per chat to avoid context length/lag issues
    
    # CAPTCHA handling
    PAUSE_ON_CAPTCHA = True
    CAPTCHA_TIMEOUT = 300  # 5 minutes max to solve CAPTCHA
    
    # Output
    OUTPUT_DIR = Path("research_output")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Selectors (DeepSeek UI - update if they change their site)
    SELECTORS = {
        "chat_input": "textarea#chat-input, textarea",
        "chat_input_container": ".ds-textarea-wrapper",
        "send_button": "button[type='submit']",
        "stop_button": "button[aria-label='Stop'], .ds-icon--stop",
        "regenerate_button": "button.ds-button--primary, [class*='regenerate']",
        "copy_button": "button[title*='Copy'], .ds-icon--copy",
        "response_area": ".ds-markdown, .markdown, .assistant-message",
        "last_response": ".ds-markdown:last-of-type, div.markdown:last-child",
        "new_chat_button": "a[href='/'], [data-testid='new-chat-button'], .ds-icon--plus",
        "user_message": ".user-message",
        "assistant_message": ".assistant-message",
        "typing_indicator": ".typing",
        "message_container": ".message-container"
    }
