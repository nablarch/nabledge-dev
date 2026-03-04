# タグリファレンス

## 全てのHTMLタグ

各カスタムタグの定義でここで定義した共通属性を参照する。

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
| accesskey | XHTMLのaccesskey属性 |
| tabindex | XHTMLのtabindex属性 |
| onfocus | XHTMLのonfocus属性 |
| onblur | XHTMLのonblur属性 |

## 動的属性の使用

動的属性が使用可能なタグでは、定義されていない属性も設定が可能となる。

### 個別属性

## formタグ

**動的属性**: サポート対象 (:ref:`tag-dynamic_attributes_tag`)

**継承属性**: :ref:`tag-generic_attributes_tag`

#### 属性

| 属性名 | 説明 |
|---|---|
| name | XHTMLのname属性 |
| action | XHTMLのaction属性 |
| method | XHTMLのmethod属性。デフォルト: `post` |
| enctype | XHTMLのenctype属性 |
| onsubmit | XHTMLのonsubmit属性 |
| onreset | XHTMLのonreset属性 |
| accept | XHTMLのaccept属性 |
| acceptCharset | XHTMLのaccept-charset属性 |
| target | XHTMLのtarget属性 |
| autocomplete | HTML5のautocomplete属性 |
| windowScopePrefixes | ウィンドウスコープ変数のプレフィックス。複数指定時はカンマ区切り。マッチするリクエストパラメータはhiddenタグとして出力 |
| useToken | トークン設定の有無。デフォルト: `false`。ただし :ref:`tag-confirmation_page_tag` 指定時はデフォルトが `true` に変更 |
| secure | URIをhttpsにするか否か。`true` でhttpsに、`false` でhttpsにしない |
| preventPostResubmit | POST再送信防止機能の使用有無。デフォルト: `false` |

## textタグ

動的属性の使用可能（:ref:`詳細 <tag-dynamic_attributes_tag>`）

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| readonly | XHTMLのreadonly属性（:ref:`論理属性 <boolean_attribute>`） |
| size | XHTMLのsize属性 |
| maxlength | XHTMLのmaxlength属性 |
| onselect | XHTMLのonselect属性 |
| onchange | XHTMLのonchange属性 |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| placeholder | HTML5のplaceholder属性 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは`nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。指定内容は、:ref:`tag-format_value`を参照 |

## searchタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name（必須） | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト：`nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。詳細は :ref:`tag-format_value` を参照 |

## telタグ

**動的属性対応**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| `name` (必須) | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| `value` | XHTMLのvalue属性。 |
| `disabled` | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| `autocomplete` | HTML5のautocomplete属性。 |
| `autofocus` | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| `errorCss` | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| `nameAlias` | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |
| `valueFormat` | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照。 |

## urlタグ

**動的属性**: 使用可能 (:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>`)

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (**必須**) | XHTMLのname属性。値表示時にvalue属性が指定されていない場合、XHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアスをカンマ区切りで設定 |
| valueFormat | 出力時のフォーマット (:ref:`tag-format_value` を参照) |

## emailタグ

動的属性の使用可否: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTML name属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTML value属性 |
| disabled | XHTML disabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照 |

## dateタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` |  |
| :ref:`tag-focus_attributes_tag` |  |
| name (必須) | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照 |

## monthタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` → 可

**継承属性**:
- :ref:`tag-generic_attributes_tag`
- :ref:`tag-focus_attributes_tag`

**属性一覧**:

| 属性 | 説明 |
|---|---|
| name | **必須**。XHTML の name 属性。値表示時に value 属性が指定されていない場合は XHTML の value 属性にも使用される |
| value | XHTML の value 属性 |
| disabled | XHTML の disabled 属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5 の autocomplete 属性 |
| autofocus | HTML5 の autofocus 属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用する CSS クラス名。デフォルト：`nablarch_error` |
| nameAlias | name 属性のエイリアスを設定する。複数指定時はカンマ区切り |
| valueFormat | 出力時のフォーマット。指定内容は :ref:`tag-format_value` を参照 |

## weekタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。指定内容は、 :ref:`tag-format_value` を参照 |

## timeタグ

動的属性をサポート（:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>`）

## 属性

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name（必須） | XHTML name属性。値表示時に value属性が未指定の場合は value属性としても使用される |
| value | XHTML value属性 |
| disabled | XHTML disabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5 autocomplete属性 |
| autofocus | HTML5 autofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定時はカンマ区切り |
| valueFormat | 出力時のフォーマット（:ref:`tag-format_value` を参照） |

## datetimeLocalタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | （詳細は参照） |
| :ref:`tag-focus_attributes_tag` | （詳細は参照） |
| name（必須） | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定時はカンマ区切り |
| valueFormat | 出力時のフォーマット（詳細は :ref:`tag-format_value` 参照） |

## numberタグ

**動的属性の使用可否**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |
| valueFormat | 出力時のフォーマット。詳細は :ref:`tag-format_value` を参照 |

## rangeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name（必須） | XHTMLのname属性。値表示時にvalue属性未指定の場合はXHTMLのvalue属性にも使用 |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定時はカンマ区切り |
| valueFormat | 出力時のフォーマット。詳細は :ref:`tag-format_value` を参照 |

## colorタグ

**動的属性**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。値表示の際、value属性が指定されていない場合はXHTMLのvalue属性にも使用される（**必須**） |
| value | XHTMLのvalue属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアスを設定（複数指定時はカンマ区切り） |
| valueFormat | 出力時のフォーマット。詳細は :ref:`tag-format_value` を参照 |

## textareaタグ

**動的属性**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name(必須) | XHTMLのname属性 |
| rows(必須) | XHTMLのrows属性 |
| cols(必須) | XHTMLのcols属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| readonly | XHTMLのreadonly属性（:ref:`論理属性 <boolean_attribute>`） |
| onselect | XHTMLのonselect属性 |
| onchange | XHTMLのonchange属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| placeholder | HTML5のplaceholder属性 |
| maxlength | HTML5のmaxlength属性 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: nablarch_error |
| nameAlias | name属性のエイリアス。複数指定する場合はカンマ区切り |

## passwordタグ

動的属性の使用可否：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (**必須**) | XHTMLのname属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| readonly | XHTMLのreadonly属性（:ref:`論理属性 <boolean_attribute>`） |
| size | XHTMLのsize属性 |
| maxlength | XHTMLのmaxlength属性 |
| onselect | XHTMLのonselect属性 |
| onchange | XHTMLのonchange属性 |
| autocomplete | HTML5のautocomplete属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| placeholder | HTML5のplaceholder属性 |
| restoreValue | 入力画面の再表示時に入力データを復元するか否か。復元する場合は `true`、復元しない場合は `false`。デフォルト：`false` |
| replacement | 確認画面用の出力時に使用する置換文字。デフォルト：`*` |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト：`nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |

## radioButtonタグ

**動的属性の使用可否**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性 |
| value (必須) | XHTMLのvalue属性 |
| label (必須) | ラベル |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| onchange | XHTMLのonchange属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |

## checkboxタグ

**動的属性**: 使用可能 (:ref:`tag-dynamic_attributes_tag`)

**継承属性**: :ref:`tag-generic_attributes_tag`, :ref:`tag-focus_attributes_tag`

| 属性 | 説明 | デフォルト |
|---|---|---|
| name (必須) | XHTML name属性 | — |
| value | XHTML value属性。チェックありの場合に使用する値 | 1 |
| autofocus | HTML5 autofocus属性（:ref:`論理属性 <boolean_attribute>`） | — |
| label | チェック時のラベル（入力画面に表示） | — |
| useOffValue | チェックなし値設定を使用するか | true |
| offLabel | チェックなし時のラベル | — |
| offValue | チェックなし時の値 | 0 |
| disabled | XHTML disabled属性（:ref:`論理属性 <boolean_attribute>`） | — |
| onchange | XHTML onchange属性 | — |
| errorCss | エラーメッセージ用CSSクラス名 | nablarch_error |
| nameAlias | name属性のエイリアス（カンマ区切り） | — |

## compositeKeyCheckboxタグ

**動的属性の使用可否**: 可

## 属性一覧

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性 |
| valueObject (必須) | XHTMLのvalue属性の代わりに使用するオブジェクト。keyNames属性で指定したプロパティを持つ必要がある |
| keyNames (必須) | 複合キーのキー名。カンマ区切りで指定 |
| namePrefix (必須) | リクエストパラメータ展開時のプレフィクス。namePrefix + '.' + keyNames値でリクエストスコープにアクセス（例：namePrefix='form', keyNames='key1,key2'→'form.key1', 'form.key2'）。表示時・サブミット時共に同じ組み合わせを使用。**重要**: name属性はnamePrefix+keyNames組み合わせと異なる名称にする必須 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| label | チェック時に使用するラベル。入力画面で表示される |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| onchange | XHTMLのonchange属性 |
| errorCss | エラーメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定時はカンマ区切り |

## compositeKeyRadioButtonタグ

**動的属性**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` より可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | ○**必須**。XHTMLのname属性 |
| valueObject | ○**必須**。XHTMLのvalue属性代わり。keyNames属性で指定したプロパティを持つ必要がある |
| keyNames | ○**必須**。複合キーのキー名をカンマ区切りで指定 |
| namePrefix | ○**必須**。リクエストパラメータ展開時のプレフィクス。例: namePrefix="form"、keyNames="key1,key2"の場合、表示時に「form.key1」「form.key2」でリクエストスコープに含まれる値を使用してチェックボックスの値を出力、サブミット時は「form.key1」「form.key2」というリクエストパラメータから選択された値が取得できる。**制約**: name属性は、namePrefix属性とkeyNames属性で指定したキーの組み合わせと異なる名称にしなければならない |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| label | チェックありの場合に使用するラベル。入力画面で表示される |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| onchange | XHTMLのonchange属性 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト値: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定する場合はカンマ区切り |

## fileタグ

**動的属性の使用可否**: 可

## 属性

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name（必須） | XHTMLのname属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| readonly | XHTMLのreadonly属性（:ref:`論理属性 <boolean_attribute>`） |
| size | XHTMLのsize属性 |
| maxlength | XHTMLのmaxlength属性 |
| onselect | XHTMLのonselect属性 |
| onchange | XHTMLのonchange属性 |
| accept | XHTMLのaccept属性 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| multiple | HTML5のmultiple属性（:ref:`論理属性 <boolean_attribute>`） |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り |

## hiddenタグ

**動的属性**: 可

HTMLタグを出力せず、ウィンドウスコープに値を出力する。

> **重要**: ウィンドウスコープは非推奨である。詳細は :ref:`tag-window_scope` を参照。

**属性一覧**

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |

## plainHiddenタグ

**動的属性**

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

**属性**

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性（**必須**）|
| disabled | XHTML disabled属性（:ref:`論理属性 <boolean_attribute>`） |

## hiddenStoreタグ

**動的属性の使用可否**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name **必須** | XHTMLのname属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |

## selectタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

このタグは :ref:`tag-generic_attributes_tag` の属性を継承します。

| 属性 | 説明 | 必須 | デフォルト値 |
|---|---|---|---|
| name | XHTML name属性 | ○ | |
| listName | 選択肢リストの名前。カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 | ○ | |
| elementLabelProperty | リスト要素からラベルを取得するためのプロパティ名 | ○ | |
| elementValueProperty | リスト要素から値を取得するためのプロパティ名 | ○ | |
| size | XHTML size属性 | | |
| multiple | XHTML multiple属性（:ref:`論理属性 <boolean_attribute>`） | | |
| disabled | XHTML disabled属性（:ref:`論理属性 <boolean_attribute>`） | | |
| tabindex | XHTML tabindex属性 | | |
| onfocus | XHTML onfocus属性 | | |
| onblur | XHTML onblur属性 | | |
| onchange | XHTML onchange属性 | | |
| autofocus | HTML5 autofocus属性（:ref:`論理属性 <boolean_attribute>`） | | |
| elementLabelPattern | ラベルを整形するためのパターン。プレースホルダ: `$LABEL$`（ラベル）、`$VALUE$`（値） | | `$LABEL$` |
| listFormat | リスト表示時に使用するフォーマット。br（brタグ）、div（divタグ）、span（spanタグ）、ul（ulタグ）、ol（olタグ）、sp（スペース区切り）から選択 | | br |
| withNoneOption | リスト先頭に選択なしのオプションを追加するか。true で追加、false で追加しない。 | | false |
| noneOptionLabel | リスト先頭に選択なしのオプションを追加する場合に使用するラベル。withNoneOptionに true を指定した場合のみ有効。 | | "" |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名 | | nablarch_error |
| nameAlias | name属性のエイリアス。複数指定する場合はカンマ区切り | | |

## radioButtonsタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name `必須` | XHTMLのname属性。 |
| listName `必須` | 選択肢リストの名前。カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得する。リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示しない。 |
| elementLabelProperty `必須` | リスト要素からラベルを取得するためのプロパティ名。 |
| elementValueProperty `必須` | リスト要素から値を取得するためのプロパティ名。 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`）。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`）。選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| elementLabelPattern | ラベルを整形するためのパターン。プレースホルダ：`$LABEL$`（ラベル）、`$VALUE$`（値）。デフォルト：`$LABEL$` |
| listFormat | リスト表示時に使用するフォーマット：br（brタグ）、div（divタグ）、span（spanタグ）、ul（ulタグ）、ol（olタグ）、sp（スペース区切り）。デフォルト：br |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト：`nablarch_error`。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## checkboxesタグ

**動的属性の使用可否**: 可

#### 属性

| 属性名 | 必須 | 説明 |
|---|---|---|
| :ref:`tag-generic_attributes_tag` | | id属性は指定不可 |
| :ref:`tag-focus_attributes_tag` | | accesskey属性は指定不可 |
| name | ○ | XHTMLのname属性 |
| listName | ○ | 選択肢リストの名前。カスタムタグはこの名前を使用してリクエストスコープから選択肢リストを取得します。リクエストスコープから取得した選択肢リストが空の場合、画面には何も表示されません。 |
| elementLabelProperty | ○ | リスト要素からラベルを取得するためのプロパティ名 |
| elementValueProperty | ○ | リスト要素から値を取得するためのプロパティ名 |
| disabled | | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| onchange | | XHTMLのonchange属性 |
| autofocus | | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`）。選択肢のうち、先頭要素のみautofocus属性を出力します。 |
| elementLabelPattern | | ラベルを整形するためのパターン。プレースホルダ: `$LABEL$`(ラベル), `$VALUE$`(値)。デフォルト: `$LABEL$` |
| listFormat | | リスト表示時に使用するフォーマット。指定可能: br(brタグ), div(divタグ), span(spanタグ), ul(ulタグ), ol(olタグ), sp(スペース区切り)。デフォルト: br |
| errorCss | | エラーメッセージ用CSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | | name属性のエイリアス。複数指定時はカンマ区切り |

## submitタグ

**動的属性の使用可否**: 可

## 属性

### 継承される属性グループ

- :ref:`tag-generic_attributes_tag`
- :ref:`tag-focus_attributes_tag`

### tag固有の属性

| 属性 | 説明 |
|---|---|
| name | XHTMLのname属性 |
| type | XHTMLのtype属性。必須 |
| uri | URI。必須。詳細は :ref:`tag-specify_uri` を参照 |
| disabled | XHTMLのdisabled属性。論理属性 (:ref:`論理属性 <boolean_attribute>` 参照) |
| value | XHTMLのvalue属性 |
| src | XHTMLのsrc属性 |
| alt | XHTMLのalt属性 |
| usemap | XHTMLのusemap属性 |
| align | XHTMLのalign属性 |
| autofocus | HTML5のautofocus属性。論理属性 (:ref:`論理属性 <boolean_attribute>` 参照) |
| allowDoubleSubmission | 二重サブミット許可の有無。`true` = 許可、`false` = 禁止。デフォルト: `true` |
| secure | URIをhttpsにするか。`true` = https、`false` = http |
| displayMethod | 認可判定・サービス提供可否判定の結果に応じた表示方法。`NODISPLAY` (非表示) / `DISABLED` (非活性) / `NORMAL` (通常表示) |
| suppressDefaultSubmit | デフォルトのサブミット用関数呼び出しをonclick属性に設定するか。`true` = 設定しない、`false` = 設定する。デフォルト: `false` |

## buttonタグ

動的属性の使用可否：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri (**必須**) | URI。:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`)。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`)。 |
| allowDoubleSubmission | 二重サブミットを許可するか否か。許可する場合は `true`、許可しない場合は `false`。デフォルトは `true`。 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false`。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。NODISPLAY（非表示）、DISABLED（非活性）、NORMAL（通常表示）のいずれかを指定。 |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。抑制する場合は `true`、抑制しない場合は `false`。デフォルトは `false`。 |

## submitLinkタグ

**動的属性対応**: ✓

**属性**

このタグは以下の属性をサポートします:

| 属性名 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | 汎用属性グループ |
| :ref:`tag-focus_attributes_tag` | フォーカス属性グループ |
| name | XHTML name属性 |
| uri | URI（必須。詳細は :ref:`tag-specify_uri` 参照） |
| shape | XHTML shape属性 |
| coords | XHTML coords属性 |
| allowDoubleSubmission | 二重サブミット許可（デフォルト: true） |
| secure | HTTPS変換（true=https、false=http） |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。以下のいずれかを指定する。NODISPLAY（非表示）、DISABLED（非活性）、NORMAL（通常表示） |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か（デフォルト: false） |

## popupSubmitタグ

動的属性の使用可否：:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` 

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性 |
| type **（必須）** | XHTMLのtype属性 |
| uri **（必須）** | URI。:ref:`tag-specify_uri` を参照 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| value | XHTMLのvalue属性 |
| src | XHTMLのsrc属性 |
| alt | XHTMLのalt属性 |
| usemap | XHTMLのusemap属性 |
| align | XHTMLのalign属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false` |
| popupWindowName | ポップアップのウィンドウ名。新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定 |
| popupOption | ポップアップのオプション情報。新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。下記のいずれかを指定: NODISPLAY (非表示)、DISABLED (非活性)、NORMAL (通常表示) |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。抑制する場合は `true`、抑制しない場合は `false`。デフォルト: `false` |

## popupButtonタグ

**動的属性**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` - 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性。 |
| uri (必須) | URI。:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性。 |
| type | XHTMLのtype属性。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`)。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`)。 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false`。 |
| popupWindowName | ポップアップのウィンドウ名。新しいウィンドウを開く際にwindow.open関数の第2引数(JavaScript)に指定する。 |
| popupOption | ポップアップのオプション情報。新しいウィンドウを開く際にwindow.open関数の第3引数(JavaScript)に指定する。 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。下記のいずれかを指定する: NODISPLAY (非表示), DISABLED (非活性), NORMAL (通常表示)。 |
| suppressDefaultSubmit | デフォルトで生成するサブミット用の関数呼び出しをonclick属性に設定しないよう抑制するか否か。抑制する場合は `true`、抑制しない場合は `false`。デフォルトは `false`。 |

## popupLinkタグ

**動的属性**: 使用可能

| 属性名 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性 |
| uri | URI（必須）。:ref:`tag-specify_uri` を参照 |
| shape | XHTMLのshape属性 |
| coords | XHTMLのcoords属性 |
| secure | URIをhttpsにするか否か。httpsの場合は `true`、httpの場合は `false` |
| popupWindowName | ポップアップウィンドウ名。window.open関数の第2引数に指定 |
| popupOption | ポップアップオプション情報。window.open関数の第3引数に指定 |
| displayMethod | 認可判定とサービス提供可否判定に応じた表示方法: NODISPLAY（非表示）、DISABLED（非活性）、NORMAL（通常表示） |
| suppressDefaultSubmit | デフォルトのサブミット用関数呼び出しをonclick属性に設定するか否か。抑制する場合は `true`、しない場合は `false`。デフォルト: `false` |

## downloadSubmitタグ

動的属性の使用が可能です。

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | ジェネリック属性 |
| :ref:`tag-focus_attributes_tag` | フォーカス属性 |
| name | XHTMLのname属性 |
| type ``必須`` | XHTMLのtype属性 |
| uri ``必須`` | URI。:ref:`tag-specify_uri` を参照 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| value | XHTMLのvalue属性 |
| src | XHTMLのsrc属性 |
| alt | XHTMLのalt属性 |
| usemap | XHTMLのusemap属性 |
| align | XHTMLのalign属性 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| allowDoubleSubmission | 二重サブミット許可。true: 許可、false: 許可しない。デフォルト: true |
| secure | URIをhttpsにするか。true: https、false: https以外 |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。NODISPLAY (非表示)、DISABLED (非活性)、NORMAL (通常表示) から選択 |
| suppressDefaultSubmit | デフォルト関数呼び出し抑制。true: 抑制、false: 抑制しない。デフォルト: false |

## downloadButtonタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性 |
| uri | **必須**。URI。:ref:`tag-specify_uri` を参照。 |
| value | XHTMLのvalue属性 |
| type | XHTMLのtype属性 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| allowDoubleSubmission | 二重サブミット許可。`true`=許可、`false`=非許可。デフォルト: `true` |
| secure | HTTPS化。`true`=https、`false`=http |
| displayMethod | 表示制御: NODISPLAY（非表示）/ DISABLED（非活性）/ NORMAL（通常表示） |
| suppressDefaultSubmit | デフォルトのサブミット関数呼び出し抑制。`true`=抑制、`false`=非抑制。デフォルト: `false` |

## downloadLinkタグ

**動的属性の使用可否**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name | XHTMLのname属性 |
| uri | URI。:ref:`tag-specify_uri` を参照。必須 |
| shape | XHTMLのshape属性 |
| coords | XHTMLのcoords属性 |
| allowDoubleSubmission | 二重サブミット許可。`true`=許可、`false`=禁止。デフォルト:`true` |
| secure | https強制。`true`=https、`false`=非https |
| displayMethod | 認可判定とサービス提供可否判定の結果に応じて表示制御を行う場合の表示方法。NODISPLAY（非表示）、DISABLED（非活性）、NORMAL（通常表示） |
| suppressDefaultSubmit | デフォルトサブミット呼び出し抑制。`true`=抑制、`false`=実行。デフォルト:`false` |

## paramタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

**属性一覧**

| 属性 | 説明 |
|---|---|
| **paramName** (必須) | サブミット時に使用するパラメータの名前 |
| **name** | 値を取得するための名前。リクエストスコープなどスコープ上のオブジェクトを参照する場合に指定。name属性とvalue属性のどちらか一方を指定。 |
| **value** | 値。直接値を指定する場合に使用。name属性とvalue属性のどちらか一方を指定。 |

## changeParamNameタグ

パラメータ名変更タグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` → 否

| 属性 | 説明 |
|---|---|
| paramName ``必須`` | サブミット時に使用するパラメータの名前 |
| inputName ``必須`` | 変更元となる元画面のinput要素のname属性 |

## aタグ

**動的属性**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| charset | XHTMLのcharset属性 |
| type | XHTMLのtype属性 |
| name | XHTMLのname属性 |
| href | XHTMLのhref属性。:ref:`tag-specify_uri` を参照 |
| hreflang | XHTMLのhreflang属性 |
| rel | XHTMLのrel属性 |
| rev | XHTMLのrev属性 |
| shape | XHTMLのshape属性 |
| coords | XHTMLのcoords属性 |
| target | XHTMLのtarget属性 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false` |

## imgタグ

## 動的属性の使用

動的属性の使用：**可**

## 属性一覧

| 属性 | 必須 | 説明 |
|---|---|---|
| 汎用属性 | | :ref:`tag-generic_attributes_tag` を参照 |
| src | ○ | XHTML の charsrc 属性。:ref:`tag-specify_uri` を参照 |
| alt | ○ | XHTML の alt 属性 |
| name | | XHTML の name 属性 |
| longdesc | | XHTML の longdesc 属性 |
| height | | XHTML の height 属性 |
| width | | XHTML の width 属性 |
| usemap | | XHTML の usemap 属性 |
| ismap | | XHTML の ismap 属性 |
| align | | XHTML の align 属性 |
| border | | XHTML の border 属性 |
| hspace | | XHTML の hspace 属性 |
| vspace | | XHTML の vspace 属性 |
| secure | | URI を https にするか否か。https にする場合は `true`、しない場合は `false` |

## linkタグ

動的属性の使用可否：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| charset | XHTMLのcharset属性 |
| href | XHTMLのhref属性。:ref:`tag-specify_uri` を参照。 |
| hreflang | XHTMLのhreflang属性 |
| type | XHTMLのtype属性 |
| rel | XHTMLのrel属性 |
| rev | XHTMLのrev属性 |
| media | XHTMLのmedia属性 |
| target | XHTMLのtarget属性 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false` |

## scriptタグ

動的属性の使用可否：可

| 属性 | 説明 |
|---|---|
| type **必須** | XHTMLのtype属性 |
| id | XHTMLのid属性 |
| charset | XHTMLのcharset属性 |
| language | XHTMLのlanguage属性 |
| src | XHTMLのsrc属性。:ref:`tag-specify_uri` を参照 |
| defer | XHTMLのdefer属性 |
| xmlSpace | XHTMLのxml:space属性 |
| secure | URIをhttpsにするか否か。httpsにする場合は `true`、しない場合は `false` |

## errorsタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` → 否

## 属性

| 属性名 | 説明 | デフォルト |
|---|---|---|
| cssClass | リスト表示においてulタグに使用するCSSクラス名 | `nablarch_errors` |
| infoCss | 情報レベルのメッセージに使用するCSSクラス名 | `nablarch_info` |
| warnCss | 警告レベルのメッセージに使用するCSSクラス名 | `nablarch_warn` |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名 | `nablarch_error` |
| filter | リストに含めるメッセージのフィルタ条件。値: `all`（全てのメッセージを表示）、`global`（入力項目に対応しないメッセージのみを表示）。globalの場合、`ValidationResultMessage` のプロパティ名が入っているメッセージを取り除いて出力する | `all` |

## errorタグ

## errorタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` — 否

### 属性

| 属性 | 説明 |
|---|---|
| name (必須) | エラーメッセージを表示する入力項目のname属性。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは `nablarch_error` 。 |
| messageFormat | メッセージ表示時に使用するフォーマット。下記のいずれかを指定する: div(divタグ)、span(spanタグ)。デフォルトはdiv。 |

## noCacheタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

**属性**: なし

## codeSelectタグ

## codeSelectタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` は可

### 属性

:ref:`tag-generic_attributes_tag` に加えて以下の属性を指定できます。

| 属性 | 説明 |
|---|---|
| `name` (必須) | XHTMLのname属性 |
| `codeId` (必須) | コードID |
| `size` | XHTMLのsize属性 |
| `multiple` | XHTMLのmultiple属性（:ref:`論理属性 <boolean_attribute>`） |
| `disabled` | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`） |
| `tabindex` | XHTMLのtabindex属性 |
| `onfocus` | XHTMLのonfocus属性 |
| `onblur` | XHTMLのonblur属性 |
| `onchange` | XHTMLのonchange属性 |
| `autofocus` | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`） |
| `pattern` | 使用するパターンのカラム名。デフォルト：指定なし |
| `optionColumnName` | 取得するオプション名称のカラム名 |
| `labelPattern` | ラベル整形パターン。プレースホルダ: `$NAME$`（コード名）、`$SHORTNAME$`（短い名前）、`$OPTIONALNAME$`（オプション名）、`$VALUE$`（コード値）。`$OPTIONALNAME$`使用時はoptionColumnName必須。デフォルト：`$NAME$` |
| `listFormat` | リスト表示フォーマット。`br`（brタグ）・`div`（divタグ）・`span`（spanタグ）・`ul`（ulタグ）・`ol`（olタグ）・`sp`（スペース区切り）から選択。デフォルト：`br` |
| `withNoneOption` | リスト先頭に選択なし項目を追加するか。`true`/`false`。デフォルト：`false` |
| `noneOptionLabel` | 選択なし項目のラベル（withNoneOption=trueの場合のみ有効）。デフォルト：`\"\"` |
| `errorCss` | エラーメッセージのCSSクラス名。デフォルト：`nablarch_error` |
| `nameAlias` | name属性のエイリアス。複数指定時はカンマ区切り |

## codeRadioButtonsタグ

**動的属性の使用可否**: 可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name (必須) | XHTMLのname属性。 |
| codeId (必須) | コードID。 |
| disabled | XHTMLのdisabled属性（:ref:`論理属性 <boolean_attribute>`）。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性（:ref:`論理属性 <boolean_attribute>`）。選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（コード略称）、`$OPTIONALNAME$`（コードオプション名称）、`$VALUE$`（コード値）。`$OPTIONALNAME$`使用時はoptionColumnName属性の指定が必須。デフォルトは`$NAME$`。 |
| listFormat | リスト表示時フォーマット。以下から選択: `br`（brタグ）、`div`（divタグ）、`span`（spanタグ）、`ul`（ulタグ）、`ol`（olタグ）、`sp`（スペース区切り）。デフォルトはbr。 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルトは`nablarch_error`。 |
| nameAlias | name属性のエイリアスを設定する。複数指定する場合はカンマ区切り。 |

## codeCheckboxesタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | id属性は指定不可。 |
| :ref:`tag-focus_attributes_tag` | accesskey属性は指定不可。 |
| name **必須** | XHTMLのname属性。 |
| codeId **必須** | コードID。 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) 。 |
| onchange | XHTMLのonchange属性。 |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) 。選択肢のうち、先頭要素のみautofocus属性を出力する。 |
| pattern | 使用するパターンのカラム名。デフォルトは指定なし。 |
| optionColumnName | 取得するオプション名称のカラム名。 |
| labelPattern | ラベルを整形するパターン。プレースホルダ: `$NAME$` (コード名称), `$SHORTNAME$` (コード略称), `$OPTIONALNAME$` (コードオプション名), `$VALUE$` (コード値)。 `$OPTIONALNAME$` 使用時はoptionColumnName属性が必須。デフォルト: `$NAME$` |
| listFormat | リスト表示時のフォーマット: br(brタグ), div(divタグ), span(spanタグ), ul(ulタグ), ol(olタグ), sp(スペース区切り)。デフォルト: br |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定する場合はカンマ区切り。 |

## codeCheckboxタグ

**タグ**: codeCheckboxタグ

**動的属性**: 可 (:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>`)

### 属性一覧

| 属性 | 説明 |
|---|---|
| :ref:`tag-generic_attributes_tag` | |
| :ref:`tag-focus_attributes_tag` | |
| name (必須) | XHTMLのname属性 |
| value | XHTMLのvalue属性。チェックありの場合に使用するコード値。デフォルト: `1` |
| autofocus | HTML5のautofocus属性 (:ref:`論理属性 <boolean_attribute>`) |
| codeId (必須) | コードID |
| optionColumnName | 取得するオプション名称のカラム名 |
| labelPattern | ラベルを整形するパターン。プレースホルダ: `$NAME$` (コード値に対応するコード名称)、`$SHORTNAME$` (コード値に対応するコードの略称)、`$OPTIONALNAME$` (コード値に対応するコードのオプション名称)、`$VALUE$` (コード値)。`$OPTIONALNAME$` を使用する場合は optionColumnName属性の指定が必須。デフォルト: `$NAME$` |
| offCodeValue | チェックなしの場合に使用するコード値。指定されない場合、codeId属性の値から検索。検索結果が2件かつ1件がvalue属性の値である場合、残りの1件を使用。見つからない場合、デフォルト値 `0` を使用 |
| disabled | XHTMLのdisabled属性 (:ref:`論理属性 <boolean_attribute>`) |
| onchange | XHTMLのonchange属性 |
| errorCss | エラーレベルのメッセージに使用するCSSクラス名。デフォルト: `nablarch_error` |
| nameAlias | name属性のエイリアス。複数指定する場合はカンマ区切り |

## codeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：可

| 属性 | 説明 |
|---|---|
| name | 表示対象のコード値を変数スコープから取得する際に使用する名前。省略した場合は、コードID属性とpattern属性にて絞り込んだコードの一覧を表示する |
| codeId **必須** | コードID |
| pattern | 使用するパターンのカラム名。デフォルト: 指定なし |
| optionColumnName | 取得するオプション名称のカラム名 |
| labelPattern | ラベルを整形するパターン。プレースホルダ: `$NAME$`(コード名称), `$SHORTNAME$`(略称), `$OPTIONALNAME$`(オプション名称), `$VALUE$`(コード値)。`$OPTIONALNAME$` 使用時は optionColumnName属性の指定が必須。デフォルト: `$NAME$` |
| listFormat | リスト表示時のフォーマット: br, div, span, ul, ol, sp(スペース区切り)。デフォルト: br |

## cspNonceタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

:ref:`セキュアハンドラでnonceを生成する設定<content_security_policy>` を行っている場合に、セキュアハンドラが生成したnonceを出力する。

| 属性 | 説明 |
|---|---|
| sourceFormat | nonceを出力する際のフォーマットを制御。プレフィックス `nonce-` を付与する場合は `true`、しない場合は `false`。プレフィックス付与時はmeta要素で使用。デフォルト: `false` |

## messageタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| messageId | メッセージID（必須） |
| option0～option9 | メッセージフォーマット用のオプション引数（0～9、最大10個） |
| language | メッセージの言語。デフォルト: スレッドコンテキストの言語 |
| var | リクエストスコープに格納する変数名。設定時はメッセージを出力せず、HTMLエスケープ/フォーマットを行わない |
| htmlEscape | HTMLエスケープ実行可否（true = する、false = しない、デフォルト: true） |
| withHtmlFormat | HTMLフォーマット(改行・半角スペース変換)実行可否。htmlEscape有効時のみ適用。デフォルト: true |

## writeタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` → 否

## 属性

| 属性名 | 説明 |
|---|---|
| name | 表示対象の値を変数スコープから取得する際に使用する名前。value属性と同時に指定できない。 |
| value | 表示対象の値。直接値を指定する場合に使用する。name属性と同時に指定できない。 |
| withHtmlFormat | HTMLフォーマット(改行と半角スペースの変換)をするか否か。HTMLフォーマットはHTMLエスケープをする場合のみ有効となる。デフォルト：`true` |
| valueFormat | 出力時のフォーマット。:ref:`tag-format_value` を参照。 |

## prettyPrintタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>`: 否

> **重要**: このタグは非推奨であるため使用しないこと。詳細は :ref:`prettyPrintタグの使用を推奨しない理由 <tag-pretty_print_tag-deprecated>` を参照。

| 属性 | 説明 |
|---|---|
| name `必須` | 表示対象の値を変数スコープから取得する際に使用する名前 |

## rawWriteタグ

## rawWriteタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

### 属性

| 属性 | 説明 |
|---|---|
| name (必須) | 表示対象の値を変数スコープから取得する際に使用する名前 |

## setタグ

**動的属性の使用可否**: :ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` で説明する属性は使用できない（否）

**属性一覧**

| 属性 | 必須 | 説明 |
|---|---|---|
| var | ○ | リクエストスコープに格納する際に使用する変数名 |
| name | | 値を取得するための名前。name属性とvalue属性のどちらか一方を指定する |
| value | | 値。直接値を指定する場合に使用する。name属性とvalue属性のどちらか一方を指定する |
| scope | | 変数を格納するスコープを設定する。指定可能: page（ページスコープ）、request（リクエストスコープ、デフォルト） |
| bySingleValue | | name属性に対応する値を単一値として取得するか否か（デフォルト: `true`） |

## includeタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 必須 | 説明 |
|---|---|---|
| path | ○ | インクルードするリソースのパス。 |

## includeParamタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ：否

| 属性 | 説明 |
|---|---|
| paramName（必須） | インクルード時に使用するパラメータの名前 |
| name | 値を取得するための名前。name属性またはvalue属性のいずれか一方を指定 |
| value | 値。直接値を指定する場合に使用。name属性またはvalue属性のいずれか一方を指定 |

## confirmationPageタグ

:ref:`動的属性の使用可否 <tag-dynamic_attributes_tag>` ： 否

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
