# キックオフ手順：Artifact でプロジェクトを管理する

大会キックオフ（2026/11/2 12:00 JST）で、新しいセッションがこのファイルを読んで最初に行うこと。
**この手順は「プロジェクト管理の器を立ち上げる」ことだけを扱う。** 作品の中身（要件・設計）は器ができてから GrillMe で一から詰める。

材料はアイデアの卵 [IDEA_EGG.md](./IDEA_EGG.md) だけ。大会前の企画書（PLAN.md など）は参考扱いで、決定事項としては使わない。

---

## 0. 前提

- 依頼主は建設会社の代表。エンジニアではない。日本語で、結論から、専門用語を避けて書く。「正本」という言葉は使わない
- このファイルを読んだセッションが **司令塔** になる。部品ごとの作業は子セッションに任せ、司令塔は全体の状態をハブに記録する

## 1. 器を立ち上げる（キックオフ直後の 30 分）

1. 提出用の新しい GitHub リポジトリを作る（大会前の記録を持ち込まないため。リポジトリ名は代表に確認）
2. `templates/project-hub.html` を **新しい Artifact として公開** する
   - capabilities は `{"db": {}, "user": {}}`
   - 公開した瞬間は空。中身はすべて共有データから描かれる
3. 動画制作ページのテンプレート `templates/video-studio.html` も新しい Artifact として公開する
   - capabilities は `{"assets":{}, "comments":{"customAnchors":true}, "db":{}, "downloads":{}, "user":{"scopes":["profile"]}}`
   - `meta/project` に `{name, subtitle, hubUrl:"<ハブの URL>", totalSec:180, summary, rules:[…]}` を入れる
   - 空の見本：テンプレートを公開した状態の見本は https://claude.ai/artifact/5WRNqEp1Yf6KLhgYabyaK8 （ハブ）と https://claude.ai/artifact/Vy1ZQmBumt1ghMBaRnrxyT （動画）。見本そのものは使わず、毎回ファイルから新しく公開する
4. ハブの共有データに初期値を入れる（ArtifactData の batch で 1 回）
   - `meta/project`：`{name, subtitle, modules:["M0",…], links:[{name:"動画制作ページ", url:"<動画の URL>"}]}`
   - `sessions/<id>`：司令塔セッション自身を 1 件
   - `tasks/<id>`：IDEA_EGG.md の「まだ決めていないこと」を担当「代表」で登録
5. 代表にハブの URL を渡す。公開した直後は非公開なので、共有するなら代表が共有メニューから行う

## 2. 卵を孵す（GrillMe → 設計）

順番を守る。前の段が「確定」になるまで次に進まない。各段の成果はハブの該当ページに書き込む。

| 段 | ハブのページ | やること |
|---|---|---|
| 1 | A-02 GrillMe 記録 | IDEA_EGG.md を材料に、代表に問いを投げて答えをもらう。1 問ずつ記録し、決まったことに「決定」を付ける |
| 2 | A-01 概要と主張 | GrillMe の結果からひとことと主張を書く |
| 3 | A-03 要件整理 | 機能要件・非機能要件・制約に番号を振る |
| 4 | A-05 スコープ | 対象・対象外・限界と改善領域 |
| 5 | A-04 作業フロー | 利用者の業務フロー、開発の進め方 |
| 6 | D-01 基本設計 | 部品の分け方と入出力 |
| 7 | D-02 応用設計 | 部品ごとの細かな決め事 |
| 8 | D-03 DB 定義書・一覧 | 共通データの一覧と定義 |
| 9 | D-04 画面一覧・遷移図 | 画面一覧と遷移 |
| 10 | M-01 工程 | 日ごとの工程表（gantt） |
| — | R-01 参照資料／R-02 背景メモ | IDEA_EGG.md の資料と背景を移す |

各ページの状態（`status`）は `empty`（未記入）→ `draft`（案）→ `fixed`（確定）。設計待ちのものは `later`。

## 3. ハブの共有データの形

Claude は ArtifactData で直接書き込む。画面からも代表がタスクとセッションを追加・変更できる。

### `meta/project`（1 件）
| 項目 | 中身 |
|---|---|
| name | プロジェクト名（サイドパネルの見出し） |
| subtitle | 見出しの下の小さな文字 |
| modules | 部品の名前の配列。タスクとセッションの「部品」の選択肢になる |
| links | `[{name, url}]`。サイドパネル下の「関連ページ」に出る（https のみ） |

### `pages/<ページ ID>`（ページごとに 1 件）
ページ ID：`overview` `grill` `requirements` `workflow` `scope` `basic` `detail` `db` `screens` `schedule` `refs` `notes`

```json
{ "status": "draft", "blocks": [ … ] }
```

`blocks` に並べられる部品：

| t | 形 | 使いどころ |
|---|---|---|
| `lead` / `p` / `note` | `{t, text}`。`**太字**` と改行が使える | 文章 |
| `h` | `{t, text, chip?}` | 小見出し |
| `list` | `{t, items:[…]}` | 箇条書き |
| `table` | `{t, head:[…], rows:[[…]], mono?:[列番号]}` | 要件・DB 定義・画面一覧 |
| `cards` | `{t, items:[{title, body?, items?}]}` | 部品の説明を並べる |
| `qa` | `{t, items:[{q, a, d?}]}` | GrillMe の記録（d に「決定」など） |
| `links` | `{t, items:[{name, url, note?}]}` | 参照資料 |
| `flow` | `{t, steps:[{who, title, note?, chip?, loop?}]}` | 業務フロー |
| `graph` | `{t, nodes:[{id, name, col, row, main?}], edges:[[from, to, kind]], caption?}` | 画面遷移図（kind 1＝主な流れ、2＝戻り、0＝補助） |
| `gantt` | `{t, days:[{d, w, kind?}], rows:[{name, from, to, kind?}]}` | 工程表（from/to は days の番号。kind は `pre` `end`） |

工程表の `days` は、タスクの「予定日」の選択肢にもなる（タスクの `day` は days の番号の文字列）。

### `tasks/<id>`
`{title, module, owner:"代表"|"Claude", priority:"P0"|"P1"|"P2", day, status:"backlog"|"todo"|"doing"|"review"|"done", sessionId, memo, createdAt}`

### `sessions/<id>`
`{name, module, status:"計画"|"実行中"|"完了", purpose, url, createdAt}`

### 動画制作ページの共有データ（参考）
| コレクション | 中身 |
|---|---|
| `meta/project` | name, subtitle, hubUrl, totalSec（既定 180）, summary, rules[] |
| `meta/style` | title, points[], refs[{name,url,note}]（絵コンテ上段のトーン枠） |
| `scenes/<id>` | order, tcIn, tcOut（"0:00"）, era, title, status（未着手／案／確定）, picture, onscreen, materials, shot, ref, frame（asset id）, line, narrationJa, subtitleEn |
| `materials/<id>` | order, group, title, url, source, rights, scene（先頭の数字で場面と結びつく）, apply（不要／必要／要確認／—）, check（確認済み／確認中／未着手）, status（候補／使う／使わない）, img, note, basis, credit, kind（image／video／audio）, asset, dur, createdAt, track（narr／bgm／sfx）, by, safeChecked |
| `pkg/<素材 id>` | mid, title, img, state（in／archived）, addedAt, archivedAt, by（パッケージ） |
| `cuts/<id>` | createdAt, label, asset（ビューワーの版） |
| `edits/<id>` | title, aspect, clips[], audio[]（track＝narr/bgm/sfx）, log[], updatedAt（編集データ） |

## 4. セッションの回し方

- 子セッションは司令塔が `create_session` で立てる。最初の指示に、担当範囲・読むファイル・守ること・成果の置き場所・終わったら send_message で報告、を必ず書く
- 立てたらハブの `sessions` に登録し、関係するタスクの `sessionId` をひも付ける
- 子セッションは正常に終わっても自動では報告しない。司令塔が状態を見に行く
- 子セッションが作る Artifact（動画制作ページなど）は子セッションが管理する。ハブ本体は司令塔だけが書き換える。リンクは `meta/project.links` に足す
- Artifact へのコメントが司令塔に届いたら、そのページを管理しているセッションに作業を渡し、コメントのスレッドに「何を誰に頼んだか」を返信する

## 5. 守ること

- 作品は大会期間中にゼロから作る。大会前のコード・自作の既存コードは持ち込まない（Japan 大会の規約を確認してから確定）
- 他社の AI API は製品に使わない
- 実案件のデータ・自社単価・施主情報は公開リポジトリと Artifact に入れない
- 動画・ページに載せる素材は、権利がはっきりしたものだけ
