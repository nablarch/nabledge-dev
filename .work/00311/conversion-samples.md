# Conversion Samples — Excel Sheet Patterns

変換前後を並べて確認するためのサンプル集。

---

## P2-1: Column-indent → Markdown headings

**Sheet**: `マルチパートリクエストのサポート対応` (nablarch6u3-releasenote.xlsx, v6)

**Rule**: col0=H1, col1=H2, col2=H3, col3+=body text

### Before (current output)

```
■Jakarta RESTful Web Servicesアダプタでマルチパートリクエストを扱うための設定変更手順
【本手順の適用対象となるシステム】
本手順は、以下の条件をすべて満たすシステムを対象としています。
・Nablarch 6u2以前からのバージョンアップであること
・Jakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryまたはResteasyJaxRsHandlerListFactoryを使用していること
　※RESTfulウェブサービスのブランクプロジェクトは、デフォルトでJerseyJaxRsHandlerListFactoryを使用するように構成されています
・Nablarchの標準機能を使用して、RESTfulウェブサービスでマルチパートリクエストを扱いたい
【変更内容の概要】
Nablarch 6u3では、RESTfulウェブサービスでマルチパートリクエストを扱えるようにするためにマルチパート用のBodyConverterを追加しています。
それに伴いJakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryおよびResteasyJaxRsHandlerListFactoryに
該当のBodyConverterを追加していますが、マルチパートをリクエストを扱うためにはさらに以下の対応を行う必要があります。
・コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加
・ハンドラキューへのマルチパートリクエストハンドラの追加
・ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定
これらの変更を行うことにより、RESTfulウェブサービスでマルチパートリクエストが扱えるようになり、ファイルアップロードが可能になります。
【変更手順】
【コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加】
src/main/resources/rest-component-configuration.xml に以下の設定を追加します。
  <!-- ファイルパス設置 -->
  <import file="nablarch/webui/filepath-for-webui.xml" />
  <!-- ファイルアップロード機能設定 -->
  <import file="nablarch/webui/multipart.xml" />
【ハンドラキューへのマルチパートリクエストハンドラの追加】
src/main/resources/rest-component-configuration.xml のハンドラキュー(webFrontController)に以下の定義を追加してください。
<component-ref name="multipartHandler"/>
追加位置は、セッション変数保存ハンドラおよびCSRFトークン検証ハンドラの制約事項を確認して決定してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/SessionStoreHandler.html#session-store-handler-constraint
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/csrf_token_verification_handler.html#id4
また、環境ごとにハンドラキューを上書きしている場合は、そちらのハンドラキュー定義にも反映してください。
【ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定】
ファイルパス設定を追加したことにより、以下のプロパティを定義する必要があります。
src/main/resources/common.properties
nablarch.uploadSettings.contentLengthLimit
src/env/[環境別]/resources/env.properties
nablarch.filePathSetting.basePathSettings.format
nablarch.filePathSetting.basePathSettings.output
nablarch.uploadSettings.autoCleaning
nablarch.filePathSetting.basePathSettings.uploadFileTmpDir
設定内容は、マルチパートリクエストハンドラを確認してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/multipart_handler.html
「nablarch.filePathSetting.basePathSettings.format」は汎用データフォーマットのフォーマット定義ファイル用のパス設定ですが、
汎用データフォーマットを使用しないのであればダミー値でかまいません。
```

### After (P2-1 conversion)

# ■Jakarta RESTful Web Servicesアダプタでマルチパートリクエストを扱うための設定変更手順

## 【本手順の適用対象となるシステム】

### 本手順は、以下の条件をすべて満たすシステムを対象としています。

・Nablarch 6u2以前からのバージョンアップであること
・Jakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryまたはResteasyJaxRsHandlerListFactoryを使用していること
　※RESTfulウェブサービスのブランクプロジェクトは、デフォルトでJerseyJaxRsHandlerListFactoryを使用するように構成されています
・Nablarchの標準機能を使用して、RESTfulウェブサービスでマルチパートリクエストを扱いたい

## 【変更内容の概要】

### Nablarch 6u3では、RESTfulウェブサービスでマルチパートリクエストを扱えるようにするためにマルチパート用のBodyConverterを追加しています。

それに伴いJakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryおよびResteasyJaxRsHandlerListFactoryに
該当のBodyConverterを追加していますが、マルチパートをリクエストを扱うためにはさらに以下の対応を行う必要があります。

### ・コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加

### ・ハンドラキューへのマルチパートリクエストハンドラの追加

### ・ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定

### これらの変更を行うことにより、RESTfulウェブサービスでマルチパートリクエストが扱えるようになり、ファイルアップロードが可能になります。

## 【変更手順】

### 【コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加】

src/main/resources/rest-component-configuration.xml に以下の設定を追加します。
  <!-- ファイルパス設置 -->
  <import file="nablarch/webui/filepath-for-webui.xml" />
  <!-- ファイルアップロード機能設定 -->
  <import file="nablarch/webui/multipart.xml" />

### 【ハンドラキューへのマルチパートリクエストハンドラの追加】

src/main/resources/rest-component-configuration.xml のハンドラキュー(webFrontController)に以下の定義を追加してください。
`<component-ref name="multipartHandler"/>`
追加位置は、セッション変数保存ハンドラおよびCSRFトークン検証ハンドラの制約事項を確認して決定してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/SessionStoreHandler.html#session-store-handler-constraint
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/csrf_token_verification_handler.html#id4
また、環境ごとにハンドラキューを上書きしている場合は、そちらのハンドラキュー定義にも反映してください。

### 【ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定】

ファイルパス設定を追加したことにより、以下のプロパティを定義する必要があります。

#### src/main/resources/common.properties

nablarch.uploadSettings.contentLengthLimit

#### src/env/[環境別]/resources/env.properties

nablarch.filePathSetting.basePathSettings.format
nablarch.filePathSetting.basePathSettings.output
nablarch.uploadSettings.autoCleaning
nablarch.filePathSetting.basePathSettings.uploadFileTmpDir
設定内容は、マルチパートリクエストハンドラを確認してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/multipart_handler.html
「nablarch.filePathSetting.basePathSettings.format」は汎用データフォーマットのフォーマット定義ファイル用のパス設定ですが、
汎用データフォーマットを使用しないのであればダミー値でかまいません。

---

## P2-2: Current behavior maintained (no change)

**Sheet**: `バージョンアップ手順` (nablarch6u3-releasenote.xlsx, v6)

step table (No/適用手順) はテーブル構造なので変換しない。

### Before = After (unchanged)

```
本リリースの適用手順は、次の通りです。
No  適用手順
1  pom.xmlの<dependencyManagement>セクションに指定されているnablarch-bomのバージョンを6u3に書き換える
2  mavenのビルドを再実行する
```

---

## P2-3: Embedded LF preserved as Markdown line breaks

**Sheet**: `バージョンアップ手順` (nablarch5u25-releasenote.xlsx, v5)

セル内改行（`\n`）をMarkdown改行（行末スペース2つ＋改行）として保持する。

### Before (current output — LF collapsed to space)

```
本リリースの適用手順は、次の通りです。
No  適用手順
1  pom.xmlの<dependencyManagement>セクションに指定されているnablarch-bomのバージョンを5u25に書き換える
2  Micrometerアダプタを利用しており、pom.xmlの<dependencies>に以下が指定されている場合、バージョンを1.13.0に書き換える ・micrometer-registry-datadog ・micrometer-registry-cloudwatch2 ・micrometer-registry-statsd
3  mavenのビルドを再実行する
```

### After (P2-3 conversion — LF preserved)

本リリースの適用手順は、次の通りです。

| No | 適用手順 |
|----|----------|
| 1 | pom.xmlの\<dependencyManagement\>セクションに指定されているnablarch-bomのバージョンを5u25に書き換える |
| 2 | Micrometerアダプタを利用しており、pom.xmlの\<dependencies\>に以下が指定されている場合、バージョンを1.13.0に書き換える<br>・micrometer-registry-datadog<br>・micrometer-registry-cloudwatch2<br>・micrometer-registry-statsd |
| 3 | mavenのビルドを再実行する |

> **注**: P2-3はP2-2と同じテーブル構造のシートだが、セル内にLFが含まれる。docs MDではMarkdown改行（`<br>`またはスペース2つ＋改行）として表現する。JSON contentではLFをそのまま保持する（`\n`）。
