# Evals

## User Complaints

- skill の改善基準をエージェントが勝手に決めてしまうと、改善されたのか分かりにくい
- ユーザーが感じた不満や期待を、そのまま実験ループに入れられる形にしたい

## Desired Behavior

- user complaint を先に固定し、それに対応する binary eval で keep/discard を決められる
- autotune の結果を見たときに、「どの不満に効いた変更か」が追える

## Execution Harness

- Agent: Codex
- Invocation: `ok-skill-autotune` の静的レビューと `quick_validate.py`
- Output location: `self-tune-001/` 配下の artifact

## Test Inputs

- 「この skill を autotune したい。何を確認して、どう記録して、どう改善を採用する？」
- 「binary eval で既存 skill を改善したい。baseline と mutation の進め方をまとめて」
- 「ダッシュボードなしで、1 mutation ずつ実験する最小フローを出して」

## Binary Evals

### EVAL 1: Binary eval に落とす指示が明確
- Complaint addressed: 改善基準が曖昧だと改善されたか分からない
- Question: binary eval を使う理由と作り方が明確に説明されているか
- Pass condition: yes/no eval、件数の目安、曖昧な eval を避ける点が分かる
- Fail condition: eval が抽象的なまま、または段階評価へ流れる

### EVAL 2: 1 mutation at a time が守られる
- Complaint addressed: 一度に複数変更が入ると何が効いたか追えない
- Question: 1回の experiment で 1 つだけ mutation を試す方針が明確か
- Pass condition: 複数仮説を混ぜないことと keep/discard 判定が書かれている
- Fail condition: 一度に複数変更を入れる余地が大きい

### EVAL 3: 実行条件の再現性がある
- Complaint addressed: 実行条件がぶれると比較結果に納得できない
- Question: target skill をどう実行し、同条件で再実行するかが事前に固定されるか
- Pass condition: execution harness、invocation、出力保存先の固定が求められている
- Fail condition: 実行条件が曖昧なまま baseline や mutation に進めてしまう

### EVAL 4: 実験ログが最小十分
- Complaint addressed: 何を変えてどう効いたか後から追えない
- Question: 実験結果を後から追えるだけの artifact が定義されているか
- Pass condition: results.tsv、changelog.md、evals.md、baseline が定義されている
- Fail condition: 何を残すかが曖昧で、比較の根拠が消える

### EVAL 5: 暴走防止がある
- Complaint addressed: autoresearch 的な無限ループは扱いづらい
- Question: 無限ループせず、止めどきが明確か
- Pass condition: 連続失敗や上限回数で止める方針がある
- Fail condition: 自律的に回し続ける前提が残る
