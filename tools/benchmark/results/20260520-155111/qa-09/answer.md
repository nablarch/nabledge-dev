**結論**: Nablarchの`BusinessDateUtil`を使用することで、OS日時（システム日時）とは独立した業務日付をデータベースで管理・取得できます。締め処理のように区分（セグメント）ごとに複数の業務日付を管理することも可能です。

**根拠**:

業務日付はデータベースのテーブルで管理します。テーブルのレイアウト:

| カラム | 内容 |
|--------|------|
| 区分（PK） | 業務日付を識別するための値（文字列型） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

**1. コンポーネント定義（`BasicBusinessDateProvider`の設定）**

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

**2. 業務日付の取得**

```java
// BusinessDateUtil で業務日付を取得
BusinessDateUtil.getDate();           // デフォルト区分で取得
BusinessDateUtil.getDate("segment");  // 区分を指定して取得
```

**3. 業務日付の更新（締め処理での日付切り替え）**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);  // 区分と日付を指定して更新
```

**4. システム日時（OS日時）の取得**

```java
// OS日時はSystemTimeUtilで取得
SystemTimeUtil.getDate();
```

**注意点**:
- `BasicBusinessDateProvider`は初期化が必要なため、`initializeList`への登録が必須です。
- 区分（セグメント）により複数の業務日付を管理できるため、「通常業務用」「締め処理用」など用途ごとに分けて管理可能です。
- バッチの障害再実行時など、特定プロセスだけ業務日付を上書きしたい場合は、システムプロパティで上書きできます（例: `-DBasicBusinessDateProvider.batch=20160317`）。

参照: `libraries-date.json:s5`, `libraries-date.json:s7`, `libraries-date.json:s8`, `libraries-date.json:s9`, `libraries-date.json:s10`