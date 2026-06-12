セクション内容を読み込みました。Step 5〜7で回答を生成・検証します。

---

**結論**: Nablarchは `SystemTimeUtil`（OS日時）と `BusinessDateUtil`（業務日付）を独立して提供しており、それぞれ異なるコンポーネントで管理できる。業務日付はDB管理の `BasicBusinessDateProvider` が担い、`setDate()` で更新可能なため、締め処理での日付進行にも対応できる。

**根拠**:

コンポーネント定義でシステム日時と業務日付を別々に設定する。

```xml
<!-- システム日時（OS日時）プロバイダ -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />

<!-- 業務日付プロバイダ（DBで管理） -->
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <property name="defaultSegment" value="00"/>
  <property name="transactionManager" ref="transactionManager" />
</component>

<!-- 初期化対象に登録 -->
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="businessDateProvider" />
    </list>
  </property>
</component>
```

業務日付テーブルのレイアウトは以下の通り（区分(PK) と 日付(yyyyMMdd形式) の2カラム）:

| 区分(PK) | 日付 |
|---|---|
| 業務日付を識別する文字列値 | yyyyMMdd形式の文字列 |

取得はそれぞれ専用ユーティリティを使う:

```java
// OS日時の取得
SystemTimeUtil.getDate();         // システム日時(OS日時)

// 業務日付の取得（区分省略時はdefaultSegmentが使われる）
BusinessDateUtil.getDate();       // 業務日付
BusinessDateUtil.getDate("01");   // 区分を指定して取得
```

締め処理などで業務日付を進める場合は `setDate()` を使う:

```java
// システムリポジトリからBasicBusinessDateProviderを取得する
BusinessDateProvider provider = SystemRepository.get("businessDateProvider");

// setDateメソッドを呼び出し、更新する
provider.setDate(segment, date);
```

バッチ障害時に特定の区分だけ過去日付で再実行したい場合は、システムプロパティで上書きできる:

```
-DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- 業務日付管理には `nablarch-common-jdbc` モジュールの追加が必要（`nablarch-core` はOS日時のみで使用可）
- `BasicBusinessDateProvider` は初期化対象リストへの登録が必要
- ウェブアプリのように全機能が1プロセスで動く場合は、システムプロパティではなくDBの日付を直接変更すればよい

参照: `libraries-date.json:s2`, `libraries-date.json:s3`, `libraries-date.json:s5`, `libraries-date.json:s6`, `libraries-date.json:s7`, `libraries-date.json:s8`, `libraries-date.json:s9`, `libraries-date.json:s10`

---