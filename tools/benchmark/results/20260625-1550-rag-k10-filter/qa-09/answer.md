はい、Nablarchには業務日付を管理・取得する専用の機能があります。

**業務日付管理機能の概要**

業務日付はデータベースで管理され、複数の区分（例：バッチ処理用「batch」、Web用「00」など）ごとに異なる日付を持てます。これにより、OS日時（システム日時）と業務日付を完全に分離して管理できます。

---

**1. コンポーネント定義の設定**

`BasicBusinessDateProvider` をコンポーネント定義に追加します。

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分省略時に使用されるデフォルト区分 -->
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

テーブルのレイアウトは「区分（PK、文字列型）」と「日付（文字列型、yyyyMMdd形式）」の2カラムです。

---

**2. 業務日付の取得**

`BusinessDateUtil` を使って取得します。

```java
// デフォルト区分で取得
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（締め処理の区分など）
String closingDate = BusinessDateUtil.getDate("closing");
```

戻り値はいずれも `yyyyMMdd` 形式の文字列です。

---

**3. 締め処理での使い分け**

締め処理のようにシステム日時と業務日付を分けたい場合、以下のように使い分けられます。

- **OS日時（システム日時）**：`SystemTimeUtil` で取得
- **業務日付**：`BusinessDateUtil.getDate("closing")` のように専用区分で取得

区分をテーブルで管理することで、処理種別ごとに独立した業務日付を保持できます。

---

**4. バッチ再実行時の日付上書き**

障害時の再実行など、特定プロセスだけ業務日付を変えたい場合は、システムプロパティで上書きできます。

```
-DBasicBusinessDateProvider.batch=20160317
```

これにより、そのプロセスのみ指定した日付が業務日付として使用されます（他プロセスには影響しません）。