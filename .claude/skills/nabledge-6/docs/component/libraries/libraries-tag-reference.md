# タグリファレンス

| このリファレンスには、Nablarchが提供するタグとその属性について記述されている。
| 各タグの使用方法や使用例などの詳細については tag を参照すること。

フォーム
| formタグ (フォーム)


入力
| textタグ (テキスト)
| searchタグ (検索テキスト)
| telタグ (電話番号)
| urlタグ (URL)
| emailタグ (メールアドレス)
| dateタグ (日付)
| monthタグ (月)
| weekタグ (週)
| timeタグ (時間)
| datetimeLocalタグ (ローカル日時)
| numberタグ (数値)
| rangeタグ (レンジ)
| colorタグ (色)
| textareaタグ (テキストエリア)
| passwordタグ (パスワード)
| radioButtonタグ (ラジオボタン)
| checkboxタグ (チェックボックス)
| fileタグ (ファイル)
| plainHiddenタグ (hidden)
| selectタグ (プルダウン)
| compositeKeyRadioButtonタグ (複合キーに対応したラジオボタン)
| compositeKeyCheckboxタグ (複合キーに対応したチェックボックス)
| radioButtonsタグ (複数のラジオボタン)
| checkboxesタグ (複数のチェックボックス)
| codeSelectタグ (コード値のプルダウン)
| codeCheckboxタグ (コード値のチェックボックス)
| codeRadioButtonsタグ (コード値の複数のラジオボタン)
| codeCheckboxesタグ (コード値の複数のチェックボッス)
| hiddenタグ (hidden暗号化)
| hiddenStoreタグ (HIDDENストア)


サブミット
フォームのサブミット
| submitタグ (inputタグのボタン)
| buttonタグ (buttonタグのボタン)
| submitLinkタグ (リンク)

別ウィンドウを開いてサブミット(ポップアップ)
| popupSubmitタグ (inputタグのボタン)
| popupButtonタグ (buttonタグのボタン)
| popupLinkタグ (リンク)

ダウンロード用のサブミット
| downloadSubmitタグ (inputタグのボタン)
| downloadButtonタグ (buttonタグのボタン)
| downloadLinkタグ (リンク)

サブミット制御
| paramタグ (サブミット時に追加するパラメータの指定)
| changeParamNameタグ (ポップアップ用のサブミット時にパラメータ名の変更)


出力
値
| writeタグ (オブジェクトの値)
| prettyPrintタグ (オブジェクトの値。修飾系のHTML(bタグなど)のみエスケープしない)
| rawWriteタグ (オブジェクトの値。HTMLエスケープしない)
| codeタグ (コード値)
| cspNonceタグ (Content Security Policyのnonceの値)
メッセージ
| messageタグ (メッセージ)
エラー
| errorsタグ (エラーメッセージの一覧表示)
| errorタグ (エラーメッセージの個別表示)

URIを指定するHTMLタグ(コンテキストパスの付加とURLリライト)
| aタグ
| imgタグ
| linkタグ
| scriptタグ

ユーティリティ
| noCacheタグ (ブラウザのキャッシュを抑制する)
| setタグ (変数に値を設定する)
| includeタグ (インクルード)
| includeParamタグ (インクルード時に追加するパラメータの指定)
| confirmationPageタグ (入力画面と確認画面を共通化)
| ignoreConfirmationタグ (部分的に確認画面の画面状態を無効化する)
| forInputPageタグ (入力画面のみボディを出力)
| forConfirmationPageタグ (確認画面のみボディを出力)

## 共通属性

各カスタムタグの定義でここで定義した共通属性を参照する。

## 全てのHTMLタグ

| 属性 | 説明 |
|---|---|
| id | XHTMLのid属性。 |
| cssClass | XHTMLのclass属性。 |
| style | XHTMLのstyle属性。 |
| title | XHTMLのtitle属性。 |
| lang | XHTMLのlang属性。 |
| xmlLang | XHTMLのxml:lang属性。 |
| dir | XHTMLのdir属性。 |
| onclick | XHTMLのonclick属性。 |
| ondblclick | XHTMLのondblclick属性。 |
| onmousedown | XHTMLのonmousedown属性。 |
| onmouseup | XHTMLのonmouseup属性。 |
| onmouseover | XHTMLのonmouseover属性。 |
| onmousemove | XHTMLのonmousemove属性。 |
| onmouseout | XHTMLのonmouseout属性。 |
| onkeypress | XHTMLのonkeypress属性。 |
| onkeydown | XHTMLのonkeydown属性。 |
| onkeyup | XHTMLのonkeyup属性。 |

<details>
<summary>keywords</summary>

popupSubmit, ポップアップサブミット, popupWindowName, popupOption, displayMethod, suppressDefaultSubmit, secure, uri, type, name, id, cssClass, style, title, lang, xmlLang, dir, onclick, ondblclick, onmousedown, onmouseup, onmouseover, onmousemove, onmouseout, onkeypress, onkeydown, onkeyup, HTMLタグ共通属性, カスタムタグ共通属性, infoCss, warnCss, errorCss, filter, エラーメッセージ一覧表示, バリデーションエラー表示, メッセージフィルタ, ValidationResultMessage, compositeKeyRadioButton, 複合キーラジオボタン, namePrefix, keyNames, valueObject, 複合キー入力, month, 月入力, HTML5 month, valueFormat, nameAlias, 動的属性, 入力フォームタグ, rawWriteタグ, 変数スコープ, 動的属性使用不可

</details>

## フォーカスを取得可能なHTMLタグ

| 属性 | 説明 |
|---|---|
| accesskey | XHTMLのaccesskey属性。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |

<details>
<summary>keywords</summary>

popupButton, ポップアップボタン, popupWindowName, popupOption, displayMethod, suppressDefaultSubmit, secure, uri, name, type, disabled, value, autofocus, accesskey, tabindex, onfocus, onblur, フォーカス属性, フォーカス取得可能タグ, errorCss, messageFormat, 入力項目エラー表示, エラーメッセージ表示, fileタグ, ファイルアップロード入力, multiple, accept, ファイル選択, onselect, onchange, readonly, size, maxlength, week, 週入力, HTML5 week, valueFormat, nameAlias, 動的属性, 入力フォームタグ, setタグ, var, scope, bySingleValue, リクエストスコープ, ページスコープ

</details>

## 動的属性の使用

動的属性が使用可能なタグでは、定義されていない属性も設定が可能となる。

<details>
<summary>keywords</summary>

popupLink, ポップアップリンク, popupWindowName, popupOption, displayMethod, suppressDefaultSubmit, secure, uri, shape, coords, 動的属性, 未定義属性, カスタムタグ動的属性, noCacheタグ, キャッシュ無効化, ブラウザキャッシュ制御, hiddenタグ, ウィンドウスコープ, 非推奨, hidden値出力, time, 時刻入力, HTML5 time, valueFormat, errorCss, nameAlias, 入力フォームタグ, includeタグ, path, インクルード, 動的属性使用不可

</details>

## 個別属性

## formタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| name | XHTMLのname属性。 |
| action | XHTMLのaction属性。 |
| method | XHTMLのmethod属性。 デフォルトは `post` 。 |
| enctype | XHTMLのenctype属性。 |
| onsubmit | XHTMLのonsubmit属性。 |
| onreset | XHTMLのonreset属性。 |
| accept | XHTMLのaccept属性。 |
| acceptCharset | XHTMLのaccept-charset属性。 |
| target | XHTMLのtarget属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| windowScopePrefixes | ウィンドウスコープ変数のプレフィックス。 複数指定する場合はカンマ区切り。 指定されたプレフィックスがマッチするリクエストパラメータをhiddenタグとして出力する。 |
| useToken | トークンを設定するか否か。 トークンを設定する場合は `true` 、設定しない場合は `false` 。 デフォルトは `false` 。 confirmationPageタグ が指定された場合は、デフォルトが `true` となる。 |
| secure | URIをhttpsにするか否か。 httpsにする場合は `true` 、しない場合は `false` 。 |
| preventPostResubmit | POST再送信防止機能を使用するか否か。 デフォルトは `false` 。 使用する場合は `true` 、しない場合は `false` 。 |

<details>
<summary>keywords</summary>

downloadSubmit, ダウンロードサブミット, ファイルダウンロード, allowDoubleSubmission, 二重サブミット, displayMethod, suppressDefaultSubmit, secure, uri, windowScopePrefixes, useToken, preventPostResubmit, フォームタグ, POST再送信防止, トークン, ウィンドウスコープ, autocomplete, name, codeId, size, multiple, disabled, tabindex, onfocus, onblur, onchange, autofocus, pattern, labelPattern, listFormat, withNoneOption, noneOptionLabel, errorCss, nameAlias, optionColumnName, コードIDセレクトボックス, ドロップダウンリスト, コード選択, plainHiddenタグ, hidden入力, hidden属性, datetimeLocal, 日時入力, HTML5 datetime-local, valueFormat, 動的属性, 入力フォームタグ, includeParamタグ, paramName, value, インクルードパラメータ

</details>

## textタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| readonly | XHTMLのreadonly属性 (論理属性) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| placeholder | HTML5のplaceholder属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

downloadButton, ダウンロードボタン, ファイルダウンロード, allowDoubleSubmission, 二重サブミット, displayMethod, suppressDefaultSubmit, secure, uri, name, type, disabled, value, autofocus, errorCss, nameAlias, valueFormat, nablarch_error, テキスト入力, placeholder, maxlength, readonly, codeId, onchange, pattern, optionColumnName, labelPattern, listFormat, コードIDラジオボタン, ラジオボタングループ, コード選択, hiddenStoreタグ, hidden入力保存, hidden属性, number, 数値入力, HTML5 number, 動的属性, 入力フォームタグ, confirmationPageタグ, path, 確認画面, 入力画面フォワード

</details>

## searchタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

downloadLink, ダウンロードリンク, ファイルダウンロード, allowDoubleSubmission, 二重サブミット, displayMethod, suppressDefaultSubmit, secure, uri, name, shape, coords, errorCss, nameAlias, valueFormat, nablarch_error, 検索テキスト, search入力, codeId, disabled, onchange, autofocus, pattern, optionColumnName, labelPattern, listFormat, コードIDチェックボックス群, 複数コード選択, selectタグ, プルダウン, listName, elementLabelProperty, elementValueProperty, withNoneOption, elementLabelPattern, 選択リスト, tabindex, onfocus, onblur, size, noneOptionLabel, range, 範囲入力, HTML5 range, 動的属性, 入力フォームタグ, ignoreConfirmationタグ, 確認スキップ, 動的属性使用不可

</details>

## telタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

param, サブミットパラメータ, paramName, リクエストスコープ, パラメータ値指定, errorCss, nameAlias, valueFormat, nablarch_error, 電話番号入力, tel入力, name, codeId, value, autofocus, optionColumnName, offCodeValue, disabled, onchange, labelPattern, コードIDチェックボックス単一, チェック状態コード値, radioButtonsタグ, ラジオボタンリスト, listName, elementLabelProperty, elementValueProperty, elementLabelPattern, listFormat, color, カラー入力, HTML5 color, 動的属性, 入力フォームタグ, forInputPageタグ, 入力画面, 動的属性使用不可

</details>

## urlタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

changeParamName, パラメータ名変更, paramName, inputName, サブミットパラメータ, errorCss, nameAlias, valueFormat, nablarch_error, URL入力, url入力, codeId, name, pattern, labelPattern, listFormat, optionColumnName, コード値表示, コード名称表示, checkboxesタグ, チェックボックスリスト, listName, elementLabelProperty, elementValueProperty, elementLabelPattern, onchange, textarea, テキストエリア, 複数行テキスト入力, rows, cols, placeholder, maxlength, 動的属性, forConfirmationPageタグ, 確認画面, 動的属性使用不可

</details>

## emailタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

アンカータグ, リンク, href, secure, target, hreflang, rel, charset, rev, shape, coords, type, name, errorCss, nameAlias, valueFormat, nablarch_error, メールアドレス入力, email入力, sourceFormat, CSPnonce, コンテンツセキュリティポリシー, nonce出力, セキュアハンドラ, submitタグ, サブミットボタン, allowDoubleSubmission, displayMethod, suppressDefaultSubmit, 二重サブミット防止, uri, password, パスワード入力, restoreValue, replacement, 確認画面置換文字, 動的属性

</details>

## dateタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

画像タグ, イメージ, src, alt, secure, usemap, width, height, longdesc, ismap, align, border, hspace, vspace, errorCss, nameAlias, valueFormat, nablarch_error, 日付入力, date入力, messageId, language, var, htmlEscape, withHtmlFormat, option0, メッセージID表示, メッセージ国際化, HTMLエスケープ, リクエストスコープ格納, buttonタグ, ボタン, allowDoubleSubmission, displayMethod, suppressDefaultSubmit, uri, radioButton, ラジオボタン, 単一選択, label, 動的属性

</details>

## monthタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

linkタグ, href, secure, rel, media, type, charset, hreflang, rev, target, name, value, withHtmlFormat, valueFormat, 値の出力, HTMLフォーマット, 変数スコープ参照, submitLinkタグ, リンクボタン, allowDoubleSubmission, displayMethod, suppressDefaultSubmit, shape, coords, uri, checkbox, チェックボックス, useOffValue, offValue, offLabel, 複数選択, errorCss, 動的属性

</details>

## weekタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

<details>
<summary>keywords</summary>

scriptタグ, JavaScript, src, secure, type, defer, xmlSpace, charset, language, name, 非推奨, prettyPrint, prettyPrintタグ廃止, compositeKeyCheckbox, 複合キーチェックボックス, valueObject, keyNames, namePrefix, 複合キー, errorCss, 動的属性

</details>

## timeタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## datetimeLocalタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## numberタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## rangeタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## colorタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## textareaタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| rows `必須` | XHTMLのrows属性。 |
| cols `必須` | XHTMLのcols属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| readonly | XHTMLのreadonly属性 (論理属性) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| placeholder | HTML5のplaceholder属性。 |
| maxlength | HTML5のmaxlength属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## passwordタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| readonly | XHTMLのreadonly属性 (論理属性) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| placeholder | HTML5のplaceholder属性。 |
| restoreValue | 入力画面の再表示時に入力データを復元するか否か。 |
|  | 復元する場合は `true` 、復元しない場合は `false` 。 |
|  | デフォルトは `false` 。 |
| replacement | 確認画面用の出力時に使用する置換文字。 |
|  | デフォルトは `*` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## radioButtonタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| value `必須` | XHTMLのvalue属性。 |
| label `必須` | ラベル。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## checkboxタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| value | XHTMLのvalue属性。 |
|  | チェックありの場合に使用する値。 |
|  | デフォルトは `1` 。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| label | チェックありの場合に使用するラベル。 |
|  | 入力画面では、このラベルが表示される。 |
| useOffValue | チェックなしの値設定を使用するか否か。 |
|  | デフォルトは `true` 。 |
| offLabel | チェックなしの場合に使用するラベル。 |
| offValue | チェックなしの場合に使用する値。 |
|  | デフォルトは `0` 。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## compositeKeyCheckboxタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| valueObject `必須` | XHTMLのvalue属性の代わりに使用するオブジェクト。 |
|  | keyNames属性で指定したプロパティを持つ必要がある。 |
| keyNames `必須` | 複合キーのキー名。 |
|  | キー名をカンマ区切りで指定する。 |
| namePrefix `必須` | リクエストパラメータに展開する際に使用するプレフィクス。 |
|  | 通常のname属性と異なり、この名称に `.` と\ |
|  | keyNames属性で指定したキー名と合致する値を通常のname属性と同様に取り扱う。 |
|  | 例えばnamePrefix属性に `form` 、keyNames属性に `key1` 、 `key2` を指定した場合、\ |
|  | 表示時には `form.key1` 、 `form.key2` で\ |
|  | リクエストスコープに含まれる値を使用してこのチェックボックスの値を出力する。 |
|  | また、サブミットしたリクエストの処理では、\ |
|  | `form.key1` 、 `form.key2` というリクエストパラメータから選択された値が取得できる。 |
|  | なお、name属性は、namePrefix属性とkeyNames属性で指定した\ |
|  | キーの組み合わせと異なる名称にしなければならない特殊な制約がある。\ |
|  | 実装時はこの点に十分注意すること。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| label | チェックありの場合に使用するラベル。 |
|  | 入力画面では、このラベルが表示される。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## compositeKeyRadioButtonタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| valueObject `必須` | XHTMLのvalue属性の代わりに使用するオブジェクト。 |
|  | keyNames属性で指定したプロパティを持つ必要がある。 |
| keyNames `必須` | 複合キーのキー名。 |
|  | キー名をカンマ区切りで指定する。 |
| namePrefix `必須` | リクエストパラメータに展開する際に使用するプレフィクス。 |
|  | 通常のname属性と異なり、この名称に `.` と\ |
|  | keyNames属性で指定したキー名と合致する値を通常のname属性と同様に取り扱う。 |
|  | 例えばnamePrefix属性に `form` 、keyNames属性に `key1` 、 `key2` を指定した場合、\ |
|  | 表示時には `form.key1` 、 `form.key2` で\ |
|  | リクエストスコープに含まれる値を使用してこのチェックボックスの値を出力する。 |
|  | また、サブミットしたリクエストの処理では、\ |
|  | `form.key1` 、 `form.key2` というリクエストパラメータから選択された値が取得できる。 |
|  | なお、name属性は、namePrefix属性とkeyNames属性で指定した\ |
|  | キーの組み合わせと異なる名称にしなければならない特殊な制約がある。\ |
|  | 実装時はこの点に十分注意すること。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| label | チェックありの場合に使用するラベル。 |
|  | 入力画面では、このラベルが表示される。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## fileタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| readonly | XHTMLのreadonly属性 (論理属性) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| accept | XHTMLのaccept属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| multiple | HTML5のmultiple属性 (論理属性) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## hiddenタグ

動的属性の使用可否 ：可

HTMLタグを出力せず、ウィンドウスコープに値を出力する。

> **Important:** ウィンドウスコープは非推奨である。 詳細は、 tag-window_scope を参照。
| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |

## plainHiddenタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |

## hiddenStoreタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |

## selectタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| listName `必須` | 選択肢リストの名前。 |
|  | カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。 |
|  | リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty `必須` | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty `必須` | リスト要素から値を取得するためのプロパティ名。 |
| size | XHTMLのsize属性。 |
| multiple | XHTMLのmultiple属性 (論理属性) 。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| elementLabelPattern | ラベルを整形するためのパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$LABEL$` : ラベル |
|  | `$VALUE$` : 値 |
|  | デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| withNoneOption | リスト先頭に選択なしのオプションを追加するか否か。 |
|  | 追加する場合は `true` 、追加しない場合は `false` 。 |
|  | デフォルトは `false` 。 |
| noneOptionLabel | リスト先頭に選択なしのオプションを追加する場合に使用するラベル。 |
|  | この属性は、withNoneOptionに `true` を指定した場合のみ有効となる。 |
|  | デフォルトは `""`。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## radioButtonsタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ      id属性は指定不可。 |  |
| フォーカスを取得可能なHTMLタグ        a | ccesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| listName `必須` | 選択肢リストの名前。 |
|  | カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。 |
|  | リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty `必須` | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty `必須` | リスト要素から値を取得するためのプロパティ名。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
|  | 選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| elementLabelPattern | ラベルを整形するためのパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$LABEL$` : ラベル |
|  | `$VALUE$` : 値 |
|  | デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## checkboxesタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ      id属性は指定不可。 |  |
| フォーカスを取得可能なHTMLタグ        a | ccesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| listName `必須` | 選択肢リストの名前。 |
|  | カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。 |
|  | リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty `必須` | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty `必須` | リスト要素から値を取得するためのプロパティ名。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
|  | 選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| elementLabelPattern | ラベルを整形するためのパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$LABEL$` : ラベル |
|  | `$VALUE$` : 値 |
|  | デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## submitタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## buttonタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## submitLinkタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## popupSubmitタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## popupButtonタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## popupLinkタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。 |
|  | 新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## downloadSubmitタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## downloadButtonタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## downloadLinkタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name | XHTMLのname属性。 |
| uri `必須` | URI。 |
|  | tag-specify_uri を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。 |
|  | 許可する場合は `true` 、許可しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。 |
|  | 下記のいずれかを指定する。 |
|  | NODISPLAY (非表示) |
|  | DISABLED (非活性) |
|  | NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。 |
|  | 抑制する場合は `true` 、抑制しない場合は `false` 。 |
|  | デフォルトは `false` 。 |

## paramタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | サブミット時に使用するパラメータの名前。 |
| name | 値を取得するための名前。 |
|  | リクエストスコープなどスコープ上のオブジェクトを参照する場合に指定する。 |
|  | name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。 |
|  | 直接値を指定する場合に使用する。 |
|  | name属性とvalue属性のどちらか一方を指定する。 |

## changeParamNameタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | サブミット時に使用するパラメータの名前。 |
| inputName `必須` | 変更元となる元画面のinput要素のname属性。 |

## aタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| charset | XHTMLのcharset属性。 |
| type | XHTMLのtype属性。 |
| name | XHTMLのname属性。 |
| href | XHTMLのhref属性。 |
|  | tag-specify_uri を参照。 |
| hreflang | XHTMLのhreflang属性。 |
| rel | XHTMLのrel属性。 |
| rev | XHTMLのrev属性。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| target | XHTMLのtarget属性。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |

## imgタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| src `必須` | XHTMLのcharsrc属性。 |
|  | tag-specify_uri を参照。 |
| alt `必須` | XHTMLのalt属性。 |
| name | XHTMLのname属性。 |
| longdesc | XHTMLのlongdesc属性。 |
| height | XHTMLのheight属性。 |
| width | XHTMLのwidth属性。 |
| usemap | XHTMLのusemap属性。 |
| ismap | XHTMLのismap属性。 |
| align | XHTMLのalign属性。 |
| border | XHTMLのborder属性。 |
| hspace | XHTMLのhspace属性。 |
| vspace | XHTMLのvspace属性。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |

## linkタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| charset | XHTMLのcharset属性。 |
| href | XHTMLのhref属性。 |
|  | tag-specify_uri を参照。 |
| hreflang | XHTMLのhreflang属性。 |
| type | XHTMLのtype属性。 |
| rel | XHTMLのrel属性。 |
| rev | XHTMLのrev属性。 |
| media | XHTMLのmedia属性。 |
| target | XHTMLのtarget属性。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |

## scriptタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| type `必須` | XHTMLのtype属性。 |
| id | XHTMLのid属性。 |
| charset | XHTMLのcharset属性。 |
| language | XHTMLのlanguage属性。 |
| src | XHTMLのsrc属性。 |
|  | tag-specify_uri を参照。 |
| defer | XHTMLのdefer属性。 |
| xmlSpace | XHTMLのxml:space属性。 |
| secure | URIをhttpsにするか否か。 |
|  | httpsにする場合は `true` 、しない場合は `false` 。 |

## errorsタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| cssClass | リスト表示においてulタグに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_errors` 。 |
| infoCss | 情報レベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_info` 。 |
| warnCss | 警告レベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_warn` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| filter | リストに含めるメッセージのフィルタ条件。 |
|  | 下記のいずれかを指定する。 |
|  | all(全てのメッセージを表示する) |
|  | global(入力項目に対応しないメッセージのみを表示) |
|  | デフォルトは `all` 。 |
|  | globalの場合、\ |
|  | のプロパティ名が入っているメッセージを取り除いて出力する。 |

## errorタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| name `必須` | エラーメッセージを表示する入力項目のname属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| messageFormat | メッセージ表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | デフォルトはdiv。 |

## noCacheタグ

動的属性の使用可否 ：否

属性なし。

## codeSelectタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| size | XHTMLのsize属性。 |
| multiple | XHTMLのmultiple属性 (論理属性) 。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| pattern | 使用するパターンのカラム名。 |
|  | デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$NAME$` : コード値に対応するコード名称 |
|  | `$SHORTNAME$` : コード値に対応するコードの略称 |
|  | `$OPTIONALNAME$` : コード値に対応するコードのオプション名称 |
|  | `$VALUE$`: コード値 |
|  | `$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。 |
|  | デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| withNoneOption | リスト先頭に選択なしのオプションを追加するか否か。 |
|  | 追加する場合は `true` 、追加しない場合は `false` 。 |
|  | デフォルトは `false` 。 |
| noneOptionLabel | リスト先頭に選択なしのオプションを追加する場合に使用するラベル。 |
|  | この属性は、withNoneOptionに `true` を指定した場合のみ有効となる。 |
|  | デフォルトは `""` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## codeRadioButtonsタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ      id属性は指定不可。 |  |
| フォーカスを取得可能なHTMLタグ        a | ccesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
|  | 選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。 |
|  | デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$NAME$` : コード値に対応するコード名称 |
|  | `$SHORTNAME$` : コード値に対応するコードの略称 |
|  | `$OPTIONALNAME$` : コード値に対応するコードのオプション名称 |
|  | `$VALUE$`: コード値 |
|  | `$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。 |
|  | デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## codeCheckboxesタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ      id属性は指定不可。 |  |
| フォーカスを取得可能なHTMLタグ        a | ccesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
|  | 選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。 |
|  | デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$NAME$` : コード値に対応するコード名称 |
|  | `$SHORTNAME$` : コード値に対応するコードの略称 |
|  | `$OPTIONALNAME$` : コード値に対応するコードのオプション名称 |
|  | `$VALUE$`: コード値 |
|  | `$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。 |
|  | デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## codeCheckboxタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| 全てのHTMLタグ |  |
| フォーカスを取得可能なHTMLタグ |  |
| name `必須` | XHTMLのname属性。 |
| value | XHTMLのvalue属性。 |
|  | チェックありの場合に使用するコード値。 |
|  | デフォルトは `1` 。 |
| autofocus | HTML5のautofocus属性 (論理属性) 。 |
| codeId `必須` | コードID。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$NAME$` : コード値に対応するコード名称 |
|  | `$SHORTNAME$` : コード値に対応するコードの略称 |
|  | `$OPTIONALNAME$` : コード値に対応するコードのオプション名称 |
|  | `$VALUE$`: コード値 |
|  | `$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。 |
|  | デフォルトは `$NAME$` 。 |
| offCodeValue | チェックなしの場合に使用するコード値。 |
|  | offCodeValue属性が指定されない場合は、 |
|  | codeId属性の値からチェックなしの場合に使用するコード値を検索する。 |
|  | 検索結果が2件、かつ1件がvalue属性の値である場合は、 |
|  | 残りの1件をチェックなしのコード値として使用する。 |
|  | 検索で見つからない場合は、デフォルト値の `0` を使用する。 |
| disabled | XHTMLのdisabled属性 (論理属性) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。 |
|  | デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。 |
|  | 複数指定する場合はカンマ区切り。 |

## codeタグ

動的属性の使用可否 ：可

| 属性 | 説明 |
|---|---|
| name | 表示対象のコード値を変数スコープから取得する際に使用する名前 |
|  | 省略した場合は、コードID属性とpattern属性にて絞り込んだコードの一覧を表示する。 |
| codeId `必須` | コードID。 |
| pattern | 使用するパターンのカラム名。 |
|  | デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。 |
|  | プレースホルダを下記に示す。 |
|  | `$NAME$` : コード値に対応するコード名称 |
|  | `$SHORTNAME$` : コード値に対応するコードの略称 |
|  | `$OPTIONALNAME$` : コード値に対応するコードのオプション名称 |
|  | `$VALUE$`: コード値 |
|  | `$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。 |
|  | デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。 |
|  | 下記のいずれかを指定する。 |
|  | br(brタグ) |
|  | div(divタグ) |
|  | span(spanタグ) |
|  | ul(ulタグ) |
|  | ol(olタグ) |
|  | sp(スペース区切り) |
|  | デフォルトはbr。 |

## cspNonceタグ

動的属性の使用可否 ：否

セキュアハンドラでnonceを生成する設定 を行っている場合に、セキュアハンドラが生成したnonceを出力する。

| 属性 | 説明 |
|---|---|
| sourceFormat | nonceを出力する際のフォーマットを制御する。 |
|  | 出力する際にプレフィックスとして `nonce-` を付与する場合は `true` 、 |
|  | しない場合は `false` 。プレフィックスを付与する場合はmeta要素で使用する。 |
|  | デフォルトは `false` 。 |

## messageタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| messageId `必須` | メッセージID。 |
| option0～option9 | メッセージフォーマットに使用するインデックスが0～9のオプション引数。 |
|  | 最大10個までオプション引数が指定できる。 |
| language | メッセージの言語。 |
|  | デフォルトはスレッドコンテキストに設定された言語。 |
| var | リクエストスコープに格納する際に使用する変数名。 |
|  | var属性が指定された場合はメッセージを出力せずにリクエストスコープに設定する。 |
|  | リクエストスコープに設定する場合はHTMLエスケープとHTMLフォーマットを行わない。 |
| htmlEscape | HTMLエスケープをするか否か。 |
|  | HTMLエスケープをする場合は `true` 、しない場合は `false` 。 |
|  | デフォルトは `true` 。 |
| withHtmlFormat | HTMLフォーマット(改行と半角スペースの変換)をするか否か。 |
|  | HTMLフォーマットはHTMLエスケープをする場合のみ有効となる。 |
|  | デフォルトは `true` 。 |

## writeタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| name | 表示対象の値を変数スコープから取得する際に使用する名前。value属性と同時に指定できない。 |
| value | 表示対象の値。直接値を指定する場合に使用する。name属性と同時に指定できない。 |
| withHtmlFormat | HTMLフォーマット(改行と半角スペースの変換)をするか否か。 |
|  | HTMLフォーマットはHTMLエスケープをする場合のみ有効となる。 |
|  | デフォルトは `true` 。 |
| valueFormat | 出力時のフォーマット。 |
|  | 指定内容は、 tag-format_value を参照。 |

## prettyPrintタグ

動的属性の使用可否 ：否

> **Important:** このタグは非推奨であるため使用しないこと。 詳細は、 prettyPrintタグの使用を推奨しない理由 を参照。
| 属性 | 説明 |
|---|---|
| name `必須` | 表示対象の値を変数スコープから取得する際に使用する名前 |

## rawWriteタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| name `必須` | 表示対象の値を変数スコープから取得する際に使用する名前 |

## setタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| var `必須` | リクエストスコープに格納する際に使用する変数名。 |
| name | 値を取得するための名前。name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。直接値を指定する場合に使用する。name属性とvalue属性のどちらか一方を指定する。 |
| scope | 変数を格納するスコープを設定する。 |
|  | 指定できるスコープを下記に示す。 |
|  | page: ページスコープ |
|  | request: リクエストスコープ |
|  | デフォルトはリクエストスコープ。 |
| bySingleValue | name属性に対応する値を単一値として取得するか否か。 |
|  | デフォルトは `true` 。 |

## includeタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| path `必須` | インクルードするリソースのパス。 |

## includeParamタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | インクルード時に使用するパラメータの名前。 |
| name | 値を取得するための名前。name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。直接値を指定する場合に使用する。name属性とvalue属性のどちらか一方を指定する。 |

## confirmationPageタグ

動的属性の使用可否 ：否

| 属性 | 説明 |
|---|---|
| path | フォワード先（入力画面）のパス。 |

## ignoreConfirmationタグ

動的属性の使用可否 ：否

属性なし。

## forInputPageタグ

動的属性の使用可否 ：否

属性なし。

## forConfirmationPageタグ

動的属性の使用可否 ：否

属性なし。
