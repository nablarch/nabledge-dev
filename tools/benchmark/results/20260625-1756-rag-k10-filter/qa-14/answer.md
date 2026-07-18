Nablarch 5からNablarch 6へのバージョンアップにおけるJakarta EE 10対応では、以下の変更がアプリケーションに影響します。

**1. アプリケーションサーバの変更**
Jakarta EE 10に対応しているアプリケーションサーバが必要です。従来のJava EE対応サーバでは動作しません。

**2. 名前空間の変更（パッケージ名の変更）**
Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更されました。アプリケーション内でこれらのパッケージをインポートしているすべての箇所を変更する必要があります。

**3. XMLスキーマ指定の変更**
`web.xml` 等のXMLファイルに記述しているXMLスキーマをJakarta EE 10対応のものに変更する必要があります。

例：
```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" ...
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" ...
         version="6.0">
```

**4. Java EE仕様の実装ライブラリの更新**
アプリケーションに組み込んでいるJava EE仕様の実装ライブラリをJakarta EE対応版に置き換える必要があります。どのライブラリをどう置き換えるかはライブラリごとに異なるため、各ライブラリの公式サイト等で確認が必要です。Jakarta EEの各仕様ページでも互換実装が紹介されています。

詳細な移行手順については、[Nablarch 6マイグレーションガイド](https://nablarch.github.io/docs/6u2/doc/migration/index.html) を参照してください。