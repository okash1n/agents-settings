---
name: ok-install
description: nix-home で Nix 管理のグローバルCLIを追加・適用・検証する。ユーザーが「Nix で入れて」「caddy や marp を追加して switch までして」など、Nix 側へ追加したい依頼をしたときに使う。~/nix-home/modules/home/base.nix を更新し、make build と make switch、command -v 検証まで実行する。
compatibility: codex,copilot
---

# OK Install

## 目的

`~/nix-home` の Nix 管理に追加したい CLI について、以下を1回の流れで完了する。

1. package 追加
2. `make build`
3. `make switch`
4. 動作確認

## 前提

- `~/nix-home` が存在する。
- `make build` / `make switch` が使える。
- macOS の権限要件（App Management など）で `switch` が止まる可能性を考慮する。
- Homebrew や npm global を使う既存運用のツール追加には使わない。導入経路が未確定なら、先に repo の実装と README を確認する。

## 手順

### 1. 追加対象を決める

- パッケージは `pkgs` セットに追加する（例: `caddy`, `marp-cli`）。

### 2. package を追加する

```bash
scripts/install_tool.sh --attr <nix-attr> --verify <command-name>
```

複数コマンド検証:

```bash
scripts/install_tool.sh --attr marp-cli --verify marp
```

AI CLI を追加する場合の例:

```bash
scripts/install_tool.sh --attr codex --verify codex
```

### 3. 失敗時の扱い

- `make switch` が権限エラー（App Management）で失敗したら、権限付与を案内して再実行する。
- `attr` が誤っている場合は、代替 `attr` を特定してから再実行する。
- 既に追加済みなら、重複追加せず build/switch/verify だけ行う。

## 品質チェック

- `modules/home/base.nix` に重複がない。
- `make build` が成功する。
- `make switch` が成功する。
- `command -v <verify>` が成功する。

## 実装補助

- package 追加ロジック: `scripts/add_package.py`
- 一括実行: `scripts/install_tool.sh`
- 対象ファイル: `~/nix-home/modules/home/base.nix`
