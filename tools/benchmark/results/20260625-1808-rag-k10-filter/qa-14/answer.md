Nablarch 5からNablarch 6へのバージョンアップにおいて、Jakarta EE 10対応でアプリケーションに影響がある主な変更点は以下のとおりです。

**1. アプリケーションサーバの変更が必要**

Jakarta EE 10に対応したアプリケーションサーバでのみ動作します。既存のアプリケーションサーバが対応していない場合は、サーバ自体の変更が必要です。

**2. パッケージ名（名前空間）の変更**

Jakarta EE 9で `javax.*` から `jakarta.*` へ名前空間が変更されました。Nablarch 6はJakarta EE 10ベースのため、ソースコード内の `javax.*` のインポートをすべて `jakarta.*` に書き換える必要があります。

**3. XMLスキーマ指定の変更**

`web.xml` 等のXMLファイルでJakarta EE 10のスキーマに変更する必要があります。

```xml
<!-- 修正前（Java EE） -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" ...
         version="3.1">

<!-- 修正後（Jakarta EE 10） -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" ...
         version="6.0">
```

**4. Java EE実装ライブラリの置き換え**

プロジェクトに組み込んでいるJava EE仕様の実装ライブラリをJakarta EE対応版に置き換える必要があります。具体的にどのライブラリが対象かはプロジェクトごとに異なるため、各ライブラリの公式サイトで確認が必要です。なお、Jakarta EEの各仕様ページでも互換実装が紹介されています（例：Jersey 3.1.0 等）。

---

まとめると、移行に必要な作業は大きく「**Nablarchのバージョンアップ**」と「**Jakarta EE対応**（名前空間変更・XMLスキーマ変更・ライブラリ更新）」の2種類です。詳細な手順はNablarchのマイグレーションガイド（`https://nablarch.github.io/docs/6/doc/migration/index.html`）を参照してください。