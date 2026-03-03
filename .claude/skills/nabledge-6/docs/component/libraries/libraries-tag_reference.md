# タグリファレンス

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

## フォーカスを取得可能なHTMLタグ

| 属性 | 説明 |
|---|---|
| accesskey | XHTMLのaccesskey属性。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |

## 動的属性の使用

動的属性が使用可能なタグでは、定義されていない属性も設定が可能となる。

## formタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| name | XHTMLのname属性。 |
| action | XHTMLのaction属性。 |
| method | XHTMLのmethod属性。デフォルトは `post` 。 |
| enctype | XHTMLのenctype属性。 |
| onsubmit | XHTMLのonsubmit属性。 |
| onreset | XHTMLのonreset属性。 |
| accept | XHTMLのaccept属性。 |
| acceptCharset | XHTMLのaccept-charset属性。 |
| target | XHTMLのtarget属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| windowScopePrefixes | ウィンドウスコープ変数のプレフィックス。複数指定する場合はカンマ区切り。指定されたプレフィックスがマッチするリクエストパラメータをhiddenタグとして出力する。 |
| useToken | トークンを設定するか否か。トークンを設定する場合は `true` 、設定しない場合は `false` 。デフォルトは `false` 。:ref:`tag-confirmation_page_tag` が指定された場合は、デフォルトが `true` となる。 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true` 、しない場合は `false` 。 |
| preventPostResubmit | POST再送信防止機能を使用するか否か。デフォルトは `false` 。使用する場合は `true` 、しない場合は `false` 。 |

## textタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| readonly | XHTMLのreadonly属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| placeholder | HTML5のplaceholder属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## searchタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## telタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## urlタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## emailタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## dateタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## monthタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## weekタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## timeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## datetimeLocalタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## numberタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## rangeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## colorタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## textareaタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| rows **必須** | XHTMLのrows属性。 |
| cols **必須** | XHTMLのcols属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| readonly | XHTMLのreadonly属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| placeholder | HTML5のplaceholder属性。 |
| maxlength | HTML5のmaxlength属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## passwordタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| readonly | XHTMLのreadonly属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| autocomplete | HTML5のautocomplete属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| placeholder | HTML5のplaceholder属性。 |
| restoreValue | 入力画面の再表示時に入力データを復元するか否か。復元する場合は `true` 、復元しない場合は `false` 。デフォルトは `false` 。 |
| replacement | 確認画面用の出力時に使用する置換文字。デフォルトは `*` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## radioButtonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| value **必須** | XHTMLのvalue属性。 |
| label **必須** | ラベル。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## checkboxタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| value | XHTMLのvalue属性。チェックありの場合に使用する値。デフォルトは `1` 。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| label | チェックありの場合に使用するラベル。入力画面では、このラベルが表示される。 |
| useOffValue | チェックなしの値設定を使用するか否か。デフォルトは `true` 。 |
| offLabel | チェックなしの場合に使用するラベル。 |
| offValue | チェックなしの場合に使用する値。デフォルトは `0` 。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## compositeKeyCheckboxタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| valueObject **必須** | XHTMLのvalue属性の代わりに使用するオブジェクト。keyNames属性で指定したプロパティを持つ必要がある。 |
| keyNames **必須** | 複合キーのキー名。キー名をカンマ区切りで指定する。 |
| namePrefix **必須** | リクエストパラメータに展開する際に使用するプレフィクス。通常のname属性と異なり、この名称に `.` とkeyNames属性で指定したキー名と合致する値を通常のname属性と同様に取り扱う。例えばnamePrefix属性に `form` 、keyNames属性に `key1` 、 `key2` を指定した場合、表示時には `form.key1` 、 `form.key2` でリクエストスコープに含まれる値を使用してこのチェックボックスの値を出力する。また、サブミットしたリクエストの処理では、 `form.key1` 、 `form.key2` というリクエストパラメータから選択された値が取得できる。なお、name属性は、namePrefix属性とkeyNames属性で指定したキーの組み合わせと異なる名称にしなければならない特殊な制約がある。実装時はこの点に十分注意すること。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| label | チェックありの場合に使用するラベル。入力画面では、このラベルが表示される。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## compositeKeyRadioButtonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| valueObject **必須** | XHTMLのvalue属性の代わりに使用するオブジェクト。keyNames属性で指定したプロパティを持つ必要がある。 |
| keyNames **必須** | 複合キーのキー名。キー名をカンマ区切りで指定する。 |
| namePrefix **必須** | リクエストパラメータに展開する際に使用するプレフィクス。通常のname属性と異なり、この名称に `.` とkeyNames属性で指定したキー名と合致する値を通常のname属性と同様に取り扱う。例えばnamePrefix属性に `form` 、keyNames属性に `key1` 、 `key2` を指定した場合、表示時には `form.key1` 、 `form.key2` でリクエストスコープに含まれる値を使用してこのチェックボックスの値を出力する。また、サブミットしたリクエストの処理では、 `form.key1` 、 `form.key2` というリクエストパラメータから選択された値が取得できる。なお、name属性は、namePrefix属性とkeyNames属性で指定したキーの組み合わせと異なる名称にしなければならない特殊な制約がある。実装時はこの点に十分注意すること。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| label | チェックありの場合に使用するラベル。入力画面では、このラベルが表示される。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## fileタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| readonly | XHTMLのreadonly属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| size | XHTMLのsize属性。 |
| maxlength | XHTMLのmaxlength属性。 |
| onselect | XHTMLのonselect属性。 |
| onchange | XHTMLのonchange属性。 |
| accept | XHTMLのaccept属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| multiple | HTML5のmultiple属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## hiddenタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

HTMLタグを出力せず、ウィンドウスコープに値を出力する。

> **重要**: ウィンドウスコープは非推奨である。詳細は、 :ref:`tag-window_scope` を参照。

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |

## plainHiddenタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |

## hiddenStoreタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |

## selectタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| name **必須** | XHTMLのname属性。 |
| listName **必須** | 選択肢リストの名前。カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty **必須** | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty **必須** | リスト要素から値を取得するためのプロパティ名。 |
| size | XHTMLのsize属性。 |
| multiple | XHTMLのmultiple属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| elementLabelPattern | ラベルを整形するためのパターン。プレースホルダを下記に示す。 `$LABEL$` : ラベル、 `$VALUE$` : 値。デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。下記のいずれかを指定する。br(brタグ)、div(divタグ)、span(spanタグ)、ul(ulタグ)、ol(olタグ)、sp(スペース区切り)。デフォルトはbr。 |
| withNoneOption | リスト先頭に選択なしのオプションを追加するか否か。追加する場合は `true` 、追加しない場合は `false` 。デフォルトは `false` 。 |
| noneOptionLabel | リスト先頭に選択なしのオプションを追加する場合に使用するラベル。この属性は、withNoneOptionに `true` を指定した場合のみ有効となる。デフォルトは `""` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## radioButtonsタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name **必須** | XHTMLのname属性。 |
| listName **必須** | 選択肢リストの名前。カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty **必須** | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty **必須** | リスト要素から値を取得するためのプロパティ名。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| elementLabelPattern | ラベルを整形するためのパターン。プレースホルダを下記に示す。 `$LABEL$` : ラベル、 `$VALUE$` : 値。デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。下記のいずれかを指定する。br(brタグ)、div(divタグ)、span(spanタグ)、ul(ulタグ)、ol(olタグ)、sp(スペース区切り)。デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## checkboxesタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| listName `必須` | 選択肢リストの名前。<br>カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。<br>リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty `必須` | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty `必須` | リスト要素から値を取得するためのプロパティ名。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。<br>選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| elementLabelPattern | ラベルを整形するためのパターン。<br>プレースホルダを下記に示す。<br>`$LABEL$` : ラベル<br>`$VALUE$` : 値<br>デフォルトは `$LABEL$` 。 |
| listFormat | リスト表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>br(brタグ)<br>div(divタグ)<br>span(spanタグ)<br>ul(ulタグ)<br>ol(olタグ)<br>sp(スペース区切り)<br>デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。<br>複数指定する場合はカンマ区切り。 |

## submitタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## buttonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## submitLinkタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## popupSubmitタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。<br>新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。<br>新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## popupButtonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。<br>新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。<br>新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## popupLinkタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| popupWindowName | ポップアップのウィンドウ名。<br>新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。<br>新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## downloadSubmitタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| type `必須` | XHTMLのtype属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| value | XHTMLのvalue属性。 |
| src | XHTMLのsrc属性。 |
| alt | XHTMLのalt属性。 |
| usemap | XHTMLのusemap属性。 |
| align | XHTMLのalign属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## downloadButtonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## downloadLinkタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri `必須` | URI。<br>:ref:`tag-specify_uri` を参照。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。<br>許可する場合は `true` 、許可しない場合は `false` 。<br>デフォルトは `true` 。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。<br>下記のいずれかを指定する。<br>NODISPLAY (非表示)<br>DISABLED (非活性)<br>NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。<br>抑制する場合は `true` 、抑制しない場合は `false` 。<br>デフォルトは `false` 。 |

## paramタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | サブミット時に使用するパラメータの名前。 |
| name | 値を取得するための名前。<br>リクエストスコープなどスコープ上のオブジェクトを参照する場合に指定する。<br>name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。<br>直接値を指定する場合に使用する。<br>name属性とvalue属性のどちらか一方を指定する。 |

## changeParamNameタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | サブミット時に使用するパラメータの名前。 |
| inputName `必須` | 変更元となる元画面のinput要素のname属性。 |

## aタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| charset | XHTMLのcharset属性。 |
| type | XHTMLのtype属性。 |
| name | XHTMLのname属性。 |
| href | XHTMLのhref属性。<br>:ref:`tag-specify_uri` を参照。 |
| hreflang | XHTMLのhreflang属性。 |
| rel | XHTMLのrel属性。 |
| rev | XHTMLのrev属性。 |
| shape | XHTMLのshape属性。 |
| coords | XHTMLのcoords属性。 |
| target | XHTMLのtarget属性。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |

## imgタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| src `必須` | XHTMLのcharsrc属性。<br>:ref:`tag-specify_uri` を参照。 |
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
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |

## linkタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| charset | XHTMLのcharset属性。 |
| href | XHTMLのhref属性。<br>:ref:`tag-specify_uri` を参照。 |
| hreflang | XHTMLのhreflang属性。 |
| type | XHTMLのtype属性。 |
| rel | XHTMLのrel属性。 |
| rev | XHTMLのrev属性。 |
| media | XHTMLのmedia属性。 |
| target | XHTMLのtarget属性。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |

## scriptタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| type `必須` | XHTMLのtype属性。 |
| id | XHTMLのid属性。 |
| charset | XHTMLのcharset属性。 |
| language | XHTMLのlanguage属性。 |
| src | XHTMLのsrc属性。<br>:ref:`tag-specify_uri` を参照。 |
| defer | XHTMLのdefer属性。 |
| xmlSpace | XHTMLのxml:space属性。 |
| secure | URIをhttpsにするか否か。<br>httpsにする場合は `true` 、しない場合は `false` 。 |

## errorsタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| cssClass | リスト表示においてulタグに使用するCSSクラス名。<br>デフォルトは `nablarch_errors` 。 |
| infoCss | 情報レベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_info` 。 |
| warnCss | 警告レベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_warn` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| filter | リストに含めるメッセージのフィルタ条件。<br>下記のいずれかを指定する。<br>all(全てのメッセージを表示する)<br>global(入力項目に対応しないメッセージのみを表示)<br>デフォルトは `all` 。<br>globalの場合、`ValidationResultMessage` のプロパティ名が入っているメッセージを取り除いて出力する。 |

## errorタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| name `必須` | エラーメッセージを表示する入力項目のname属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| messageFormat | メッセージ表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>div(divタグ)<br>span(spanタグ)<br>デフォルトはdiv。 |

## noCacheタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

属性なし。

## codeSelectタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| size | XHTMLのsize属性。 |
| multiple | XHTMLのmultiple属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| tabindex | XHTMLのtabindex属性。 |
| onfocus | XHTMLのonfocus属性。 |
| onblur | XHTMLのonblur属性。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| pattern | 使用するパターンのカラム名。<br>デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。<br>プレースホルダを下記に示す。<br>`$NAME$` : コード値に対応するコード名称<br>`$SHORTNAME$` : コード値に対応するコードの略称<br>`$OPTIONALNAME$` : コード値に対応するコードのオプション名称<br>`$VALUE$`: コード値<br>`$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。<br>デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>br(brタグ)<br>div(divタグ)<br>span(spanタグ)<br>ul(ulタグ)<br>ol(olタグ)<br>sp(スペース区切り)<br>デフォルトはbr。 |
| withNoneOption | リスト先頭に選択なしのオプションを追加するか否か。<br>追加する場合は `true` 、追加しない場合は `false` 。<br>デフォルトは `false` 。 |
| noneOptionLabel | リスト先頭に選択なしのオプションを追加する場合に使用するラベル。<br>この属性は、withNoneOptionに `true` を指定した場合のみ有効となる。<br>デフォルトは `""` 。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。<br>複数指定する場合はカンマ区切り。 |

## codeRadioButtonsタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。<br>選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。<br>デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。<br>プレースホルダを下記に示す。<br>`$NAME$` : コード値に対応するコード名称<br>`$SHORTNAME$` : コード値に対応するコードの略称<br>`$OPTIONALNAME$` : コード値に対応するコードのオプション名称<br>`$VALUE$`: コード値<br>`$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。<br>デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>br(brタグ)<br>div(divタグ)<br>span(spanタグ)<br>ul(ulタグ)<br>ol(olタグ)<br>sp(スペース区切り)<br>デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。<br>複数指定する場合はカンマ区切り。 |

## codeCheckboxesタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| codeId `必須` | コードID。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。<br>選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。<br>デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。<br>プレースホルダを下記に示す。<br>`$NAME$` : コード値に対応するコード名称<br>`$SHORTNAME$` : コード値に対応するコードの略称<br>`$OPTIONALNAME$` : コード値に対応するコードのオプション名称<br>`$VALUE$`: コード値<br>`$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。<br>デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>br(brタグ)<br>div(divタグ)<br>span(spanタグ)<br>ul(ulタグ)<br>ol(olタグ)<br>sp(スペース区切り)<br>デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。<br>複数指定する場合はカンマ区切り。 |

## codeCheckboxタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name `必須` | XHTMLのname属性。 |
| value | XHTMLのvalue属性。<br>チェックありの場合に使用するコード値。<br>デフォルトは `1` 。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| codeId `必須` | コードID。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。<br>プレースホルダを下記に示す。<br>`$NAME$` : コード値に対応するコード名称<br>`$SHORTNAME$` : コード値に対応するコードの略称<br>`$OPTIONALNAME$` : コード値に対応するコードのオプション名称<br>`$VALUE$`: コード値<br>`$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。<br>デフォルトは `$NAME$` 。 |
| offCodeValue | チェックなしの場合に使用するコード値。<br>offCodeValue属性が指定されない場合は、codeId属性の値からチェックなしの場合に使用するコード値を検索する。<br>検索結果が2件、かつ1件がvalue属性の値である場合は、残りの1件をチェックなしのコード値として使用する。<br>検索で見つからない場合は、デフォルト値の `0` を使用する。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。<br>デフォルトは `nablarch_error` 。 |
| nameAlias | name属性のエイリアスを設定する。<br>複数指定する場合はカンマ区切り。 |

## codeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| name | 表示対象のコード値を変数スコープから取得する際に使用する名前<br>省略した場合は、コードID属性とpattern属性にて絞り込んだコードの一覧を表示する。 |
| codeId `必須` | コードID。 |
| pattern | 使用するパターンのカラム名。<br>デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。<br>プレースホルダを下記に示す。<br>`$NAME$` : コード値に対応するコード名称<br>`$SHORTNAME$` : コード値に対応するコードの略称<br>`$OPTIONALNAME$` : コード値に対応するコードのオプション名称<br>`$VALUE$`: コード値<br>`$OPTIONALNAME$` を使用する場合は、optionColumnName属性の指定が必須となる。<br>デフォルトは `$NAME$` 。 |
| listFormat | リスト表示時に使用するフォーマット。<br>下記のいずれかを指定する。<br>br(brタグ)<br>div(divタグ)<br>span(spanタグ)<br>ul(ulタグ)<br>ol(olタグ)<br>sp(スペース区切り)<br>デフォルトはbr。 |

## cspNonceタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

:ref:`セキュアハンドラでnonceを生成する設定<content_security_policy>` を行っている場合に、セキュアハンドラが生成したnonceを出力する。

| 属性 | 説明 |
|---|---|
| sourceFormat | nonceを出力する際のフォーマットを制御する。<br>出力する際にプレフィックスとして `nonce-` を付与する場合は `true` 、しない場合は `false` 。プレフィックスを付与する場合はmeta要素で使用する。<br>デフォルトは `false` 。 |

## messageタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| messageId `必須` | メッセージID。 |
| option0〜option9 | メッセージフォーマットに使用するインデックスが0〜9のオプション引数。<br>最大10個までオプション引数が指定できる。 |
| language | メッセージの言語。<br>デフォルトはスレッドコンテキストに設定された言語。 |
| var | リクエストスコープに格納する際に使用する変数名。<br>var属性が指定された場合はメッセージを出力せずにリクエストスコープに設定する。<br>リクエストスコープに設定する場合はHTMLエスケープとHTMLフォーマットを行わない。 |
| htmlEscape | HTMLエスケープをするか否か。<br>HTMLエスケープをする場合は `true` 、しない場合は `false` 。<br>デフォルトは `true` 。 |
| withHtmlFormat | HTMLフォーマット(改行と半角スペースの変換)をするか否か。<br>HTMLフォーマットはHTMLエスケープをする場合のみ有効となる。<br>デフォルトは `true` 。 |

## writeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| name | 表示対象の値を変数スコープから取得する際に使用する名前。value属性と同時に指定できない。 |
| value | 表示対象の値。直接値を指定する場合に使用する。name属性と同時に指定できない。 |
| withHtmlFormat | HTMLフォーマット(改行と半角スペースの変換)をするか否か。<br>HTMLフォーマットはHTMLエスケープをする場合のみ有効となる。<br>デフォルトは `true` 。 |
| valueFormat | 出力時のフォーマット。<br>指定内容は、:ref:`tag-format_value` を参照。 |

## prettyPrintタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

> **重要**: このタグは非推奨であるため使用しないこと。詳細は、:ref:`prettyPrintタグの使用を推奨しない理由 <tag-pretty_print_tag-deprecated>` を参照。

| 属性 | 説明 |
|---|---|
| name `必須` | 表示対象の値を変数スコープから取得する際に使用する名前 |

## rawWriteタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| name `必須` | 表示対象の値を変数スコープから取得する際に使用する名前 |

## setタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| var `必須` | リクエストスコープに格納する際に使用する変数名。 |
| name | 値を取得するための名前。name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。直接値を指定する場合に使用する。name属性とvalue属性のどちらか一方を指定する。 |
| scope | 変数を格納するスコープを設定する。<br>指定できるスコープを下記に示す。<br>page: ページスコープ<br>request: リクエストスコープ<br>デフォルトはリクエストスコープ。 |
| bySingleValue | name属性に対応する値を単一値として取得するか否か。<br>デフォルトは `true` 。 |

## includeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| path `必須` | インクルードするリソースのパス。 |

## includeParamタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| paramName `必須` | インクルード時に使用するパラメータの名前。 |
| name | 値を取得するための名前。name属性とvalue属性のどちらか一方を指定する。 |
| value | 値。直接値を指定する場合に使用する。name属性とvalue属性のどちらか一方を指定する。 |

## confirmationPageタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| path | フォワード先（入力画面）のパス。 |

## ignoreConfirmationタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

属性なし。

## forInputPageタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

属性なし。

## forConfirmationPageタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

属性なし。
