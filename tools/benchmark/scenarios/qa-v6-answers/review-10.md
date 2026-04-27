**質問**: Nablarch のバージョンアップで壊れにくいコードにしたい。将来変わるかもしれない部分を自分のコードで使っていないかチェックする方法はある？

---

**結論**: Nablarch は「公開 API」と「非公開 API」を `@Published` アノテーションで区別しており、参照先の Javadoc に `@Published` が付いていないクラス・メソッドは **非公開 API**（将来変わる可能性がある）。自分のコードが非公開 API を使っていないかは、静的解析ツール（IntelliJ IDEA プラグイン、または IntelliJ 非依存の SpotBugs ベースツール）でチェックできる。 — `about/about-nablarch/about-nablarch-nablarch_api.json#s1`、`development-tools/java-static-analysis/java-static-analysis-java_static_analysis.json#s3`

**① 公開 API と非公開 API の判定**
参照したクラスやメソッドが公開 API かは、Javadoc 上の `@Published` で判断する:
- `@Published` あり: 公開 API（`@Published(tag="architect")` ならアーキテクト向け）
- クラス・メソッドのいずれにも `@Published` なし: 非公開 API

例:
- `DaoContext`: クラスに `@Published(tag="architect")` → アーキテクト向け公開 API
- `BasicDaoContext#findAll`: `@Published` なし → 非公開 API — `about/about-nablarch/about-nablarch-nablarch_api.json#s1`

> **補足**: Nablarch 6 からは非公開 API も含めた Javadoc を提供している（Java バージョンアップに伴う Javadoc 拡張の仕様変更が理由。Nablarch 5 までは公開 API のみ）。 — `about/about-nablarch/about-nablarch-nablarch_api.json#s1`

**② チェックツール**
Nablarch は使用不許可 API チェックに2種類のツールを提供している:
- **nablarch-intellij-plugin**: IntelliJ IDEA 用プラグイン。Nablarch 非公開 API 使用時に警告、ブラックリスト Java API の使用時にも警告。
- **使用不許可 API チェックツール（SpotBugs プラグイン）**: IntelliJ IDEA 非依存。IntelliJ を使わない環境でも利用可能。ブランクプロジェクトには Maven 実行設定があらかじめ組み込まれており、すぐにチェックを実施できる。 — `development-tools/java-static-analysis/java-static-analysis-java_static_analysis.json#s3`
