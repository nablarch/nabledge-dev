**結論**: テスト時にシステム日時を任意の値に切り替えるには、`SystemTimeProvider` インターフェースを実装したクラスを作成し、テスト用のコンポーネント定義でそのクラスを差し替えます。本番とテストの切り替えは「コンポーネント定義で指定するクラスを差し替えるだけ」で実現できます。

**根拠**:

Nablarch の日付管理機能は、コンポーネント定義で指定されたクラスを通じてシステム日時・業務日付を取得する仕組みになっています。そのため、コンポーネント定義を差し替えるだけで本番とテストの動作を切り替えられます。

**システム日時の切り替え手順**

1. `SystemTimeProvider` インターフェースを実装したクラスを作成する（例: テスト用に固定日時を返すクラス）
2. テスト用のコンポーネント定義で `systemTimeProvider` という名前でそのクラスを登録する

本番環境では、デフォルト実装の `BasicSystemTimeProvider` を使用します:

```xml
<!-- 本番用 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト時は、このコンポーネント定義を差し替え用のクラス（任意日時を返す独自実装）に変更することで切り替えます。

**業務日付を切り替えたい場合**

同様に `BusinessDateProvider` インターフェースを実装したクラスを作成し、`businessDateProvider` という名前でコンポーネント定義に登録します:

```xml
<!-- 本番用 -->
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

テスト時はコンポーネント定義を差し替えることで任意の日付を返せます。

**注意点**:
- `BusinessDateProvider` を使う場合、`BasicApplicationInitializer` の `initializeList` への登録も必要です
- 業務日付はデータベースで管理されるため、依存モジュール `nablarch-common-jdbc` が必要です

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s7, libraries-date.json:s12, libraries-date.json:s13