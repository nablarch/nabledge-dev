はい、Nablarchには業務日付を管理・取得する専用の機能があります。

## 業務日付管理機能の概要

Nablarchは**システム日時（OS日時）とは独立した「業務日付」**をデータベースで管理する仕組みを持っています。締め処理のように「業務上の日付」と「システム日時」を分けて扱いたいユースケースに対応しています。

## 設定方法

`BasicBusinessDateProvider` をコンポーネント定義に追加します。コンポーネント名は **`businessDateProvider`** と指定してください。

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

**テーブルレイアウト（例: `BUSINESS_DATE` テーブル）:**

| カラム | 型 | 説明 |
|---|---|---|
| 区分（PK） | 文字列 | 業務日付を識別する値（例: "00", "batch"） |
| 日付 | 文字列 | 業務日付（yyyyMMdd形式） |

複数の区分を持てるため、例えば「通常処理用」「バッチ処理用」など締め処理の種別ごとに別々の業務日付を管理できます。

## 業務日付の取得方法

`BusinessDateUtil` を使って取得します。

```java
// デフォルト区分で取得
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（例: バッチ用）
String bizDate = BusinessDateUtil.getDate("batch");
```

戻り値は `yyyyMMdd` 形式の文字列です。

## バッチ再実行時の日付上書き

障害時の再実行で過去の業務日付を指定したい場合は、システムプロパティで上書きできます。

```
-DBasicBusinessDateProvider.batch=20160317
```

これにより、そのプロセスのみ任意の業務日付で動作させることができます（他プロセス・DBの値には影響しません）。

## まとめ

- **DBで業務日付を管理** → `BasicBusinessDateProvider` + 業務日付テーブル
- **区分で複数日付を管理** → 締め処理の種別ごとに区分を分けて運用可能
- **取得は `BusinessDateUtil.getDate()`** → OS日時とは完全に独立
- **テスト・再実行時の切り替え** → コンポーネント差し替えまたはシステムプロパティで対応