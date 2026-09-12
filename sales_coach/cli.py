from __future__ import annotations

import argparse
import os
import sys

from .llm import AnthropicChatClient
from .models import Scenario
from .session import PracticeSession
from .storage import ScenarioStore, save_transcript

DEFAULT_SCENARIOS_DIR = "scenarios"
DEFAULT_OUT_DIR = "out/transcripts"


def _build_chat_client(args: argparse.Namespace) -> AnthropicChatClient:
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("error: no API key found. Pass --api-key or set ANTHROPIC_API_KEY.", file=sys.stderr)
        raise SystemExit(1)
    return AnthropicChatClient(model=args.model, api_key=api_key)


def _create_scenario_interactively() -> Scenario:
    print("Let's set up a scenario. Press enter to skip a field.")
    name = input("Scenario name: ").strip() or "Untitled scenario"
    product = input("What are you selling (product/service)? ").strip()
    persona = input("Who is the customer? (age, situation, mindset) ").strip()
    traits = input("Personality traits (comma-separated, e.g. 'skeptical, chatty'): ").strip()
    objections = input("Objections to focus on (comma-separated, e.g. 'price, needs to think about it'): ").strip()
    difficulty = input("Difficulty (easy/medium/hard) [medium]: ").strip() or "medium"
    goal = input("What does success look like for this scenario? ").strip()
    return Scenario(
        name=name,
        product_or_service=product,
        customer_persona=persona,
        personality_traits=[t.strip() for t in traits.split(",") if t.strip()],
        objections_focus=[o.strip() for o in objections.split(",") if o.strip()],
        difficulty=difficulty,
        goal=goal,
    )


def cmd_scenarios_list(args: argparse.Namespace) -> int:
    store = ScenarioStore(args.scenarios_dir)
    names = store.list()
    if not names:
        print(f"No scenarios saved in {args.scenarios_dir}/")
        return 0
    for name in names:
        print(name)
    return 0


def cmd_scenarios_create(args: argparse.Namespace) -> int:
    store = ScenarioStore(args.scenarios_dir)
    scenario = _create_scenario_interactively()
    path = store.save(scenario)
    print(f"Saved scenario to {path}")
    return 0


def cmd_practice(args: argparse.Namespace) -> int:
    store = ScenarioStore(args.scenarios_dir)
    if args.scenario:
        scenario = store.load(args.scenario)
    else:
        scenario = _create_scenario_interactively()
        if args.save:
            path = store.save(scenario)
            print(f"Saved scenario to {path}")

    chat_client = _build_chat_client(args)
    session = PracticeSession(scenario, chat_client)

    print(f"\n=== Practicing: {scenario.name} ===")
    if scenario.goal:
        print(f"Goal: {scenario.goal}")
    print("Type your side of the conversation. Commands: /hint  /feedback  /end  /quit\n")

    opening = session.opening_line()
    print(f"Customer: {opening}\n")

    while True:
        try:
            line = input("You: ").strip()
        except EOFError:
            line = "/end"

        if not line:
            continue
        if line == "/quit":
            print("Ending practice without feedback.")
            return 0
        if line == "/end":
            print("\n--- Coaching feedback ---")
            print(session.feedback())
            path = save_transcript(session.transcript, args.out_dir)
            print(f"\nTranscript saved to {path}")
            return 0
        if line == "/hint":
            print(f"\nCoach: {session.hint()}\n")
            continue
        if line == "/feedback":
            print(f"\nCoach (so far): {session.feedback()}\n")
            continue

        reply = session.say(line)
        print(f"Customer: {reply}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales_coach",
        description="Practice retail sales conversations with an AI customer and get coaching feedback.",
    )
    parser.add_argument("--model", default="claude-sonnet-5", help="Anthropic model to use")
    parser.add_argument("--api-key", default=None, help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)")
    parser.add_argument("--scenarios-dir", default=DEFAULT_SCENARIOS_DIR, help="Directory of saved scenario JSON files")
    sub = parser.add_subparsers(dest="command", required=True)

    p_practice = sub.add_parser("practice", help="Start an interactive practice session.")
    p_practice.add_argument("--scenario", default=None, help="Name of a saved scenario to load; omit to build one interactively")
    p_practice.add_argument("--save", action="store_true", help="Save an interactively-built scenario for reuse")
    p_practice.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Where to save the transcript and feedback")
    p_practice.set_defaults(func=cmd_practice)

    p_scenarios = sub.add_parser("scenarios", help="Manage saved scenarios.")
    scenarios_sub = p_scenarios.add_subparsers(dest="scenarios_command", required=True)
    p_list = scenarios_sub.add_parser("list", help="List saved scenarios.")
    p_list.set_defaults(func=cmd_scenarios_list)
    p_create = scenarios_sub.add_parser("create", help="Interactively create and save a new scenario.")
    p_create.set_defaults(func=cmd_scenarios_create)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
