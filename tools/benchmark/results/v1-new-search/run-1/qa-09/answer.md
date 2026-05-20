**結論**: NablarchはOS日時とは独立した業務日付管理機能を提供しており、`BusinessDateUtil`で業務日付を取得できます。締め処理のように複数の業務日付が必要な場合は、「区分」で識別する複数業務日付管理にも対応しています。

**根拠**:

業務日付はデータベーステーブルで管理します。テーブル構成は以下の通りです。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別するための文字列値（例: "00", "batch"） |
| 日付 | 業務日付。文字列型（yyyyMMdd形式） |

コンポーネント定義に `BasicBusinessDateProvider` を設定します。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <!-- テーブル名 -->
  <property name="tableName" value="BUSINESS_DATE" />
  <!-- 区分のカラム名 -->
  <property name="segmentColumnName" value="SEGMENT"/>
  <!-- 日付のカラム名 -->
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略して業務日付を取得した場合に使用される区分 -->
  <property name="defaultSegment" value="00"/>
  <!-- データベースアクセスに使用するトランザクションマネージャ -->
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

業務日付の取得は `BusinessDateUtil` を使います。OS日時はそれとは別に `SystemTimeUtil` で取得できます。

業務日付の更新（締め処理での日付繰り越しなど）は以下のように行います。

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の `initializeList` への登録が必須です。
- バッチの障害再実行時など特定プロセスだけ業務日付を変えたい場合は、システムプロパティ `-DBasicBusinessDateProvider.<区分>=yyyyMMdd` で上書きできます。
- 業務日付管理機能を使用するには `nablarch-common-jdbc` モジュールが必要です。

参照: libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s10, libraries-date.json:s2