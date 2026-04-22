# リクエスト単体テストの実施方法(ファイルアップロード)

ファイルアップロードのテストは、ウェブアプリケーションのテストの一種である。
したがって、ファイルアップロードのテストを実施するには、ウェブアプリケーションの\ index\ が前提となる。

ファイルアップロードのテストをする場合、HTTPリクエストパラメータにアップロードファイルを指定する必要がある。\
本項では、HTTPリクエストパラメータにアップロードファイルを指定する方法を解説する。\

## アップロードファイルの記述方法

HTTPリクエストパラメータの値に、以下の記述をすることで、
HTTPリクエストパラメータにアップロードファイルを指定できる。

```text
${attach:ファイルパス}
```
> **Tip:** ファイルパスは、\ **テスト実行時のカレントディレクトリからの相対パス**\ 、すなわち、\ プロジェクトルートディレクトリからの相対パスで記述する。

## バイナリファイルの場合

画像ファイル等、バイナリファイルをアップロードする場合は、事前にファイルを配置しておき、
そのファイルへのパスを指定する。


以下の例では、uploadfileというキーで、プロジェクト配下のtest/resources/images\
ディレクトリにあるpicture.pngをアップロードする。

```text
<project_root>
     + test
        + resources
           + images
              + picture.png
```
------


`LIST_MAP=requestParams`

<table>
<thead>
<tr>
  <th>uploadfile</th>
  <th>comment</th>
  <th>public</th>
</tr>
</thead>
<tbody>
<tr>
  <td>`${attach:test/resources/images/picture.png}`</td>
  <td>アップロードします。</td>
  <td>`false`</td>
</tr>
</tbody>
</table>


------

## 固定長ファイル、CSVファイルの場合

\ 固定長ファイル\や
CSVファイル\ をアップロードする場合、\
そのファイル内容をテストデータシートに記載する。\
テスト実行時に、自動テストフレームワークがこのデータを元にファイルを作成する。


以下の例では、workディレクトリ配下にmember_list.csvファイルを作成し、
そのファイルをアップロード対象として指定している。

------

`LIST_MAP=requestParams`

<table>
<thead>
<tr>
  <th>uploadfile</th>
  <th>comment</th>
</tr>
</thead>
<tbody>
<tr>
  <td>`${attach:work/member_list.csv}`</td>
  <td>10月度新規会員を登録</td>
</tr>
</tbody>
</table>


`SETUP_FIXED=work/member_list.csv`



// ディレクティブ

<table>
<tbody>
<tr>
  <td>text-encoding</td>
  <td>Windows-31J</td>
  <td></td>
</tr>
<tr>
  <td>record-separator</td>
  <td>CRLF</td>
  <td></td>
</tr>
</tbody>
</table>

// データ

<table>
<thead>
<tr>
  <th>name</th>
  <th>age</th>
  <th>address</th>
</tr>
</thead>
<tbody>
<tr>
  <td>山田太郎</td>
  <td>30</td>
  <td>東京都港区芝浦1-1</td>
</tr>
<tr>
  <td>田中次郎</td>
  <td>20</td>
  <td>大阪府門真市東田町2-2</td>
</tr>
</tbody>
</table>

------

> **Tip:** 固定長ファイルやCSVファイルをアップロードする場合でも、 バイナリファイルと同様に、事前にファイルを用意しておくことも可能であるが、 テストデータの保守容易性を考慮するとテストデータシートに記載しておくべきである。
