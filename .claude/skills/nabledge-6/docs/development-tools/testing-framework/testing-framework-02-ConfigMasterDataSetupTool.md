# マスタデータ投入ツール インストールガイド

## 概要

index\ のインストール方法について説明する。


# 前提事項


* 以下のツールがインストール済みであること

* Eclipse
* Maven

* Nablarchのアーキタイプ から生成されたプロジェクトであること
* テーブルが作成済みであること
* バックアップ用スキーマにテーブルが作成済みであること\ [#]_

.. [#]
バックアップ用スキーマおよびそのテーブルの作成については、\
『\ ../../06_TestFWGuide/04_MasterDataRestore\ 』の\ master_data_backup_settings\ を参照。



# 提供方法

本ツールはnablarch-testing-XXX.jar にて提供する。

ツール使用前に、プロジェクトのユニットテストと同じDB設定を使用できるようにするためにプロジェクトのコンパイルと、ツールの実行に必要なjarファイルのダウンロードを行なう。
以下のコマンドを実行する。

```text
mvn compile
mvn dependency:copy-dependencies -DoutputDirectory=lib
```
以下のファイルをダウンロードし、プロジェクトのディレクトリ(pom.xmlが存在するディレクトリ）にディレクトリ付きで展開する。

* [master-data-setup-tool.zip](../../../knowledge/assets/testing-framework-02-ConfigMasterDataSetupTool/master-data-setup-tool.zip)

上記ファイルに含まれる設定ファイルを下記に示す。

<table>
<thead>
<tr>
  <th>ファイル名</th>
  <th>説明</th>
</tr>
</thead>
<tbody>
<tr>
  <td>tool/db/data/master_data-build.properties</td>
  <td>環境設定用プロパティファイル</td>
</tr>
<tr>
  <td>tool/db/data/master_data-build.xml</td>
  <td>Antビルドファイル</td>
</tr>
<tr>
  <td>tool/db/data/master_data-log.properties</td>
  <td>ログ出力プロパティファイル</td>
</tr>
<tr>
  <td>tool/db/data/master_data-app-log.properties</td>
  <td>ログ出力プロパティファイル</td>
</tr>
<tr>
  <td>tool/db/data/MASTER_DATA.xlsx</td>
  <td>マスタデータファイル</td>
</tr>
</tbody>
</table>

本ツールを実行する前に以下のコマンドを実行する。

```text
mvn compile
mvn dependency:copy-dependencies -DoutputDirectory=lib
```

## プロパティファイルの書き換え

マスタデータ自動復旧機能が使用する、バックアップスキーマ名を設定する。


```bash
# テスト用マスタデータバックアップスキーマ名
masterdata.test.backup-schema=nablarch_test_master
```
その他の設定値については、ディレクトリ構造が変わらない限り修正の必要はない。


# Eclipseとの連携設定

以下の設定をすることでEclipseから本ツールを起動できる。

<details>
<summary>keywords</summary>

前提条件, インストール要件, Eclipse インストール, Maven インストール, Nablarchアーキタイプ, テーブル作成済み, バックアップ用スキーマ, マスタデータ投入ツール前提, nablarch-testing jar, nablarch-testing-XXX.jar, mvn compile, mvn dependency:copy-dependencies, DoutputDirectory=lib, 提供方法, ツールセットアップ, マスタデータ投入ツール インストール, jarファイル ダウンロード, masterdata.test.backup-schema, バックアップスキーマ設定, マスタデータ投入ツール設定, プロパティファイル, master-data-setup-tool.zip, MASTER_DATA.xlsx, master_data-build.properties, master_data-log.properties, master_data-app-log.properties

</details>

## Antビュー起動

ツールバーから、ウィンドウ(Window)→設定(Show View)を選択し、Antビューを開く。



![](../../../knowledge/assets/testing-framework-02-ConfigMasterDataSetupTool/open_ant_view.png)

<details>
<summary>keywords</summary>

Eclipse連携, Antビュー起動, Eclipseツール設定, マスタデータ投入ツール Eclipse, Show View

</details>

## ビルドファイル登録

＋印のアイコンを押下し、ビルドスクリプトを選択する。

![](../../../knowledge/assets/testing-framework-02-ConfigMasterDataSetupTool/register_build_file.png)
Antビルドファイル(master_data-build.xml)を選択する。

![](../../../knowledge/assets/testing-framework-02-ConfigMasterDataSetupTool/select_build_file.png)
Antビューに登録したビルドファイルが表示されることを確認する。

![](../../../knowledge/assets/testing-framework-02-ConfigMasterDataSetupTool/build_file_in_view.png)

<details>
<summary>keywords</summary>

master_data-build.xml, Antビルドファイル登録, Eclipseビルドファイル, マスタデータ投入ツール設定, Antビュー

</details>
