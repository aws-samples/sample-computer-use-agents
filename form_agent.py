"""
Form Agent - Automated Form Filling Example

An agent that can navigate to web forms and fill them out automatically.
Demonstrates a common RPA-style use case for computer-use agents.

Prerequisites:
    pip install -r requirements.txt
    playwright install chromium

Learning objectives:
- Understand form automation with AI agents
- See how agents identify and interact with form fields
- Learn patterns for data entry automation
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


SYSTEM_PROMPT = """You are a form automation assistant.

When asked to fill a form:
1. If no browser session exists, create one
2. Navigate to the specified URL
3. Identify all form fields (inputs, textareas, selects, checkboxes)
4. Fill each field with the provided data
5. Review the filled form before submitting
6. Submit the form if requested
7. Confirm the result (success message, redirect, etc.)

Be careful with:
- Required fields (marked with * or 'required')
- Field validation (email format, phone numbers, etc.)
- CAPTCHA or bot detection (report if encountered)

Keep the browser session open for follow-up questions unless asked to close it.
Always describe what fields you find and what data you're entering."""


class FormAgent:
    """Manages browser lifecycle for form automation."""
    
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
        """Execute a form automation task. Output streams via the callback handler."""
        if self._needs_reinit():
            self._initialize()
        
        self.stream_handler.reset()
        self.agent(user_input)
        self._mark_session_used()


def main():
    """Run the form automation agent demo."""
    print("Form Automation Agent")
    print("=" * 40)
    print("This agent can fill out web forms automatically.")
    print("Type 'quit' to exit\n")

    print("Example: Try a test form")
    print("  'Go to https://httpbin.org/forms/post and fill the form with:")
    print("   Customer: Test User")
    print("   Telephone: 555-1234")
    print("   Email: test@example.com")
    print("   Comments: Automated test submission'")
    print("\nTip: You can paste multi-line prompts!\n")

    form_agent = FormAgent()

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
            form_agent.run(user_input)
            elapsed = time.time() - start_time
            print(f"\n({elapsed:.1f}s)\n")
        except Exception as e:
            print(f"\nError: {e}")
            print("Reinitializing browser...\n")
            form_agent._initialize()


if __name__ == "__main__":
    main()
