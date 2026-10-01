"""
Desktop Agent - Full Screen Control Example

An agent that can control your entire desktop—mouse, keyboard, screenshots,
and any application. Uses OCR to understand screen content.

Prerequisites:
    pip install -r requirements.txt
    
    # Install Tesseract OCR:
    # macOS: brew install tesseract
    # Linux: sudo apt-get install tesseract-ocr
    # Windows: https://github.com/UB-Mannheim/tesseract/wiki

Learning objectives:
- Understand full desktop automation with AI agents
- See how agents use OCR to interpret screen content
- Learn patterns for cross-application automation

Note: This agent requires screen recording permissions on macOS.
You may be prompted to grant access in System Preferences > Privacy & Security.
"""

import sys
import time
import os
from pathlib import Path

# Pin runtime artifacts to this lab's folder regardless of where the script
# was launched from. strands_tools.use_computer saves OCR screenshots to a
# hardcoded "./screenshots" relative path — without chdir, that folder
# lands wherever the user happened to be when they ran the script.
_LAB_DIR = Path(__file__).resolve().parent
os.chdir(_LAB_DIR)
os.environ["STRANDS_BROWSER_SCREENSHOTS_DIR"] = str(_LAB_DIR / "screenshots")

from shared.model import get_model
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler
from strands import Agent
from strands.tools.executors.sequential import SequentialToolExecutor

try:
    from strands_tools import use_computer
except ImportError:
    print("Error: strands-agents-tools not installed with use_computer support")
    print("Run: pip install -r requirements.txt")
    print("\nAlso install Tesseract OCR:")
    print("  macOS: brew install tesseract")
    print("  Linux: sudo apt-get install tesseract-ocr")
    sys.exit(1)


SYSTEM_PROMPT = """You are a desktop automation assistant with full control over the computer.

You can:
- analyze_screen: Capture screenshot and extract text with OCR (do this first!)
- click: Click at coordinates (x, y) with optional click_type (left, right, double)
- move_mouse: Move cursor to position
- drag: Click and drag from one point to another
- type: Type text at current cursor position
- key_press: Press a single key (enter, tab, escape, etc.)
- hotkey: Press key combinations (e.g., "cmd+c", "ctrl+v", "alt+tab")
- scroll: Scroll up/down/left/right at coordinates
- open_app: Open an application by name
- close_app: Close an application by name
- screen_size: Get screen dimensions

IMPORTANT WORKFLOW:
1. Always start by analyzing the screen to see what's visible
2. Use the OCR results to find element coordinates
3. Click on elements using their center coordinates from the analysis
4. After actions, analyze again to verify the result

When clicking UI elements:
- Use the center_x and center_y coordinates from analyze_screen results
- Provide app_name parameter to ensure the correct window has focus

Be careful and precise. Describe what you see and what you're doing."""


class DesktopAgent:
    """Manages desktop automation agent."""
    
    def __init__(self):
        # Streaming handler announces each `use_computer` action and streams
        # the model's narration as it analyses the screen and decides what
        # to do next.
        self.stream_handler = StreamingCallbackHandler()
        self.agent = Agent(
            model=get_model(),
            system_prompt=SYSTEM_PROMPT,
            tools=[use_computer],
            callback_handler=self.stream_handler,
            # Run desktop tool calls sequentially. The use_computer tool uses a
            # shared event loop with nest_asyncio; under Python 3.13 concurrent
            # tool calls raise "Leaving task X does not match the current task Y".
            tool_executor=SequentialToolExecutor(),
        )
    
    def run(self, user_input: str) -> None:
        """Execute a desktop automation task. Output streams via the callback handler."""
        self.stream_handler.reset()
        self.agent(user_input)


os.environ["BYPASS_TOOL_CONSENT"] = "true"

def main():
    """Run the desktop automation agent demo."""
    print("Desktop Automation Agent")
    print("=" * 40)
    print("This agent can control your entire desktop:")
    print("  - Mouse clicks and movement")
    print("  - Keyboard input and hotkeys")
    print("  - Screenshot and OCR analysis")
    print("  - Open and close applications")
    print("\nType 'quit' to exit\n")

    print("Example prompts to try:")
    print("  - Analyze the screen and tell me what you see")
    print("  - Open Calculator and compute 42 * 3")
    print("  - Take a screenshot and find all buttons")
    print("  - Open Notes and create a new note with today's date")
    print("\nTip: You can paste multi-line prompts!\n")

    desktop_agent = DesktopAgent()

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
            desktop_agent.run(user_input)
            elapsed = time.time() - start_time
            print(f"\n({elapsed:.1f}s)\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
