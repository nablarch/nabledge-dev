# Bean ValidationとNablarch Validationの機能比較

ここでは、Nablarchの提供するバリデーション機能と [Jakarta Bean Validation(外部サイト、英語)](https://jakarta.ee/specifications/bean-validation/) の機能比較を示す。

| 機能 | Bean  Validation | Nablarch  Validation | Jakarta  Bean Validation |
|---|---|---|---|
| バリデーション対象の項目を指定できる | ○ [#property_validation]_ | ○  解説書へ | ○ |
| 階層構造を持つJava Beansオブジェクトに  対してバリデーションできる | ○ [#jsr]_ | ○  解説書へ | ○ |
| メソッドの引数、戻り値に対してバリデーションできる | × [#method]_ | × [#method]_ | ○ |
| 相関バリデーションができる | ○  解説書へ | ○  解説書へ | ○ |
| バリデーションの実行順序を指定できる | × [#order]_ | ○  解説書へ | ○ |
| 特定の項目の値を条件に  バリデーション項目を切り替えることが出来る | ○ [#conditional]_ | ○  解説書へ | ○ |
| エラーメッセージに埋め込みパラメータを使用できる | ○ [#parameter]_  解説書へ | ○  解説書へ | ○ |
| ドメインバリデーションができる | ○  解説書へ | ○  解説書へ | × |
| 値の型変換ができる | × [#type_converter]_ | ○  解説書へ | × |
| 値の正規化ができる | × [#normalized]_ | ○  解説書へ | × |
| エラーメッセージに項目名を埋め込むことができる | ○  解説書へ | ○  解説書へ | × |
Formの全ての項目に対してバリデーションを行うことで、不正な入力値の受付を防ぐことが出来る。 
このため、Bean Validationでは、項目指定のバリデーション実行は推奨していない。 
どうしても指定の項目に対してのみバリデーションを行いたい場合には、
`ValidatorUtil#validate` を使用すること。
対応方法は、 [Jakarta Bean Validation(外部サイト、英語)](https://jakarta.ee/specifications/bean-validation/) の仕様に準拠する。
Nablarchでは外部からデータを受け付けたタイミングで必ずバリデーションを行うため、
メソッドの引数や戻り値に対するバリデーションには対応していない。
バリデーションの実行順は制御できないため、バリデーションの実行順序を期待するような実装は行わないこと。
例えば、項目毎のバリデーション後に相関バリデーションが実行されるといったことを期待してはならない。
[Jakarta Bean Validation(外部サイト、英語)](https://jakarta.ee/specifications/bean-validation/) のクラスレベルのバリデーション機能を使用して、ロジックによりバリデーション項目を切り替えること。
Bean Validationでは、EL式を使用してパラメータを埋め込むこともできる。
Bean Validationでは、プロパティの型は全てStringとして定義する(Stringで定義する理由)ため型変換は行わない。
型変換が必要な場合には、バリデーション実施後に `BeanUtil` を使って型変換する。
正規化は、Bean Validationの機能ではなくハンドラとして提供している。正規化が必要な場合には、 ノーマライズハンドラ を使用して行う。
