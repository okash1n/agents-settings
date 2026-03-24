# /dev-cycle - 統合開発サイクル

設計 → 開発計画 → PR 単位の開発を一気通貫で回す。サブコマンドで特定フェーズだけを実行することも可能。

## 使い方

```
/dev-cycle                              → 00-review/ 内の状態から自動判断して続行
/dev-cycle <topic>                      → design から全フェーズを通しで実行
/dev-cycle design <topic>               → 設計だけ作る + 内部レビュー
/dev-cycle plan <design-file>           → 開発計画だけ作る + 内部レビュー
/dev-cycle run <plan-file> [PR-N]       → 指定 PR から開発サイクルを回す
```

## 初期化

**すべてのサブコマンドの前に実行する**:

1. プロジェクトルートに `00-review/` がなければ作成する
2. `.git/info/exclude` に `00-review/` がなければ追記する（リポジトリを汚さない）

---

## Phase A: Design（設計）

**トリガー**: `/dev-cycle design <topic>` または `/dev-cycle <topic>` の最初のステップ

### 手順

1. `00-review/` にコンテキスト調査の結果を整理する
2. 設計書を `00-review/<topic>-design.md` に作成する
   - 目的、制約、設計判断、エッジケース、リスクを含める
3. **内部並列レビュー**を実行する（→ 共通手順「内部レビュー」参照）
4. 指摘を修正し、全件クリアするまでループする
5. 設計書の最終版を保存する

**出力**: `00-review/<topic>-design.md`

6. TodoWrite で `[x] Phase A: Design` にし、Phase B に自動遷移する

---

## Phase B: Plan（開発計画）

**トリガー**: `/dev-cycle plan <design-file>` または Phase A の完了後に自動遷移

### 手順

1. 設計書を読み、PR 分割・依存関係・リリース計画を策定する
2. 計画書を `00-review/<topic>-plan.md` に作成する
   - 各 PR の目的、変更対象、バージョン番号、依存、リスクを含める
3. **内部並列レビュー**を実行する（→ 共通手順「内部レビュー」参照）
4. 指摘を修正し、全件クリアするまでループする
5. 計画書の最終版を保存する

**出力**: `00-review/<topic>-plan.md`

6. TodoWrite で `[x] Phase B: Plan` にし、Plan の結果から Phase C の PR 一覧 Todo を展開して Phase C に自動遷移する

---

## Phase C: Run（PR 単位の開発サイクル）

**トリガー**: `/dev-cycle run <plan-file> [PR-N]` または Phase B の完了後に自動遷移

計画書の各 PR に対して以下のサイクルを回す。PR 間でユーザーに確認せず一気に進める。

### C-1: 実装

1. 計画書から該当 PR のセクションを読み、変更内容・制約・依存を把握する
2. TodoWrite で当該 PR の Step Todo（C-1〜C-8）を展開する
3. 作業ブランチを作成する（命名規則: PR タイトルから導出）
4. 各タスク完了時に lint/検証を実行する（プロジェクトに応じて `shellcheck`, `tsc`, `eslint` 等）
5. 既存テストを実行し、リグレッションがないことを確認する

### C-2: 内部レビュー 1 周目

6. **内部並列レビュー**を実行する（→ 共通手順「内部レビュー」参照）
7. 全レビュー結果を集約し、指摘を一覧化する

### C-3: 1 周目の指摘修正

8. CRITICAL → HIGH → MEDIUM の順に修正する（LOW/SUGGESTION は判断して対応）
9. 修正ごとに lint + テストを再実行する

### C-4: PR 作成（Bot レビュー開始）

10. 変更をコミットする（Conventional Commits 形式）
11. PR を作成する（Bot レビューが自動開始される）
12. CHANGELOG エントリをバージョン見出し (`## [x.y.z]`) に直接書く（Unreleased は使わない）

### C-5: 内部レビュー 2 周目以降（Bot レビューと並走）

13. Bot レビュー待ちの間に 2 周目の内部レビューを回す
14. 指摘があれば修正 → push → 再レビュー。**指摘ゼロになるまでループ**する
15. 2 周目以降は、前周で修正した箇所に焦点を当てる

### C-6: Bot レビュー対応

16. Bot レビューのコメントを取得する (`gh api repos/.../pulls/.../comments`)
17. 各指摘に対応し、push する

### C-7: マージ & リリース

18. `gh pr merge <number> --squash --delete-branch` でマージする
19. `git checkout main && git pull` で main を最新化する
20. **リリースが必要な場合のみ** (計画書にバージョン番号がある、または既存のリリース運用がある場合):
    - バージョンタグを作成して push する: `git tag v<x.y.z> && git push origin v<x.y.z>`
    - GitHub Release を作成する: `gh release create v<x.y.z> --title "v<x.y.z>" --notes "<CHANGELOG 該当セクション>"`
    - リリース運用がないリポジトリではスキップする

### C-8: 次の PR へ

22. 完了した PR の Step Todo（C-1〜C-8）を削除し、親タスク `[x] Phase C: PR-N` に畳む
23. 計画書の次の PR がある場合: 次 PR の Step Todo を展開し、**ユーザーに確認せず即座に C-1 に戻る**
24. 計画書の全 PR が完了したら Phase D（アーカイブ）に進む

---

## Phase D: Archive（完了後のアーカイブ）

**トリガー**: 全 PR の完了後に自動実行

1. `00-review/archive/` がなければ作成する
2. 設計書と計画書を `00-review/archive/YYYY-MM-DD-<topic>/` に移動する
3. 完了報告をユーザーに出す

---

## 共通手順: 内部レビュー

**全フェーズ (A/B/C) で共通の並列レビュー手順**:

1. **N 観点の内部レビューサブエージェント** (code-reviewer 等): 対象に応じた観点で検証
2. **N 観点の Codex 委譲サブエージェント** (general-purpose → mcp__codex__codex): 同数のサブエージェントを立て、各自が Codex MCP にレビューを委譲する
3. 合計 2N 個のサブエージェントを **1 つのメッセージで並列起動** する
4. 全結果を集約し、指摘を severity (CRITICAL/HIGH/MEDIUM/LOW/SUGGESTION) 別に一覧化する
5. CRITICAL → HIGH → MEDIUM の順に修正し、再レビュー → **指摘ゼロまでループ**

**レビュー観点の例** (対象に応じて調整):

| 対象 | 観点 |
|------|------|
| 設計書 | アーキテクチャ整合性、実現可能性、リスク網羅性、依存関係 |
| 計画書 | PR 境界の適切さ、依存順序、バージョニング、リスク評価 |
| コード | Shell 正確性、エッジケース、セキュリティ、互換性、テスト品質、ドキュメント整合性 |

---

## 進行ルール

### TodoWrite によるチェーン駆動

各フェーズの完了時に「次フェーズの Todo を立てる」Todo を仕込み、チェーンが途切れないようにする。

**開始時に立てる Todo（Phase レベル）**:

```
- [ ] Phase A: Design
- [ ] Phase B: Plan
- [ ] Phase B 完了後: Plan の結果から Phase C の PR 一覧 Todo を展開
```

**Phase B 完了時に展開**:

```
- [x] Phase A: Design
- [x] Phase B: Plan
- [ ] Phase C: PR-1 (<タイトル>)
- [ ] Phase C: PR-2 (<タイトル>)
- [ ] Phase C: PR-N (<タイトル>)
- [ ] Phase D: Archive
```

**各 PR 開始時に Step を展開**:

```
- [ ] C-1: 実装
- [ ] C-2: 内部レビュー
- [ ] C-3: 指摘修正
- [ ] C-4: PR 作成
- [ ] C-5: 内部レビュー 2 周目
- [ ] C-6: Bot レビュー対応
- [ ] C-7: マージ & リリース
- [ ] C-8: 完了した Step を畳み、次 PR の Step を展開
```

**チェーンのポイント（3 箇所）**:

1. **Phase B 完了時** → Plan の結果から PR 一覧の Todo を立てる
2. **各 PR 開始時** → その PR の Step Todo を展開する
3. **C-8** → 完了した PR の Step を畳んで親を `[x]` にし、次 PR の Step を展開する（＝ 2 に戻る）

**畳みルール**: 完了した PR の C-1〜C-8 は削除し、親タスク `[x] Phase C: PR-N` だけ残す。これにより TodoWrite は常時 15〜20 行程度に収まる。

### その他

- **PR 間で止まらない**。ユーザーに確認・報告・提案をせず、即座に次の PR の Phase C-1 に入る
- **コンテキストが不足しそうな場合は自分で `/compact` する**。ユーザーに判断を委ねない
- **Bot レビューが来ていない場合はスキップして進む**。Bot レビューは非同期で来るので、待たずに次の PR に進んでよい。来たら戻って対応する

---

## 注意事項

- main に直接コミットしない。必ず PR 経由
- Codex レビューは直接 MCP を叩かず、サブエージェント経由で委譲する
- PR 間で確認を入れず、計画書の最後まで一気に回す
- 各 PR のバージョン番号は計画書に従う
- `00-review/` は `.git/info/exclude` で除外し、リポジトリにコミットしない
