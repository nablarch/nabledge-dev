# JSR310(Date and Time API)アダプタ

## 概要

JSR310(Date and Time API)で追加された日時関連を使用可能にするためのアダプタを提供する。
このアダプタを使用することで、 BeanUtil でJSR310(Date and Time API)を使用できる。

> **Important:** 本アダプタで提供される機能はNablarch 6u2よりフレームワーク本体に取り込まれているため、本アダプタを使用せずとも BeanUtil でJSR310(Date and Time API)を使用できる。 本アダプタは後方互換を維持するために残している。
> **Important:** 本アダプタで対応している型は以下の通り。 これら以外の型を扱いたい場合は、プロジェクト側でConverterの追加などを行う必要がある。 * `LocalDate` * `LocalDateTime`

## モジュール一覧

```xml
<!-- JSR310アダプタ -->
<dependency>
  <groupId>com.nablarch.integration</groupId>
  <artifactId>nablarch-jsr310-adaptor</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-jsr310-adaptor, LocalDate, LocalDateTime, JSR310アダプタ, Date and Time API, 後方互換, BeanUtil JSR310対応

</details>

## 使用方法

変換可能な型や変換ルールなどの詳細は、 `converter一覧` を参照。

設定
システムリポジトリ のコンポーネント設定ファイルに以下を追加することで、本機能が有効になる。

```xml
<import file="JSR310.xml" />
```
> **Tip:** 文字列から変換する際のフォーマットを変更したい場合は、以下の作業が必要となる。 フォーマットなどの定義を持つクラスを作成する extdoc:`DateTimeConfiguration <nablarch.integration.jsr310.util.DateTimeConfiguration>` の実装クラスを追加し、 日付や日時のフォーマットを定義する。 基本実装の `BasicDateTimeConfiguration` を参考にすると良い 追加したクラスをコンポーネント設定ファイルに定義する コンポーネント名を `dateTimeConfiguration` として、コンポーネントを定義する。 例を以下に示す。 .. code-block:: xml <component name="dateTimeConfiguration" class="sample.SampleDateTimeConfiguration" />

<details>
<summary>keywords</summary>

DateTimeConfiguration, BasicDateTimeConfiguration, dateTimeConfiguration, JSR310有効化, 日時フォーマット設定, コンポーネント設定, JSR310.xml

</details>
