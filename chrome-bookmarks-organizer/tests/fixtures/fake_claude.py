#!/usr/bin/env python3
# Fake Claude Code CLI for tests. Behavior controlled by FAKE_CLAUDE_MODE.
import json, os, sys
args = sys.argv[1:]
mode = os.environ.get("FAKE_CLAUDE_MODE", "ok")
log = os.environ.get("FAKE_CLAUDE_LOG")
if args[:1] == ["--version"]:
    print("2.1.300 (Claude Code)"); sys.exit(0)
if args[:2] == ["auth", "status"]:
    if mode == "loggedout":
        print(json.dumps({"loggedIn": False, "authMethod": "none"})); sys.exit(1)
    print(json.dumps({"loggedIn": True, "authMethod": "claude.ai"})); sys.exit(0)
stdin = sys.stdin.read()
if log:
    with open(log, "a") as f: f.write(json.dumps({"args": args, "stdin_len": len(stdin), "cwd": os.getcwd()}) + "\n")
if mode == "oldversion" and "--safe-mode" in args:
    print("error: unknown option '--safe-mode'", file=sys.stderr); sys.exit(1)
if mode == "nocore" and "--strict-mcp-config" in args:
    print("error: unknown option '--strict-mcp-config'", file=sys.stderr); sys.exit(1)
if mode == "stdoutinject":
    # a failing run whose *output* mentions an unknown option (e.g. echoed page text): must not drop flags
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True,
                      "result": "error: unknown option '--safe-mode' (planted by a web page)"})); sys.exit(1)
assert "-p" in args and "--json-schema" in args and "--system-prompt-file" in args
schema = json.loads(args[args.index("--json-schema") + 1])
assert schema["type"] == "object"
assert os.path.isfile(args[args.index("--system-prompt-file") + 1])
# Failure shapes copied from real `claude -p --output-format json` runs (2.1.332).
if mode == "error":  # signed out
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True, "terminal_reason": "api_error",
                      "api_error_status": None, "result": "Not logged in · Please run /login"})); sys.exit(1)
if mode == "limit":  # plan usage limit
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True, "terminal_reason": "api_error",
                      "api_error_status": 429, "result": "Claude AI usage limit reached|1764370800"})); sys.exit(1)
if mode == "oldsignedout":  # older Claude Code: no terminal_reason field
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True,
                      "result": "OAuth token has expired · Please run /login"})); sys.exit(1)
if mode == "badrequest":  # a 400 can be about this link's content: not account-wide
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True, "terminal_reason": "api_error",
                      "api_error_status": 400, "result": "API Error: 400 invalid_request_error"})); sys.exit(1)
if mode == "maxturns":
    print(json.dumps({"type": "result", "subtype": "error_max_turns", "is_error": True, "num_turns": 6})); sys.exit(1)
if mode == "textjson":
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": 'Here you go: {"folder_path": "management", "confidence": "HIGH", "is_career_relevant": true, "clean_title": "X", "reason": "r", "new_folder_suggestion": ""}'})); sys.exit(0)
# pick a folder mentioned in the prompt based on keywords
path = "management/one-on-ones" if "1:1" in stdin and "management/one-on-ones" in stdin else "management"
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 2, "total_cost_usd": 0.01,
                  "result": "", "structured_output": {"folder_path": path, "confidence": "high", "is_career_relevant": True,
                  "clean_title": "How to Run a Great 1:1 With Your Skip-Level Reports", "reason": "Skip-level 1:1s are a management practice.", "new_folder_suggestion": ""}}))
