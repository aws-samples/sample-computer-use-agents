# Agents That Use Computers: Browsers, Desktops, and the GUI Frontier

*Let an agent operate the same software a person does by seeing the user's screen and interacting with browsers or applications*

---

This is the fourth post in our series on [AWS Prescriptive Guidance for Agentic AI Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/). Each post focuses on the concepts and patterns behind a single agent type, paired with a [hands-on sample on GitHub](README.md).

## Introduction

So far in this series, our agents have acted through clean interfaces: text, function tools, and tool servers.

But most software was built for *people*, not programs. There's no simple method to "click the export button in this dashboard" or "fill out this legacy web form." A **computer-use agent** can. It operates a browser or desktop the way a human would, looking at the screen, deciding what to do, and moving the mouse and keyboard to do it. The agent becomes a proxy that acts inside interfaces designed for humans.

By the end of this post, you'll understand:
- What makes computer use different from calling a tool
- How an agent perceives a screen and decides what to do
- The trade-offs between a local browser, a managed browser, and full desktop control
- When operating a GUI is the right approach and when it isn't

---

## The Road to Computer Use: A Brief History

Automating human interfaces isn't new. What's new is doing it with reasoning instead of brittle scripts.

### Scripted automation and RPA

For decades, the way to automate a GUI was to script it. Robotic process automation (RPA) industrialized this for the enterprise. It worked, but it was fragile. If you move a button, rename a field, or change a layout, the script broke. The automation had no understanding of what it was looking at; it only knew "click at (420, 315)."

### Vision-language models change the input

Vision-language models (VLMs) or LLMs that accept images alongside text, let a system look at a screenshot and reason about it. Suddenly an agent could find an element by what it *is* rather than where it sits, which is far more robust and dependable

### Computer use as a first-class capability (2024)

In October 2024, [Anthropic introduced computer use](https://www.anthropic.com/news/3-5-models-and-computer-use), letting a model interpret a screen and emit actions as structured output. It reframed GUI automation as a reasoning problem rather than a scripting one. Cloud platforms followed with managed environments for running these agents safely; on AWS, [Amazon Bedrock AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) provides a managed browser with a live view and session recording, so an agent can drive a real browser without one running on your laptop.

---

## What Makes Computer Use Different

<img src="images/computer-use-agents.png" width="600" alt="Diagram of a computer-use agent: a query and visual context feed an LLM that reasons and invokes browser, shell, and editor tools on a tool server, updating memory and visual inputs in a loop before returning a response." />

A tool-calling agent works with structured inputs and outputs: it calls `get_weather("Seattle")` and gets back clean JSON. A computer-use agent works with a *picture of a screen* and a set of low-level actions. That changes the loop in two ways.

**First**, perception is visual and approximate. The agent observes the screen through a VLM, sometimes with OCR to read text and has to infer what's actionable. **Second**, action is indirect. Instead of returning a value, the agent moves a cursor, clicks coordinates, types keystrokes, then *looks again* to see whether the action worked. Observe, act, re-observe: the agent closes the loop visually because the interface gives no structured confirmation.

Memory matters more here, too. Multi-step GUI tasks require the agent to track where it is and what it has already done, because the screen alone doesn't always tell it.

---

## Three Ways to Operate a Computer

The pattern spans a spectrum from a contained browser to your entire desktop, trading convenience for reach.

| Approach | Scope | Runs where | Best for |
|----------|-------|------------|----------|
| **Local browser** | One browser | Your machine | Development, web research, scraping, form-filling |
| **Managed browser** | One browser | AWS, managed | Enterprise workflows needing audit, recording, and scale |
| **Full desktop** | Any application | Your machine | Cross-app automation beyond the browser |

A **local browser** is the easiest place to start. The agent drives a window directly on your machine. A **managed browser** moves that browser into the cloud, adding a live view, session recording, and the isolation enterprises need. **Full desktop control** is the most powerful and the most consequential: the agent reads the whole screen and drives the mouse and keyboard across any application, which means it can do real damage if it goes wrong.

---

## When to Use Computer-Use Agents

Reach for a computer-use agent when the system you need to operate has no usable API and was built for a human.

| Use Case | Example |
|----------|---------|
| **Developer agents** | Writing and running code in an IDE |
| **Repetitive digital workflows** | Moving data between apps that don't integrate |
| **Software testing / QA** | Simulated users exercising a UI |
| **Accessibility** | Navigating interfaces from high-level or voice instructions |
| **Smart RPA** | Reasoning-enhanced automation that adapts when the UI shifts |

### When to Use Something Else

If there's an API, use it. Computer use is the approach of last resort. It's powerful precisely because it works when nothing else can, but slower and more fragile than a clean integration. And because a desktop agent can take destructive, unattended actions, keep it sandboxed and put a human in the loop for anything consequential.

---

## What's Next

You now understand how an agent perceives and operates a human interface, why vision-language models made that practical, and how local, managed, and desktop approaches trade off. The natural next step is to see it run. The **[companion sample](README.md)** drives a local Chromium browser, a managed AgentCore browser, and the full desktop.

Computer-use agents are general operators. But some work calls for an agent that specializes in one craft, for example writing software. In the [next post](https://github.com/aws-samples/sample-coding-agents/blob/main/Coding%20Agents%20-%20From%20Autocomplete%20to%20Autonomous%20Software%20Work.md), we'll explore coding agents that generate, review, and refactor code.

---

## Resources

- [Companion sample: Computer-Use Agents](README.md)
- [AWS Prescriptive Guidance - Computer-use agents](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/computer-use-agents.html)
- [Amazon Bedrock AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [Strands Agents Documentation](https://strandsagents.com/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)

---

**Tim Sitze** is a Solutions Architect at Amazon Web Services, where he works with cybersecurity ISVs to design and scale their products on AWS. He specializes in security, AI/ML, IoT and data platform architectures, and has partnered on workloads spanning identity threat intelligence, agentic AI, and cloud-native security operations. Tim is based in the Washington, D.C. area.  
