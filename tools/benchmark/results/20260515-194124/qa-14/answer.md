**結論**: Nablarch 5からNablarch 6へのバージョンアップにおいて、Jakarta EE 10対応でアプリケーションに影響がある変更は主に2点です。(1) Jakarta EE 10対応のアプリケーションサーバへの移行、(2) Javaバージョンを17に変更する必要があります。加えて、パッケージ名・依存関係の変更がアプリケーションコードに影響します。

**根拠**:

**1. Jakarta EE 10対応（影響あり）**
- Jakarta EE 10に対応したアプリケーションサーバ上で動作させる必要があります
- Jakarta EE 10への移行に伴い、**パッケージ名や依存関係などを変更する必要があります**
  - 例: `javax.*` → `jakarta.*` へのパッケージ名変更
- 変更内容の詳細はマイグレーションガイドを参照: https://nablarch.github.io/docs/6u2/doc/migration/index.html

**2. 必要Javaバージョンの変更（影響あり）**
- Jakarta EE 10対応に伴い、動作に必要なJavaのバージョンが **Java 17** に変更されました
- 実行環境のJavaバージョンを17にする必要があります

**3. 提供されなくなったコンポーネント（使用している場合は影響あり）**
- 以下はNablarch 6では提供されません:
  - ETL基盤
  - 帳票ライブラリ
  - ワークフローライブラリ
  - UI開発基盤

**注意点**:
- パッケージ名変更（`javax.*` → `jakarta.*`）はアプリケーションコード全体に影響するため、移行作業は広範囲になる可能性があります
- 詳細な移行手順は必ずマイグレーションガイドを参照してください
- ETL基盤・帳票ライブラリ・ワークフローライブラリ・UI開発基盤を使用している場合は、代替手段の事前検討が必要です

参照: `releases-nablarch6-releasenote-6.json#s2`, `releases-nablarch6-releasenote-6.json#s3`, `releases-nablarch6u2-releasenote-6u2（5u25からの変更点）.json#s2`, `releases-nablarch6u2-releasenote-6u2（5u25からの変更点）.json#s4`