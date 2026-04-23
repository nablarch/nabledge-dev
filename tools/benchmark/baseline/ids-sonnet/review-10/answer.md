**結論**: `Published` アノテーションが付いていない非公開 API を使っていないかチェックするツールが 2 種類提供されている。これを使うことでバージョンアップで壊れにくいコードを書ける。

**根拠**:

Nablarch の後方互換性ポリシーの対象は `nablarch.core.util.annotation.Published` が付与された公開 API のみ。非公開 API（`Published` なし）は後方互換性が維持されないバージョンアップが行われる場合があるため、プロジェクトで使用しないことが求められている。使用した場合、バージョンアップ時に思わぬ不具合が発生する可能性があると明記されている。（`about/about-nablarch/about-nablarch-versionup_policy.json:s4`）

非公開 API の使用を検知するツールとして以下の 2 種類が提供されている（`development-tools/java-static-analysis/java-static-analysis-java_static_analysis.json:s3`）:

1. **nablarch-intellij-plugin**: IntelliJ IDEA 用プラグイン。Nablarch 非公開 API 使用時に警告を表示し、ブラックリストに登録した Java API 使用時にも警告する。
2. **SpotBugs プラグイン（使用不許可 API チェックツール）**: IntelliJ IDEA に依存しない SpotBugs ベースのツール。ブランクプロジェクトには Maven で実行するための設定があらかじめ用意されており、すぐに使用可能。

また、`@Deprecated` が付いている API も注意が必要で、特に不具合・セキュリティ問題が理由で非推奨となったものは、新たな問題が見つかっても対応されないため、移行先の新 API を使うことが必須とされている。（`about/about-nablarch/about-nablarch-policy.json:s12`）

**注意点**:

- アダプタは後方互換性ポリシーの対象外。`Published` が付いていても外部ライブラリの破壊的変更により壊れる場合がある。（`about/about-nablarch/about-nablarch-versionup_policy.json:s4`）
- 致命的な不具合・脆弱性対応時は公開 API でも後方互換が維持できない場合がある。（`about/about-nablarch/about-nablarch-policy.json:s10`）
- ログのレベル・文言の変更、JDK バージョンアップ起因の問題対応なども後方互換の例外となりえる。（`about/about-nablarch/about-nablarch-versionup_policy.json:s6`）

参照: about/about-nablarch/about-nablarch-versionup_policy.json:s4, about/about-nablarch/about-nablarch-versionup_policy.json:s5, about/about-nablarch/about-nablarch-versionup_policy.json:s6, about/about-nablarch/about-nablarch-policy.json:s10, about/about-nablarch/about-nablarch-policy.json:s12, development-tools/java-static-analysis/java-static-analysis-java_static_analysis.json:s3