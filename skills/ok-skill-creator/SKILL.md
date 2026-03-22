---
name: ok-skill-creator
description: agents-settings/skills 配下で Codex/Copilot 互換の Agent Skill を作成・更新するときに使う。この skill は一般的な skill 設計の置き換えではなく、system の skill-creator に agents-settings 固有の運用ルールを重ねる policy overlay として使う。
compatibility: codex,copilot
---

# OK Skill Creator

## 目的

`ok-skill-creator` は、一般的な skill 設計そのものを教え直すための skill ではない。  
まず system の `skill-creator` の原則に従い、その上に `agents-settings` 固有の配置・互換性・検証・同期ルールを追加するための policy overlay として使う。

`skill-creator` が利用できる場合は、その設計原則を優先する。  
`skill-creator` が利用できない場合のみ、この skill 単体で最低限の設計・実装・検証まで進める。

## Trigger Examples

- 「agents-settings に新しい skill を追加して」
- 「この repo の既存 skill を改善して」
- 「Codex/Copilot 互換で skill を作りたい」

## Overlay Contract

- 一般的な skill 設計原則は `skill-creator` を優先する。
- この skill は `agents-settings` で守るべき追加制約だけを扱う。
- `skill-creator` と矛盾しない限り、その内容を再説明しない。
- ユーザーに直接 CLI / スクリプト実行を要求しない。実行は常にエージェントが代行する。
- 状態変更を伴う操作（追加・更新・削除・有効化・無効化など）は、実行前に必ず1回の確認ターンを挟む。

## agents-settings 追加ルール

### 1. 作成先

- skill 作成先は `~/ghq/github.com/okash1n/agents-settings/skills` を優先する。
- 各エージェントの home 配下 `skills/` を直接編集しない。
- home 配下の `skills/` は repo 内 `codex/skills` `copilot/skills` を経由する前提で扱う。

### 2. 互換性

- frontmatter に `compatibility: codex,copilot` を入れる。
- Codex / Copilot で差分がある場合は本文で明記する。
- 特定エージェント専用の手順だけで完結させない。
- Codex/Copilot で同じ skill 名・同じ構造を前提にする。

### 3. 外部依存の扱い

- `references/source-manifest.json` は必須ではない。
- 長期追跡したい Web/API/仕様書など、再取得可能な外部一次情報を根拠として残したい場合にだけ任意で使う。
- 一時的なローカルパスや、このマシン固有の参照を根拠として manifest に記録する前提にはしない。
- 実装方式は毎回比較して選ぶ。候補は 公式CLI / SDK / 直接HTTP。
- 公式CLI が最適な場合は、直接インストールを既定にせず、まず `nix-home` の既存実装で Nix / Homebrew / 公式導線のどれを採っているか確認する。
- 外部 API 系の skill は、実装前に実 URL・実認証・最小リクエストでプリフライト疎通を行う。

### 4. 品質ゲート

- `SKILL.md` frontmatter を検証する。
- ディレクトリ名と skill 名の整合を検証する。
- `source-manifest` を使う場合は JSON 構造を検証する。
- `skills-ref validate` が使える場合は併用する。

### 5. 同期

- すぐ反映したい場合は repo ルートの `scripts/apply_symlinks.py` を使う。
- `make switch` は skill 配布の本線ではない。
- repo 管理の symlink 一覧は `symlinks.json` に置く。

## 最小フロー

1. `skill-creator` の原則に従って、発火条件、構造、必要リソースを決める。
2. 作成先を `agents-settings/skills` に固定する。
3. この repo の追加ルールに合わせて `SKILL.md`、`scripts/`、`references/`、`assets/` を整える。
4. 再利用価値の高い外部一次情報を根拠として残したい場合だけ `references/source-manifest.json` を作る。
5. `scripts/quick_validate.py` と、利用可能なら `skills-ref validate` で検証する。
6. すぐ使いたい場合だけ `scripts/apply_symlinks.py` で同期する。

## 完了条件

- 発火条件が具体的で判定可能
- `SKILL.md` frontmatter が妥当で、ディレクトリ名と一致
- `compatibility: codex,copilot` が入っている
- Codex / Copilot の扱いが本文に明記されている
- `source-manifest` を使う場合だけ、その内容が妥当である
- 公式CLI 採用時は、`nix-home` の既存導入方針と矛盾しない
- ユーザーに直接 CLI 実行を要求していない
- 検証が通っている

## 参照

- Agent Skills 仕様チェック: `references/agentskills-spec-checklist.md`
- agents-settings の運用メモ: `references/agents-settings-skills.md`
- source-manifest 形式: `references/source-manifest-format.md`
- 実装方式の選定: `references/implementation-strategy.md`
