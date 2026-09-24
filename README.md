# lazyjerry-dev-tools

LazyJerry 的 Claude Code plugin 集合。整個 repo 就是一個 plugin marketplace，名稱也叫 `lazyjerry-dev-tools`。

plugin 和 skill 的差別在於 plugin 可以帶 hook：Claude Code 在事件發生時會直接執行 hook，規則能強制生效，不必靠模型自己遵守指示。

## 快速安裝

```sh
claude plugin marketplace add lazyjerry/lazyjerry-dev-tools
claude plugin install <plugin 名稱>@lazyjerry-dev-tools
```

裝好後重開 Claude Code。

在 Claude Code 對話裡，也可以先用 `/plugin marketplace add lazyjerry/lazyjerry-dev-tools` 加入 marketplace，再從 `/plugin` 選單挑要裝的 plugin。

## Plugin 清單與說明

有哪些 plugin、各自做什麼，以及更新、停用、移除和新增 plugin 的方法，都寫在 [plugins/README.md](plugins/README.md)。

## 目錄結構

```
.claude-plugin/marketplace.json   marketplace 清單
plugins/<名稱>/                    一個 plugin 一個目錄
  .claude-plugin/plugin.json      plugin 設定與版本號
  hooks/hooks.json                hook 設定
  scripts/                        hook 腳本
```
