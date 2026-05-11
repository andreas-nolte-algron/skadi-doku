#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

if ! echo "$COMMAND" | grep -qE 'git\s+commit'; then
  exit 0
fi

MARKER="$CLAUDE_PROJECT_DIR/.git/commit-via-skill"

if [[ -f "$MARKER" ]]; then
  rm -f "$MARKER"
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
EOF
else
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Commit blockiert: Nutze /save statt manuellem git commit."}}
EOF
fi
