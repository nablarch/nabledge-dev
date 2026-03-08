# コード管理

## 機能概要

アプリケーションで使用する値と名称とのマッピングを管理する機能。

> **重要**: 動的に変化するコード（「商品コード」「企業コード」等）は管理対象外。このような情報はアプリケーションでマスタ用テーブルを作成して対処すること。

> **重要**: この機能を使用すると、コードの名称を持つテーブルとコード値を持つテーブルにRDBMSの参照整合性制約を設定できない。制約チェックには :ref:`code-validation` を使用すること。

> **補足**: 静的なコード情報はenumで表現するほうが良い。理由: (1) DBを使ったコード定義は大掛かりでメンテナンスコストが高い (2) DB使用時はJava上のコード値定数との二重メンテナンスが発生する。ただしNablarchはenumの値とDBの値との相互変換機能を持たないため、enumの値をDBに登録できない。Domaを使用することでenumのDB登録が可能になる。Doma使用時は :ref:`doma_adaptor` を参照。

**国際化**: 言語ごとに名称を管理可能。詳細は :ref:`code-use_multilingualization` を参照。

**テーブル管理**: 値及び名称の情報をデータベース上で管理する。事前にDBにテーブルを作成し、静的なコード情報をテーブルに登録しておくこと。詳細は :ref:`code-setup_table` を参照。

## モジュール一覧

**モジュール**:
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

## コード管理機能を使用する為の初期設定

コード管理に必要なテーブル構造と設定ファイル例。

**テーブル構造**

コード情報は以下の2テーブルで管理する:
- **コードパターンテーブル**: 各VALUEの使用可否フラグ（PATTERN列）を管理
- **コード名称テーブル**: 名称・略称・オプション名称を管理

2テーブルはIDとVALUEで紐付く。

各カラムの用途:

| カラム名 | 用途 |
|---|---|
| ID | コード情報を一意に識別するID（性別区分・住所区分ごとに一意） |
| VALUE | コード情報内の名称を識別する値（例: `male`, `female`） |
| PATTERN | 値を使用するか否かのフラグ（`0`または`1`）。不要な場合は省略可 |
| LANG | 言語（日本語のみなら`ja`を設定） |
| SORT_ORDER | ソート順（昇順で結果が返される） |
| NAME | VALUEに対応した名称 |
| SHORT_NAME | VALUEに対応した略称 |
| OPTIONAL_NAME | 名称・略称以外の表示文言（カラム名・カラム数は任意定義可能） |

**設定ファイルのポイント**:
- `BasicCodeManager` のコンポーネント名は **codeManager** とすること
- `BasicStaticDataCache` の `loadOnStartup` 設定値は :ref:`static_data_cache-cache_timing` を参照
- `BasicCodeLoader` と `BasicStaticDataCache` は初期化対象リストに設定すること

```xml
<component name="codeLoader" class="nablarch.common.code.BasicCodeLoader">
  <property name="codePatternSchema">
    <component class="nablarch.common.code.schema.CodePatternSchema">
      <!-- テーブル名およびカラム名を設定する -->
    </component>
  </property>
  <property name="codeNameSchema">
    <component class="nablarch.common.code.schema.CodeNameSchema">
      <!-- テーブル名およびカラム名を設定する -->
    </component>
  </property>
</component>

<component name="codeCache" class="nablarch.core.cache.BasicStaticDataCache">
  <property name="loader" ref="codeLoader"/>
  <property name="loadOnStartup" value="false"/>
</component>

<component name="codeManager" class="nablarch.common.code.BasicCodeManager">
  <property name="codeDefinitionCache" ref="codeCache"/>
</component>

<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="codeLoader"/>
      <component-ref name="codeCache"/>
    </list>
  </property>
</component>
```

## 機能毎に使用するコード情報を切り替える

機能ごとに表示・非表示を切り替えたい場合は、コードパターンテーブルにパターン列を定義して使用する。

パターン列は `CodePatternSchema.patternColumnNames` に設定することで使用可能。設定方法は :ref:`code-setup_table` を参照。

パターン指定時のカラム名は、設定ファイルに設定したカラム名と**厳密に一致**させる必要がある。

**コードパターンテーブル例（PATTERN1とPATTERN2を定義、PATTERN2ではOTHERを非表示）**:

| ID | VALUE | PATTERN1 | PATTERN2 |
|---|---|---|---|
| GENDER | MALE | 1 | 1 |
| GENDER | FEMALE | 1 | 1 |
| GENDER | OTHER | 1 | 0 |

**コード名称テーブル例**:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | FEMALE | ja | 2 | 女性 | 女 |
| GENDER | OTHER | ja | 3 | その他 | 他 |

**Javaでのパターン指定取得**:
```java
// PATTERN1のリストを取得（[MALE, FEMALE, OTHER]が取得できる）
List<String> pattern1 = CodeUtil.getValues("GENDER", "PATTERN1");

// PATTERN2のリストを取得（[MALE, FEMALE]が取得できる）
List<String> pattern2 = CodeUtil.getValues("GENDER", "PATTERN2");
```

**JSP（カスタムタグライブラリ）でのパターン指定**（`pattern`属性にパターン名を指定）:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```
PATTERN2を指定すると男性と女性のみが出力される。カスタムタグライブラリの詳細は :ref:`tag-code_input_output` を参照。

## 名称の多言語化対応

コード名称テーブルに言語ごとのデータを用意することで多言語化対応が可能。

**コード名称テーブル例（`ja`と`en`をサポート）**:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | FEMALE | ja | 2 | 女性 | 女 |
| GENDER | OTHER | ja | 3 | その他 | 他 |
| GENDER | MALE | en | 1 | Male | M |
| GENDER | FEMALE | en | 2 | Female | F |
| GENDER | OTHER | en | 3 | Unknown | - |

**言語指定でコード情報を取得**（`CodeUtil` を使用）:
```java
// 名称
CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE);    // -> 男性
CodeUtil.getName("GENDER", "MALE", Locale.ENGLISH);     // -> Male

// 略称
CodeUtil.getShortName("GENDER", "MALE", Locale.JAPANESE); // -> 男
CodeUtil.getShortName("GENDER", "MALE", Locale.ENGLISH);  // -> M
```

> **重要**: JSP用カスタムタグライブラリでは言語指定による値の取得はできない。カスタムタグライブラリが使用する言語情報の詳細は :ref:`tag-code_input_output` を参照。

## 画面などで表示する名称のソート順を定義する

コード名称テーブルのSORT_ORDERカラムに設定した値の昇順で一覧が返される。ソート順は言語ごとに設定可能。

**コード名称テーブル例（MALE→FEMALE→OTHERの順に表示）**:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | FEMALE | ja | 2 | 女性 | 女 |
| GENDER | OTHER | ja | 3 | その他 | 他 |

カスタムタグライブラリの `codeSelect` を使用した場合、`MALE(男性)`→`FEMALE(女性)`→`OTHER(その他)` の順に表示される。

## 名称、略称以外の名称を定義する

名称・略称以外の表示文言が必要な場合は、コード名称テーブルにオプション名称カラムを定義する。カラム名・カラム数は任意定義可能。

オプション名称カラムの設定方法は `CodePatternSchema.patternColumnNames` に設定する。設定ファイルへの設定方法は :ref:`code-setup_table` を参照。

オプション名称取得時のカラム名は設定ファイルに設定したカラム名と**厳密に一致**させる必要がある。

**コード名称テーブル例（`FORM_NAME`と`KANA_NAME`のオプション名称カラムを定義）**:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME | FORM_NAME | KANA_NAME |
|---|---|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 | Male | おとこ |
| GENDER | FEMALE | ja | 2 | 女性 | 女 | Female | おんな |
| GENDER | OTHER | ja | 3 | その他 | 他 | Other | そのた |

**Javaでのオプション名称取得**（`CodeUtil` を使用）:
```java
CodeUtil.getOptionalName("GENDER", "MALE", "KANA_NAME"); // -> おとこ
CodeUtil.getOptionalName("GENDER", "FEMALE", "FORM_NAME", Locale.JAPANESE); // -> Female
```

**JSP（カスタムタグライブラリ）でのオプション名称表示**（`optionColumnName`にカラム名、`labelPattern`に `$OPTIONALNAME$` を指定）:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" optionColumnName="KANA_NAME" cssClass="form-control" labelPattern="$OPTIONALNAME$"/>
```

## 入力値が有効なコード値かチェックする

入力値がコードの有効範囲内かをアノテーションのみでチェック可能。

**:ref:`bean_validation` を使用する場合** — `CodeValue` アノテーションを使用:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

**:ref:`nablarch_validation` を使用する場合** — `CodeValue` アノテーションを使用:
```java
@CodeValue(codeId = "GENDER")
public void setGender(String gender) {
  this.gender = gender;
}
```

入力画面で :ref:`パターン <code-use_pattern>` を使用して選択できる値を制限した場合、バリデーション時にも `pattern` 属性でそのパターン内で有効な値かをチェックできる:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

> **補足**: :ref:`ドメインバリデーション <bean_validation-domain_validation>` では1ドメインにつき1パターンしか指定できない。複数パターンに対応するにはパターンごとにドメインを定義する（全パターン分定義する必要はなく、バリデーションで必要なドメインのみでよい）。
> ```java
> public class SampleDomainBean {
>   // PATTERN1用のドメイン
>   @CodeValue(codeId = "FLOW_STATUS", pattern = "PATTERN1")
>   String flowStatusGeneral;
>
>   // PATTERN2用のドメイン
>   @CodeValue(codeId = "FLOW_STATUS", pattern = "PATTERN2")
>   String flowStatusGuest;
> }
> ```
