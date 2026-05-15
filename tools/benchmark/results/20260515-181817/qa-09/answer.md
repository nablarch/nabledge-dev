**結論**: Nablarch 6 では `BusinessDateUtil` を使用することで、OS日時ではなく業務上の日付を取得できます。業務日付はデータベースで管理され、複数の「区分」で分けて管理できるため、締め処理などでシステム日時と業務日付を独立して扱うことが可能です。

**根拠**:

**業務日付管理機能の概要**

Nablarch の業務日付管理機能では、コンポーネント定義で指定されたクラスを切り替えることで、OS日時と業務日付を分けて取得できます。業務日付はデータベースのテーブルで管理され、「区分（セグメント）」という概念を使って複数の業務日付を同時に管理できます。

締め処理のように「処理対象の業務日付」と「実行時のシステム日時」を分けて管理したいケースに適しています。

**設定方法**

`BasicBusinessDateProvider` をコンポーネント定義に追加します。コンポーネント名は `businessDateProvider` と指定し、初期化リストにも含める必要があります。

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

管理テーブルのレイアウト:

| カラム | 説明 |
|--------|------|
| 区分 (PK) | 業務日付を識別する文字列値（例: "00", "batch", "closing"） |
| 日付 | 業務日付（文字列型、yyyyMMdd形式） |

**取得方法**

```java
// デフォルト区分で業務日付を取得
BusinessDateUtil.getDate();

// 区分を指定して取得
BusinessDateUtil.getDate("closing");
```

**業務日付の更新方法**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date);
```

**注意点**:

- 業務日付テーブルの初期データは事前に登録しておく必要があります
- 初期化リストへの登録を忘れると起動時にエラーになります
- バッチ障害時の再実行などで特定プロセスのみ業務日付を上書きしたい場合は、JVMのシステムプロパティで上書き可能です（例: `-DBasicBusinessDateProvider.batch=20160317`）
- ウェブアプリケーションのように全機能が1プロセスで動く場合は、DBのテーブル値を直接更新する方が簡単です

参照: `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s7`, `component/libraries/libraries-date.json#s8`, `component/libraries/libraries-date.json#s9`, `component/libraries/libraries-date.json#s10`