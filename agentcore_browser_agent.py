"""
AgentCore Browser Agent - Managed Browser Example

An agent that uses Amazon Bedrock AgentCore Browser for managed browser automation.
Provides live view, session recording, and enterprise security features.

Prerequisites:
    pip install -r requirements.txt
    
    AWS Setup:
    - Enable model access for Anthropic Claude in the Amazon Bedrock console
    - Attach IAM policy with bedrock-agentcore:*Browser* permissions
    - See: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-onboarding.html

Learning objectives:
- Understand managed browser automation with AgentCore
- See how to use live view and session recording
- Learn enterprise browser automation patterns
"""

import os
import sys
import time
from pathlib import Path

# Pin runtime artifacts to this lab's folder regardless of where the script
# was launched from. strands_tools.browser defaults to "./screenshots" (CWD
# relative), and strands_tools.use_computer hardcodes the same relative
# path. Without this, running the agent from elsewhere drops a screenshots/
# folder at that other location.
_LAB_DIR = Path(__file__).resolve().parent
os.chdir(_LAB_DIR)
os.environ["STRANDS_BROWSER_SCREENSHOTS_DIR"] = str(_LAB_DIR / "screenshots")

from shared.model import get_model, get_region
from shared.input_utils import get_multiline_input
from shared.streaming import StreamingCallbackHandler

# Apply nest_asyncio to allow nested event loops (required for AgentCore Browser)
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("Warning: nest-asyncio not installed. Run: pip install -r requirements.txt")

from strands import Agent
from strands.tools.executors.sequential import SequentialToolExecutor

# Import AgentCore Browser tool
try:
    from strands_tools.browser import AgentCoreBrowser
except ImportError:
    print("Error: Required packages not installed")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


# Region comes from the shared config (.env AWS_REGION, then the AWS profile).
# AgentCore Browser has no regional constraint beyond service availability.
AWS_REGION = get_region()

SYSTEM_PROMPT = """You are a web automation assistant using a managed browser.

When given a task:
1. Create a browser session if one doesn't exist
2. Navigate to the relevant website
3. Describe what you see on the page
4. Interact with elements as needed
5. Extract and summarize the requested information

Keep the browser session open for follow-up questions unless asked to close it.
Be concise in your responses."""


class AgentCoreBrowserAgent:
    """Manages AgentCore Browser lifecycle and agent interactions."""
    
    def __init__(self, region: str):
        self.region = region
        self.browser_tool = None
        self.agent = None
        # Streaming handler announces each browser action as the model decides
        # to take it (`[tool] browser`) and streams the model's narration.
        self.stream_handler = StreamingCallbackHandler()
        self._initialize()
    
    def _initialize(self):
        """Create fresh browser tool and agent."""
        self.browser_tool = AgentCoreBrowser(region=self.region)
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
    
    def run(self, user_input: str) -> None:
        """Execute a browser task. Output streams via the callback handler."""
        self.stream_handler.reset()
        self.agent(user_input)


def main():
    """Run the AgentCore browser agent demo."""
    print("AgentCore Browser Agent (Managed)")
    print("=" * 40)
    print(f"Region: {AWS_REGION}")
    print("\nThis agent uses a managed browser in AWS.")
    print("Type 'quit' to exit\n")

    # Initialize AgentCore Browser
    print("Initializing AgentCore Browser...")
    try:
        browser_agent = AgentCoreBrowserAgent(region=AWS_REGION)
    except Exception as e:
        print(f"Error initializing AgentCore Browser: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured")
        print("  2. IAM permissions for bedrock-agentcore:*Browser* actions")
        print("  3. Model access for Anthropic Claude enabled in the Bedrock console")
        return

    print("Browser initialized!")
    print("\nView live sessions at:")
    print(f"https://{AWS_REGION}.console.aws.amazon.com/bedrock-agentcore/home?region={AWS_REGION}#/browser\n")

    print("Example prompts to try:")
    print("  - Go to https://docs.aws.amazon.com and search for 'Bedrock'")
    print("  - Navigate to https://aws.amazon.com/bedrock and list the key features")
    print("\nTip: You can paste multi-line prompts!\n")

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
