"""Toy agent loop. Every step re-sends the whole transcript, so prompt size grows
linearly and total spend grows quadratically: a token cascade."""
import sys
import time

MAX_STEPS = 8          # last-resort guard
TOKEN_BUDGET = 6_000   # cumulative prompt tokens
REPEAT_LIMIT = 2       # identical tool calls allowed


def tokens(text: str) -> int:
    return len(text) // 4  # ~4 chars per token


def fake_model(step: int) -> tuple[str, str]:
    plan = [("search", "loop guards"), ("read", "docs/agents.md")]
    return plan[step] if step < len(plan) else ("search", "retry policy")  # stuck


def run(guarded: bool) -> tuple[int, int]:
    transcript, spent, calls = "SYSTEM: you are a helpful agent. " * 40, 0, {}
    for step in range(1, (MAX_STEPS if guarded else 12) + 1):
        prompt = tokens(transcript)
        spent += prompt
        call = fake_model(step - 1)
        calls[call] = calls.get(call, 0) + 1
        time.sleep(0.25)  # model latency
        print(f"step {step:>2}  prompt={prompt:>5}  spent={spent:>6}  -> {call[0]}({call[1]!r})")
        if guarded and calls[call] > REPEAT_LIMIT:
            print(f"GUARD  {call[0]}({call[1]!r}) repeated {calls[call]}x -> stop")
            return step, spent
        if guarded and spent > TOKEN_BUDGET:
            print(f"GUARD  spent {spent} > budget {TOKEN_BUDGET} -> stop")
            return step, spent
        transcript += f"TOOL {call[0]} -> " + "result text " * 60  # tool output appended
    print(f"HALT   step {step}: {'max steps' if guarded else 'demo cutoff, nothing stops it'}, spent={spent}")
    return step, spent


if __name__ == "__main__":
    guarded = "--no-guards" not in sys.argv
    steps, spent = run(guarded)
    if guarded:
        assert spent <= TOKEN_BUDGET and steps < MAX_STEPS, (steps, spent)
        print(f"PASS   stopped at step {steps}, spent {spent} <= budget {TOKEN_BUDGET}")
