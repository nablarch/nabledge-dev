# 認可チェックハンドラ

## 概要

本ハンドラでは、 リクエストに対する認可チェック を行う。

認可チェックは、ライブラリの permission_check を使用して行う。
そのため、本ハンドラを使用するには、
`PermissionFactory` を実装したクラスを本ハンドラに設定する必要がある。

本ハンドラでは、以下の処理を行う。

* 認可チェック

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-permission-check-handler/flow.png)

## ハンドラクラス名

* `nablarch.common.permission.PermissionCheckHandler`

<details>
<summary>keywords</summary>

PermissionCheckHandler, nablarch.common.permission.PermissionCheckHandler, PermissionFactory, nablarch.common.permission.PermissionFactory, 認可チェックハンドラ, ハンドラクラス

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-auth</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-common-auth, com.nablarch.framework, モジュール, 依存関係

</details>

## 制約

スレッドコンテキスト変数管理ハンドラ より後ろに配置すること
本ハンドラではスレッドコンテキスト上に設定されたリクエストIDとユーザIDをもとに認可チェックを行うため、
スレッドコンテキスト変数管理ハンドラ より後ろに本ハンドラを配置する必要がある。

内部フォーワードハンドラ より後ろに配置すること
内部フォーワードが行われた際に、フォーワード先のリクエストID（ 内部リクエストID ）をもとに
認可チェックを行いたい場合は、 内部フォーワードハンドラ より後ろに本ハンドラを配置する必要がある。
合わせて、 スレッドコンテキスト変数管理ハンドラ の `attributes` に `InternalRequestIdAttribute` を追加すること。

HTTPエラー制御ハンドラ より後ろに配置すること
認可チェックエラーの場合に表示するエラーページを指定するため、
HTTPエラー制御ハンドラ より後ろに本ハンドラを配置する必要がある。

<details>
<summary>keywords</summary>

InternalRequestIdAttribute, nablarch.common.handler.threadcontext.InternalRequestIdAttribute, ハンドラ配置順序, 制約, スレッドコンテキスト, 内部リクエストID

</details>

## リクエストに対する認可チェック

ログイン中のユーザが、現在のリクエスト(リクエストID)に対して権限を持っているかをチェックする。
チェックの詳細は、 permission_check を参照。

権限がある場合
業務ロジック や
画面表示の制御 で参照できるように、
認可チェックに使用した `Permission` をスレッドローカルに設定する。
そして、後続ハンドラを呼び出す。

権限がない場合
`Forbidden(403)` を送出する。

チェック対象のリクエストIDをフォーワード先のリクエストIDに変更したい場合は、
`PermissionCheckHandler.setUsesInternalRequestId`
でtrueを指定する。デフォルトはfalseである。

<details>
<summary>keywords</summary>

PermissionCheckHandler, Permission, nablarch.common.permission.Permission, Forbidden, nablarch.fw.results.Forbidden, setUsesInternalRequestId, リクエスト認可チェック, 権限チェック, 403エラー, 内部リクエストID

</details>

## 権限がない場合に表示するエラーページを指定する

権限がない場合に表示するエラーページは、HTTPエラー制御ハンドラで指定する。
指定方法は、 デフォルトページの設定 を参照。

<details>
<summary>keywords</summary>

エラーページ指定, 403エラーページ, HTTPエラー制御ハンドラ, HttpErrorHandler_DefaultPage

</details>

## 特定のリクエストを認可チェックから除外する

ログイン前のリクエストなど、認可チェックを除外したいリクエストがある場合は、
`PermissionCheckHandler.setIgnoreRequestIds`
で指定する。

```xml
<component name="permissionCheckHandler"
           class="nablarch.common.permission.PermissionCheckHandler">
  <property name="permissionFactory" ref="permissionFactory"/>
  <!-- 認可チェックを除外するリクエストIDをカンマ区切りで指定する -->
  <property name="ignoreRequestIds" value="/action/login,/action/logout" />
</component>
```

<details>
<summary>keywords</summary>

setIgnoreRequestIds, PermissionCheckHandler, nablarch.common.permission.PermissionCheckHandler, 認可チェック除外, ログイン前リクエスト

</details>
