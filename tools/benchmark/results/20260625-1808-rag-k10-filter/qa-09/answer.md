はい、Nablarchには業務日付を管理・取得する専用の機能があります。

## 業務日付管理機能の概要

業務日付はデータベースで管理し、OS日時とは独立して取得できます。締め処理のように「システム日時と業務日付を分けて管理したい」用途に適しています。

## セットアップ

まずデータベースに業務日付テーブルを用意します（区分(PK)と日付の2カラム構成）。

次に `BasicBusinessDateProvider` をコンポーネント定義に追加します：

```xml
<component name="businessDateProvider" class="nablarch.core.date.BasicBusinessDateProvider">
  <property name="tableName" value="BUSINESS_DATE" />
  <property name="segmentColumnName" value="SEGMENT"/>
  <property name="dateColumnName" value="BIZ_DATE"/>
  <!-- 区分を省略した場合に使用されるデフォルト区分 -->
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

コンポーネント名は **`businessDateProvider`** と指定する必要があります。

## 業務日付の取得

`BusinessDateUtil` を使って取得します：

```java
// デフォルト区分で取得（yyyyMMdd形式の文字列）
String bizDate = BusinessDateUtil.getDate();

// 区分を指定して取得（例：締め処理用の区分）
String bizDate = BusinessDateUtil.getDate("closing");
```

**区分**を使うことで、用途別（通常業務用・締め処理用など）に複数の業務日付をデータベース上で管理し、それぞれ独立して取得できます。

## バッチ再実行時の上書き

障害時の再実行で過去日付を業務日付として使いたい場合は、システムプロパティで上書きできます：

```
-DBasicBusinessDateProvider.batch=20160317
```

形式：`BasicBusinessDateProvider.<区分>=yyyyMMdd`

これにより該当プロセスのみ任意の日付で動作させることができます。