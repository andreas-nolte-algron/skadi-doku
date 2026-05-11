#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
CWD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null)

if echo "$COMMAND" | grep -qE 'git\s+(commit|push)'; then
  OUR_REPO="$(cd "$CLAUDE_PROJECT_DIR" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)"
  TARGET_REPO="$(cd "$CWD" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)"

  if [[ -n "$OUR_REPO" && -n "$TARGET_REPO" && "$OUR_REPO" != "$TARGET_REPO" ]]; then
    # Fresh repo (no commits) = build-team creating new team → allow
    TARGET_HAS_COMMITS=$(cd "$CWD" 2>/dev/null && git rev-parse --verify HEAD 2>/dev/null)
    [[ -z "$TARGET_HAS_COMMITS" ]] && exit 0

    cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"BLOCKED: Git commit/push in fremdem Repo ($TARGET_REPO). User pusht selbst."}}
EOF
    exit 0
  fi
fi
exit 0
