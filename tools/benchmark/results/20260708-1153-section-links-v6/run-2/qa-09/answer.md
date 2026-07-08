**結論**: Nablarchには「日付管理」機能があり、OS日時（システム日時）と業務日付を独立して管理・取得できます。業務日付はデータベースで管理され、`BusinessDateUtil`で取得します。

**根拠**:

**1. 業務日付の設定（コンポーネント定義）**

業務日付はデータベースのテーブルで管理します。テーブルレイアウト：

| カラム | 内容 |
|---|---|
| 区分（PK） | 業務日付を識別する文字列 |
| 日付 | 業務日付（yyyyMMdd形式の文字列） |

`BasicBusinessDateProvider` をコンポーネント定義に追加します：

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
// BusinessDateUtilで業務日付を取得する
String bizDate = BusinessDateUtil.getDate(); // デフォルト区分
String bizDate = BusinessDateUtil.getDate("batch"); // 区分指定
```

**3. OS日時（システム日時）の設定と取得**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

```java
// SystemTimeUtilでOS日時を取得する
Date sysDate = SystemTimeUtil.getDate();
```

**4. 業務日付の更新（締め処理後の日付進行）**

```java
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");
provider.setDate(segment, date); // 例: provider.setDate("00", "20260101")
```

**5. バッチ実行時に業務日付を上書きしたい場合**

システムプロパティで特定プロセスのみ業務日付を上書きできます：

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付管理機能は `nablarch-common-jdbc` モジュールへの依存が必要です
- `BasicBusinessDateProvider` は初期化が必要なため、`initializer` の `initializeList` に必ず追加してください
- ウェブアプリケーションのように全機能が1プロセス内で動く場合は、DBのレコードを直接更新することで業務日付を変更できます

参照:
- 日付管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-date.md
  システム日時(OS日時)と業務日付の切り替えができる
  業務日付管理機能を使うための設定
  業務日付を取得する
  システム日時の管理機能を使うための設定
  システム日時を取得する
  業務日付を任意の日付に上書く
  業務日付を更新する