# Claude Code plugins

給 Claude Code 用的 plugin。和 skill 不同，plugin 可以帶 hook，由 Claude Code 在事件發生時強制執行，不靠模型自己遵守指示。

整個 lazyjerry-dev-tools repo 就是一個 marketplace，名稱也是 `lazyjerry-dev-tools`，清單在 repo 根目錄的 [.claude-plugin/marketplace.json](../.claude-plugin/marketplace.json)。

## Plugin 清單

| Plugin | 類型 | 說明 |
|--------|------|------|
| [plan-bash-guard](plan-bash-guard/) | PreToolUse hook | Plan Mode 下拒絕會觸發權限提示的 Bash 寫法：變數賦值、`$`／反引號展開、`for`／`while`／`until` 迴圈、`;` 與 `&&` 串接（多行指令也算）。單一指令和 `\|` 管線照常放行，其他權限模式不受影響。被擋下時會要求模型改用 Read／Grep／Glob，或拆成單一指令並寫出相對路徑。需要 `python3`。 |

## 安裝

每台裝置做一次。在終端機執行：

```sh
claude plugin marketplace add lazyjerry/lazyjerry-dev-tools
claude plugin install plan-bash-guard@lazyjerry-dev-tools
```

在 Claude Code 對話裡也可以用 `/plugin marketplace add lazyjerry/lazyjerry-dev-tools` 加入 marketplace，再用 `/plugin` 選單挑要裝的 plugin。

裝好後重開 Claude Code，或在對話中開一次 `/hooks` 確認 hook 已載入。

### 從手動設定改用 plugin

如果這台裝置之前手動把 hook 寫進 `~/.claude/settings.json`，裝好 plugin 後要把手動那份移除，不然同一個檢查會跑兩次：

- 刪掉 `~/.claude/settings.json` 裡 `PreToolUse` 下 `matcher` 為 `Bash`、指令指向 `~/.claude/hooks/plan-bash-guard.py` 的那一組。
- 刪掉 `~/.claude/hooks/plan-bash-guard.py`。

### 推上 GitHub 前先在本機測

marketplace 可以直接指向本機目錄：

```sh
claude plugin marketplace add "/path/to/lazyjerry-dev-tools"
claude plugin install plan-bash-guard@lazyjerry-dev-tools
```

## 更新

```sh
claude plugin marketplace update lazyjerry-dev-tools
claude plugin update plan-bash-guard@lazyjerry-dev-tools
```

更新後要重開 Claude Code 才會生效。

## 停用與移除

```sh
claude plugin disable plan-bash-guard@lazyjerry-dev-tools     # 暫停，保留安裝
claude plugin uninstall plan-bash-guard@lazyjerry-dev-tools   # 移除
```

## 新增或修改 plugin

- 一個 plugin 一個目錄：`plugins/<名稱>/`，目錄名與 `.claude-plugin/plugin.json` 的 `name` 一致，用 kebab-case。
- Hook 設定放 `hooks/hooks.json`，腳本放 `scripts/`。hook 指令用 `${CLAUDE_PLUGIN_ROOT}` 指向腳本，不寫死絕對路徑。
- 腳本只用 Bash 或 Python（標準函式庫），不依賴要另外安裝的套件，其他裝置裝好 plugin 就能直接跑。
- 新增 plugin 後，在根目錄的 `.claude-plugin/marketplace.json` 的 `plugins` 補一筆，並在上方「Plugin 清單」補一列。
- 修改 plugin 後，把 `plugin.json` 的 `version` 往上調。各裝置靠版本號判斷有沒有更新，版本沒變就不會更新。
- 推上去前先跑 `claude plugin validate plugins/<名稱>` 與 `claude plugin validate .`。
