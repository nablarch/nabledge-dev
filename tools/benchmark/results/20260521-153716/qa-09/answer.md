セクションが読み込めました。回答を生成します。

---

**結論**: Nablarchの業務日付管理機能（`BusinessDateUtil` / `BasicBusinessDateProvider`）を使用することで、OS日時とは独立した業務日付をデータベースで管理・取得できます。締め処理などで複数の業務日付（区分）を並行管理することも可能です。

**根拠**:

### システム日時と業務日付の違い

| 種別 | 取得方法 | データソース |
|---|---|---|
| システム日時（OS日時） | `SystemTimeUtil` | OS |
| 業務日付 | `BusinessDateUtil` | データベース（専用テーブル） |

コンポーネント定義で指定するクラスを差し替えるだけで取得方法を切り替えることができます（テストでの差し替えも容易）。

### 業務日付テーブルのレイアウト

| カラム | 内容 |
|---|---|
| 区分（PK） | 業務日付を識別するための値。文字列型 |
| 日付 | 業務日付。文字列型でyyyyMMdd形式 |

締め処理のように複数の業務日付を管理したい場合は、区分（セグメント）を使い分けます。

### 設定（コンポーネント定義）

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

初期化が必要なため、`initializer` の `initializeList` に追加してください。

### 業務日付の取得

```java
// BusinessDateUtil を使用して業務日付を取得
BusinessDateUtil.getDate();               // デフォルト区分の業務日付を取得
BusinessDateUtil.getDate("closing");      // 区分を指定して取得（例：締め処理用の区分）
```

### 業務日付の更新（締め処理など）

```java
// システムリポジトリから BasicBusinessDateProvider を取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDate メソッドで業務日付を更新する
provider.setDate(segment, date);
```

### バッチ再実行時の業務日付上書き

障害時の再実行で特定プロセスのみ過去日付を使いたい場合は、システムプロパティで上書き可能です。

```
-DBasicBusinessDateProvider.batch=20160317
```

（区分が `batch` の日付を `2016/03/17` に上書く例）

**注意点**:
- `BasicBusinessDateProvider` はコンポーネント定義で初期化リスト（`initializeList`）に追加する必要があります。設定しないと起動時エラーになります。
- ウェブアプリケーションのように全機能が1プロセス内で動作する場合は、データベース上の日付を直接更新すれば全機能に反映されます。
- バッチでのシステムプロパティ上書きはそのプロセスのみに影響します。

参照: `component/libraries/libraries-date.json:s7`, `component/libraries/libraries-date.json:s8`, `component/libraries/libraries-date.json:s10`, `component/libraries/libraries-date.json:s9`, `component/libraries/libraries-date.json:s2`

---