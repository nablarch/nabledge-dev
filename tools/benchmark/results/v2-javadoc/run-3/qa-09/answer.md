十分な情報が得られました。回答を生成します。

---

**結論**: Nablarchは `BusinessDateUtil` を使用することで、OS日時とは独立した業務日付を取得できます。業務日付はデータベースのテーブルで管理し、区分（segment）によって複数の業務日付（例：オンライン用・バッチ用）を使い分けることもできます。

**根拠**:

### 1. 業務日付管理機能の設定

`BasicBusinessDateProvider` をコンポーネント定義に追加します。業務日付はDBテーブルで管理します（テーブル構造：区分(PK)・日付）。

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

### 2. 業務日付の取得（アプリケーションコード）

```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（例：締め処理用の区分）
String closingDate = BusinessDateUtil.getDate("closing");
```

システム日時（OS日時）が必要な場合は `SystemTimeUtil` を使用します：

```java
// OS日時を取得
Date sysDate = SystemTimeUtil.getDate();
Timestamp sysTimestamp = SystemTimeUtil.getTimestamp();
LocalDateTime sysLocalDateTime = SystemTimeUtil.getLocalDateTime();
```

### 3. 業務日付の更新（締め処理での日付更新）

締め処理の実行後に業務日付を翌営業日へ進める場合：

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);  // dateはyyyyMMdd形式
```

### 4. バッチ再実行時に特定日付で上書きたい場合

JVM起動時のシステムプロパティで上書きできます：

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付のデフォルト動作はキャッシュ有り（1リクエスト中は同じ値が返る）。リクエストごとにDBから取得したい場合は `setCacheEnabled(false)` を設定してください。
- 区分を活用することで、オンライン処理とバッチ処理で異なる業務日付（更新タイミングが違う場合など）を管理できます。

参照: `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s6`, `component/libraries/libraries-date.json:s7`, `component/libraries/libraries-date.json:s8`, `component/libraries/libraries-date.json:s9`, `component/libraries/libraries-date.json:s10`, `javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s6`, `javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s7`, `javadoc/javadoc-nablarch-core-date-SystemTimeUtil.json:s9`

---