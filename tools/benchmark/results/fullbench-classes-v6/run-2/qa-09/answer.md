**結論**: Nablarchは`BusinessDateUtil`で業務日付、`SystemTimeUtil`でOS日時を別々に取得する機能を提供しており、締め処理のような業務日付管理にも対応しています。区分（segment）で複数の業務日付（画面処理用・バッチ用など）を使い分けることも可能です。

**根拠**:

**1. 業務日付テーブルの設定**

業務日付はデータベースのテーブルで管理します。テーブルには区分（PK）と日付（yyyyMMdd形式）のカラムが必要です。

コンポーネント定義への追加:
```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <!-- テーブル名 -->
  <property name="tableName" value="BUSINESS_DATE" />
  <!-- 区分のカラム名 -->
  <property name="segmentColumnName" value="SEGMENT"/>
  <!-- 日付のカラム名 -->
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分省略時に使用されるデフォルト区分 -->
  <property name="defaultSegment" value="00"/>
  <!-- データベースアクセスに使用するトランザクションマネージャ -->
  <property name="transactionManager" ref="transactionManager" />
</component>

<!-- 初期化対象に追加 -->
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

システム日時の設定:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**2. 業務日付の取得**

```java
// デフォルト区分の業務日付を取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して業務日付を取得（例: 締め処理用の区分）
String closingDate = BusinessDateUtil.getDate("closing");
```

**3. OS日時（システム日時）の取得**

```java
// Date型で取得
Date systemTime = SystemTimeUtil.getDate();

// LocalDateTime型で取得
LocalDateTime systemTime = SystemTimeUtil.getLocalDateTime();

// yyyyMMdd形式の文字列で取得
String dateStr = SystemTimeUtil.getDateString();
```

**4. 締め処理後の業務日付更新**

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、指定区分の業務日付を更新する（日付はyyyyMMdd形式）
provider.setDate(segment, date);
```

**注意点**:
- `BasicBusinessDateProvider`は初期化が必要なため、`initializer`の`initializeList`への設定が必須です。
- バッチの障害再実行時に特定区分の日付を過去日に上書きしたい場合は、システムプロパティで指定できます:
  ```
  -DBasicBusinessDateProvider.batch=20160317
  ```
- ウェブアプリケーションのように1プロセスで全機能が動く場合は、データベースのレコードを直接更新するだけで対応できます。

参照: component/libraries/libraries-date.json:s5, component/libraries/libraries-date.json:s6, component/libraries/libraries-date.json:s7, component/libraries/libraries-date.json:s8, component/libraries/libraries-date.json:s10, javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s6, javadoc/javadoc-nablarch-core-date-BusinessDateUtil.json:s7, javadoc/javadoc-nablarch-core-date-SystemTimeUtil.json:s9