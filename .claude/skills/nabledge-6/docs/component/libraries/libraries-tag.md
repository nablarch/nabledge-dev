# Jakarta Server Pagesカスタムタグ

## 機能概要

## HTMLエスケープ漏れを防げる

HTMLの中では「<」「>」「\"」といった文字は、特別な意味を持つため、それらを含む値をそのままJSPで出力してしまうと、悪意のあるユーザが容易にスクリプトを埋め込むことができ、クロスサイトスクリプティング(XSS)と呼ばれる脆弱性につながってしまう。そのため、入力値を出力する場合、HTMLエスケープが必要になる。

ところが、JSPでEL式を使って値を出力すると、HTMLエスケープされない。そのため、値の出力時はHTMLエスケープを考慮した実装が常に必要になり、生産性の低下につながる。

カスタムタグは、デフォルトでHTMLエスケープするので、カスタムタグを使って実装している限り、HTMLエスケープ漏れを防げる。

> **重要**: JavaScriptに対するエスケープ処理は、提供してないため、scriptタグのボディやonclick属性など、JavaScriptを記述する部分には、動的な値(入力データなど)を埋め込まないこと。JavaScriptを記述する部分に動的な値(入力データなど)を埋め込む場合は、プロジェクトの責任でエスケープ処理を実施すること。

HTMLエスケープの詳細は :ref:`tag-html_escape` と :ref:`tag-html_unescape` を参照。

## 入力画面と確認画面のJSPを共通化して実装を減らす

多くのシステムでは、入力画面と確認画面でレイアウトが変わらず、似たようなJSPを作成している。

カスタムタグでは、入力画面と確認画面のJSPを共通化する機能を提供しているので、入力画面向けに作成したJSPに、確認画面との差分(例えば、ボタンなど)のみを追加実装するだけで、確認画面を作成でき、生産性の向上が期待できる。

入力画面と確認画面の共通化については :ref:`tag-make_common` を参照。

## カスタムタグの対象範囲と制約

> **重要**: カスタムタグは、以下のような単純な画面遷移があるウェブアプリケーションを対象にしている。そのため、操作性を重視したリッチな画面作成やSPA(シングルページアプリケーション)に対応していない。
>
> * 検索画面→詳細画面による検索/詳細表示
> * 入力画面→確認画面→完了画面による登録/更新/削除
> * ポップアップ(別ウィンドウ、別タブ)による入力補助
>
> プロジェクトでJavaScriptを多用する場合は、カスタムタグが出力するJavaScriptとプロジェクトで作成するJavaScriptで副作用が起きないように注意する。カスタムタグが出力するJavaScriptについては :ref:`tag-onclick_override` を参照。

## HTML5属性のサポート

> **重要**: HTML5で追加された属性は、:ref:`動的属性<dynamic_attribute>` を使用して記述できる。ただし、頻繁に使用されそうな次の属性は予めカスタムタグの属性として定義している。また、HTML5で追加されたinput要素は、それぞれ :ref:`tag-text_tag` をベースに追加されている。各input要素固有の属性はカスタムタグで個別に定義していないため、動的属性により指定する必要がある。
>
> **追加した属性**（属性を追加したHTMLのタグ名をカッコ内に記載）:
>
> * autocomplete(input、password、form)
> * autofocus(input、textarea、select、button)
> * placeholder(text、password、textarea)
> * maxlength(textarea)
> * multiple(input)
>
> **追加したinput要素**:
>
> * :ref:`tag-search_tag` (検索テキスト)
> * :ref:`tag-tel_tag` (電話番号)
> * :ref:`tag-url_tag` (URL)
> * :ref:`tag-email_tag` (メールアドレス)
> * :ref:`tag-date_tag` (日付)
> * :ref:`tag-month_tag` (月)
> * :ref:`tag-week_tag` (週)
> * :ref:`tag-time_tag` (時間)
> * :ref:`tag-datetimeLocal_tag` (ローカル日時)
> * :ref:`tag-number_tag` (数値)
> * :ref:`tag-range_tag` (レンジ)
> * :ref:`tag-color_tag` (色)

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web-tag</artifactId>
</dependency>

<!-- hidden暗号化を使う場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-encryption</artifactId>
</dependency>

<!-- ファイルダウンロードを使う場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web-extension</artifactId>
</dependency>
```

## カスタムタグの設定



## カスタムタグを使用する(taglibディレクティブの指定方法)



## 入力フォームを作る



## 選択項目(プルダウン/ラジオボタン/チェックボックス)を表示する



## チェックボックスでチェックなしに対する値を指定する



## 入力データを画面間で持ち回る(ウィンドウスコープ)



## クライアントに保持するデータを暗号化する(hidden暗号化)



## 複合キーのラジオボタンやチェックボックスを作る



## 複数のボタン/リンクからフォームをサブミットする



## サブミット前に処理を追加する



## プルダウン変更などの画面操作でサブミットする



## ボタン/リンク毎にパラメータを追加する



## 認可チェック/サービス提供可否に応じてボタン/リンクの表示/非表示を切り替える



## 別ウィンドウ/タブを開くボタン/リンクを作る(ポップアップ)



## ファイルをダウンロードするボタン/リンクを作る



## 二重サブミットを防ぐ



## サーバ側のトークンをデータベースに保存する



## 入力画面と確認画面を共通化する



## 変数に値を設定する



## GETリクエストを使用する



## 値を出力する



## HTMLエスケープせずに値を出力する



## フォーマットして値を出力する



## エラー表示を行う



## コード値を表示する



## メッセージを出力する



## 言語毎にリソースパスを切り替える



## ブラウザのキャッシュを防止する



## 静的コンテンツの変更時にクライアント側のキャッシュを参照しないようにする



## 論理属性を指定する



## 任意の属性を指定する



## 論理属性の扱い



## Content Security Policy(CSP)に対応する



## セキュアハンドラが生成したnonceを任意の要素に埋め込む



## カスタムタグが生成する要素に対してJavaScriptで処理を追加する



## 拡張例



## カスタムタグのルール



## :ref:`tag_reference`

:ref:`tag_reference`を参照。
