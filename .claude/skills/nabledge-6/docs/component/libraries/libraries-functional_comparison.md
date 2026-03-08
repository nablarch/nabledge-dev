# データバインドと汎用データフォーマットの比較表

## データバインドと汎用データフォーマットの比較表

データバインド（:ref:`data_bind`）と汎用データフォーマット（:ref:`data_format`）の機能比較。

| 機能 | データバインド | 汎用データフォーマット |
|---|---|---|
| CSVの入出力ができる | ○ :ref:`解説書へ <data_bind-csv_format>` | ○ :ref:`解説書へ <data_format-support_type>` |
| レコード毎にフォーマットの異なるCSVの入出力ができる | × [1] | ○ :ref:`解説書へ <data_format-multi_layout_data>` |
| CSVの定義を設定できる（カンマやクォート文字を変更することできる） | ○ :ref:`解説書へ <data_bind-csv_format>` | ○ :ref:`解説書へ <data_format-variable_data_directive>` |
| 固定長データの入出力ができる | ○ :ref:`解説書へ <data_bind-fixed_length_format>` | ○ :ref:`解説書へ <data_format-support_type>` |
| レコード毎にフォーマットの異なる固定長データの入出力ができる | ○ :ref:`解説書へ <data_bind-fixed_length_format-multi_layout>` | ○ :ref:`解説書へ <data_format-multi_layout_data>` |
| JSONデータの入出力ができる | × [2] | ○ :ref:`解説書へ <data_format-support_type>` |
| XMLデータの入出力ができる | × [3] | ○ :ref:`解説書へ <data_format-support_type>` |
| データ入出力時に値の変換ができる（trimやパック数値やゾーン数値の変換など） | △ [4] | ○ :ref:`解説書へ <data_format-value_convertor>` |
| データの寄せ字ができる（システムで許容可能な文字への変換などを指す） | × [5] | ○ :ref:`解説書へ <data_format-replacement>` |

凡例：○：提供あり　△：一部提供あり　×：提供なし　－：対象外

[1] レコード毎に異なるフォーマットのCSVを扱う場合には、:ref:`data_format` を使用すること。
[2] JSONデータの入出力は未実装。JSONデータを扱う場合は、:ref:`data_format` やOSSを使用すること。
[3] XMLデータの入出力は未実装。XMLデータを扱う場合は、:ref:`data_format` やJakarta XML Bindingを使用すること。
[4] 固定長データのみtrim等のコンバータを提供している。CSVで値を変換したい場合は、出力前及び入力後に変換すること。
[5] 入力データの寄せ字(文字変換)は、文字変換用のハンドラを作成し対応すること。
