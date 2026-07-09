**結論:** NablarchにはOS日時と独立して業務日付をデータベースで管理する「業務日付管理機能」がある。OS日時は`SystemTimeUtil`、業務日付は`BusinessDateUtil`でそれぞれ取得でき、締め処理でも区分(segment)を使って複数の業務日付を管理できる。

**根拠:**

**業務日付管理機能の設定**

業務日付はデータベースのテーブルで管理する。テーブルのレイアウトは次のとおり:

| カラム | 説明 |
|--------|------|
| 区分(PK) | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

コンポーネント定義に`BasicBusinessDateProvider`を追加する（初期化リストへの登録が必要）:

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

**業務日付の取得**

`BusinessDateUtil`を使用する:

```java
// デフォルト区分の業務日付を取得（戻り値: yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（締め処理で区分ごとに管理する場合）
String bizDate = BusinessDateUtil.getDate("batch");

// 全区分の業務日付をMapで取得（キー:区分, 値:yyyyMMdd）
Map<String, String> allDates = BusinessDateUtil.getAllDate();
```

**システム日時(OS日時)の取得**

`SystemTimeUtil`を使用する:

```java
// Date型で取得
Date sysDate = SystemTimeUtil.getDate();

// Timestamp型で取得
Timestamp sysTimestamp = SystemTimeUtil.getTimestamp();

// LocalDateTime型で取得
LocalDateTime sysLocalDt = SystemTimeUtil.getLocalDateTime();
```

**締め処理での業務日付の更新**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);  // dateはyyyyMMdd形式
```

バッチの障害時再実行など、特定プロセスだけ業務日付を上書きしたい場合はシステムプロパティで指定できる:

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点:**
- 業務日付管理機能を使う場合は`nablarch-common-jdbc`への依存関係が必要
- `BasicBusinessDateProvider`は初期化が必要なため、`initializeList`への登録を忘れずに

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