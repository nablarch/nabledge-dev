**結論**: Nablarchには業務日付管理機能があり、`BusinessDateUtil`を使ってデータベースで管理された業務日付を取得できます。「区分」で複数の業務日付を分けて管理できるため、締め処理と通常処理で別の業務日付を持つことも可能です。

**根拠**:

業務日付はデータベースのテーブルで管理します。テーブルのレイアウトは以下のとおりです。

| カラム | 内容 |
|--------|------|
| 区分（PK） | 業務日付を識別するための文字列値 |
| 日付 | 業務日付（yyyyMMdd形式の文字列） |

**1. コンポーネント定義の設定**

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
  <!-- トランザクションマネージャ -->
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

業務日付の取得には `BusinessDateUtil` を使用します（区分を指定して複数の業務日付を使い分けられます）。

**3. 業務日付の更新（締め処理での日付更新）**

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

**注意点**:
- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の初期化対象リストに必ず追加してください。
- バッチ障害時の再実行で過去日付を使いたい場合は、システムプロパティで業務日付を上書きできます。形式: `-DBasicBusinessDateProvider.<区分>=yyyyMMdd`（例: `-DBasicBusinessDateProvider.batch=20160317`）。ただしこの上書きは再実行プロセスのみに効果があるため、ウェブアプリケーションのように全機能が1プロセスで動く場合はデータベースの値を直接変更する方が適切です。

参照: libraries-date.json:s2, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---