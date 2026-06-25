はい、Nablarchには業務日付を管理・取得する専用機能があります。

## 業務日付管理機能の設定

`BasicBusinessDateProvider` をコンポーネント定義に追加します。業務日付はデータベースのテーブルで管理します。

**テーブルレイアウト:**
| 区分（PK） | 日付（yyyyMMdd形式） |
|---|---|
| 締め処理用区分（例: `"closing"`） | 業務上の基準日 |
| デフォルト区分（例: `"00"`） | 通常業務日付 |

**コンポーネント定義（component-configuration.xml）:**
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

## 業務日付の取得方法

`BusinessDateUtil` を使います。締め処理では区分を指定することで、通常業務とは独立した日付を管理できます。

```java
// デフォルト区分の業務日付を取得
String bizDate = BusinessDateUtil.getDate();

// 締め処理用区分を指定して取得（区分でシステム日時と業務日付を分離）
String closingDate = BusinessDateUtil.getDate("closing");
```

## 再実行時の業務日付上書き

バッチ障害時の再実行で過去日付を使いたい場合、システムプロパティで特定プロセスのみ上書きできます。

```
-DBasicBusinessDateProvider.closing=20260601
```

これにより、対象プロセスだけ業務日付を変更でき、他のプロセスへの影響を避けられます。

## まとめ

- **システム日時**（OS日時）: `SystemTimeUtil` で取得
- **業務日付**: `BusinessDateUtil.getDate(segment)` で取得
- 区分（segment）を使い分けることで、締め処理用・通常処理用など複数の業務日付を独立して管理できます