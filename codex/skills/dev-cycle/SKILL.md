---
name: dev-cycle
description: 設計から開発計画、PR 単位の開発、内部レビュー、マージまでを一気通貫で回す。00-review/ の状態から継続実行したいときや、多角的レビュー込みで自律開発サイクルを進めたいときに使う。
compatibility: codex
---

# Dev Cycle

設計 → 開発計画 → PR 単位の開発を一気通貫で回す。サブコマンドで特定フェーズだけを実行することも可能。

## 使い方

```text
dev-cycle                              → 00-review/ 内の状態から自動判断して続行
dev-cycle <topic>                      → design から全フェーズを通しで実行
dev-cycle design <topic>               → 設計だけ作る + 内部レビュー
dev-cycle plan <design-file>           → 開発計画だけ作る + 内部レビュー
dev-cycle run <plan-file> [PR-N]       → 指定 PR から開発サイクルを回す
```

## 初期化

すべてのサブコマンドの前に実行する:

1. `scripts/review_workspace.sh init` を実行する
2. helper が失敗したら停止し、失敗内容を報告する

helper の役割:

- プロジェクトルートに `00-review/` を作成する
- `.git/info/exclude` に `00-review/` がなければ追記する

## Phase A: Design（設計）

トリガー: `dev-cycle design <topic>` または `dev-cycle <topic>` の最初のステップ

### 手順

1. `00-review/` にコンテキスト調査の結果を整理する
2. 設計書を `00-review/<topic>-design.md` に作成する
   - 目的、制約、設計判断、エッジケース、リスクを含める
3. 共通手順「内部レビュー」を実行する
4. 指摘を修正し、全件クリアするまでループする
5. 設計書の最終版を保存する
6. `update_plan` で `Phase A: Design` を `completed` にし、`Phase B: Plan` を `in_progress` にして自動遷移する

出力: `00-review/<topic>-design.md`

## Phase B: Plan（開発計画）

トリガー: `dev-cycle plan <design-file>` または Phase A の完了後に自動遷移

### 手順

1. 設計書を読み、PR 分割・依存関係・リリース計画を策定する
2. 計画書を `00-review/<topic>-plan.md` に作成する
   - 各 PR の目的、変更対象、バージョン番号、依存、リスクを含める
3. 共通手順「内部レビュー」を実行する
4. 指摘を修正し、全件クリアするまでループする
5. 計画書の最終版を保存する
6. `update_plan` で `Phase B: Plan` を `completed` にし、Plan の結果から Phase C の PR 一覧 step を展開して Phase C に自動遷移する

出力: `00-review/<topic>-plan.md`

## Phase C: Run（PR 単位の開発サイクル）

トリガー: `dev-cycle run <plan-file> [PR-N]` または Phase B の完了後に自動遷移

計画書の各 PR に対して以下のサイクルを回す。PR 間でユーザーに確認せず一気に進める。

### C-1: 実装

1. 計画書から該当 PR のセクションを読み、変更内容・制約・依存を把握する
2. `update_plan` で当該 PR の Step（C-1〜C-8）を展開する
3. 作業ブランチを作成する
   - 命名規則は PR タイトルまたはリポジトリの既存慣習から導出する
4. PR 内のタスクを分解し、1 つずつ実装する
5. 各タスク完了時に lint / 検証を実行する
   - プロジェクトに応じて `shellcheck`, `tsc`, `eslint` など
6. 既存テストを実行し、リグレッションがないことを確認する

### C-2: 内部レビュー 1 周目

6. 共通手順「内部レビュー」を実行する
7. 全レビュー結果を集約し、指摘を一覧化する

### C-3: 1 周目の指摘修正

8. `CRITICAL` → `HIGH` → `MEDIUM` の順に修正する
   - `LOW` / `SUGGESTION` は判断して対応する
9. 修正ごとに lint + テストを再実行する

### C-4: PR 作成（Bot レビュー開始）

10. 変更をコミットする
    - リポジトリの運用に明確な別ルールがなければ Conventional Commits を優先する
11. PR を作成する
12. CHANGELOG エントリが必要な場合は、既存の運用に従って反映する
    - バージョン見出しへ直接書く運用があるならそれに従う
    - Unreleased 運用ならそれに従う

### C-5: 内部レビュー 2 周目以降（Bot レビューと並走）

13. Bot レビュー待ちの間に 2 周目の内部レビューを回す
14. 指摘があれば修正 → push → 再レビュー。指摘ゼロになるまでループする
15. 2 周目以降は、前周で修正した箇所に焦点を当てる

### C-6: Bot レビュー対応

16. Bot レビューのコメントを取得する
17. 各指摘に対応し、push する

### C-7: マージ & リリース

18. PR をマージする
    - 既存のリポジトリ運用がなければ squash merge を優先する
19. `main` を最新化する
20. リリースが必要な場合のみ、既存のリリース運用に従ってタグ作成や release を行う
    - 計画書にバージョン番号がある、または既存のリリース運用がある場合に限る

### C-8: 次の PR へ

21. 完了した PR の Step（C-1〜C-8）を plan から外し、親 step `Phase C: PR-N` を `completed` に畳む
22. 計画書の次の PR がある場合は、次 PR の Step を展開し、ユーザーに確認せず即座に C-1 に戻る
23. 計画書の全 PR が完了したら Phase D（アーカイブ）に進む

## Phase D: Archive（完了後のアーカイブ）

トリガー: 全 PR の完了後に自動実行

1. `00-review/archive/` がなければ作成する
2. 設計書と計画書を `00-review/archive/YYYY-MM-DD-<topic>/` に移動する
3. 完了報告をユーザーに出す

## 共通手順: 内部レビュー

全フェーズ (A/B/C) で共通の並列レビュー手順:

1. まず対象に応じて `N` 観点のレビュー観点集合を決める
2. `N` 観点の内部レビューサブエージェントを立て、各 agent に 1 観点だけを担当させる
3. 同じ `N` 観点でもう一度サブエージェントを立て、各 agent に `claude -p` を使った独立レビューを担当させる
4. 合計 `2N` 個のサブエージェントを 1 つのまとまりとして、可能な限り並列起動する
5. 全結果を集約し、指摘を severity (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `SUGGESTION`) 別に一覧化する
6. `CRITICAL` → `HIGH` → `MEDIUM` の順に修正し、再レビューする
7. 指摘ゼロになるまでループする

### `claude -p` レビュー lane のルール

- 親エージェントが直接 `claude -p` を叩いてはいけない。必ず review 用サブエージェント経由で実行する
- `claude -p` は実装委譲ではなく独立レビュー専用に使う
- 各 reviewer には 1 観点だけを渡す
- 必要最小限の文脈だけを渡す
- severity 付きの簡潔な指摘を返すよう求める
- 親エージェントが一括で全部レビューせず、観点ごとに分離された review lane を保つ

推奨コマンド形:

```bash
claude -p \
  --model claude-opus-4-6 \
  --permission-mode dontAsk \
  --add-dir . \
  "<担当観点に限定したレビュー依頼>"
```

### レビュー観点の例

対象に応じて調整するが、最低でも 3 観点以上を明示する。

| 対象 | 観点 |
|------|------|
| 設計書 | アーキテクチャ整合性、実現可能性、リスク網羅性、依存関係 |
| 計画書 | PR 境界の適切さ、依存順序、バージョニング、リスク評価 |
| コード | 正確性、エッジケース、セキュリティ、互換性、テスト品質、ドキュメント整合性 |

## 進行ルール

### `update_plan` によるチェーン駆動

各フェーズの完了時に「次フェーズの step を立てる」更新を行い、チェーンが途切れないようにする。

開始時に立てる step（Phase レベル）:

```text
- [in_progress] Phase A: Design
- [pending] Phase B: Plan
- [pending] Phase B 完了後: Plan の結果から Phase C の PR 一覧 step を展開
```

Phase B 完了時に展開する step:

```text
- [completed] Phase A: Design
- [completed] Phase B: Plan
- [pending] Phase C: PR-1 (<タイトル>)
- [pending] Phase C: PR-2 (<タイトル>)
- [pending] Phase C: PR-N (<タイトル>)
- [pending] Phase D: Archive
```

各 PR 開始時に展開する step:

```text
- [in_progress] PR-1 / C-1: 実装
- [pending] PR-1 / C-2: 内部レビュー
- [pending] PR-1 / C-3: 指摘修正
- [pending] PR-1 / C-4: PR 作成
- [pending] PR-1 / C-5: 内部レビュー 2 周目
- [pending] PR-1 / C-6: Bot レビュー対応
- [pending] PR-1 / C-7: マージ & リリース
- [pending] PR-1 / C-8: 完了した Step を畳み、次 PR の Step を展開
```

チェーンのポイント（3 箇所）:

1. Phase B 完了時 → Plan の結果から PR 一覧の step を立てる
2. 各 PR 開始時 → その PR の Step を展開する
3. C-8 → 完了した PR の Step を plan から外し、親 step を `completed` にし、次 PR の Step を展開する

フラット運用のルール:

- `PR-1 / C-1: 実装` のような prefix 付き step で表現する
- 完了した PR の C-1〜C-8 は plan から外し、親 step `Phase C: PR-N` だけを `completed` として残す
- plan は常時 15〜20 行程度に収まるよう維持する

### その他

- PR 間で止まらない。ユーザーに確認・報告・提案をせず、即座に次の PR の Phase C-1 に入る
- コンテキストが不足しそうな場合は自分で compact や要約を行う。ユーザーに判断を委ねない
- Bot レビューが来ていない場合はスキップして進む。後で来たら戻って対応する

## 注意事項

- `main` に直接コミットしない。必ず PR 経由
- `00-review/` は `.git/info/exclude` で除外し、リポジトリにコミットしない
- `claude -p` レビューは親エージェントが直接実行せず、必ずサブエージェント経由で委譲する
- 多角的レビューは必須機能であり、省略しない
