**結論**: NablarchはOS日時（システム日時）と業務日付を別々のAPIで管理する機能を標準提供しています。システム日時は`SystemTimeUtil`、業務日付は`BusinessDateUtil`でそれぞれ独立して取得できます。

---

**根拠**:

### システム日時の取得

`BasicSystemTimeProvider`をコンポーネント定義に設定し、`SystemTimeUtil`で取得します。

**設定:**
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**取得:**
```java
// Date型で取得
Date systemDate = SystemTimeUtil.getDate();

// Timestamp型で取得
Timestamp ts = SystemTimeUtil.getTimestamp();

// LocalDateTime型で取得
LocalDateTime ldt = SystemTimeUtil.getLocalDateTime();
```

---

### 業務日付の取得

業務日付はデータベースのテーブルで管理します。テーブルのレイアウトは以下の通りです。

| カラム | 説明 |
|---|---|
| 区分 (PK) | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

**設定:**
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

**取得:**
```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（例：バッチ用の区分 "batch"）
String batchBizDate = BusinessDateUtil.getDate("batch");
```

---

### 締め処理での業務日付更新

締め処理の完了後に業務日付を翌営業日に進める場合は、`BasicBusinessDateProvider#setDate`を使います。

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

---

### 注意点

- **区分の活用**: オンライン処理とバッチ処理で更新タイミングが異なる場合、区分（`SEGMENT`）を分けて管理することができます（例: `"online"` / `"batch"`）。
- **障害再実行時の上書き**: バッチの再実行時に特定プロセスだけ過去日付で動かしたい場合は、システムプロパティで上書きできます。
  ```
  -DBasicBusinessDateProvider.batch=20260317
  ```
  ウェブアプリのように全機能が1プロセスの場合は、データベース上の日付を直接変更してください。
- 業務日付管理機能を使用するには `nablarch-common-jdbc` モジュールへの依存が必要です。

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc-nablarch-core-date-BusinessDateUtil.json:s7