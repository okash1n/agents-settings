# agents-settings

AI エージェント向けの静的設定ファイルと共通 skill を管理するリポジトリ。

repo 管理の symlink は `symlinks.json` に明示し、`scripts/apply_symlinks.py` で適用する。

## 管理対象

- `codex/`
- `copilot/`
- `skills/`

## 方針

- `~/.codex` `~/.copilot` にある runtime state は Git 管理しない。
- Git 管理するのは、各エージェントの静的設定ファイルと共通 skill の実体だけに限定する。
- ホーム配下には file 単位または skill ディレクトリ単位の symlink として配布する。

## 共通 skill の同期

共通 skill は `skills/` に置く。
各エージェントの共通 skill は `codex/skills` `copilot/skills` から参照し、
各 `ok-*` は repo 直下の `skills/` を指す symlink として管理する。
ホーム配下の `~/.codex/skills` `~/.copilot/skills` は
それぞれ対応する repo 内 `*/skills` への symlink にする。

home 配下の file symlink、`skills` ディレクトリ差し替え、共通 skill の agent 別展開は、次を使う。

```bash
python3 scripts/apply_symlinks.py
```

管理境界:

- `symlinks.json` に載っているものだけが repo 管理の symlink
- `*/skills` 配下の `ok-*` は repo 管理の共通 skill
- `codex/skills/.system` や `kb-*`、`copilot/skills/ok-mcp-toggle` など manifest にないものは local runtime state として扱い、Git 追跡しない
