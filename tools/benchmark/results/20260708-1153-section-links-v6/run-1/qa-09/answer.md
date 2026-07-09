**結論**: NablarchにはOS日時とは独立した**業務日付管理機能**が標準で備わっており、`BusinessDateUtil.getDate()` で業務日付を取得、`BasicBusinessDateProvider.setDate()` で更新（締め処理時）できます。システム日時（OS日時）は `SystemTimeUtil.getTimestamp()` / `getDate()` / `getLocalDateTime()` で取得します。

---

**根拠**:

### 業務日付の設定（コンポーネント定義）

業務日付はデータベースのテーブルで管理します。テーブルのレイアウト:

| 区分(PK) | 業務日付を識別するための値。文字列型 |
|---|---|
| 日付 | 業務日付。文字列型で値はyyyyMMdd形式 |

コンポーネント定義に `BasicBusinessDateProvider` を追加します（コンポーネント名は `businessDateProvider` 固定）:

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

### 業務日付の取得

```java
// デフォルト区分で取得 (yyyyMMdd形式)
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得
String bizDate = BusinessDateUtil.getDate("segment");
```

### 締め処理での業務日付更新

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

### システム日時（OS日時）の設定と取得

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

```java
// java.util.Date として取得
Date systemDate = SystemTimeUtil.getDate();

// java.sql.Timestamp として取得
Timestamp ts = SystemTimeUtil.getTimestamp();

// java.time.LocalDateTime として取得（Nablarch 6u1以降）
LocalDateTime ldt = SystemTimeUtil.getLocalDateTime();
```

---

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要なため、`BasicApplicationInitializer` の `initializeList` に設定すること
- 複数の業務日付（例：複数の締め区分）を持ちたい場合は、「区分」カラムで識別する設計になっている
- バッチ障害時の再実行で過去日付を使いたい場合は、JVMシステムプロパティ `-DBasicBusinessDateProvider.<区分>=20160317` で上書きできる（ウェブアプリでは不要でDBのレコードを直接変更する）

参照:
- 日付管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-date.md
  システム日時(OS日時)と業務日付の切り替えができる
  システム日時の管理機能を使うための設定
  システム日時を取得する
  業務日付管理機能を使うための設定
  業務日付を取得する
  業務日付を任意の日付に上書く
  業務日付を更新する