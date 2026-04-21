# Bean ValidationとNablarch Validationの機能比較

## 概要

ここでは、Nablarchの提供するバリデーション機能と |jsr349| の機能比較を示す。

| 機能 | Bean \|br\| Validation | Nablarch \|br\| Validation | Jakarta \|br\| Bean Validation |
|---|---|---|---|
| バリデーション対象の項目を指定できる | ○ [#property_validation]_ | ○ \|br\| 解説書へ | ○ |
| 階層構造を持つJava Beansオブジェクトに \|br\| 対してバリデーションできる | ○ [#jsr]_ | ○ \|br\| 解説書へ | ○ |
| メソッドの引数、戻り値に対してバリデーションできる | × [#method]_ | × [#method]_ | ○ |
| 相関バリデーションができる | ○ \|br\| 解説書へ | ○ \|br\| 解説書へ | ○ |
| バリデーションの実行順序を指定できる | × [#order]_ | ○ \|br\| 解説書へ | ○ |
| 特定の項目の値を条件に \|br\| バリデーション項目を切り替えることが出来る | ○ [#conditional]_ | ○ \|br\| 解説書へ | ○ |
| エラーメッセージに埋め込みパラメータを使用できる | ○ [#parameter]_ \|br\| 解説書へ | ○ \|br\| 解説書へ | ○ |
| ドメインバリデーションができる | ○ \|br\| 解説書へ | ○ \|br\| 解説書へ | × |
| 値の型変換ができる | × [#type_converter]_ | ○ \|br\| 解説書へ | × |
| 値の正規化ができる | × [#normalized]_ | ○ \|br\| 解説書へ | × |
| エラーメッセージに項目名を埋め込むことができる | ○ \|br\| 解説書へ | ○ \|br\| 解説書へ | × |
Formの全ての項目に対してバリデーションを行うことで、不正な入力値の受付を防ぐことが出来る。 |br|
このため、Bean Validationでは、項目指定のバリデーション実行は推奨していない。 |br|
どうしても指定の項目に対してのみバリデーションを行いたい場合には、
:java:extdoc:`ValidatorUtil#validate <nablarch.core.validation.ee.ValidatorUtil.validate(java.lang.Object,java.lang.String...)>` を使用すること。
対応方法は、 |jsr349| の仕様に準拠する。
Nablarchでは外部からデータを受け付けたタイミングで必ずバリデーションを行うため、
メソッドの引数や戻り値に対するバリデーションには対応していない。
バリデーションの実行順は制御できないため、バリデーションの実行順序を期待するような実装は行わないこと。
例えば、項目毎のバリデーション後に相関バリデーションが実行されるといったことを期待してはならない。
|jsr349| のクラスレベルのバリデーション機能を使用して、ロジックによりバリデーション項目を切り替えること。
Bean Validationでは、EL式を使用してパラメータを埋め込むこともできる。
Bean Validationでは、プロパティの型は全てStringとして定義する(:ref:`Stringで定義する理由 <bean_validation-form_property>`)ため型変換は行わない。
型変換が必要な場合には、バリデーション実施後に :java:extdoc:`BeanUtil <nablarch.core.beans.BeanUtil>` を使って型変換する。
正規化は、Bean Validationの機能ではなくハンドラとして提供している。正規化が必要な場合には、 ノーマライズハンドラ を使用して行う。
.. |jsr349| raw:: html

<a href="https://jakarta.ee/specifications/bean-validation/" target="_blank">Jakarta Bean Validation(外部サイト、英語)</a>

.. |br| raw:: html

<br />
