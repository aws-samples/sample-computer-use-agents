"""
Test Examples - Interactive walkthrough of Computer-Use Agent patterns

Run this file to explore different browser automation approaches.

Prerequisites:
    pip install -r requirements.txt
    playwright install chromium
"""

import os
from pathlib import Path

# Pin runtime artifacts to this lab's folder regardless of where the script
# was launched from. strands_tools.browser defaults to "./screenshots"
# (CWD relative) and strands_tools.use_computer hardcodes the same path.
_LAB_DIR = Path(__file__).resolve().parent
os.chdir(_LAB_DIR)
os.environ["STRANDS_BROWSER_SCREENSHOTS_DIR"] = str(_LAB_DIR / "screenshots")

from shared.model import get_model, get_region
from shared.input_utils import get_multiline_input
from strands.tools.executors.sequential import SequentialToolExecutor


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_local_browser():
    """Test local browser automation with Playwright."""
    print_header("Local Browser Agent (Playwright)")
    
    try:
        from strands import Agent
        from strands_tools.browser import LocalChromiumBrowser
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nInstall required packages:")
        print("  pip install -r requirements.txt")
        print("  playwright install chromium")
        return False

    print("Creating agent with local browser tool...")
    browser_tool = LocalChromiumBrowser()
    agent = Agent(
        model=get_model(),
        system_prompt="You are a web assistant. Describe what you see on web pages.",
        tools=[browser_tool.browser],
        callback_handler=None,
        tool_executor=SequentialToolExecutor(),
    )

    print("Testing: Navigate to a simple page and describe it\n")
    
    try:
        response = agent("Go to https://quotes.toscrape.com and describe what you see")
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_agentcore_browser():
    """Test AgentCore Browser (managed browser in AWS)."""
    print_header("AgentCore Browser Agent (Managed)")
    
    try:
        from strands import Agent
        from strands_tools.browser import AgentCoreBrowser
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nInstall required packages:")
        print("  pip install -r requirements.txt")
        return False

    region = get_region()
    print(f"Using AWS region: {region}")
    print("Initializing AgentCore Browser...\n")

    try:
        browser_tool = AgentCoreBrowser(region=region)
        agent = Agent(
            model=get_model(),
            system_prompt="You are a web assistant using a managed browser.",
            tools=[browser_tool.browser],
            callback_handler=None,
            tool_executor=SequentialToolExecutor(),
        )

        print("Testing: Navigate to AWS docs\n")
        response = agent("Go to https://aws.amazon.com and describe the main heading")
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured")
        print("  2. IAM permissions for bedrock-agentcore:*Browser* actions")
        print("  3. Model access for Anthropic Claude enabled in the Bedrock console")
        return False


def test_form_filling():
    """Test form filling capabilities."""
    print_header("Form Filling Test")
    
    try:
        from strands import Agent
        from strands_tools.browser import LocalChromiumBrowser
    except ImportError:
        print("Required packages not installed. Skipping.")
        return False

    print("Creating form automation agent...")
    browser_tool = LocalChromiumBrowser()
    agent = Agent(
        model=get_model(),
        system_prompt="""You are a form automation assistant.
        Identify form fields and fill them with provided data.""",
        tools=[browser_tool.browser],
        callback_handler=None,
        tool_executor=SequentialToolExecutor(),
    )

    print("Testing: Navigate to a test form page\n")
    
    try:
        response = agent(
            "Go to https://httpbin.org/forms/post and describe the form fields you see"
        )
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_data_extraction():
    """Test web scraping capabilities."""
    print_header("Data Extraction Test")
    
    try:
        from strands import Agent
        from strands_tools.browser import LocalChromiumBrowser
    except ImportError:
        print("Required packages not installed. Skipping.")
        return False

    print("Creating scraper agent...")
    browser_tool = LocalChromiumBrowser()
    agent = Agent(
        model=get_model(),
        system_prompt="""You are a web scraping assistant.
        Extract data and return it in a structured format.""",
        tools=[browser_tool.browser],
        callback_handler=None,
        tool_executor=SequentialToolExecutor(),
    )

    print("Testing: Extract data from a sample site\n")
    
    try:
        response = agent(
            "Go to https://quotes.toscrape.com and extract the first 2 quotes with their authors"
        )
        print(f"Response: {response}\n")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run interactive test menu."""
    print("\n" + "=" * 60)
    print("  Computer-Use Agents - Test Examples")
    print("=" * 60)
    
    while True:
        print("\nSelect a test to run:")
        print("  1. Local Browser Agent (Playwright)")
        print("  2. AgentCore Browser Agent (AWS Managed)")
        print("  3. Form Filling Test")
        print("  4. Data Extraction Test")
        print("  5. Run All Tests")
        print("  q. Quit")
        
        choice = get_multiline_input("\nChoice: ").strip().lower()
        
        if choice == "1":
            test_local_browser()
        elif choice == "2":
            test_agentcore_browser()
        elif choice == "3":
            test_form_filling()
        elif choice == "4":
            test_data_extraction()
        elif choice == "5":
            print("\nRunning all tests...\n")
            results = {
                "Local Browser": test_local_browser(),
                "AgentCore Browser": test_agentcore_browser(),
                "Form Filling": test_form_filling(),
                "Data Extraction": test_data_extraction(),
            }
            print_header("Test Results")
            for test_name, passed in results.items():
                status = "✓ PASSED" if passed else "✗ FAILED"
                print(f"  {test_name}: {status}")
        elif choice in ["q", "quit", "exit"]:
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
