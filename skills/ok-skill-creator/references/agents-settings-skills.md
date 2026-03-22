# agents-settings での Agent Skill 運用

## ソース管理場所

- `~/ghq/github.com/okash1n/agents-settings/skills/<skill-name>/`

## エージェント別 skills ディレクトリ

- `~/ghq/github.com/okash1n/agents-settings/codex/skills/<skill-name>`
- `~/ghq/github.com/okash1n/agents-settings/copilot/skills/<skill-name>`

各 `ok-*` は上記から共通ソース `skills/<skill-name>` を指す symlink として置く。

## ホーム配下の同期先

- `~/.codex/skills -> ~/ghq/github.com/okash1n/agents-settings/codex/skills`
- `~/.copilot/skills -> ~/ghq/github.com/okash1n/agents-settings/copilot/skills`

## 推奨フロー

- 即時反映: `../../scripts/apply_symlinks.py`
- `symlinks.json` に repo 管理の symlink 一覧を明示し、`scripts/apply_symlinks.py` が `ok-*` symlink の生成と home 配下 `skills` の差し替えを担当する
- `nix-home` の `make switch` は skill 配布を担当しない

## 依存ツール方針

- Skill 実装で公式CLIを使う場合、グローバル導入方法は `nix-home` の既存方針に合わせる。
- Nix 追加が適切なケースでは attr 探索は `ok-search`、導入は `ok-install` を使う。
- `npm -g` / `pip install` / `go install` / `cargo install` / `brew install` / `curl | sh` を、その場しのぎのグローバル導入手段として勝手に実行しない。

## 安全ルール

- 同名の通常ファイル/通常ディレクトリは上書きしない。
- 既存 `~/.{agent}/skills` が通常ディレクトリの場合は中身を repo 側 `*/skills` へ移してから symlink に置き換える。
- `skills` 配下の skill は Codex/Copilot 共通利用を前提に設計する。
