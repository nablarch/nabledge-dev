**結論**: Nablarchには「日付管理」機能があり、OS日時（システム日時）と業務日付を明確に分けて管理できます。業務日付は `BusinessDateUtil` で取得し、締め処理などで複数の業務日付（区分別）をデータベースで管理できます。

**根拠**:

業務日付はデータベーステーブルで管理します。テーブル構造は以下の通りです。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別する文字列（例: "00", "batch", "closing" など） |
| 日付 | yyyyMMdd形式の文字列 |

コンポーネント定義への追加：

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

業務日付の取得：

```java
BusinessDateUtil.getDate();          // デフォルト区分で取得
BusinessDateUtil.getDate("closing"); // 区分を指定して取得（締め処理用など）
```

OS日時（システム日時）を取得したい場合は SystemTimeUtil を使用：

```java
SystemTimeUtil.getDate();  // OS日時を取得
```

業務日付の更新（締め処理での日付送り）：

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date); // 区分と新しい日付(yyyyMMdd)を指定して更新
```

業務日付の一時上書き（バッチ再実行時）：
```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:

- 業務日付管理機能は `nablarch-common-jdbc` モジュールが必要です（システム日時のみなら `nablarch-core` のみで可）
- `BasicBusinessDateProvider` は初期化が必要なため、`initializeList` への追加を忘れずに行ってください
- 締め処理でシステム日時と業務日付を分けて管理する場合、区分（SEGMENT）を用途別（例: 通常処理用 "00"、締め処理用 "closing" など）に分けることで複数の業務日付を独立して管理できます
- コンポーネント定義のクラスを差し替えることで、テスト時などに業務日付の取得方法を切り替えることも可能です

参照: libraries-date.json#s7, libraries-date.json#s8, libraries-date.json#s10, libraries-date.json#s9