"""
Test script: Claude Agent SDK + Anthropic PPTX Skill.

Uses the Agent SDK with the official Anthropic pptx skill to generate
a front page slide for a Maverx training, using the master template.
Tracks token usage and estimated cost.
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    AssistantMessage,
    TextBlock,
)

PROMPT = """\
Take the existing Maverx master template at master/maverx_master.pptx and produce \
a single-slide PowerPoint that contains ONLY slide 2 of that template (the "Agenda" \
slide), with its text rewritten.

Steps:
1. Start from master/maverx_master.pptx.
2. Keep only slide 2 (the Agenda slide); remove every other slide so the result is \
exactly 1 slide.
3. Rewrite the text on that slide with a fresh, sensible agenda for a Maverx training \
called "Mastering Prompt Engineering". Keep the Maverx house style intact — Space \
Grotesk for the title, Raleway for body text, primary color #0D006A (dark blue), \
accent #F59235 (orange). Preserve the slide's existing layout, fonts, sizes and \
positioning; only change the words.

Save the result to output/test_sdk_output.pptx.

The final file must be exactly 1 slide — the rewritten Agenda slide only.
"""

total_input_tokens = 0
total_output_tokens = 0


async def main():
    global total_input_tokens, total_output_tokens

    print("Claude Agent SDK + PPTX Skill test")
    print(f"API key: ...{os.environ.get('ANTHROPIC_API_KEY', 'NOT SET')[-8:]}")
    print("-" * 60)

    async for message in query(
        prompt=PROMPT,
        options=ClaudeAgentOptions(
            cwd=str(Path(__file__).parent),
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Skill"],
            permission_mode="bypassPermissions",
            setting_sources=["project"],
            skills=["pptx"],
            max_turns=30,
        ),
    ):
        if isinstance(message, AssistantMessage):
            if hasattr(message, "usage") and message.usage:
                total_input_tokens += message.usage.get("input_tokens", 0)
                total_output_tokens += message.usage.get("output_tokens", 0)
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print("-" * 60)
            print(f"Stop reason: {message.stop_reason}")
            if message.result:
                print(message.result)

    # Cost estimate (Claude Sonnet 4.6 pricing)
    # Input: $3/1M tokens, Output: $15/1M tokens
    input_cost = total_input_tokens * 3.0 / 1_000_000
    output_cost = total_output_tokens * 15.0 / 1_000_000
    total_cost = input_cost + output_cost

    print("\n" + "=" * 60)
    print("TOKEN USAGE & COST ESTIMATE")
    print(f"  Input tokens:  {total_input_tokens:,}")
    print(f"  Output tokens: {total_output_tokens:,}")
    print(f"  Est. cost:     ${total_cost:.4f}")
    print(f"    (input: ${input_cost:.4f} + output: ${output_cost:.4f})")
    print("=" * 60)

    out_path = Path(__file__).parent / "output" / "test_sdk_output.pptx"
    if out_path.exists():
        size_kb = out_path.stat().st_size / 1024
        print(f"\nSUCCESS: {out_path.name} created ({size_kb:.1f} KB)")
    else:
        print(f"\nFAILED: output file was not created")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
