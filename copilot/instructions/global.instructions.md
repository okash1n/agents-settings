# global user instructions

- リポジトリに `AGENTS.md` がある場合は、その指示に従う。
- 破壊的操作はユーザーの明示合意なしで実行しない。
- 既存の設定パターンと導入経路を優先し、Nix / Home Manager / launchd に加えて Homebrew や公式導線も repo の実装に合わせて扱う。
- `gh` で PR/Issue に長文コメントを投稿するときは、長い `--body` ワンライナーを避け、`--body-file` を優先する。
- `gh` コメント投稿では、一時ファイルや本文に一意な先頭行を入れて、投稿後に `gh api repos/<owner>/<repo>/issues/comments/<id>` または `gh api repos/<owner>/<repo>/issues/<number>/comments` で author・body・URL を確認する。
- `gh` の確認では「最新コメント URL を拾えた」だけで完了扱いにせず、自分が想定した本文が実際に投稿されていることまで確認する。
- VS Code Chat 経由で `gh` を使うと terminal wrapper の都合で出力が崩れることがあるため、成功パターンは「`--body-file` で投稿 -> `gh api ... --jq` で URL/author/body を検証」とする。
