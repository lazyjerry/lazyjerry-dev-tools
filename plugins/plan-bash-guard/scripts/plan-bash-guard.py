#!/usr/bin/env python3
"""PreToolUse(Bash) hook：Plan Mode 下拒絕會觸發權限提示的 Bash 寫法。

攔截：變數賦值、$ / 反引號展開、for/while/until 迴圈、; 與 && 串接（換行視同 ;）。
放行：單一指令與 | 管線。非 plan 模式一律放行。
解析失敗時放行，避免 hook 本身擋住正常工作。

用法：由 Claude Code 在每次 Bash 工具呼叫前執行，從 stdin 讀 hook payload（JSON）。
      要拒絕時在 stdout 印出 permissionDecision=deny；放行時不輸出。
手動測試：
  echo '{"permission_mode":"plan","tool_input":{"command":"L=/a; ls $L"}}' | python3 plan-bash-guard.py
前置條件：python3（只用標準函式庫）。
"""
import json
import re
import sys

EXPAND_NEXT = re.compile(r"[A-Za-z_{(0-9@*#?!$-]")
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?\+?=")
LOOP_WORDS = {"for", "while", "until"}
# 這些字之後的下一個字仍可能是賦值（export L=...）
DECL_WORDS = {"export", "declare", "local", "readonly", "typeset"}

LABELS = {
    "assign": "變數賦值（如 L=\"...\"）",
    "expand": "變數或指令展開（$VAR、${...}、$(...)、反引號）",
    "loop": "for / while / until 迴圈",
    "chain": "; 或 && 串接（含多行指令）",
}


def find_issues(cmd):
    issues = set()
    quote = None
    word = ""
    cmd_start = True
    i, n = 0, len(cmd)

    def flush():
        nonlocal word, cmd_start
        if word and cmd_start:
            if word in LOOP_WORDS:
                issues.add("loop")
                cmd_start = False
            elif ASSIGN.match(word):
                issues.add("assign")
            elif word not in DECL_WORDS:
                cmd_start = False
        word = ""

    while i < n:
        c = cmd[i]
        nxt = cmd[i + 1] if i + 1 < n else ""

        if quote == "'":
            if c == "'":
                quote = None
            word += c
            i += 1
            continue

        if quote == '"':
            if c == "\\":
                word += c + nxt
                i += 2
                continue
            if c == '"':
                quote = None
            elif (c == "$" and EXPAND_NEXT.match(nxt)) or c == "`":
                issues.add("expand")
            word += c
            i += 1
            continue

        if c == "\\":
            word += c + nxt
            i += 2
            continue
        if c in "'\"":
            quote = c
            word += c
        elif (c == "$" and EXPAND_NEXT.match(nxt)) or c == "`":
            issues.add("expand")
            word += c
        elif c in " \t":
            flush()
        elif c in ";\n":
            flush()
            if cmd[i + 1:].strip():
                issues.add("chain")
            cmd_start = True
        elif c == "&":
            flush()
            if nxt == "&":
                issues.add("chain")
                i += 1
            cmd_start = True
        elif c in "|(":
            flush()
            if c == "|" and nxt == "|":
                i += 1
            cmd_start = True
        elif c == ")":
            flush()
        else:
            word += c
        i += 1

    flush()
    return issues


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if payload.get("permission_mode") != "plan":
        return
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    try:
        issues = find_issues(cmd)
    except Exception:
        return
    if not issues:
        return

    found = "、".join(LABELS[k] for k in ("assign", "expand", "loop", "chain") if k in issues)
    reason = (
        f"Plan Mode 禁止此 Bash 寫法：{found}。"
        "這類指令無法自動放行，會跳出權限提示。"
        "請改用 Read / Grep / Glob 原生工具（可在同一回合並行多個呼叫），"
        "或拆成單一指令、直接寫出相對路徑，不要用變數存路徑。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
