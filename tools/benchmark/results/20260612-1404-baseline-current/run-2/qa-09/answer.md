**結論**: Nablarchには `BusinessDateUtil` を使った業務日付管理機能が標準で提供されており、OS日時（`SystemTimeUtil`）と業務日付を明確に分けて取得・管理できます。締め処理での日付更新も `BasicBusinessDateProvider.setDate()` で行えます。

---

**根拠**:

**システム日時（OS日時）の取得**

コンポーネント定義に `BasicSystemTimeProvider` を追加し、`SystemTimeUtil` で取得します：

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

---

**業務日付の設定とDBテーブル構成**

業務日付はDBテーブルで「区分」ごとに複数管理できます：

| カラム | 説明 |
|---|---|
| 区分（PK） | 業務日付を識別する文字列（例：`online`、`batch`） |
| 日付 | 業務日付（yyyyMMdd形式） |

コンポーネント定義：

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略した場合に使用されるデフォルト区分 -->
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>
```

初期化リストへの追加も必要です。

---

**業務日付の取得**

```java
// デフォルト区分で取得
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得
String batchDate = BusinessDateUtil.getDate("batch");

// 全区分の業務日付を取得
Map<String, String> allDates = BusinessDateUtil.getAllDate();
```

---

**締め処理での業務日付更新**

```java
// SystemRepositoryからproviderを取得して更新
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);
```

---

**バッチ再実行時の任意日付上書き（障害対応）**

特定プロセスのみ過去日付で実行したい場合は、起動時のシステムプロパティで指定します：

```
-DBasicBusinessDateProvider.batch=20160317
```

この方法では他のプロセスに影響を与えず、再実行プロセスだけ業務日付を上書けます。

---

**注意点**:
- 業務日付はDBテーブルで管理するため、`nablarch-common-jdbc` への依存が必要です
- `BasicBusinessDateProvider` は初期化リスト（`initializer`）への登録が必須です
- コンポーネント定義のシステム日時を切り替えることで、テスト時に日時・日付を差し替えることも可能です

参照: `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s6`, `component/libraries/libraries-date.json:s7`, `component/libraries/libraries-date.json:s8`, `component/libraries/libraries-date.json:s9`, `component/libraries/libraries-date.json:s10`, `javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s6`, `javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s7`