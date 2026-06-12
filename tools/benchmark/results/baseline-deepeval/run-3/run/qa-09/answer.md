**結論**: NablarchはOS日時とは独立した「業務日付」を管理する機能を標準で提供している。業務日付は `BusinessDateUtil` で取得し、DBのテーブルで管理するため、締め処理のようにシステム日時と業務日付を分けて扱う要件に対応できる。

---

**根拠**:

**システム日時 (OS日時) の取得**

```java
// OS日時はSystemTimeUtilで取得する
SystemTimeUtil.getDate();
```

コンポーネント定義に `BasicSystemTimeProvider` を設定する:

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**業務日付の取得**

```java
// 業務日付はBusinessDateUtilで取得する
BusinessDateUtil.getDate();
```

**業務日付の設定 (コンポーネント定義)**

業務日付はDBテーブルで管理する。テーブルのレイアウト:

| カラム | 内容 |
|--------|------|
| 区分 (PK) | 業務日付を識別する文字列 |
| 日付 | yyyyMMdd形式の文字列 |

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

**業務日付の更新 (締め処理後の日付を進める)**

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// 区分と新しい日付を指定して更新する
provider.setDate(segment, date);
```

**特定プロセスのみ業務日付を上書く (バッチ再実行時など)**

システムプロパティで指定することで、そのプロセスのみ業務日付を上書ける:

```
-DBasicBusinessDateProvider.batch=20160317
```

---

**注意点**:

- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の `initializeList` に必ず追加すること
- 区分(Segment)を使って複数の業務日付を管理できる(例: 「通常締め」「月次締め」など用途別に区分を分けて管理)
- ウェブアプリのように単一プロセスの場合は、DBの値を直接変更すれば全機能に反映される

参照: libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s7, libraries-date.json:s8, libraries-date.json:s9, libraries-date.json:s10

---