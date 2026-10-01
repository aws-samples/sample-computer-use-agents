"""
Playwright Agent - Local Browser Example

An agent that uses a local browser to navigate websites and extract information.
Uses the strands-agents-tools LocalChromiumBrowser with Playwright.

Prerequisites:
    pip install -r requirements.txt
    playwright install chromium

Learning objectives:
- Understand browser automation with AI agents
- See how agents interpret and interact with web pages
- Learn the browser tool's capabilities

Note: The browser window is managed by Playwright. If you manually close the 
browser window, it may remain in your dock until you exit the agent (type 'quit').
This is normal Playwright behavior - the browser process is tied to this script.
"""

import os
import sys
import time
from pathlib import Path

# Pin runtime artifacts to this lab's folder regardless of where the script
# was launched from. strands_tools.browser defaults to "./screenshots"
# (CWD relative); without this, running the agent from elsewhere drops a
# screenshots/ folder at that other location.
_LAB_DIR = Path(__file__).resolve().parent
os.chdir(_LAB_DIR)
os.environ["STRANDS_BROWSER_SCREENSHOTS_DIR"] = str(_LAB_DIR / "screenshots")

from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent
from strands.tools.executors.sequential import SequentialToolExecutor

try:
    from strands_tools.browser import LocalChromiumBrowser
except ImportError:
    print("Error: strands-agents-tools not installed")
    print("Run: pip install -r requirements.txt")
    print("Then: playwright install chromium")
    sys.exit(1)


SYSTEM_PROMPT = """You are a web research assistant with browser access.

When given a task:
1. If no browser session exists, create one
2. Navigate to the relevant website
3. Describe what you see on the page
4. Interact with elements as needed (click, type, scroll)
5. Extract and summarize the requested information

IMPORTANT: Keep the browser session open after completing tasks so you can handle 
follow-up questions. Only close the session if the user explicitly asks you to 
close the browser.

Be concise in your responses. Focus on answering the user's question."""


class BrowserAgent:
    """Manages browser lifecycle and agent interactions."""
    
    def __init__(self):
        self.browser_tool = None
        self.agent = None
        self._had_session = False
        # Streaming handler announces each browser action (`[tool] browser`)
        # and streams the model's narration token-by-token.
        self.stream_handler = StreamingCallbackHandler()
        self._initialize()
    
    def _initialize(self):
        """Create fresh browser tool and agent."""
        self.browser_tool = LocalChromiumBrowser()
        self.agent = Agent(
            model=get_model(),
            system_prompt=SYSTEM_PROMPT,
            tools=[self.browser_tool.browser],
            callback_handler=self.stream_handler,
            # Run browser tool calls sequentially. strands_tools.browser uses a
            # shared event loop with nest_asyncio; under Python 3.13 concurrent
            # tool calls raise "Leaving task X does not match the current task Y".
            tool_executor=SequentialToolExecutor(),
        )
        self._had_session = False
    
    def _needs_reinit(self) -> bool:
        """Check if browser needs reinitialization."""
        if self.browser_tool is None or self.agent is None:
            return True
        
        # Check if agent closed the session
        if hasattr(self.browser_tool, '_sessions'):
            if len(self.browser_tool._sessions) == 0 and self._had_session:
                return True
        
        # Check if browser disconnected (user closed window)
        if hasattr(self.browser_tool, '_browser') and self.browser_tool._browser:
            try:
                if not self.browser_tool._browser.is_connected():
                    return True
            except Exception:
                return True
        
        return False
    
    def _mark_session_used(self):
        """Track that a session has been created."""
        if hasattr(self.browser_tool, '_sessions') and len(self.browser_tool._sessions) > 0:
            self._had_session = True
    
    def run(self, user_input: str) -> None:
        """Execute a browser task, reinitializing if needed. Streams via callback handler."""
        if self._needs_reinit():
            self._initialize()
        
        self.stream_handler.reset()
        self.agent(user_input)
        self._mark_session_used()


def main():
    """Run the browser agent demo."""
    print("Playwright Agent (Local Browser)")
    print("=" * 40)
    print("This agent can navigate websites, click elements,")
    print("fill forms, and extract information.")
    print("Type 'quit' to exit\n")

    print("Example prompts to try:")
    print("  - Go to https://wikipedia.org and describe the featured article")
    print("  - Navigate to https://books.toscrape.com and list the first 3 book titles")
    print("  - Go to https://quotes.toscrape.com and extract the first 2 quotes")
    print("  - Close the browser (then ask a new question to start fresh)\n")
    print("Tip: You can paste multi-line prompts!\n")

    browser_agent = BrowserAgent()

    while True:
        user_input = get_multiline_input("You: ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            print("\nAgent: ", end="", flush=True)
            start_time = time.time()
            browser_agent.run(user_input)
            elapsed = time.time() - start_time
            print(f"\n({elapsed:.1f}s)\n")
        except Exception as e:
            print(f"\nError: {e}")
            print("Reinitializing browser...\n")
            browser_agent._initialize()


if __name__ == "__main__":
    main()
