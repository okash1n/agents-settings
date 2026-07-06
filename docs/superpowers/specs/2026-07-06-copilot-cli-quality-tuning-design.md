# Copilot CLI 品質・検証チューニング 設計

- 日付: 2026-07-06
- ステータス: ユーザー承認済み（実装前）
- 対象: `okash1n/agents-settings` の `copilot/`（`~/.copilot` へ symlink 配備）
- 参考元: `cloudnative-co/claude-code-starter-kit`

## 背景と目的

GitHub Copilot CLI を本格利用するにあたり、claude-code-starter-kit が Claude Code に提供している品質向上の仕組みを Copilot CLI に移植する。スコープは以下で合意済み。

- 対象サーフェス: Copilot CLI のみ（VS Code Copilot Chat・Copilot coding agent は対象外）
- 重視点: 品質・検証の徹底（ガードレール・三者整合・コマンド体験は主目的にしない）
- 移植範囲: コア検証系のみ（tdd-workflow / security-review の移植、verify 強化、共通指示の規範強化）
- アプローチ: skill 移植 + 規範追記 + 設定基盤の是正

## 前提調査の要点（2026-07-06 時点）

実機は Copilot CLI 1.0.68（2026-02-25 GA）。設計判断に効く事実は次のとおり。

1. skill は `~/.copilot/skills/<name>/SKILL.md` に置き、frontmatter は `name` / `description` / `allowed-tools` / `argument-hint`（v1.0.64）等をサポートする。`/skill-name` でスラッシュ起動でき、description による自動マッチも効く。ユーザー定義 slash command 機構は無いため、コマンド体験は skill で代替する。
2. v1.0.35（2026-04）でユーザー設定は `~/.copilot/settings.json` に分離され、`config.json` は「CLI が自動管理する内部状態」になった。実機に `settings.json` が存在しないため、現在 `config.json` に書かれている `model: "claude-opus-4.6-fast"` と `effortLevel: "high"` は効いていない可能性が高い。
3. `effortLevel` は `low | medium | high | xhigh`（v1.0.60 以降、Anthropic モデルには max 相当の最上位もある）。
4. CLI ビルトインに `/review` `/security-review`、code-review / rubber-duck サブエージェントが存在する。starter kit の security-review 移植はビルトインの置き換えではなく、チェックリスト知識ベースとしての補完と位置づける。
5. hooks の正式な置き場は `settings.json` の `hooks` キーまたは `~/.copilot/hooks/*.json`。イベント名は camelCase（`sessionEnd` 等）。

出典: docs.github.com の Copilot CLI config-dir reference / add-skills / use-hooks / hooks-reference / custom-agents-configuration、`github/copilot-cli` リポジトリの changelog.md。

## 設計

### A. skill 構成（3本）

#### A-1. `verify` 強化（既存 `copilot/skills/verify/SKILL.md` を改訂）

- starter kit の verification-loop 相当へ拡張する。現行に不足している以下を追加する。
  - テスト工程でのカバレッジ報告（ツールが出す場合のみ）
  - secrets スキャン: gitleaks / trufflehog が導入済みなら使い、無ければ `git diff` の追加行を目視確認する（リポジトリ全体の grep だけで PASS を出さない）。デバッグ出力の残留確認は既存の Log Audit を維持
  - Diff レビュー: `git diff --stat` 等で変更全体を確認し、意図しない変更・エラー処理漏れ・エッジケースを見る
- レポート形式に `Diff` 行を追加する。既存の固定レポート形式・モード体系（quick / full / pre-commit / pre-pr）は維持する。
- frontmatter に `argument-hint: "[quick|full|pre-commit|pre-pr]"` を追加し、`/verify pre-pr` のような起動体験を実現する。
- `compatibility: codex,copilot` は CLI に無視されるが、repo 内の管理情報として維持する。
- codex 側の複製（`codex/skills/verify/SKILL.md`）にも同内容を反映する。両ファイルが本文で「整合を保つ」と明記しているため。末尾 Compatibility 節の差分のみ維持する。

#### A-2. `tdd` 新設（`copilot/skills/tdd/`）

- 構成: `SKILL.md` + `references/test-templates.md` + `references/testing-mistakes.md` + `scripts/check-coverage.sh`。
- `SKILL.md` は starter kit の tdd-workflow を基に、次を調整する。
  - `/tdd` コマンド・`tdd-guide` agent への参照（Claude Code 固有）を除去
  - starter kit `commands/tdd.md` の 5 ステップ簡約版を「クイックモード」節として吸収
  - starter kit `commands/test-coverage.md` のカバレッジ分析手順を節として吸収
  - カバレッジ閾値の「80%」ハードコードは「プロジェクト基準に従う（例 80%）」に統一
  - 発動抑制条件（明示的な TDD 要求またはカバレッジ要件のある新機能開発のみ。通常のバグ修正では focused test のみ）を維持
- `references/` 2 ファイルは無改変で移植する（JS/TS 特化である旨の注記は SKILL.md 側で維持）。
- `check-coverage.sh` は既存バグ 2 件を修正して移植する: (1) pass/fail 判定が未実装（閾値を表示するだけ）、(2) pytest の `--cov-report=term-summary` は存在しないオプション（正しくは `term`）。

#### A-3. `security-review` 新設（`copilot/skills/security-review/`）

- 構成: `SKILL.md` + `references/vulnerability-patterns.md` + `assets/security-checklist.md`。starter kit のディレクトリ構造を維持し、上流との diff 追従を容易にする。
- frontmatter を Copilot 規約へ変換する（`name` + `description`。Claude 固有の `when_to_use` の内容は description に統合）。
- SKILL.md 冒頭に「ビルトイン `/security-review` の補完として、体系的チェックリストと修正パターンを提供する」旨を 1 行明記する。
- verify skill の secrets スキャン工程から本 skill を参照する。

### B. `copilot-instructions.md` への規範追記

「検証と完了条件」セクションを新設し、starter kit の `rules/anti-patterns.md`・`rules/testing.md` の核心を既存の文体（だ・である調、絵文字なし）で追記する。追記する規範:

- 必要なテスト・チェックが実際に通るまで、完了と主張しない。
- 最小の関連チェックを先に実行し、完了報告の前に広い検証を行う。
- skip・失敗したチェックは理由と残リスク付きで報告する。
- コミット前・PR 前の検証には verify skill を使う。TDD の依頼時は tdd skill、認証・ユーザー入力・secrets 等に触れる変更では security-review skill を参照する。
- API・コマンド・import・ファイルパスは使用前に実在確認する。同じアプローチが繰り返し失敗したら、止まって別アプローチかブロッカー報告に切り替える。

既存の「変更した挙動にはテストを付ける」（コーディング規約）はそのまま残す。

### C. 設定基盤の是正

- `copilot/settings.json` を新設し、`~/.copilot/settings.json` への symlink として配備する。内容:
  - `model`: 実装時に `copilot help config` の実選択肢を確認して設定する。現候補は `claude-opus-4.8-fast`（現行の `claude-opus-4.6-fast` は選択肢に無い可能性が高い）。fast 系の premium request 倍率も実装時に確認する。
  - `effortLevel`: `"xhigh"`（品質重視。Anthropic モデル向けの max 相当が選択肢にあれば比較して選ぶ）。
  - `hooks`: 既存の kb-mcp session-end hook を現行スキーマ（イベント名 `sessionEnd`、`version: 1` 形式）へ移設する。
- `config.json` は宣言的管理から外す。
  - `symlinks.json` から `copilot/config.json` のエントリを削除する。
  - 実機の `~/.copilot/config.json` は symlink から実ファイルに戻し、runtime 値（`firstLaunchAt` / `last_logged_in_user` / `trusted_folders` 等）を CLI の自動管理に委ねる。
  - repo 側の `copilot/config.json` は削除する（内容は settings.json と実機ファイルに引き継ぐ）。
  - 現 `config.json` の各キーは現行リファレンスと突き合わせて監査し、ユーザー意図の設定（`includeCoAuthoredBy` 等）は正しい置き場（settings.json または実機 config.json）へ移す。表記が snake_case / camelCase 混在している点も正式キー名に正す。
- リスクと対策: hooks 移設で kb-mcp session-end hook が壊れないことを実装時に必ず確認する（設定ロードは `copilot --list-env` で、hook 発火はテストセッションで確認）。

### D. 配備と検証

- `copilot/skills/.gitignore` に `!tdd` `!tdd/**` `!security-review` `!security-review/**` を追記する（ホワイトリスト方式のため、忘れると git 管理から漏れる）。
- `symlinks.json`: `copilot/settings.json` のエントリを追加し、`copilot/config.json` のエントリを削除する。
- `apply_symlinks.py` が manifest から消えた home symlink の解消に対応していない場合、実機での symlink 解消（config.json の実ファイル復元）は手動手順とし、PR 説明に記載する。
- `~/.copilot/skills` はディレクトリごと repo への symlink 済みのため、skill 追加に伴う `apply_symlinks.py` の再実行は不要。
- 検証手順:
  1. `copilot skill list` で verify / tdd / security-review の 3 skill が Personal skills として認識されること
  2. `copilot --list-env` で instructions / settings のロード状態を確認すること
  3. 非対話 `copilot -p` でモデル・effort の反映と verify skill のスモーク実行を確認すること
  4. `shellcheck` を `check-coverage.sh` に実行すること
  5. kb-mcp session-end hook の発火を確認すること
- `README.md` の「方針」「管理対象」記述を settings.json / config.json の扱い変更に合わせて数行更新する。

## 今回対応しないこと

- `osaka.instructions.md` の未配備（`symlinks.json` 未登録）: 意図的か不明なので、本件とは独立に確認する。
- codex / claude 側の変更（A-1 の verify ミラー反映のみ例外）。
- VS Code Copilot Chat・Copilot coding agent 対応。
- verify の共有 skill 化（codex / copilot の二重管理解消）。
- rubber-duck・`subagents.agents` の effort チューニング等のビルトイン活用設定。
- `memory` 設定の宣言的管理。

## リスク・未確認事項

- `~/.copilot/instructions/*.instructions.md` で `applyTo` frontmatter が有効かは公式未確認（公式 Doc は「全セッションに適用」とのみ記載）。既存ファイルの動作には影響しないため今回は現状維持。
- SKILL.md の `compatibility` フィールドは Copilot CLI がサポートするか未確認。未認識キーは無視される仕様のため実害はない。
- model の実選択肢・fast 系の premium request 倍率は実装時に確認する。
- hooks 移設は動作確認まで完了して初めて完了とみなす。確認できない場合は、管理外となった実機 `config.json` に既存 hooks を残したまま段階移行する。
- docs.github.com は随時更新されるため、本設計の CLI 仕様記述は 2026-07-06 時点のスナップショット。

## 実装順序（概略）

1. A-2 / A-3: 新規 skill 2 本の移植（`.gitignore` 追記を含む）
2. A-1: verify 強化と codex ミラー反映
3. B: `copilot-instructions.md` 規範追記
4. C: `settings.json` 新設・`config.json` 管理外し・hooks 移設
5. D: 配備・検証・README 更新

詳細なタスク分解は writing-plans で行う。
