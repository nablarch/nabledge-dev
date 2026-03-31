**結論**: コード値のプルダウン入力には `n:codeSelect` タグを使用する。コードIDを指定するだけでコードマスタから選択肢を自動取得してプルダウンを表示する。

**根拠**:

## 1. コード値専用プルダウンタグ (n:codeSelect)

コード値のプルダウン表示には `n:codeSelect` カスタムタグを使用する。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" cssClass="form-control" />
```

### 主な属性

| 属性名 | 必須 | 説明 |
|---|---|---|
| name | ○ | フォームのプロパティ名 |
| codeId | ○ | コードID |
| pattern | | 使用するパターンのカラム名（デフォルト: 指定なし） |
| labelPattern | | ラベル整形パターン（`$NAME$`=コード名称、`$SHORTNAME$`=略称、`$VALUE$`=コード値）。デフォルト: `$NAME$` |
| withNoneOption | | 選択なしオプションを先頭に追加するか（デフォルト: `false`） |
| noneOptionLabel | | 選択なしオプションのラベル |

## 2. パターンを指定して表示するコード値を絞り込む

コードパターンを使用して機能ごとに表示するコード値を切り替えられる。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

ラベル整形パターンの指定例:

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

## 3. Maven依存関係

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code-jdbc</artifactId>
</dependency>
```

## 4. 入力値のバリデーション

選択されたコード値が有効かチェックするには `@CodeValue` アノテーションを使用する。

Bean Validation の場合:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

パターンを指定して有効値を制限する場合:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

## 5. 一般的なプルダウン (n:select) との違い

コード値を使わない一般的なプルダウンには `n:select` を使用し、アクションでリクエストスコープにリストを設定する。

```java
// アクション側
EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
context.setRequestScopedVar("industries", industries);
```

```jsp
<!-- JSP側 -->
<n:select listName="industries"
          elementValueProperty="industryCode"
          elementLabelProperty="industryName"
          name="form.industryCode"
          withNoneOption="true"
          cssClass="form-select" />
```

`n:codeSelect` はコードマスタから自動取得するため、アクション側でのリスト設定は不要。

**注意点**:
- カスタムタグでは言語指定によるコード値の取得はできない。言語指定でコード値を取得したい場合は、アクションで `CodeUtil` を直接使用すること
- タグリファレンスを使用するため、JSPに `<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>` ディレクティブの指定が必要

参照: `component/libraries/libraries-tag.json#s1`、`component/libraries/libraries-code.json#s2`、`component/libraries/libraries-tag_reference.json#s4`、`component/libraries/libraries-code.json#s6`
