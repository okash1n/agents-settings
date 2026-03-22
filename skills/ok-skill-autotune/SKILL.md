---
name: ok-skill-autotune
description: existing Skill を binary eval で反復改善するときに使う。1回に1つだけ prompt mutation を試し、results.tsv と changelog.md を残しながら、改善した変更だけを採用する。ダッシュボードや自律無限ループは前提にしない。
compatibility: codex,copilot
---

# OK Skill Autotune

## Overview

既存の Skill を少しずつ改善するための skill。
やることは 3 つに絞る。

1. ユーザーの不満と期待を binary eval に落とす
2. 1回に1つだけ mutation を試す
3. `results.tsv` と `changelog.md` に結果を残す

この skill は dashboard や無限ループを前提にしない。
各 experiment は明示的に区切り、改善しなかった変更は捨てる。

改善の基準はエージェントが勝手に決めない。
ユーザーが「何が嫌だったか」「どうなってほしいか」を先に固定し、それを eval suite に変換してから実験を始める。

## Trigger Examples

- 「この skill を autotune したい」
- 「binary eval で skill の改善実験を回したい」
- 「1 mutation ずつ試して結果ログを残したい」
- 「この SKILL.md を少しずつ改善して」

## User Interaction Contract

- ユーザーに直接 CLI / スクリプト実行を要求しない。
- 実験の初期化、ログ作成、検証実行はエージェントが代行する。
- 実験開始前に、対象 skill とユーザー定義の eval 条件を確認する。
- 状態変更を伴う mutation は、必ず1回の確認ターンを挟んでから実行する。
- 破壊的変更はしない。改善しなかった mutation は元に戻す。
- エージェント都合の評価軸を勝手に採用しない。まずユーザーの不満点を聞き、それを eval に変換する。

## Inputs To Confirm

- 対象 skill の `SKILL.md` パス
- ユーザーが不満に思った点 2〜5 件
- ユーザーが期待する改善後の挙動
- テスト入力 3〜5 件
- binary eval 3〜6 件
- 1 mutation あたりの runs 数
- 実験上限回数が必要かどうか

## User-Driven Eval Design

- 最初に、ユーザーの不満をそのまま短文で列挙する。
- 次に、それぞれを yes/no で判定できる eval へ変換する。
- eval はエージェント視点の抽象品質ではなく、ユーザーが困った失敗に直接対応させる。
- 期待する改善が曖昧な場合は、実験を始める前に「何が pass か」を一度だけ確認する。
- `evals.md` には、元の不満文と、それに対応する eval を両方残す。

## Execution Harness Contract

- baseline 前に、対象 skill をどう起動するかを 1 つに固定する。
- 各 run で変えてよいのは input と skill 本文だけにする。
- invocation 方法、使用する agent、出力保存先は `evals.md` か run メモに残す。
- output の保存場所が曖昧なまま experiment を始めない。
- 対象 skill の実行が自動化できない場合でも、どの手順で同じ条件を再現するかを先に言語化する。

## Workflow

### 1. Baseline を固定する

- 対象 skill を読み、何を改善したいかを短く言語化する。
- ユーザーの不満と期待を binary eval に落とす。
- 実行 harness を固定し、同じ条件で再実行できるようにする。
- `scripts/init_run.py --skill <path>` で run ディレクトリを作る。
- baseline の `SKILL.md` を `SKILL.md.baseline` に保存する。
- 変更前の skill で baseline を実行し、`results.tsv` に experiment `0` として記録する。

### 2. Mutation を 1 つだけ入れる

- failure の傾向を見て、直す点を 1 つに絞る。
- どの user complaint を改善する mutation なのかを明示する。
- 同時に複数の仮説を混ぜない。
- 典型例:
  - 曖昧な指示を具体化する
  - 優先順位の低い位置にある重要指示を前へ出す
  - recurring failure に対して anti-pattern を追加する
  - 悪さをしている冗長な説明を削る

### 3. 評価して keep / discard を決める

- 同じ test inputs と、ユーザー合意済みの同じ eval を使って再実行する。
- score が改善したら keep する。
- 同点または悪化なら discard し、`SKILL.md` を直前の keep 状態へ戻す。
- 毎回 `results.tsv` と `changelog.md` を更新する。

### 4. 止めどきを守る

- 良い mutation が連続で出なくなったら止める。
- 上限回数に達したら止める。
- 無限に回し続ける前提では進めない。

## Eval Rules

- eval は必ず binary にする。
- 1〜7 のような段階評価は使わない。
- 「何を満たせば pass か」を短く明文化する。
- eval 数は 3〜6 件に抑える。
- eval 自体が target skill の output を不自然に縛っていないか確認する。
- eval ごとに、どの user complaint に対応するかを明記する。

## Log Artifacts

run ディレクトリには最低限これを残す。

- `results.tsv`
- `changelog.md`
- `evals.md`
- `SKILL.md.baseline`
- 必要なら run ごとの output 保管先メモ

`results.tsv` の列:

```text
experiment	score	max_score	pass_rate	status	change_summary
```

`changelog.md` には各 experiment ごとに次を書く。

- 何を変えたか
- どの user complaint を狙ったか
- なぜ効くと思ったか
- keep/discard
- どの eval が改善 / 悪化したか

## Commands

run ディレクトリ初期化:

```bash
scripts/init_run.py --skill /absolute/path/to/SKILL.md
```

run 名を明示する場合:

```bash
scripts/init_run.py --skill /absolute/path/to/SKILL.md --run-name experiment-a
```

## Keep / Discard Policy

- keep:
  - score が改善した
  - 同点でも明確に単純化され、次の実験の土台として有利
- discard:
  - score が悪化した
  - 同点だが複雑化した
  - eval を誤魔化しているだけに見える
  - ユーザーの不満には効いていないのに、形式的な score だけが上がった

## Notes

- この skill は target skill の自動実行基盤自体までは提供しない。
- 実行方法が skill ごとに異なるので、そこは対象 skill に合わせて設計する。
- ただし experiment を始める前に、再現可能な execution harness だけは固定する。
- まずは手動寄りの実験ループで十分。dashboard や常駐オーケストレーションは後回しでよい。
- `agents-settings` 配下の skill を対象にする場合は、必要なら `ok-skill-creator` の品質ゲートも併用する。
- この skill の価値は、ユーザーの不満を改善サイクルに繰り返し取り込めることにある。
