十分な情報が揃いました。回答を生成します。

---

**結論**: Nablarchは業務日付とシステム日時(OS日時)を独立した機能として提供しています。業務日付は `BusinessDateUtil.getDate()` で取得し、システム日時は `SystemTimeUtil.getDate()` / `getTimestamp()` / `getLocalDateTime()` で取得できます。複数区分の管理も可能なため、締め処理向けに「オンライン用」「バッチ用」など区分を分けて管理できます。

---

**根拠**:

### 1. 業務日付の設定（コンポーネント定義）

業務日付はDBテーブルで管理します。まずコンポーネント定義に `BasicBusinessDateProvider` を追加します。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <!-- テーブル名 -->
  <property name="tableName" value="BUSINESS_DATE" />
  <!-- 区分のカラム名 -->
  <property name="segmentColumnName" value="SEGMENT"/>
  <!-- 日付のカラム名 -->
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略した場合に使用されるデフォルト区分 -->
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

管理するDBテーブルのレイアウト:

| カラム | 内容 |
|--------|------|
| 区分(PK) | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

### 2. システム日時の設定

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

### 3. 取得方法

**業務日付の取得** (`BusinessDateUtil`):

```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式のString）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（締め処理で区分を分ける場合）
String onlineDate = BusinessDateUtil.getDate("online");
String batchDate  = BusinessDateUtil.getDate("batch");

// 全区分の業務日付を取得
Map<String, String> allDates = BusinessDateUtil.getAllDate();
```

**システム日時の取得** (`SystemTimeUtil`):

```java
Date          sysDate      = SystemTimeUtil.getDate();
Timestamp     sysTimestamp = SystemTimeUtil.getTimestamp();
LocalDateTime sysLdt       = SystemTimeUtil.getLocalDateTime();
String        sysDateStr   = SystemTimeUtil.getDateString(); // yyyyMMdd形式
```

### 4. 業務日付の更新（締め処理での日付更新）

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

### 5. 業務日付の上書き（バッチ再実行時）

特定プロセスのみ業務日付を変更したい場合はシステムプロパティで指定できます。

```
# 区分"batch"の業務日付を2016/03/17に上書き
-DBasicBusinessDateProvider.batch=20160317
```

---

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要なため、`initializeList` への設定を忘れないこと
- 業務日付は文字列型（yyyyMMdd形式）で返却されます
- ウェブアプリケーションのように全機能が1プロセスで動く場合は、DBのレコードを直接更新する方法が簡単です

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-SystemTimeUtil.json:s9, javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc-nablarch-core-date-BusinessDateUtil.json:s7

---