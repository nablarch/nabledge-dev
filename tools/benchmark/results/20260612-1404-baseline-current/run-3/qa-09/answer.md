**結論**: NablarchはOS日時と業務日付を分離管理する機能を標準提供しており、`SystemTimeUtil`でOS日時を、`BusinessDateUtil`で業務日付を独立して取得できます。業務日付はデータベーステーブルで管理され、区分（segment）によって複数の業務日付（例：オンライン用・バッチ用）を使い分けることも可能です。

---

**根拠**:

**1. システム日時（OS日時）の取得**

コンポーネント定義に `BasicSystemTimeProvider` を `systemTimeProvider` という名前で登録します。

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

アプリケーションコードでは `SystemTimeUtil` を使用します。

```java
// Date型で取得
Date sysDate = SystemTimeUtil.getDate();
// Timestamp型で取得
Timestamp sysTs = SystemTimeUtil.getTimestamp();
// LocalDateTime型で取得
LocalDateTime sysLdt = SystemTimeUtil.getLocalDateTime();
// yyyyMMdd形式の文字列で取得
String sysDateStr = SystemTimeUtil.getDateString();
```

---

**2. 業務日付の設定と取得**

業務日付はデータベーステーブルで管理します。テーブルのレイアウトは以下の通りです。

| カラム | 説明 |
|--------|------|
| 区分（PK） | 業務日付を識別するための文字列 |
| 日付 | 業務日付（yyyyMMdd形式の文字列） |

コンポーネント定義に `BasicBusinessDateProvider` を追加します（初期化対象への登録も必要）。

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

アプリケーションコードでは `BusinessDateUtil` を使用します。

```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して業務日付を取得（例：バッチ処理用の区分"batch"）
String batchBizDate = BusinessDateUtil.getDate("batch");

// 全区分の業務日付をMapで取得
Map<String, String> allDates = BusinessDateUtil.getAllDate();
```

---

**3. 締め処理での業務日付更新**

`BasicBusinessDateProvider` の `setDate` メソッドでデータベース上の業務日付を更新します。

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// 指定区分の業務日付を更新（yyyyMMdd形式）
provider.setDate("00", "20260616");
```

---

**4. バッチ再実行時の業務日付上書き（バッチ限定）**

障害再実行時など、特定プロセスのみ任意の日付で動かしたい場合はシステムプロパティで上書きできます。

```
-DBasicBusinessDateProvider.batch=20160317
```

---

**注意点**:
- 業務日付管理機能の使用には `nablarch-common-jdbc` モジュールが必要です（システム日時管理のみなら `nablarch-core` だけで可）。
- `BasicBusinessDateProvider` のキャッシュ機能はデフォルトで有効です。オンライン処理では1リクエスト中はキャッシュされるため、同一リクエスト内で業務日付を更新しても反映されません。
- `setDate` に渡す日付が `yyyyMMdd` 形式でない場合、または区分や日付が null/空文字列の場合は `IllegalArgumentException` がスローされます。

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10, javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc-nablarch-core-date-BusinessDateUtil.json:s7, javadoc-nablarch-core-date-BusinessDateUtil.json:s8, javadoc-nablarch-core-date-BasicBusinessDateProvider.json:s29