Nablarch 5からNablarch 6へのバージョンアップにおいて、Jakarta EE 10対応でアプリケーションに影響がある主な変更は以下の通りです。

**1. Jakarta EE 10対応アプリケーションサーバが必要**

Jakarta EE 10に対応しているアプリケーションサーバ上で動作させる必要があります。従来のJava EE対応サーバでは動作しません。

**2. 名前空間の変更（`javax.*` → `jakarta.*`）**

Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更されました。後方互換性は維持されないため、プロジェクト内のインポート文をすべて書き換える必要があります。

**3. XMLスキーマ指定の変更**

`web.xml` 等のXMLファイルで指定しているXMLスキーマをJakarta EE 10対応のものに変更する必要があります。

例：
```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" ...
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" ...
         version="6.0">
```

**4. Java EE仕様の実装ライブラリの置き換え**

プロジェクトに組み込んでいるJava EE仕様の実装ライブラリをJakarta EE対応版に置き換える必要があります。どのライブラリをどれに置き換えるかは実装ライブラリごとに異なるため、各ライブラリの公式サイトや [Jakarta EEの各仕様のページ](https://jakarta.ee/specifications/) で互換実装を確認してください。

---

移行の全体像としては、「Nablarchのバージョンアップ（5→6）」と「Jakarta EE 10対応」の2つを合わせて実施する必要があります。詳細な手順はマイグレーションガイド（https://nablarch.github.io/docs/6/doc/migration/index.html）を参照してください。