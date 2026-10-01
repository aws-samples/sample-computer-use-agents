"""
Scraper Agent - Web Data Extraction Example

An agent that can navigate websites and extract structured data.
Demonstrates web scraping patterns with AI-driven navigation.

Prerequisites:
    pip install -r requirements.txt
    playwright install chromium

Learning objectives:
- Understand web scraping with AI agents
- See how agents extract and structure data
- Learn patterns for handling pagination and dynamic content
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


SYSTEM_PROMPT = """You are a web scraping assistant.

When asked to extract data:
1. If no browser session exists, create one
2. Navigate to the target website
3. Identify the data structure (lists, tables, cards, etc.)
4. Extract the requested information
5. Return data in a clean, structured format (JSON when appropriate)

Handle common challenges:
- Pagination: Navigate through pages if needed
- Dynamic content: Wait for elements to load
- Infinite scroll: Scroll to load more content
- Rate limiting: Be respectful of the website

Keep the browser session open for follow-up questions unless asked to close it.

Always describe:
- What page structure you observe
- How many items you found
- Any issues encountered (missing data, blocked, etc.)"""


class ScraperAgent:
    """Manages browser lifecycle for web scraping."""
    
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
        
        if hasattr(self.browser_tool, '_sessions'):
            if len(self.browser_tool._sessions) == 0 and self._had_session:
                return True
        
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
        """Execute a scraping task. Output streams via the callback handler."""
        if self._needs_reinit():
            self._initialize()
        
        self.stream_handler.reset()
        self.agent(user_input)
        self._mark_session_used()


def main():
    """Run the web scraper agent demo."""
    print("Web Scraper Agent")
    print("=" * 40)
    print("This agent can extract structured data from websites.")
    print("Type 'quit' to exit\n")

    print("Example prompts to try:")
    print("  - Go to https://books.toscrape.com and extract the first 5 book titles and prices")
    print("  - Navigate to https://quotes.toscrape.com and get the first 3 quotes with authors")
    print("\nTip: You can paste multi-line prompts!\n")

    scraper_agent = ScraperAgent()

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
            scraper_agent.run(user_input)
            elapsed = time.time() - start_time
            print(f"\n({elapsed:.1f}s)\n")
        except Exception as e:
            print(f"\nError: {e}")
            print("Reinitializing browser...\n")
            scraper_agent._initialize()


if __name__ == "__main__":
    main()
