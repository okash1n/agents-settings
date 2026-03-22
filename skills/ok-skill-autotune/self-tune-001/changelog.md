# Changelog

## Experiment 0 - baseline

**Score:** 3/5 (60.0%)
**Change:** 変更なし。初版のまま評価
**Reasoning:** まず現状の強みと不足を切り分けるため
**Result:** binary eval、1 mutation at a time、artifact、stop conditions は明確だった。一方で user complaint を eval に変換する契約が弱く、target skill の invocation 方法と output 保存先を baseline 前に固定する契約も薄かった
**Failing outputs:** 改善の軸がユーザー基準で固定されず、実行再現性にも弱さがある

## Experiment 1 - keep

**Score:** 5/5 (100.0%)
**Change:** user complaint 起点の eval 設計と `Execution Harness Contract` を追加し、baseline 前に invocation、agent、output 保存先を固定するようにした
**Reasoning:** あなたの不満を keep/discard 判定へ直接つなげるには、user complaint を eval に変換し、その上で比較条件も固定する必要があるため
**Result:** ユーザー起点の改善軸と再現性の eval が改善し、5/5 になった。既存のシンプルさは大きく崩れていない
**Failing outputs:** 現時点では顕著な失敗なし
