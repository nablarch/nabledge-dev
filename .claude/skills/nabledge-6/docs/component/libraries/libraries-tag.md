# Jakarta Server Pagesカスタムタグ

## 機能概要

> **補足**: Nablarch 5ではJSPカスタムタグと呼ばれていた。Java EEがEclipse Foundationに移管され仕様名が変わったことに伴い「Jakarta Server Pagesカスタムタグ」に名称変更された。変更されたのは名称のみで、機能的な差はない。

ウェブアプリケーションの画面作成を支援するカスタムタグを提供する。

### 制約条件

- Jakarta Server Pages 3.1以降をサポートしているWebコンテナで動作
- 条件分岐やループなどの制御にはJakarta Standard Tag Libraryを使用
- XHTML 1.0 Transitionalに対応した属性をサポート
- クライアントのJavaScriptが必須 (:ref:`tag-onclick_override` 参照)
- GETリクエストで一部のカスタムタグが使用できない (:ref:`tag-using_get` 参照)

### HTML5属性とinput要素サポート

> **重要**: HTML5で追加された属性は :ref:`動的属性 <dynamic_attribute>` を使用して記述できる。次の属性は予めカスタムタグの属性として定義している:

**追加属性**:
- autocomplete (input、password、form)
- autofocus (input、textarea、select、button)
- placeholder (text、password、textarea)
- maxlength (textarea)
- multiple (input)

**追加されたinput要素**:
- :ref:`tag-search_tag` (検索テキスト)
- :ref:`tag-tel_tag` (電話番号)
- :ref:`tag-url_tag` (URL)
- :ref:`tag-email_tag` (メールアドレス)
- :ref:`tag-date_tag` (日付)
- :ref:`tag-month_tag` (月)
- :ref:`tag-week_tag` (週)
- :ref:`tag-time_tag` (時間)
- :ref:`tag-datetimeLocal_tag` (ローカル日時)
- :ref:`tag-number_tag` (数値)
- :ref:`tag-range_tag` (レンジ)
- :ref:`tag-color_tag` (色)

各input要素固有の属性はカスタムタグで個別に定義していないため、動的属性により指定する必要がある。

### 対象ユースケース

> **重要**: このカスタムタグは以下のような単純な画面遷移があるWebアプリケーションを対象にしている。操作性を重視したリッチな画面作成やSPA(シングルページアプリケーション)に対応していない:
>
> - 検索画面→詳細画面による検索/詳細表示
> - 入力画面→確認画面→完了画面による登録/更新/削除
> - ポップアップ(別ウィンドウ、別タブ)による入力補助

プロジェクトでJavaScriptを多用する場合は、カスタムタグが出力するJavaScriptとプロジェクトで作成するJavaScriptで副作用が起きないよう注意する。カスタムタグが出力するJavaScriptについては :ref:`tag-onclick_override` を参照。

## HTMLエスケープ漏れを防げる

HTMLの中では「<」「>」「\"」といった文字は特別な意味を持つ。これらを含む値をそのままJSPで出力すると、悪意のあるユーザが容易にスクリプトを埋め込むことができ、クロスサイトスクリプティング(XSS)と呼ばれる脆弱性につながる。入力値を出力する場合、HTMLエスケープが必要になる。

JSPでEL式を使って値を出力する場合、HTMLエスケープされない。そのため、値の出力時はHTMLエスケープを考慮した実装が常に必要になり、生産性の低下につながる。

カスタムタグはデフォルトでHTMLエスケープするため、カスタムタグを使って実装している限り、HTMLエスケープ漏れを防げる。

> **重要**: JavaScriptに対するエスケープ処理は提供していないため、scriptタグのボディやonclick属性など、JavaScriptを記述する部分には動的な値(入力データなど)を埋め込まないこと。JavaScriptを記述する部分に動的な値を埋め込む場合は、プロジェクトの責任でエスケープ処理を実施すること。

参照:
- :ref:`tag-html_escape`
- :ref:`tag-html_unescape`

## 入力画面と確認画面のJSPを共通化して実装を減らす

多くのシステムでは、入力画面と確認画面でレイアウトが変わらず、似たようなJSPを作成している。

カスタムタグでは、入力画面と確認画面のJSPを共通化する機能を提供しているため、入力画面向けに作成したJSPに、確認画面との差分(ボタンなど)のみを追加実装するだけで確認画面を作成でき、生産性の向上が期待できる。

参照:
- :ref:`tag-make_common`

:ref:`ウィンドウスコープ<tag-window_scope>` や :ref:`tag-hidden_tag` の値はクライアント側で改竄・参照されるため、カスタムタグでは改竄・参照防止を目的にhidden暗号化機能を提供する。

デフォルトではすべての :ref:`tag-form_tag` で暗号化を行い、すべてのリクエストで復号及び改竄チェックを行う。したがって、アプリケーションプログラマは実装の必要がない。

> **重要**: この機能は仕様が複雑で使用困難であり、:ref:`ウィンドウスコープ <tag-window_scope>` の暗号化対象データ使用も非推奨であるため、本機能も非推奨とする。特に理由がない限り、:ref:`useHiddenEncryption <tag-use_hidden_encryption>` は `false` を設定すること。

## モジュール一覧

**モジュール**:

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web-tag</artifactId>
</dependency>

<!-- hidden暗号化を使う場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-encryption</artifactId>
</dependency>

<!-- ファイルダウンロードを使う場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web-extension</artifactId>
</dependency>
```

## カスタムタグの設定

> **補足**: カスタムタグの説明ではすべての属性について説明していないため、各カスタムタグで指定できる属性については、:ref:`tag_reference` を参照すること。

カスタムタグの設定は、:ref:`nablarch_tag_handler` と `CustomTagConfig` により行う。

**:ref:`nablarch_tag_handler`**

カスタムタグを使用したリクエストを処理する際に、以下の機能に必要となる前処理を行うハンドラ。カスタムタグを使用する場合、このハンドラの設定が必須。

必須対象機能:
* :ref:`tag-checkbox_off_value`
* :ref:`tag-hidden_encryption`
* :ref:`tag-submit_change_parameter`
* :ref:`tag-composite_key`

**`CustomTagConfig`**

カスタムタグのデフォルト値を設定するクラス。選択項目のラベルパターンなど、カスタムタグの属性は、個々の画面で毎回設定するよりも、アプリケーション全体で統一したデフォルト値を使用したい場合がある。そのため、カスタムタグのデフォルト値の設定をこのクラスで行う。

デフォルト値の設定は、このクラスを ``customTagConfig`` という名前でコンポーネント定義に追加して行う。設定項目については、 `CustomTagConfig` を参照。

## カスタムタグを使用する(taglibディレクティブの指定方法)

カスタムタグとJSTLを使用する場合、それぞれのtaglibディレクティブを指定する。

```jsp
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
```

## 入力フォームを作る

カスタムタグを使用して入力フォームを作成する。

**カスタムタグ一覧:**
- `n:form` - フォームタグ
- `n:text` など - 入力関連カスタムタグ
- `n:submit` など - サブミット関連カスタムタグ
- `n:error` など - エラー表示関連カスタムタグ

### 入力値の復元

バリデーションエラーで再表示した場合、カスタムタグがリクエストパラメータから入力値を自動復元する。

### 初期値の出力

初期値を表示するには：
1. アクション側でリクエストスコープに初期値オブジェクトを設定
2. カスタムタグの`name`属性でリクエストスコープ変数名と対応させる

### サブミット先URI指定

フォーム内の複数ボタン/リンクから異なるURIにサブミット可能。`uri`属性でサブミット先を指定する。

### 実装例

```jsp
<n:form>
  <div>
    <label>ユーザID</label>
    <n:text name="form.userId" />
    <n:error name="form.userId" messageFormat="span" errorCss="alert alert-danger" />
  </div>
  <div>
    <label>パスワード</label>
    <n:password name="form.password" />
    <n:error name="form.password" messageFormat="span" errorCss="alert alert-danger" />
  </div>
  <div style="padding: 8px 0;">
    <n:submit type="submit" uri="/action/login" value="ログイン" />
  </div>
</n:form>
```

### 出力結果

![ログインフォーム](../../knowledge/component/libraries/assets/libraries-tag/login_form.png)

### n:form名属性の制約

:ref:`tag-form_tag` の`name`属性には以下の制約がある：

**画面内で一意な名前**

カスタムタグはサブミット制御にJavaScriptを使用する。このJavaScriptはサブミット対象フォームを特定するために :ref:`tag-form_tag` の`name`属性を使用する。そのため、アプリケーションで`name`属性を指定する場合は、画面内で一意な名前を指定する必要がある。

アプリケーションで`name`属性を指定しない場合、カスタムタグが自動的に一意な値を設定する。

**JavaScriptの変数名の構文に従う**

:ref:`tag-form_tag` の`name`属性はJavaScriptで使用されるため、JavaScriptの変数名の構文に則った値を指定する必要がある。

変数名の構文：
- 先頭は英字
- 2文字目以降は英数字またはアンダーバー

## 選択項目(プルダウン/ラジオボタン/チェックボックス)を表示する

選択項目(プルダウン/ラジオボタン/チェックボックス)を表示する場合、以下のカスタムタグを使用する：

- :ref:`tag-select_tag` (プルダウン)
- :ref:`tag-radio_buttons_tag` (複数のラジオボタン)
- :ref:`tag-checkboxes_tag` (複数のチェックボックス)

選択肢リスト（選択肢のラベルと値をもつオブジェクトのリスト）をアクション側でリクエストスコープに設定し、カスタムタグで参照して表示する。

> **補足**: 選択状態の判定は、選択された値と選択肢の値をともに `Object#toString` してから行う。

### 実装例

**選択肢を保持するクラス:**

```java
public class Plan {
    private String planId;      // 選択肢の値
    private String planName;    // 選択肢のラベル
    
    public Plan(String planId, String planName) {
        this.planId = planId;
        this.planName = planName;
    }
    
    public String getPlanId() { return planId; }
    public String getPlanName() { return planName; }
}
```

**アクション：選択肢リストをリクエストスコープに設定**

```java
List<Plan> plans = Arrays.asList(
    new Plan("A", "フリー"),
    new Plan("B", "ベーシック"),
    new Plan("C", "プレミアム")
);
context.setRequestScopedVar("plans", plans);
```

### プルダウン (select_tag)

**属性:**
- `listName`: リスト変数名（リクエストスコープから取得）
- `elementLabelProperty`: ラベルを表すプロパティ名
- `elementValueProperty`: 値を表すプロパティ名

**JSP:**

```jsp
<n:select name="form.plan1"
          listName="plans"
          elementLabelProperty="planName"
          elementValueProperty="planId" />
```

**出力されるHTML:**

```html
<select name="form.plan1">
  <option value="A" selected="selected">フリー</option>
  <option value="B">ベーシック</option>
  <option value="C">プレミアム</option>
</select>
```

### ラジオボタン (radio_buttons_tag)

**属性:** select_tagと同じ。加えて、`listFormat`属性でHTML出力形式を指定可能（div、span、ul、ol、スペース区切り）。デフォルトはbrタグ。

**JSP:**

```jsp
<n:radioButtons name="form.plan2"
                listName="plans"
                elementLabelProperty="planName"
                elementValueProperty="planId" />
```

**出力されるHTML:**

```html
<input id="nablarch_radio1" type="radio" name="form.plan2" value="A" />
<label for="nablarch_radio1">フリー</label><br />
<input id="nablarch_radio2" type="radio" name="form.plan2" value="B" checked="checked" />
<label for="nablarch_radio2">ベーシック</label><br />
<input id="nablarch_radio3" type="radio" name="form.plan2" value="C" />
<label for="nablarch_radio3">プレミアム</label><br />
```

### チェックボックス (checkboxes_tag)

**属性:** radio_buttons_tagと同じ。`listFormat`属性でHTML出力形式を指定可能。デフォルトはbrタグ。

**JSP:**

```jsp
<n:checkboxes name="form.plan4"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
```

**出力されるHTML:**

```html
<input id="nablarch_checkbox1" type="checkbox" name="form.plan4" value="A" checked="checked" />
<label for="nablarch_checkbox1">フリー</label><br />
<input id="nablarch_checkbox2" type="checkbox" name="form.plan4" value="B" />
<label for="nablarch_checkbox2">ベーシック</label><br />
<input id="nablarch_checkbox3" type="checkbox" name="form.plan4" value="C" />
<label for="nablarch_checkbox3">プレミアム</label><br />
```

### HTMLデザインの自由度が必要な場合

> **重要**: :ref:`tag-radio_buttons_tag` と :ref:`tag-checkboxes_tag` はカスタムタグが選択肢をすべて出力するため、出力されるHTMLに制限が出る。デザイン会社が作成したHTMLをベースに開発する場合など、プロジェクトでデザインをコントロールできない場合は、JSTLの`c:forEach`タグと :ref:`tag-radio_tag` または :ref:`tag-checkbox_tag` を使って実装し、選択肢を表示するHTMLを自由に実装できる。

```jsp
<c:forEach items="${plans}" var="plan">
  <!-- 前後に好きなHTMLを追加できる -->
  <n:radioButton name="form.plan3" label="${plan.planName}" value="${plan.planId}" />
</c:forEach>
```

## チェックボックスでチェックなしに対する値を指定する

HTMLのcheckboxタグはチェックなしの場合、リクエストパラメータが送信されない制限があります。単一入力項目としてのcheckboxタグはデータベース上のフラグ項目に対応することが多く、チェックなしの場合にも値を設定する必要があります。checkboxタグではチェックなしに対応する値を指定できます。

**属性:**

- `useOffValue`: チェックなしの値設定を使用するか否か（デフォルト: `true`）。複数選択の場合は`false`を指定
- `offLabel`: チェックなしの場合に使用するラベル。入力画面と確認画面を共通化した場合、確認画面で表示
- `offValue`: チェックなしの場合に使用する値（デフォルト: `0`）

**使用例:**

```jsp
<n:checkbox name="form.useMail" value="true" label="使用する"
            offLabel="使用しない" offValue="false" />
```

> **補足**: この機能は :ref:`nablarch_tag_handler` と :ref:`hidden暗号化 <tag-hidden_encryption>` を使って実現されています。checkboxタグ出力時にチェックなしに対応する値をhiddenタグに出力し、:ref:`nablarch_tag_handler` がリクエスト受付時にcheckboxタグがチェックされていない場合のみ、リクエストパラメータにチェックなしに対応する値を設定します。

## 入力データを画面間で持ち回る(ウィンドウスコープ)

:ref:`session_store` 使用が推奨される。理由:
- ウィンドウスコープはキー/値ペアでデータ保持するため、Bean をそのまま格納できず、データをバラす必要があり実装が煩雑
- カスタムタグの属性指定で設定するため実装難易度が高い

**概要**: クライアント側にhiddenタグとしてデータを保持。サーバ側(セッション)保持に比べ、複数ウィンドウやブラウザ戻るボタン使用での柔軟な画面設計が可能。データは :ref:`hidden暗号化<tag-hidden_encryption>` で暗号化。クライアント側での書き換え(Ajax利用など)はできない。

**設定方法**: :ref:`tag-form_tag` の `windowScopePrefixes` 属性を指定。パラメータ名が指定値に **前方一致** するリクエストパラメータがウィンドウスコープに設定される。例: `windowScopePrefixes="user"` で `users` で始まるパラメータも対象。

**Beanを格納する場合の実装例**:

```java
Person person = new Person();
person.setName("名前");
person.setAge("年齢");

// アクション側
request.setParam("person.name", person.getName());
request.setParam("person.age", person.getAge());

// JSP側
<n:hidden name="person.name" />
<n:hidden name="person.age" />
```

**画面間データ持ち回り実装例**: 検索条件(`searchCondition.*`)と入力データ(`user.*`)を持ち回る

```jsp
<!-- 検索画面: ウィンドウスコープのデータを送信しない -->
<n:form>

<!-- 更新画面: 検索条件のみを送信 -->
<n:form windowScopePrefixes="searchCondition">

<!-- 更新確認画面: 検索条件と入力データを送信 -->
<n:form windowScopePrefixes="searchCondition,user">

<!-- 更新完了画面: 検索条件のみを送信 -->
<n:form windowScopePrefixes="searchCondition">
```

画面遷移でのデータフロー:
1. 検索画面 → ウィンドウスコープなし
2. 更新画面 → searchCondition をhiddenで持ち回り
3. 更新確認画面 → searchCondition と user をhiddenで持ち回り
4. 更新完了画面 → searchCondition をhiddenで持ち回り

> **重要**: hiddenで送信するデータは最小限に。表示用データはhiddenで引き回さず都度DBから取得(データ量増加→通信速度低下、メモリ圧迫)

> **重要**: ウィンドウスコープのデータをアクション側で使用する場合は :ref:`バリデーション<validation>` を実施

> **補足**: :ref:`tag-form_tag` は既に入力項目として出力したリクエストパラメータはhiddenタグの出力から除外

> **補足**: ログイン情報など業務全般で必要な情報はサーバ側(セッション)に保持

## hidden暗号化の仕組み

hidden暗号化は :ref:`tag-form_tag` と :ref:`nablarch_tag_handler` で実現される。:ref:`tag-form_tag` が暗号化を、:ref:`nablarch_tag_handler` が復号及び改竄チェックを行う。

![hidden暗号化処理フロー](../../knowledge/component/libraries/assets/libraries-tag/hidden_encryption.png)

## 暗号化処理

暗号化は `Encryptor` インタフェース実装クラスが行う。デフォルトアルゴリズムは `AES(128bit)`。

暗号化アルゴリズムを変更する場合は、`Encryptor` を実装したクラスをコンポーネント定義に `hiddenEncryptor` という名前で追加すること。

#### 暗号化対象データ

各 :ref:`tag-form_tag` で、以下のデータをまとめて暗号化し1つのhiddenタグで出力する：

- カスタムタグの :ref:`tag-hidden_tag` で明示的に指定したhiddenパラメータ
- :ref:`ウィンドウスコープ<tag-window_scope>` の値
- :ref:`サブミットを行うカスタムタグ <tag_reference_submit>` で指定したリクエストID
- :ref:`サブミットを行うカスタムタグ <tag_reference_submit>` で追加した :ref:`パラメータ<tag-submit_change_parameter>`

#### 改竄検知

改竄を検知するため、上記データから生成したハッシュ値を含める。リクエストIDは異なるフォーム間での値入れ替え改竄検知に、ハッシュ値は値の書き換え改竄検知に使用される。暗号化結果はBASE64エンコードしhiddenタグに出力される。

> **補足**: :ref:`tag-hidden_tag` で指定したhiddenパラメータは暗号化に含まれるため、クライアント側JavaScriptで値操作不可。値操作が必要な場合は :ref:`tag-plain_hidden_tag` を使用して暗号化しないhiddenタグを出力すること。

## 復号処理

復号処理は :ref:`nablarch_tag_handler` が行う。以下の場合に改竄と判定し、設定で指定された画面に遷移させる：

- 暗号化したhiddenパラメータ(`nablarch_hidden`)が存在しない
- BASE64デコード失敗
- 復号失敗
- 暗号化時生成ハッシュ値と復号後ハッシュ値不一致
- 暗号化時リクエストIDと受け付けたリクエストIDの不一致

## 暗号化に使用する鍵

鍵は有効期間を短くするためセッション毎に生成される。したがって、同一ユーザがログインをやり直した場合、ログイン前の画面から処理継続不可となる。

## 設定

:ref:`tag-setting` により、以下の設定ができる。

#### useHiddenEncryptionプロパティ

| 項目 | 値 |
|---|---|
| 説明 | hidden暗号化を使用するか否か |
| デフォルト | `true` |

#### noHiddenEncryptionRequestIdsプロパティ

| 項目 | 値 |
|---|---|
| 説明 | hidden暗号化を行わないリクエストID |

hidden暗号化が使用できないリクエスト：

- ログイン画面などアプリケーション入口のリクエスト
- ブックマークからの遷移リクエスト
- 外部サイトからの遷移リクエスト

これらのリクエストは暗号化したhiddenパラメータ(`nablarch_hidden`)またはセッション鍵が存在しないため、当プロパティを設定しないと改竄エラーになる。

#### 設定値の参照

`noHiddenEncryptionRequestIdsプロパティの設定値は :ref:`tag-form_tag` と :ref:`nablarch_tag_handler` が暗号化と復号の際に参照して処理を行う。

**:ref:`tag-form_tag` の動作**：
- 暗号化対象のリクエストIDが1つでも含まれれば暗号化
- 含まれなければ暗号化しない

**:ref:`nablarch_tag_handler` の動作**：
- リクエストIDが暗号化対象の場合のみ復号

## 複合キーのラジオボタンやチェックボックスを作る

一覧画面でデータ選択時は、ラジオボタンやチェックボックスを使用する。データ識別値が単一の場合は :ref:`tag-radio_tag` や :ref:`tag-checkbox_tag` を使用できるが、複合キーの場合は単純に実装できない。カスタムタグで複合キー対応のラジオボタン・チェックボックスを提供する。

* :ref:`tag-composite_key_radio_button_tag` - 複合キー対応ラジオボタン
* :ref:`tag-composite_key_checkbox_tag` - 複合キー対応チェックボックス

> **重要**: この機能を使用するには、`CompositeKeyConvertor` と `CompositeKeyArrayConvertor` をコンポーネント定義に追加する必要がある。設定方法は :ref:`nablarch_validation-definition_validator_convertor` を参照。

> **重要**: この機能は `CompositeKeyConvertor` と `CompositeKeyArrayConvertor` を使用するため、:ref:`nablarch_validation` でのみ使用できる。:ref:`bean_validation` は対応していない。

### フォーム

複合キーを保持するプロパティは `CompositeKey` として定義する。

```java
public class OrderItemsForm {
    // 一覧表示で複数データに対する複合キーを受け付けるので、配列として定義する
    public CompositeKey[] orderItems;

    // CompositeKeyTypeアノテーションで複合キーのサイズを指定する
    @CompositeKeyType(keySize = 2)
    public void setOrderItems(CompositeKey[] orderItems) {
        this.orderItems = orderItems;
    }
}
```

### JSP

n:compositeKeyCheckbox タグの属性：

- **name属性**: フォームのプロパティ名に合わせて指定
- **valueObject属性**: 複合キーの値を持つオブジェクト
- **keyNames属性**: valueObject から複合キー値を取得するプロパティ名。指定順でCompositeKeyに設定される
- **namePrefix属性**: 複合キー値をリクエストパラメータに展開する際のプレフィクス。name属性と異なる値を指定する必要がある

```jsp
<table>
  <thead>
    <tr>
      <!-- ヘッダ出力は省略 -->
    </tr>
  </thead>
  <tbody>
    <c:forEach var="orderItem" items="${orderItems}">
    <tr>
      <td>
        <n:compositeKeyCheckbox
          name="form.orderItems"
          label=""
          valueObject="${orderItem}"
          keyNames="orderId,productId"
          namePrefix="orderItems" />
      </td>
      <!-- 以下略 -->
    </tr>
    </c:forEach>
  </tbody>
</table>
```

## 複数のボタン/リンクからフォームをサブミットする

フォームのサブミットはボタンとリンクに対応し、カスタムタグを使用して行う。1つのフォームに複数のボタンとリンクを配置できる。

### フォームのサブミット

- :ref:`tag-submit_tag` (inputタグのボタン)
- :ref:`tag-button_tag` (buttonタグのボタン)
- :ref:`tag-submit_link_tag` (リンク)

### 別ウィンドウを開いてサブミット(ポップアップ)

- :ref:`tag-popup_submit_tag` (inputタグのボタン)
- :ref:`tag-popup_button_tag` (buttonタグのボタン)
- :ref:`tag-popup_link_tag` (リンク)

### ダウンロード用のサブミット

- :ref:`tag-download_submit_tag` (inputタグのボタン)
- :ref:`tag-download_button_tag` (buttonタグのボタン)
- :ref:`tag-download_link_tag` (リンク)

タグ名が `popup` から始まるタグは新しいウィンドウをオープンし、オープンしたウィンドウに対してサブミットを行う。タグ名が `download` から始まるタグはダウンロード用のサブミットを行う。詳細は以下を参照：

- :ref:`tag-submit_popup`
- :ref:`tag-submit_download`

カスタムタグではボタン/リンクとURIを関連付けるためにname属性とuri属性を指定する。name属性はフォーム内で一意な名前を指定する。name属性の指定がない場合はカスタムタグで一意な名前が自動で出力される。uri属性の指定方法については :ref:`tag-specify_uri` を参照。

### 実装例

```jsp
<!-- name属性は自動で出力されるので指定しなくてよい。 -->
<n:submit type="submit" uri="login" value="ログイン" />
```

## サブミット前に処理を追加する

フォームのサブミットは、JavaScriptを使用してボタン/リンク毎のURIを組み立てることで実現している。カスタムタグはグローバル領域にこのJavaScript関数を出力し、ボタン/リンクのonclick属性にその関数呼び出しを設定した状態でHTMLを出力する。

### カスタムタグが出力するJavaScript関数のシグネチャ

```javascript
/**
 * @param event イベントオブジェクト
 * @param element イベント元の要素(ボタン又はリンク)。未指定の場合は第1引数のeventからcurrentTarget、targetプロパティの優先順位でイベント元の要素を取得する。
 * @return イベントを伝搬させないため常にfalse
 */
function nablarch_submit(event, element)
```

**JSP例:**
```jsp
<n:form>
  <!-- 省略 -->
  <n:submit type="submit" uri="login" value="ログイン" />
</n:form>
```

**HTML出力:**
```html
<script type="text/javascript">
<!--
function nablarch_submit(event, element) {
  // 省略
}
-->
</script>
<form name="nablarch_form1" method="post">
  <!-- onclick属性にサブミット制御を行うJavaScript関数が設定される。 -->
  <input type="submit" name="nablarch_form1_1" value="ログイン"
         onclick="return window.nablarch_submit(event, this);" />
</form>
```

### サブミット前に処理を追加する

サブミット前に処理を追加したい場合は、onclick属性にアプリケーションで作成したJavaScript関数を指定する。カスタムタグはonclick属性が指定された場合、サブミット用のJavaScript関数を呼び出さない。この場合、アプリケーションで作成したJavaScriptで、カスタムタグが設定する :ref:`JavaScript関数 <tag-submit_function>` を呼び出す必要がある。

> **重要**: Content Security Policy(CSP)に対応する場合は、onclick属性にインラインでJavaScriptを記述してしまうとCSPに対応しようとしているにもかかわらず `unsafe-inline` を使いセキュリティレベルを低下させてしまう、もしくは `unsafe-hashes` を利用することになってしまう。このため、 :ref:`tag-content_security_policy` の手順に従い外部スクリプトまたはnonce属性を指定したscript要素に追加の処理を実装することを推奨する。

### 実装例

確認ダイアログを表示してからサブミットする例:

**JavaScript:**
```javascript
function popUpConfirmation(event, element) {
  if (window.confirm("登録します。よろしいですか？")) {
    // カスタムタグが出力するJavaScript関数を明示的に呼び出す。
    return nablarch_submit(event, element);
  } else {
    // キャンセル
    return false;
  }
}
```

**JSP:**
```jsp
<n:submit type="submit" uri="register" value="登録"
          onclick="return popUpConfirmation(event, this);" />
```

## プルダウン変更などの画面操作でサブミットする

カスタムタグはサブミット制御にJavaScriptを使用。サブミット制御関数はボタン/リンクのonclick属性に指定されることが前提。

プルダウン変更などの画面操作でサブミットする場合、サブミットさせたいボタンのクリックイベントを発生させる。

> **重要**: CSP対応の場合、onclick属性にインラインJavaScriptを記述するとセキュリティレベルが低下する（unsafe-inlineまたはunsafe-hashesが必要）。:ref:`tag-content_security_policy` の手順に従い、外部スクリプトまたはnonce属性付きscript要素に処理を実装すること。

**実装例 (JSP)**:

```jsp
<n:select name="form.plan"
          listName="plans"
          elementLabelProperty="planName"
          elementValueProperty="planId"
          onchange="window.document.getElementById('register').click(); return false;" />

<n:submit id="register" type="submit" uri="register" value="登録" />
```

> **重要**: 上記の例ではonchangeに直接JavaScriptを記載しているが、実際のプロジェクトではオープンソースJavaScriptライブラリなどを使い、処理を動的にバインドすることを推奨する。

## ボタン/リンク毎にパラメータを追加する

カスタムタグでは、フォームのボタンやリンク毎にパラメータを追加するためのカスタムタグを提供する。

関連: :ref:`tag_param_tag` (サブミット時に追加するパラメータの指定)

## 実装例

検索結果から一覧画面でリンク毎にパラメータを追加する。

```jsp
<n:form>
  <table>
    <!-- テーブルのヘッダ行は省略 -->
    <c:forEach var="person" items="${persons}">
      <tr>
        <td>
          <n:submitLink uri="/action/person/show">
            <n:write name="person.personName" />
            <!-- パラメータ名に"personId"を指定している。 -->
            <n:param paramName="personId" name="person.personId" />
          </n:submitLink>
        </td>
      </tr>
    </c:forEach>
  </table>
</n:form>
```

> **重要**: パラメータを追加する場合は、その数に応じてリクエストのデータ量は増大する。そのため、一覧画面で詳細画面へのリンク毎にパラメータを追加する場合は、パラメータをプライマリキーだけにするなど、必要最小限のパラメータのみ追加する。

## 認可チェック/サービス提供可否に応じてボタン/リンクの表示/非表示を切り替える

:ref:`permission_check` と :ref:`service_availability` の結果に応じて、:ref:`フォームのサブミットを行うボタン/リンク<tag_reference_submit>` の表示を切り替える機能を提供する。

これにより、ユーザが実際にボタン/リンクを選択する前に該当機能が使用可能かどうかが分かるため、ユーザビリティの向上につながる。

### 動作

:ref:`フォームのサブミットを行うボタン/リンク<tag_reference_submit>` に指定されたリクエストIDに対して、:ref:`permission_check` と :ref:`service_availability` を行い、``権限なし`` または ``サービス提供不可`` の場合に表示切り替えを行う。

### 表示パターン

3つの表示パターンがある:

**非表示**

タグを出力しない。

**非活性**

タグを非活性にする。

- ボタンの場合: disabled属性を有効化
- リンクの場合: ラベルのみ表示するか、非活性リンク描画用JSPをインクルード

JSPインクルードを行う場合、:ref:`tag-setting` で `submitLinkDisabledJspプロパティ` を指定する。

**通常表示**

通常どおりタグが出力される。表示方法の切り替えを行わない。

### 設定

デフォルト表示は ``通常表示`` である。

:ref:`tag-setting` で `displayMethodプロパティ` を指定することで、デフォルトを変更できる。

個別に表示方法を変更したい場合は、``displayMethod`` 属性に指定する。

### 実装例

```jsp
<!-- NODISPLAY(非表示)、DISABLED(非活性)、NORMAL(通常表示)のいずれかを指定 -->
<n:submit type="button" uri="login" value="ログイン" displayMethod="NORMAL" />
```

> **補足**: アプリケーションで表示制御に使用する判定処理を変更したい場合は、:ref:`tag-submit_display_control_change` を参照。

## 別ウィンドウ/タブを開くボタン/リンクを作る(ポップアップ)

ポップアップタグ（複数ウィンドウの立ち上げをサポートするカスタムタグ）を提供する。

- :ref:`tag-popup_submit_tag` (inputタグのボタン)
- :ref:`tag-popup_button_tag` (buttonタグのボタン)
- :ref:`tag-popup_link_tag` (リンク)

> **重要**: これらのタグは非推奨である。理由：
> - 外部サイトへのリンク/ボタンの場合、ブラウザによっては新しいウィンドウで開けない（例：IEの保護モード）。:ref:`tag-a_tag` またはhtmlタグで回避可能。
> - サブウィンドウを用いた画面遷移は利便性が低い。ページ内ポップアップが一般的。オープンソースライブラリで対応可能。

ポップアップタグは、画面内フォームのサブミット機能と異なる：
- 新しいウィンドウをオープンし、そのウィンドウに対してサブミット
- 入力項目のパラメータ名を変更可能

実装はJavaScriptのwindow.open関数を使用する。

### 実装例

指定したスタイルでウィンドウを開く検索ボタン：

```jsp
<!--
  popupWindowName属性: ウィンドウ名。window.open関数の第2引数に指定。
  popupOption属性: オプション情報。window.open関数の第3引数に指定。
-->
<n:popupButton uri="/action/person/list"
               popupWindowName="postalCodeSupport"
               popupOption="width=400, height=300, menubar=no, toolbar=no, scrollbars=yes">
  検索
</n:popupButton>
```

### ウィンドウ名の設定

popupWindowName属性が未指定の場合、:ref:`tag-setting` で `popupWindowNameプロパティ` のデフォルト値が使用される。デフォルト値が未設定の場合、JavaScriptのDate関数から取得した現在時刻（ミリ秒）がウィンドウ名に使用される。

デフォルト値の設定有無による動作：
- **設定した場合**: 常に同じウィンドウ名を使用 → オープンするウィンドウが1つ
- **未設定の場合**: 常に異なるウィンドウ名を使用 → 常に新しいウィンドウをオープン

### パラメータ名変更

ポップアップタグは、元画面のフォームに含まれる全てのinput要素を動的に追加してサブミットする。オープンしたウィンドウのアクションと元画面のアクションでパラメータ名が異なる場合がある。

このため、:ref:`tag-change_param_name_tag` を使用してパラメータ名を変更できる。

#### 実装例

![popup_postal_code.png](../../knowledge/component/libraries/assets/libraries-tag/popup_postal_code.png)

検索ボタン選択時に、郵便番号欄の入力値で住所を検索する別ウィンドウを開く：

```jsp
<n:form>
  <div>
    <label>郵便番号</label>
    <n:text name="form.postalCode" />
    <n:popupButton uri="/action/postalCode/show">
      検索
      <!-- パラメータ名"form.postalCode"を"condition.postalCode"に変更 -->
      <n:changeParamName inputName="form.postalCode" paramName="condition.postalCode" />
      <!-- パラメータの追加も可能 -->
      <n:param paramName="condition.max" value="10" />
    </n:popupButton>
  </div>
</n:form>
```

### オープンしたウィンドウへのアクセス方法

別ウィンドウを開いた状態で元画面が遷移した場合、不要となった別ウィンドウを全て閉じるなど、アプリケーションでオープンしたウィンドウにアクセスしたい場合がある。

カスタムタグは、オープンしたウィンドウに対する参照をJavaScriptのグローバル変数に保持する：

```javascript
// keyはウィンドウ名
var nablarch_opened_windows = {};
```

元画面遷移時に不要となった別ウィンドウを全て閉じる実装例：

```javascript
// onunloadイベントハンドラにバインド
onunload = function() {
  for (var key in nablarch_opened_windows) {
    var openedWindow = nablarch_opened_windows[key];
    if (openedWindow && !openedWindow.closed) {
      openedWindow.close();
    }
  }
  return true;
};
```

## ファイルをダウンロードするボタン/リンクを作る

## コンポーネント概要

ファイルをダウンロードするボタン/リンクを作成するために、以下のコンポーネントを提供する。

### ダウンロードタグ

- :ref:`tag-download_submit_tag` (inputタグ形式のボタン)
- :ref:`tag-download_button_tag` (buttonタグ形式のボタン)
- :ref:`tag-download_link_tag` (リンク)

### ダウンロードユーティリティ

**`StreamResponse`**

ストリームからHTTPレスポンスメッセージを生成するクラス。ファイルシステム上のファイルまたはデータベースのBLOB型カラムに格納したバイナリデータをダウンロードする場合に使用する。`File` または `Blob` のダウンロードに対応。

**`DataRecordResponse`**

データレコードからHTTPレスポンスメッセージを生成するクラス。検索結果など、アプリケーションで使用するデータをダウンロードする場合に使用する。ダウンロードデータは :ref:`data_format` を使用してフォーマットされる。Map<String, ?>型データ（`SqlRow` など）のダウンロードに対応。

## 重要な制約事項

> **重要**: カスタムタグではフォームのサブミット制御にJavaScriptを使用しているため、画面内のフォームに対するサブミット（:ref:`tag-submit_tag` など）でダウンロードすると、同じフォーム内の他のサブミットが機能しなくなる。ダウンロードするボタンやリンクには必ずダウンロードタグを使用すること。

## ダウンロードタグの特徴

ダウンロードタグは通常のフォーム送信タグと異なり：

- 新しいフォームを作成し、新規フォームに対してサブミットを行う
- 入力項目のパラメータ名を変更できる

パラメータ名の変更は :ref:`tag-change_param_name_tag` を使用。使い方はポップアップタグと同じため、:ref:`ポップアップ時のパラメータ名変更 <tag-submit_change_param_name>` を参照。

## 実装例：ファイルダウンロード

ボタン押下時にサーバ上のファイルをダウンロード。

**JSP**

```jsp
<n:downloadButton uri="/action/download/tempFile">ダウンロード</n:downloadButton>
```

**アクション**

```java
public HttpResponse doTempFile(HttpRequest request, ExecutionContext context) {
    File file = getTempFile();
    
    // FileのダウンロードにはStreamResponseを使用
    // コンストラクタ引数にダウンロード対象のファイルと
    // リクエスト処理の終了時にファイルを削除する場合はtrue、削除しない場合はfalseを指定
    // ファイルの削除はフレームワークが行う
    // 通常ダウンロード用のファイルはダウンロード後に不要となるためtrueを指定する
    StreamResponse response = new StreamResponse(file, true);
    response.setContentType("application/pdf");
    response.setContentDisposition(file.getName());
    
    return response;
}
```

## 実装例：BLOB型カラムのダウンロード

テーブルの行データ毎にリンクを表示し、選択されたリンクに対応するデータをダウンロード。

**テーブル構造**

| カラム(論理名) | カラム(物理名) | データ型 | 補足 |
|---|---|---|---|
| ファイルID | FILE_ID | CHAR(3) | PK |
| ファイル名 | FILE_NAME | NVARCHAR2(100) | |
| ファイルデータ | FILE_DATA | BLOB | |

**JSP**

```jsp
<!-- recordsという名前で行データのリストがリクエストスコープに設定されているものとする -->
<c:forEach var="record" items="${records}" varStatus="status">
  <n:set var="fileId" name="record.fileId" />
  <div>
    <n:downloadLink uri="/action/download/tempFile">
      <n:write name="record.fileName" />(<n:write name="fileId" />)
      <n:param paramName="fileId" name="fileId" />
    </n:downloadLink>
  </div>
</c:forEach>
```

**アクション**

```java
public HttpResponse tempFile(HttpRequest request, ExecutionContext context) {
    SqlRow record = getRecord(request);
    
    // BlobのダウンロードにはStreamResponseクラスを使用
    StreamResponse response = new StreamResponse((Blob) record.get("FILE_DATA"));
    response.setContentType("image/jpeg");
    response.setContentDisposition(record.getString("FILE_NAME"));
    
    return response;
}
```

## 実装例：データレコードのダウンロード

テーブルの全データをCSV形式でダウンロード。

**テーブル構造**

| カラム(論理名) | カラム(物理名) | データ型 | 補足 |
|---|---|---|---|
| メッセージID | MESSAGE_ID | CHAR(8) | PK |
| 言語 | LANG | CHAR(2) | PK |
| メッセージ | MESSAGE | NVARCHAR2(200) | |

**フォーマット定義** (N11AA001.fmt)

```
file-type:        "Variable"
text-encoding:    "Shift_JIS"
record-separator: "\n"
field-separator:  ","

[header]
1   messageId    N "メッセージID"
2   lang         N "言語"
3   message      N "メッセージ"

[data]
1   messageId    X
2   lang         X
3   message      N
```

**JSP**

```jsp
<n:downloadSubmit type="button" uri="/action/download/tempFile" value="ダウンロード" />
```

**アクション**

```java
public HttpResponse doCsvDataRecord(HttpRequest request, ExecutionContext context) {
    SqlResultSet records = getRecords(request);
    
    // データレコードのダウンロードにはDataRecordResponseクラスを使用
    // コンストラクタ引数にフォーマット定義のベースパス論理名と
    // フォーマット定義のファイル名を指定する
    DataRecordResponse response = new DataRecordResponse("format", "N11AA001");
    
    // DataRecordResponse#writeメソッドを使用してヘッダを書き込む
    // フォーマット定義に指定したデフォルトのヘッダ情報を使用するため、
    // 空のマップを指定する
    response.write("header", Collections.<String, Object>emptyMap());
    
    for (SqlRow record : records) {
        response.write("data", record);
    }
    
    response.setContentType("text/csv; charset=Shift_JIS");
    response.setContentDisposition("メッセージ一覧.csv");
    
    return response;
}
```

## 二重サブミットを防ぐ

二重サブミットの防止は、データベースにコミットを伴う処理を要求する画面で使用する。防止方法はクライアント側とサーバ側の2つがあり、両方を併用する必要がある。

### クライアント側での役割

ユーザがボタンをダブルクリックした場合や、サーバからのレスポンス待機中に再度ボタンをクリックした場合に、リクエストを2回以上送信するのを防止する。

### サーバ側での役割

ブラウザの戻るボタンにより完了画面から確認画面に遷移して再度サブミットした場合など、アプリケーションが既に処理済みのリクエストを重複して処理しないようにする。

### 両方の併用が必要な理由

> **重要**: どちらか一方のみ使用した場合の懸念:
> - クライアント側のみ使用：リクエストを重複して処理する恐れがある
> - サーバ側のみ使用：ボタンのダブルクリックで2回リクエストが送信されると、サーバ処理順によっては二重サブミットエラーが返されて、ユーザに処理結果が返されない恐れがある

## クライアント側の二重サブミット防止

JavaScriptを使用して実現する。1回目のサブミット時に対象要素のonclick属性を書き換えて、2回目以降のサブミット要求はサーバ側に送信しない。ボタンの場合はdisabled属性を設定して、画面上でクリックできない状態にする。

## 対応カスタムタグ

**フォームのサブミット:**
- :ref:`tag-submit_tag` (inputタグのボタン)
- :ref:`tag-button_tag` (buttonタグのボタン)
- :ref:`tag-submit_link_tag` (リンク)

**ダウンロード用のサブミット:**
- :ref:`tag-download_submit_tag` (inputタグのボタン)
- :ref:`tag-download_button_tag` (buttonタグのボタン)
- :ref:`tag-download_link_tag` (リンク)

上記カスタムタグのallowDoubleSubmission属性に `false` を指定することで、特定のボタン及びリンクだけを対象に二重サブミットを防止する。

## 実装例

登録ボタンはデータベースにコミットを行うので、登録ボタンのみ二重サブミットを防止する場合:

```jsp
<!--
  allowDoubleSubmission属性: 二重サブミットを許可するか否か。
                             許可する場合は true、許可しない場合は false。
                             デフォルトは true。
-->
<n:submit type="button" name="back" value="戻る" uri="./back" />
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

## 補足

クライアント側の二重サブミット防止を使用している画面で、サブミット後にサーバレスポンスが返ってこない場合、ユーザがブラウザの中止ボタンを押すとボタンは非活性(disabled属性)が続くため、再度サブミットできなくなる。この場合、ユーザはサブミットに使用したボタン以外のボタンまたはリンクを使用して処理を継続できる。

## サーバ側の二重サブミット防止

サーバ側で発行した一意なトークンをサーバ側(セッション)とクライアント側(hiddenタグ)に保持し、サーバ側で突合することで実現する。トークンは1回のチェックに限り有効である。

トークンを設定するJSPまたはアクションと、トークンのチェックを行うアクションで、それぞれ作業が必要である。

## JSPでトークンの設定

:ref:`tag-form_tag` のuseToken属性を指定することで行う。

### 実装例

```jsp
<!--
  useToken属性: トークンを設定するか否か。
                設定する場合は true、設定しない場合は false。
                デフォルトは false。
                入力画面と確認画面を共通化した場合、確認画面ではデフォルトが true。
                共通化した場合は指定しなくてよい。
-->
<n:form useToken="true">
```

## アクションでトークンの設定

JSP以外のテンプレートエンジンを採用している場合は、:ref:`use_token_interceptor` で設定する。詳細は :ref:`use_token_interceptor` を参照。

## トークンのチェック

トークンのチェックは :ref:`on_double_submission_interceptor` を使用する。詳細は :ref:`on_double_submission_interceptor` を参照。

## セッションスコープに保存するキーを変更

発行されたトークンはセッションスコープに`/nablarch_session_token`というキーで保存される。このキーはコンポーネント設定ファイルで変更できる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーを"sessionToken"へ変更 -->
  <property name="doubleSubmissionTokenSessionAttributeName" value="sessionToken" />
</component>
```

## リクエストスコープに保存するキーを変更

発行されたトークンはThymeleafなどのテンプレートに埋め込むときに使用できるよう、リクエストスコープに`nablarch_request_token`というキーで保存される。このキーはコンポーネント設定ファイルで変更できる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- キーを"requestToken"へ変更 -->
  <property name="doubleSubmissionTokenRequestAttributeName" value="requestToken" />
</component>
```

## hiddenに埋め込むときのname属性を変更

トークンをhiddenに埋め込むとき、name属性は`nablarch_token`という値を設定する。このname属性値はコンポーネント設定ファイルで変更できる。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- name属性に設定する値を"hiddenToken"へ変更 -->
  <property name="doubleSubmissionTokenParameterName" value="hiddenToken" />
</component>
```

## 重要な制限事項

サーバ側の二重サブミット防止では、トークンをサーバ側のセッションに格納しているため、同一ユーザの複数リクエストに対して別々にトークンをチェックできない。

このため、同一ユーザにおいて、サーバ側の二重サブミットを防止する画面遷移(登録確認→登録完了や更新確認→更新完了など)のみ、複数ウィンドウや複数タブを使用して並行で行うことができない。

これらの画面遷移を並行して行った場合は、後に確認画面に遷移した画面のみ処理を継続でき、先に確認画面に遷移した画面はトークンが古いため、二重サブミットエラーとなる。

## トークン発行

トークンの発行は `UUIDV4TokenGenerator` が行う。36文字のランダムな文字列を生成する。トークンの発行処理を変更したい場合は :ref:`tag-double_submission_server_side_change` を参照。

## サーバ側のトークンをデータベースに保存する

デフォルト実装ではサーバ側トークンはHTTPセッションに保存される。スケールアウト時にはスティッキーセッションやセッションレプリケーション設定が必要。

データベースに保存することで、サーバ設定不要で複数サーバ間でトークン共有が可能。

![db-double-submit](../../knowledge/component/libraries/assets/libraries-tag/db-double-submit.png)

## 入力画面と確認画面を共通化する

:ref:`入力項目のカスタムタグ <tag_reference_input>` を使用することで、入力画面と全く同じJSP記述のまま確認画面用を出力できる。

## 使用するカスタムタグ

:ref:`tag-confirmation_page_tag`
: 確認画面のJSPで入力画面のJSPへのパスを指定して、入力画面と確認画面の共通化を行う

:ref:`tag-for_input_page_tag`
: 入力画面でのみ表示したい部分を指定する

:ref:`tag-for_confirmation_page_tag`
: 確認画面でのみ表示したい部分を指定する

:ref:`tag-ignore_confirmation_tag`
: 確認画面で、確認画面向けの表示を無効化したい部分に指定する。チェックボックスを使用した項目で、確認画面でもチェック欄を表示したい場合などに使用する

> **補足**: 入力・確認画面の表示制御は入力系のタグが対象。ただし、以下のタグは異なる動作:
> - :ref:`tag-plain_hidden_tag`: 画面遷移の状態などを画面間で受け渡す目的で使用することを想定し、入力・確認画面ともに出力する
> - :ref:`tag-hidden_store_tag`: :ref:`session_store` に保存したデータを画面間で受け渡すために使用するため、入力・確認画面ともに出力する

## 実装例

![入力画面と確認画面の共通化例](../../knowledge/component/libraries/assets/libraries-tag/make_common_input_confirm.png)

### 入力画面のJSP

```jsp
<n:form>
  <!--
    入力欄は、入力画面と確認画面で同じJSP記述を使用する。
  -->
  <div>
    <label>名前</label>
    <n:text name="form.name" />
  </div>
  <div>
    <label>メール</label>
    <n:checkbox name="form.useMail" label="使用する" offLabel="使用しない" />
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>
  <!--
   ボタン表示は、入力画面と確認画面で異なるので、
   forInputPageタグとforConfirmationPageタグを使用する。
  -->
  <div style="padding: 8px 0;">
    <n:forInputPage>
      <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
    </n:forInputPage>
    <n:forConfirmationPage>
      <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
      <n:submit type="submit" uri="/action/sample/register" value="登録" />
    </n:forConfirmationPage>
  </div>
</n:form>
```

### 確認画面のJSP

```jsp
<!--
  入力画面のJSPへのパスを指定する。
-->
<n:confirmationPage path="./input.jsp" />
```

## 変数に値を設定する

:ref:`tag-set_tag` を使用して、JSP内で変数に値を設定する。

**使用例：**
```
<!-- var属性に変数名を指定する。-->
<n:set var="title" value="ユーザ情報登録" />
<head>
  <!-- 変数の出力にはwriteタグを使用する。 -->
  <title><n:write name="title" /></title>
</head>
<body>
  <h1><n:write name="title" /></h1>
</body>
```

> **重要**: :ref:`tag-set_tag` で設定した変数を出力する場合、:ref:`tag-set_tag` はHTMLエスケープ処理を実施しないため、出力時は必ず :ref:`tag-write_tag` タグを使用すること。

### 変数を格納するスコープを指定する

scope属性で変数を格納するスコープを指定する。リクエストスコープ(`request`)またはページスコープ(`page`)を指定できる。

scope属性の指定がない場合、変数はリクエストスコープに設定される。

ページスコープは、アプリケーション全体で使用されるUI部品を作成する場合に、他JSPの変数とのバッティングを防ぐ場合に使用する。

### 変数に配列やコレクションの値を設定する

:ref:`tag-set_tag` は、name属性指定時にデフォルトで単一値として値を取得する。配列やコレクションの場合は先頭要素が返される。

ほとんどの場合はデフォルトのまま問題ないが、**共通で使用されるUI部品を作成する場合に配列やコレクション全体を取得したい場合**がある。このようなケースでは、:ref:`tag-set_tag` の bySingleValue属性に `false` を指定することで、配列やコレクション全体をそのまま取得できる。

## GETリクエストを使用する

GETリクエスト使用時は、カスタムタグの隠れたパラメータ出力が無効化されるため、以下の制限が発生します。

### 背景

カスタムタグは隠れた暗号化（:ref:`hidden暗号化<tag-hidden_encryption>`）やパラメータ追加機能（:ref:`パラメータ追加<tag-submit_change_parameter>`）を実現するため、hiddenパラメータを出力しています。:ref:`tag-form_tag` でGETを指定した場合、これらのhiddenパラメータがURLに付加されるため、以下の問題が発生します：

- 業務機能に不要なパラメータが増加
- URLの長さ制限により正しくリクエストできない可能性

### 対応

:ref:`tag-form_tag` でGET指定時、hiddenパラメータは出力されません。これにより上記問題は発生しませんが、hiddenパラメータに依存する一部のカスタムタグが使用制限または使用不可となります。

### 使用制限のあるカスタムタグ

**対象**：:ref:`tag-checkbox_tag`、:ref:`tag-code_checkbox_tag`

**制限理由**：これらのタグは隠れた暗号化（:ref:`hidden暗号化<tag-hidden_encryption>`）を使用してチェックなし判定を実装しているため、GETリクエストでは使用できません。

**対応方法**：:ref:`バリデーション<validation>` 後に値をnull判定し、チェック有無を判断してアクション側でチェックなしに対する値を設定します。

### 使用不可となるカスタムタグの対応

以下のカスタムタグはGETリクエスト時に使用不可です。代替方法を使用してください。

#### hiddenタグの代替

**対応方法**：:ref:`tag-plain_hidden_tag` を使用します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:hidden name="test" />

<%-- GETの場合 --%>
<n:plainHidden name="test" />
```

#### submitタグの代替

**対応方法**：HTMLのinputタグ（type="submit"）を使用します。サブミット先URIは :ref:`tag-form_tag` のaction属性に指定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:submit type="button" uri="search" value="検索" />
</n:form>

<%-- GETの場合 --%>
<n:form method="GET" action="search">
  <input type="submit" value="検索" />
</n:form>
```

#### buttonタグの代替

**対応方法**：HTMLのbuttonタグ（type="submit"）を使用します。サブミット先URIは :ref:`tag-form_tag` のaction属性に指定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:button type="submit" uri="search" value="検索" />
</n:form>

<%-- GETの場合 --%>
<n:form method="GET" action="search">
  <button type="submit" value="検索" />
</n:form>
```

#### submitLinkタグの代替

**対応方法**：:ref:`tag-a_tag` を使用し、onclick属性に画面遷移のJavaScript関数を指定します。関数は :ref:`tag-script_tag` 内に記述します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:text name="test" />
  <n:submitLink type="button" uri="search" value="検索" />
</n:form>

<%-- GETの場合 --%>
<input type="text" name="test" id="test" />
<n:a href="javascript:void(0);" onclick="searchTest();">検索</n:a>
<n:script type="text/javascript">
  var searchTest = function() {
    var test = document.getElementById('test').value;
    location.href = 'search?test=' + test;
  }
</n:script>
```

#### popupSubmitタグの代替

**対応方法**：HTMLのinputタグ（type="button"）を使用し、onclick属性にJavaScriptのwindow.open()関数を指定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:popupSubmit type="button" value="検索" uri="search"
    popupWindowName="popupWindow" popupOption="width=700,height=500" />
</n:form>

<%-- GETの場合 --%>
<n:form method="GET">
  <input type="button" value="検索"
    onclick="window.open('search', 'popupWindow', 'width=700,height=500')" />
</n:form>
```

#### popupButtonタグの代替

**対応方法**：HTMLのbuttonタグ（type="submit"）を使用し、onclick属性にJavaScriptのwindow.open()関数を指定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:popupButton type="submit" value="検索" uri="search"
    popupWindowName="popupWindow" popupOption="width=700,height=500" />
</n:form>

<%-- GETの場合 --%>
<n:form method="GET">
  <button type="button" value="検索"
    onclick="window.open('search', 'popupWindow', 'width=700,height=500')" />
</n:form>
```

#### popupLinkタグの代替

**対応方法**：:ref:`tag-a_tag` を使用し、onclick属性にポップアップ表示のJavaScript関数を指定します。関数は :ref:`tag-script_tag` 内に記述します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:text name="test" />
  <n:popupLink type="button" value="検索" uri="search"
    popupWindowName="popupWindow" popupOption="width=700,height=500" />
</n:form>

<%-- GETの場合 --%>
<input type="text" name="test" id="test" />
<n:a href="javascript:void(0);" onclick="openTest();" >検索</n:a>
<n:script type="text/javascript">
  var openTest = function() {
    var test = document.getElementById('test').value;
    window.open('search?test=' + test,
                'popupWindow', 'width=700,height=500')
  }
</n:script>
```

#### paramタグの代替

**対応方法**：パラメータを追加したいボタン/リンク毎に :ref:`tag-form_tag` を記述し、form内にそれぞれパラメータを設定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:submit type="button" uri="search" value="検索">
    <n:param paramName="changeParam" value="テスト１"/>
  </n:submit>
  <n:submit type="button" uri="search" value="検索">
    <n:param paramName="changeParam" value="テスト２"/>
  </n:submit>
</n:form>

<%-- GETの場合 --%>
<n:form method="GET" action="search">
  <n:set var="test" value="テスト１" />
  <input type="hidden" name="changeParam" value="<n:write name='test' />" />
  <input type="submit" value="検索" />
</n:form>

<n:form method="GET" action="search">
  <n:set var="test" value="テスト２" />
  <input type="hidden" name="changeParam" value="<n:write name='test' />" />
  <input type="submit" value="検索" />
</n:form>
```

#### changeParamNameタグの代替

**対応方法**：基本的には :ref:`tag-a_tag` と同様です。window.open()の第一引数に、クエリストリングの変更後パラメータ名を指定します。

**実装例**：
```jsp
<%-- POSTの場合 --%>
<n:form>
  <n:text name="test" />
  <n:popupSubmit type="button" value="検索" uri="search"
      popupWindowName="popupWindow" popupOption="width=700,height=500">
    <n:changeParamName inputName="test" paramName="changeParam" />
  </n:popupSubmit>
</n:form>

<%-- GETの場合 --%>
<input type="text" name="test" id="test" />
<input type="button" value="検索" onclick="openTest();" />
<n:script type="text/javascript">
  var openTest = function() {
    var test = document.getElementById('test').value;
    window.open('search?changeParam=' + test,
                'popupWindow', 'width=700,height=500');
  }
</n:script>
```

## 値を出力する

値を出力には、:ref:`tag-write_tag`を使用する。

アクション側でリクエストスコープに設定したオブジェクトに、name属性を指定することでアクセスする。

## 実装例

### アクション

```java
// リクエストスコープに"person"という名前でオブジェクトを設定する。
Person person = new Person();
person.setPersonName("名前");
context.setRequestScopedVar("person", person);
```

### JSP

```jsp
<!-- name属性を指定してオブジェクトのpersonNameプロパティにアクセスする。 -->
<n:write name="person.personName" />
```

## HTMLエスケープせずに値を出力する

アクションなどで設定された値をページ上に出力する場合は :ref:`tag-write_tag` を使用するが、HTMLエスケープせずに値を出力したい場合は以下のカスタムタグを使用する：

- :ref:`prettyPrintタグ <tag-html_unescape_pretty_print_tag>`
- :ref:`rawWriteタグ <tag-html_unescape_raw_write_tag>`

これらのカスタムタグは、システム管理者がメンテナンス情報を設定できるシステムで、特定の画面や表示領域のみで使用することを想定している。

## prettyPrintタグ

`<b>`、`<del>` のような装飾系のHTMLタグをエスケープせずに出力するカスタムタグ。

## 設定方法

使用可能なHTMLタグ及び属性は :ref:`tag-setting` で以下を設定できる：

- **クラス**: `CustomTagConfig`
- **プロパティ**: `safeTags` / `safeAttributes`

デフォルトで使用可能なタグ、属性はリンク先を参照。

## 非推奨について

> **重要**: このタグは以下の問題があるため非推奨とする。

**問題1**: 使用可能なタグだけでなく、そのタグで使用する属性も含めて全て `CustomTagConfig` に設定しなければならない。例えば、`a` タグを使用可能にしたい場合は `safeTags` に `a` を追加するだけでなく、`safeAttributes` にも `href` などの `a` タグで使用する属性を全て定義する必要がある。

**問題2**: 入力された文字列が `CustomTagConfig` に設定したタグ、属性のみを使用しているかのチェックしか行っておらず、HTMLとして正しいかどうかをチェックしていない。

## 代替方法

利用者が任意の装飾を施した文字列を画面に出力するような機能を実現したい場合は、以下の手順を参考にPJの要件に合わせて実装すること：

1. OSSのHTMLパーサを使用して入力された値をパースし、使用できないHTMLタグが含まれていないかをバリデーションする
2. :ref:`rawWriteタグ <tag-html_unescape_raw_write_tag>` を使用して画面に出力する

簡易的な装飾であれば、利用者にMarkdownで入力してもらい、OSSのJavaScriptライブラリを使用してクライアントサイドでMarkdownからHTMLに変換する方法もある。

## セキュリティに関する注意

> **警告**: :ref:`tag-pretty_print_tag` で出力する変数の内容が、不特定のユーザによって任意に設定できるものであった場合、脆弱性の要因となる可能性がある。使用可能なHTMLタグ及び属性を設定する場合は、その選択に十分に留意すること。例えば、<script>タグやonclick属性を使用可能とした場合、クロスサイトスクリプティング(XSS)脆弱性の直接要因となるため、これらのタグや属性を使用可能としないこと。

## rawWriteタグ

変数中の文字列の内容をエスケープせずにそのまま出力するカスタムタグ。

## セキュリティに関する注意

> **警告**: :ref:`tag-raw_write_tag` で出力する変数の内容が、不特定のユーザによって任意に設定できるものであった場合、クロスサイトスクリプティング(XSS)脆弱性の直接の要因となる。そのため、:ref:`tag-raw_write_tag` の使用には十分な考慮が必要である。

## フォーマットして値を出力する

カスタムタグでは、日付や金額などの値を人が見やすい形式にフォーマットして出力する機能を提供する。

:ref:`format` を使用してフォーマットする方法と、valueFormat属性を使用してフォーマットする2種類の方法が存在する。以下の理由から、:ref:`format` を使用してフォーマットする方法を推奨する：

* :ref:`format` を使用する方法：ファイル出力やメッセージングなどの他の出力機能との共通部品を使用でき、設定が1箇所に集約される。また、使用できるタグに制限がない。
* valueFormat属性を使用する方法：カスタムタグが独自実装のため、カスタムタグでのみ使用可能。他の出力機能でフォーマットが必要な場合は別途設定が必要となり、フォーマット設定が複数箇所に分散する。また、使用できるタグは :ref:`tag-write_tag` と :ref:`tag-text_tag` に限定される。

## :ref:`format` を使用したフォーマット

:ref:`format` を使用する場合は、EL式内で ``n:formatByDefault`` または ``n:format`` を使用して、フォーマットした文字列をvalue属性に設定する。

EL式は JSP上で ``${<評価したい式>}`` と記述することで、評価結果を出力できる記述方法である。``n:formatByDefault`` 及び ``n:format`` をEL式内で使用することで、:ref:`format` の ``FormatterUtil`` を呼び出して値をフォーマットできる。

**実装例**：

```html
<!-- フォーマッタのデフォルトのパターンでフォーマットする場合
  第一引数に使用するフォーマッタ名を指定する
  第二引数にフォーマット対象の値を指定する
  value属性にEL式で n:formatByDefault の呼び出しを記述する -->
<n:write value="${n:formatByDefault('dateTime', project.StartDate)}" />

<!-- 指定したパターンでフォーマットする場合
  第一引数に使用するフォーマッタ名を指定する
  第二引数にフォーマット対象の値を指定する
  第三引数にフォーマットのパターンを指定する
  value属性にEL式で n:format の呼び出しを記述する -->
<n:text name="project.StartDate" value="${n:format('dateTime', project.StartDate, 'yyyy年MM月dd日')}" />
```

> **重要**: EL式ではリクエストパラメータを参照できない。:ref:`bean_validation` を使用してウェブアプリケーションのユーザ入力値のチェックを行う場合は :ref:`bean_validation_onerror` の設定が必要。上記の設定が使用できない場合は、``n:set`` を使用して値をリクエストパラメータから取り出してページスコープにセットしてから出力すること。

**実装例（bean_validation使用時）**：

```jsp
<n:set var="projectEndDate" name="form.projectEndDate" scope="page" />
<n:text name="form.projectEndDate" nameAlias="form.date"
  value="${n:formatByDefault('dateTime', projectEndDate)}"
  cssClass="form-control datepicker" errorCss="input-error" />
```

## valueFormat属性を使用したフォーマット

valueFormat属性を指定することでフォーマットして値を出力する。valueFormat属性の指定がない場合は、フォーマットせずに値を出力する。使用できるタグは :ref:`tag-write_tag` と :ref:`tag-text_tag` のみである。

フォーマットは ``データタイプ{パターン}`` 形式で指定する。カスタムタグでデフォルトで提供しているデータタイプ：

* :ref:`yyyymmdd (年月日)<tag-format_yyyymmdd>`
* :ref:`yyyymm (年月)<tag-format_yyyymm>`
* :ref:`dateTime (日時)<tag-format_datetime>`
* :ref:`decimal (10進数)<tag-format_decimal>`

### yyyymmdd（年月日）

年月日のフォーマット。値は yyyyMMdd 形式またはパターン形式の文字列を指定する。パターンには `SimpleDateFormat` が規定している構文を指定する。パターン文字には y(年)、M(月)、d(月における日)のみ指定可能。

パターン文字列を省略した場合は、:ref:`tag-setting` (yyyymmddPatternプロパティ)に設定されたデフォルトのパターンを使用する。パターンの後に区切り文字 ``|`` を使用してフォーマットのロケールを指定できる。ロケールを明示的に指定しない場合は、`ThreadContext` の言語を使用する。`ThreadContext` が設定されていない場合は、システムデフォルトロケール値を使用する。

**実装例**：

```properties
# デフォルトのパターンとスレッドコンテキストに設定されたロケールを使用する。
valueFormat="yyyymmdd"

# 明示的に指定されたパターンと、スレッドコンテキストに設定されたロケールを使用する。
valueFormat="yyyymmdd{yyyy/MM/dd}"

# デフォルトのパターンを使用し、ロケールのみ指定する場合。
valueFormat="yyyymmdd{|ja}"

# パターン、ロケールの両方を明示的に指定する場合。
valueFormat="yyyymmdd{yyyy年MM月dd日|ja}"
```

> **重要**: :ref:`tag-text_tag` のvalueFormat属性を指定した場合、入力画面にもフォーマットした値が出力される。入力された年月日をアクションで取得する場合は、:ref:`ウィンドウスコープ <tag-window_scope>` および `Nablarch独自のバリデーションが提供する年月日コンバータ` を使用する。:ref:`tag-text_tag` と :ref:`ウィンドウスコープ <tag-window_scope>` 、`年月日コンバータ` が連携し、valueFormat属性に指定されたパターンを使用した値変換とバリデーションを行う。なお、:ref:`bean_validation` は :ref:`tag-text_tag` のvalueFormat属性に対応していない。

> **重要**: :ref:`ウィンドウスコープ <tag-window_scope>` を使用しない場合は、:ref:`tag-text_tag` のvalueFormat属性を指定してもvalueFormat属性の値がサーバサイドに送信されないためバリデーションエラーが発生してしまう。その場合は `YYYYMMDD` アノテーションのallowFormat属性を指定することで、入力値のチェックを行うことができる。

### yyyymm（年月）

年月のフォーマット。値は yyyyMM 形式またはパターン形式の文字列を指定する。使用方法は yyyymmdd と同じ。

### dateTime（日時）

日時のフォーマット。値は `Date` 型を指定する。パターンには `SimpleDateFormat` が規定している構文を指定する。

デフォルトでは、`ThreadContext` に設定された言語とタイムゾーンに応じた日時が出力される。パターン文字列の後に区切り文字 ``|`` を使用してロケールおよびタイムゾーンを明示的に指定できる。

:ref:`tag-setting` (dateTimePatternプロパティ、patternSeparatorプロパティ)を使用して、パターンのデフォルト値の設定と、区切り文字 ``|`` を変更できる。

**実装例**：

```properties
# デフォルトのパターンとThreadContextに設定されたロケール、タイムゾーンを使用する場合。
valueFormat="dateTime"

# デフォルトのパターンを使用し、ロケールおよびタイムゾーンのみ指定する場合。
valueFormat="dateTime{|ja|Asia/Tokyo}"

# デフォルトのパターンを使用し、タイムゾーンのみ指定する場合。
valueFormat="dateTime{||Asia/Tokyo}"

# パターン、ロケール、タイムゾーンを全て指定する場合。
valueFormat="dateTime{yyyy年MMM月d日(E) a hh:mm|ja|America/New_York}"

# パターンとタイムゾーンを指定する場合。
valueFormat="dateTime{yy/MM/dd HH:mm:ss||Asia/Tokyo}"
```

### decimal（10進数）

10進数のフォーマット。値は `Number` 型又は数字の文字列を指定する。文字列の場合、3桁ごとの区切り文字(1,000,000のカンマ)を取り除いた後でフォーマットされる。パターンには `DecimalFormat` が規定している構文を指定する。

デフォルトでは、`ThreadContext` に設定された言語を使用して、言語に応じた形式で値が出力される。言語を直接指定することで、指定された言語に応じた形式で値を出力できる。言語の指定は、パターンの末尾に区切り文字 ``|`` を使用して言語を付加することで行う。

:ref:`tag-setting` (patternSeparatorプロパティ)を使用して、区切り文字 ``|`` を変更できる。

**実装例**：

```properties
# ThreadContextに設定された言語を使用し、パターンのみ指定する場合。
valueFormat="decimal{###,###,###.000}"

# パターンと言語を指定する場合。
valueFormat="decimal{###,###,###.000|ja}"
```

> **補足**: 本機能では値のフォーマットのみを行うため、丸め動作の設定は行わない（`DecimalFormat` のデフォルトが使用される）。丸め処理を行いたい場合には、アプリケーション側で処理を行い、本機能を用いてフォーマット処理を行うこと。

> **重要**: :ref:`tag-text_tag` のvalueFormat属性を指定した場合、入力画面にもフォーマットした値が出力される。入力された数値をアクションで取得する場合は数値コンバータ（`BigDecimalConvertor` 、`IntegerConvertor` 、`LongConvertor` ）を使用する。:ref:`tag-text_tag` と数値コンバータが連携し、valueFormat属性に指定された言語に対応する値変換とバリデーションを行う。なお、:ref:`bean_validation` は :ref:`tag-text_tag` のvalueFormat属性に対応していない。

> **補足**: パターンに桁区切りと小数点を指定する場合は、言語に関係なく常に桁区切りにカンマ、小数点にドットを使用すること。例えば、スペイン語(es)の場合は、桁区切りがドット、小数点がカンマにフォーマットされるが、パターン指定では常に桁区切りにカンマ、小数点にドットを指定する：``valueFormat="decimal{###,###,###.000|es}"``

## エラー表示を行う

エラー表示の機能：

- :ref:`エラーメッセージの一覧表示 <tag-write_error_errors_tag>`
- :ref:`エラーメッセージの個別表示 <tag-write_error_error_tag>`
- :ref:`入力項目のハイライト表示 <tag-write_error_css>`

> **補足**: エラー表示に使用するカスタムタグは、リクエストスコープから `ApplicationException` を取得してエラーメッセージを出力する。`ApplicationException` は :ref:`on_error_interceptor` を使用してリクエストスコープに設定する。

### エラーメッセージの一覧表示

画面上部にエラーメッセージを一覧表示する場合は :ref:`tag-errors_tag` を使用する。

**すべてのエラーメッセージを表示する場合**

`filter="all"` を指定する。

```jsp
<n:errors filter="all" errorCss="alert alert-danger" />
```

![](../../knowledge/component/libraries/assets/libraries-tag/errors_all.png)

**入力項目に対応しないエラーメッセージのみを表示する場合**

`filter="global"` を指定する。

```java
throw new ApplicationException(
  MessageUtil.createMessage(MessageLevel.ERROR, "errors.duplicateName"));
```

```jsp
<n:errors filter="global" errorCss="alert alert-danger" />
```

![](../../knowledge/component/libraries/assets/libraries-tag/errors_global.png)

### エラーメッセージの個別表示

入力項目ごとにエラーメッセージを表示する場合は :ref:`tag-error_tag` を使用する。

**基本的な使用法**

入力項目と同じ名前を `name` 属性に指定する。

```jsp
<div>
  <label>名前</label>
  <n:text name="form.userName" />
  <n:error name="form.userName" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

![](../../knowledge/component/libraries/assets/libraries-tag/error.png)

**相関バリデーションエラーの表示**

:ref:`bean_validation-correlation_validation` のエラーメッセージを特定の項目の近くに表示する場合も :ref:`tag-error_tag` を使用する。

相関バリデーションの例：

```java
@AssertTrue(message = "パスワードが一致しません。")
public boolean isComparePassword() {
    return Objects.equals(password, confirmPassword);
}
```

JSP実装：

```jsp
<div>
  <label>パスワード</label>
  <n:password name="form.password" nameAlias="form.comparePassword" />
  <n:error name="form.password" messageFormat="span" errorCss="alert alert-danger" />
  <n:error name="form.comparePassword" messageFormat="span" errorCss="alert alert-danger" />
</div>
<div>
  <label>パスワード(確認用)</label>
  <n:password name="form.confirmPassword" nameAlias="form.comparePassword" />
  <n:error name="form.confirmPassword" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

![](../../knowledge/component/libraries/assets/libraries-tag/error_correlation_validation.png)

`nameAlias` 属性で相関バリデーションのプロパティ名を指定すると、複数の入力項目を紐付けられる。

### 入力項目のハイライト表示

入力項目のカスタムタグは、エラーがある入力項目の `class` 属性に CSS クラス名を追記する（デフォルト: `nablarch_error`）。

このクラス名に CSS でスタイルを指定することで、エラーがある入力項目をハイライト表示する。

`nameAlias` 属性を指定することで、複数の入力項目を紐付けて、:ref:`bean_validation-correlation_validation` でエラーになった場合に複数の入力項目をハイライト表示できる。

CSS例：

```css
input.nablarch_error,select.nablarch_error {
  background-color: #FFFFB3;
}
```

JSP例：

```jsp
<div>
  <label>パスワード</label>
  <n:password name="form.password" nameAlias="form.comparePassword" />
  <n:error name="form.password" messageFormat="span" errorCss="alert alert-danger" />
  <n:error name="form.comparePassword" messageFormat="span" errorCss="alert alert-danger" />
</div>
<div>
  <label>パスワード(確認用)</label>
  <n:password name="form.confirmPassword" nameAlias="form.comparePassword" />
  <n:error name="form.confirmPassword" messageFormat="span" errorCss="alert alert-danger" />
</div>
```

![](../../knowledge/component/libraries/assets/libraries-tag/error_css.png)

## コード値を表示する

カスタムタグでは、 :ref:`code` から取得したコード値の選択項目や表示項目を出力するコード値専用のカスタムタグを提供する。

**提供タグ:**
- :ref:`tag-code_tag` (コード値)
- :ref:`tag-code_select_tag` (コード値のプルダウン)
- :ref:`tag-code_checkbox_tag` (コード値のチェックボックス)
- :ref:`tag-code_radio_buttons_tag` (コード値の複数のラジオボタン)
- :ref:`tag-code_checkboxes_tag` (コード値の複数のチェックボックス)

**実装例で使用するコードデータ**

コードパターンテーブル:

| ID | VALUE | PATTERN1 | PATTERN2 |
|---|---|---|---|
| GENDER | MALE | 1 | 1 |
| GENDER | FEMALE | 1 | 1 |
| GENDER | OTHER | 1 | 0 |

コード名称テーブル:

| ID | VALUE | LANG | SORT_ORDER | NAME | SHORT_NAME |
|---|---|---|---|---|---|
| GENDER | MALE | ja | 1 | 男性 | 男 |
| GENDER | FEMALE | ja | 2 | 女性 | 女 |
| GENDER | OTHER | ja | 3 | その他 | 他 |

**:ref:`tag-code_tag` (コード値)**

JSP実装例:
```jsp
<!--
  以下の属性指定により、コード値の出力を制御する。
  codeId属性: コードID。
  pattern属性: 使用するパターンのカラム名。
               デフォルトは指定なし。
  optionColumnName属性: 取得するオプション名称のカラム名。
  labelPattern属性: ラベルを整形するパターン。
                    使用できるプレースホルダは以下のとおり。
                    $NAME$: コード値に対応するコード名称
                    $SHORTNAME$: コード値に対応するコードの略称
                    $OPTIONALNAME$: コード値に対応するコードのオプション名称。
                                    このプレースホルダを使用する場合は、
                                    optionColumnName属性の指定が必須となる。
                    $VALUE$: コード値
                    デフォルトは$NAME$。
-->
<n:code name="user.gender"
        codeId="GENDER" pattern="PATTERN1"
        labelPattern="$VALUE$:$NAME$($SHORTNAME$)"
        listFormat="div" />
```

HTML出力:
```html
<!--
  "user.gender"が"FEMALE"の場合
  listFormat属性でdivを指定しているのでdivタグで出力される。
-->
<div>FEMALE:女性(女)</div>
```

**:ref:`tag-code_select_tag` (コード値のプルダウン)**

属性指定はcodeタグと同じ。

JSP実装例:
```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

HTML出力:
```html
<!-- "form.gender"が"FEMALE"の場合 -->

<!-- 入力画面 -->
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>

<!-- 確認画面 -->
<div>FEMALE-女</div>
```

> **重要**: カスタムタグでは言語指定によるコード値の取得はできない。カスタムタグは `CodeUtil` のロケールを指定しないAPIを使用している。言語指定でコード値を取得する場合は、アクションで `CodeUtil` を使用して値を取得すること。

## メッセージを出力する

メッセージID指定のメッセージを出力するカスタムタグ。国際化アプリケーションでユーザが選択した言語に応じて画面文言を切り替える場合に使用。

**タグ**: `<n:message />`

**属性仕様**:

| 属性名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| messageId | String | ○ | | メッセージID |
| var | String | | | 結果を格納する変数名 |
| option0 | String | | | メッセージに埋め込むオプション値0 |
| option1 | String | | | メッセージに埋め込むオプション値1 |
| language | String | | | メッセージの言語を指定 |
| htmlEscape | boolean | | true | HTMLエスケープの有効/無効 |

**使用例**:

```jsp
<!-- 基本：メッセージID指定 -->
<n:message messageId="page.not.found" />

<!-- 変数に格納 -->
<n:message var="title" messageId="title.user.register" />
<n:message var="appName" messageId="title.app" />

<!-- オプション値を埋め込み -->
<n:message messageId="title.template" option0="${title}" option1="${appName}" />

<!-- 言語指定 -->
<n:message messageId="page.not.found" language="ja" />

<!-- HTMLエスケープ無効化 -->
<n:message messageId="page.not.found" htmlEscape="false" />
```

## 言語毎にリソースパスを切り替える

## 言語毎にリソースパスを切り替える

リソースパスを扱うカスタムタグは、言語設定をもとにリソースパスを動的に切り替える機能をもつ。以下のカスタムタグが言語毎のリソースパスの切り替えに対応している。

- :ref:`tag-a_tag`
- :ref:`tag-img_tag`
- :ref:`tag-link_tag`
- :ref:`tag-script_tag`
- :ref:`tag-confirmation_page_tag`（入力画面と確認画面を共通化）
- :ref:`tag-include_tag`（インクルード）

これらのカスタムタグでは、`ResourcePathRule`のサブクラスを使用して言語毎のリソースパスを取得することで切り替えを行う。デフォルトで提供するサブクラスについては、:ref:`http_response_handler-change_content_path`を参照。

> **補足**: :ref:`tag-include_tag`は動的なJSPインクルードを言語毎のリソースパスの切り替えに対応させるために提供している。:ref:`tag-include_param_tag`を使用してインクルード時に追加するパラメータを指定する。
>
> ```jsp
> <!-- path属性にインクルードするリソースのパスを指定する。 -->
> <n:include path="/app_header.jsp">
>     <!--
>       paramName属性にパラメータ名、value属性に値を指定する。
>       スコープ上に設定された値を使用する場合はname属性を指定する。
>       name属性とvalue属性のどちらか一方を指定する。
>     -->
>     <n:includeParam paramName="title" value="ユーザ情報詳細" />
> </n:include>
> ```

## ブラウザのキャッシュを防止する

:ref:`tag-no_cache_tag` を使用してブラウザのキャッシュ防止を行う。キャッシュを防止したい画面の JSP で指定する。

実装例：

```jsp
<!-- headタグ内にnoCacheタグを指定する。 -->
<head>
  <n:noCache/>
  <!-- 以下省略。 -->
</head>
```

:ref:`tag-no_cache_tag` を指定すると、以下のレスポンスヘッダとHTMLがブラウザに返る。

レスポンスヘッダ：

```
Expires Thu, 01 Jan 1970 00:00:00 GMT
Cache-Control no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma no-cache
```

HTML：

```html
<head>
  <meta http-equiv="pragma" content="no-cache">
  <meta http-equiv="cache-control" content="no-cache">
  <meta http-equiv="expires" content="0">
</head>
```

> **重要**: :ref:`tag-no_cache_tag` は :ref:`tag-include_tag` (<jsp:include>) でincludeされるJSPでは指定できないため、必ずforwardされるJSPで指定すること。ただし、システム全体でブラウザのキャッシュ防止を使用する場合は、各JSPで実装漏れが発生しないように、プロジェクトで :ref:`ハンドラ <nablarch_architecture-handler_queue>` を作成し一律設定すること。:ref:`ハンドラ <nablarch_architecture-handler_queue>` では、上記のレスポンスヘッダ例の内容をレスポンスヘッダに設定する。

> **補足**: HTTPの仕様上は、レスポンスヘッダのみを指定すればよいはずであるが、この仕様に準拠していない古いブラウザのためにmetaタグも指定している。

> **補足**: ブラウザのキャッシュ防止は、以下のブラウザでHTTP/1.0かつSSL(https)が適用されない通信において有効にならない。このため、ブラウザのキャッシュ防止を使用する画面は、必ずSSL通信を適用するように設計すること。問題が発生するブラウザ：IE6、IE7、IE8

## 静的コンテンツの変更時にクライアント側のキャッシュを参照しないようにする

クライアント側(ブラウザ)でキャッシュを有効化している場合、サーバ上に配置した静的コンテンツを置き換えても、クライアント側では最新のコンテンツではなくキャッシュされた古いコンテンツが表示される可能性がある。

この問題を回避するため、以下のカスタムタグの `href` 属性および `src` 属性で指定された静的コンテンツのURIにパラメータでバージョンを付加する機能を提供する：

* :ref:`tag-link_tag`
* :ref:`tag-img_tag`
* :ref:`tag-script_tag`
* :ref:`tag-submit_tag`
* :ref:`tag-popup_submit_tag`
* :ref:`tag-download_submit_tag`

これにより、静的コンテンツ置き換え時にクライアント側のキャッシュではなく最新の静的コンテンツを参照できる。

パラメータに付加する静的コンテンツのバージョンは、:ref:`設定ファイル(propertiesファイル)<repository-environment_configuration>` に設定する。設定ファイルに静的コンテンツのバージョンが設定されていない場合は、この機能は無効化される。

**プロパティ名**: `static_content_version`

設定例：

```properties
# 静的コンテンツのバージョン
static_content_version=1.0
```

> **重要**: この機能は以下の理由により非推奨とする：
>
> * `static_content_version` による静的コンテンツのバージョンはアプリケーション内で1つしか定義できないため、値を変更すると全ての静的コンテンツ(変更していないものも含む)がキャッシュではなく最新の静的コンテンツを参照してしまう。
>
> 静的コンテンツの変更時にキャッシュを参照しないようにするには、この機能を使用するのではなく、静的コンテンツのファイル名を変更する等で対応すること。

## 論理属性を指定する

カスタムタグで定義されている論理属性は、`true` / `false` を指定して属性の出力有無を制御できる。

**true を指定した場合：属性が出力される**

JSP：
```jsp
<!-- 論理属性にtrueを指定 -->
<n:text name="form.userId" disabled="true" />
```

HTML：
```html
<!-- 論理属性が出力される -->
<input type="text" name="form.userId" disabled="disabled" />
```

**false を指定した場合：属性が出力されない**

JSP：
```jsp
<!-- 論理属性にfalseを指定 -->
<n:text name="form.userId" disabled="false" />
```

HTML：
```html
<!-- 論理属性が出力されない -->
<input type="text" name="form.userId" />
```

## 任意の属性を指定する

カスタムタグでは `jakarta.servlet.jsp.tagext.DynamicAttributes` インタフェースを使用して動的属性を扱っている。これにより、HTML5で追加された属性を含む任意の属性をカスタムタグで出力できる。HTMLを出力するタグについては動的属性を使用可能としている。

## 論理属性の扱い

論理属性として扱う動的属性は、`true`/`false`を指定して出力有無を制御できる。

デフォルトでは以下の動的属性を論理属性として扱う：

* async
* autofocus
* checked
* disabled
* formnovalidate
* hidden
* ismap
* itemscope
* multiple
* nomodule
* novalidate
* readonly
* required
* reversed
* selected

論理属性として扱う動的属性は変更できる。変更する場合は論理属性のリストを `CustomTagConfig` の `dynamicBooleanAttributesプロパティ` に設定する。

## Content Security Policy(CSP)に対応する

:ref:`セキュアハンドラでnonceを生成する設定<content_security_policy>` を行うと、カスタムタグの動作が次のように変化する。

* :ref:`tag-form_tag` が生成するJavaScriptをscript要素にまとめ、nonce属性にセキュアハンドラが生成したnonceを設定する
  * 自動でonclick属性に指定する関数呼び出しを含む
* :ref:`tag-script_tag` が生成するscript要素のnonce属性にセキュアハンドラが生成したnonceを設定する
* セキュアハンドラが生成したnonceを :ref:`tag-csp_nonce_tag` で出力できるようになる

これらの機能をCSPへの対応に利用できる。

> **重要**: NablarchでのCSP対応はnonceを利用することで実現する。nonceはHTML内に埋め込まれることも多いため、JSPから生成されるHTMLがリクエストの都度変化することを意味する。

## セキュアハンドラが生成したnonceを任意の要素に埋め込む

## セキュアハンドラが生成したnonceを任意の要素に埋め込む

:ref:`tag-csp_nonce_tag` は :ref:`セキュアハンドラ<content_security_policy>` で生成したnonceを出力するカスタムタグです。

CSP対応時、スクリプトやスタイルはインラインではなく外部ファイルとして作成することを推奨します。既存コンテンツがインライン記述の場合、このタグを使用して対象要素にnonce属性を設定して対応できます。

### 使用例（style要素）

JSPテンプレート:
```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

出力HTML:
```html
<style nonce="DhcnhD3khTMePgXwdayK9BsMqXjhguVV">
  <!-- 省略 -->
</style>
```

> **補足**: :ref:`tag-script_tag` で作成したscript要素については、:ref:`セキュアハンドラ<content_security_policy>` でnonce生成が有効な場合、nonce属性が自動で付与されます。script要素のnonce属性が必要な場合は :ref:`tag-csp_nonce_tag` ではなく :ref:`tag-script_tag` を使用してください。

> **補足**: Content-Security-Policyをレスポンスヘッダで設定できない場合、meta要素で設定できます。その場合、:ref:`tag-csp_nonce_tag` の `sourceFormat` 属性を `true` に設定すると、nonceが `nonce-[生成されたnonce]` フォーマットで出力されるため、これをmeta要素に埋め込んでください。

## カスタムタグが生成する要素に対してJavaScriptで処理を追加する

**制約**: onclick属性などのインラインスクリプトを直接指定すると、Content-Security-Policyのポリシーを緩める必要があり、セキュリティレベルが低下します。

**実装手順**:
1. id属性やname属性を使用して、カスタムタグが生成する要素を識別可能にする
2. 生成された要素をセレクタで特定し、追加処理を外部スクリプトファイルまたはnonce付きscript要素として実装する
3. :ref:`JavaScriptを生成する<tag-onclick_override>` カスタムタグの場合、``suppressDefaultSubmit``属性を``true``に設定して生成を抑制する

**JSP例**:
```jsp
<n:form>
  <%-- suppressDefaultSubmitをtrueに設定してカスタムタグによるデフォルトのJavaScriptの生成を抑制する --%>
  <n:submit id="register_button" type="submit" uri="register" suppressDefaultSubmit="true" value="登録" />
</n:form>
```

**JavaScript例**:
```javascript
function popUpConfirmation(event) {
  // フォーム本来のサブミット処理をキャンセルする
  event.preventDefault();

  if (window.confirm('登録します。よろしいですか？')) {
    // カスタムタグが出力するJavaScript関数を明示的に呼び出す。
    // 第2引数のelementはnablarch_submit関数内でeventから導出する
    nablarch_submit(event);
  }
}

// idを指定して処理を登録する
document.querySelector('#register_button').addEventListener('click', popUpConfirmation);
```

**属性**:
- ``suppressDefaultSubmit``: カスタムタグによるJavaScript自動生成を抑制するかどうか（``true``で抑制）

## 拡張例

### フォーマッタを追加する

**:ref:`format` を使用する場合**

:ref:`format` を使用する場合、フォーマッタの追加方法は :ref:`format` のフォーマッタを追加するの項を参照。

**valueFormat属性を使用する場合**

フォーマットは、`ValueFormatter` インタフェースを実装したクラスが行う。実装したクラスをコンポーネント定義に追加することでフォーマットを変更できる。

コンポーネント定義への追加は、Map型でデータタイプ名をキーに、`ValueFormatter` を実装したクラスを値に指定する。

フォーマッタのマップは、`valueFormatters` という名前でコンポーネント定義に追加する。フレームワークがデフォルトでサポートしているフォーマット設定例：

```xml
<map name="valueFormatters">
  <entry key="yyyymmdd">
    <value-component class="nablarch.common.web.tag.YYYYMMDDFormatter" />
  </entry>
  <entry key="yyyymm">
    <value-component class="nablarch.common.web.tag.YYYYMMFormatter" />
  </entry>
  <entry key="dateTime">
    <value-component class="nablarch.common.web.tag.DateTimeFormatter" />
  </entry>
  <entry key="decimal">
    <value-component class="nablarch.common.web.tag.DecimalFormatter" />
  </entry>
</map>
```

### ボタン/リンクの表示制御に使う判定処理を変更する

:ref:`tag-submit_display_control` に使用する判定処理を変更したい場合は、`DisplayControlChecker` インタフェースを実装することで変更できる。

実装したクラスを :ref:`tag-setting` で `displayControlCheckersプロパティ` に指定する。

設定例：

```xml
<list name="displayControlCheckers" >
  <!-- サービス提供可否についてはデフォルトのDisplayControlCheckerを指定する -->
  <component class="nablarch.common.web.tag.ServiceAvailabilityDisplayControlChecker" />
  <!-- 認可チェックについてはプロジェクトでカスタマイズしたDisplayControlCheckerを指定する -->
  <component class="com.sample.app.CustomPermissionDisplayControlChecker" />
</list>

<component name="customTagConfig"
           class="nablarch.common.web.tag.CustomTagConfig">
   <!-- 判定条件を設定する。 -->
  <property name="displayControlCheckers" ref="displayControlCheckers" />
</component>
```

### クライアント側の二重サブミット防止で、二重サブミット発生時の振る舞いを追加する

:ref:`クライアント側の二重サブミット防止 <tag-double_submission_client_side>` を使用していて、アプリケーションで二重サブミット発生時の振る舞いを追加する場合は、JavaScriptでコールバック関数を実装する。

フレームワークのJavaScript関数は、2回目以降のサブミット要求が発生した場合、コールバック関数が存在していれば、コールバック関数を呼び出す。

コールバック関数のシグネチャ：

```javascript
/**
 * @param element 二重サブミットが行われた対象要素(ボタン又はリンク)
 */
function nablarch_handleDoubleSubmission(element) {
  // ここに処理を記述する。
}
```

### サーバ側の二重サブミット防止で、トークンの発行処理を変更する

:ref:`サーバ側の二重サブミット防止 <tag-double_submission_server_side>` を使用していて、トークンの発行処理を変更したい場合は、`TokenGenerator` インタフェースを実装することで変更できる。

実装したクラスをコンポーネント定義に `tokenGenerator` という名前で追加する。

## 命名ルール

カスタムタグの名前規定（CSSクラス名、JavaScript関数名など）は、個別アプリケーションとの重複を避けるため、プレフィックス `nablarch_` を使用する。個別アプリケーションでは `nablarch_` から始まる名前を使用しないこと。

対象範囲：
- HTMLの属性値
- CSSのクラス名
- JavaScriptの関数名とグローバル変数名
- ページスコープ、リクエストスコープ、セッションスコープの変数名

## 入力/出力データへのアクセスルール

カスタムタグの入力/出力タグ（:ref:`tag-text_tag`、:ref:`tag-write_tag`など）は、name属性の値に基づいてデータにアクセスする。

**name属性の指定方法**：
- オブジェクト/Mapのプロパティ：ドット区切り
- List/配列の要素：角括弧でインデックス指定

**検索順序**（最初に見つかった値を使用。見つからなければ空文字列を出力）：
1. Pageスコープ
2. リクエストスコープ
3. リクエストパラメータ
4. セッションスコープ

**実装例 - オブジェクトアクセス**：

アクション：
```java
PersonForm form = new PersonForm();
form.setPersonName("名前");
context.setRequestScopedVar("form", form);
```

JSP：
```jsp
<n:text name="form.personName" />
```

**実装例 - List要素アクセス**：

アクション：
```java
PersonsForm form = new PersonsForm();
List<Person> persons = UniversalDao.findAll(Person.class);
form.setPersons(persons);
context.setRequestScopedVar("form", form);
```

JSP：
```jsp
<c:forEach items="${form.persons}" varStatus="status">
  <n:text name="form.persons[${status.index}].personName" />
</c:forEach>
```

> **補足**: リクエストパラメータが検索対象に含まれるのは、入力フォーム再表示時に入力値を復元するため。Nablarchカスタムタグとは異なり、JSTLタグはリクエストパラメータにアクセスできないため、必要に応じてアクション側で明示的にリクエストスコープに値を設定すること。

> **補足**: リクエストスコープをリクエストパラメータより先に検索するのは、入力フォーム再表示時に入力値を変更できるようにするため。例えば、ラジオボタンを未選択状態に戻したい場合は、アクション側でリクエストスコープに空文字を設定する。

## URIの指定方法

カスタムタグのURI属性の指定方法：

**絶対URL**（http/httpsから始まるパス）

他システム連携などでホストが異なる場合に使用。タグは指定パスをそのまま使用する。

```jsp
<n:a href="https://github.com/coastland">coastland</n:a>
```

**コンテキストからの相対パス**（/から始まるパス）

アプリケーション内のパス指定時に使用。タグは指定パスの先頭にコンテキストパスを付加して使用する。

```jsp
<n:submit type="submit" uri="/action/person/register" value="登録" />
```

**現在のパスからの相対パス**（/から始まらないパス、絶対URL除く）

アプリケーション内のパス指定時に使用。タグは指定パスをそのまま使用する。

```jsp
<n:submit type="submit" uri="login" value="ログイン" />
```

**HTTP/HTTPS切り替え**

コンテキストからの相対パスの場合、secure属性でHTTP/HTTPSを切り替え可能。secure属性指定時、タグはsecure属性の設定値（http用ポート、https用ポート、ホスト）とコンテキストパスを使用してURIを組み立てる。

設定例：
- http用ポート: 8080
- https用ポート: 443
- ホスト: sample.co.jp

HTTP→HTTPS切り替え（secure="true"）：
```jsp
<n:submit type="button" name="login" value="ログイン" uri="/action/login" secure="true" />
```
→ `https://sample.co.jp:443/<コンテキストパス>/action/login`

HTTPS→HTTP切り替え（secure="false"）：
```jsp
<n:submitLink name="logout" uri="/action/logout" secure="false">ログアウト</n:submitLink>
```
→ `https://sample.co.jp:8080/<コンテキストパス>/action/logout`

http用ポート未指定時：
→ `https://sample.co.jp/<コンテキストパス>/action/logout`

> **補足**: secure属性は遷移先のプロトコルを切り替えるボタン/リンクのみで使用。遷移先プロトコルが同じ場合（http→http、https→https）はsecure属性を指定しない。

secure属性使用時、以下のカスタムタグ設定が必要：
- `portプロパティ`
- `securePortプロパティ`
- `hostプロパティ`

## HTMLエスケープと改行、半角スペース変換

**HTMLエスケープ**

カスタムタグは、原則として出力時にすべてのHTML属性をHTMLエスケープする。

| 元文字 | エスケープ後 |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

> **重要**: EL式はHTMLエスケープを実施しないため、値出力にEL式を使用しないこと。値出力には :ref:`tag-write_tag` などのカスタムタグを使用。ただし、JSTLのforEachタグやカスタムタグの属性にオブジェクトを設定する場合など、直接出力しない箇所ではEL式を使用して問題ない。

**改行・半角スペース変換**

確認画面などで入力データを出力する際、HTMLエスケープに加えて改行と半角スペースを変換する。

| 元文字 | 変換後 |
|---|---|
| 改行コード（\n、\r、\r\n） | `<br />` |
| 半角スペース | `&nbsp;` |

## tag_reference

:ref:`tag_reference` を参照。
