# 認可チェックハンドラ

## 概要

本ハンドラでは、 permission_check_handler-request_checking を行う。

認可チェックは、ライブラリの permission_check を使用して行う。
そのため、本ハンドラを使用するには、
`PermissionFactory` を実装したクラスを本ハンドラに設定する必要がある。

本ハンドラでは、以下の処理を行う。

* 認可チェック

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-permission-check-handler/flow.png)

## ハンドラクラス名

* `nablarch.common.permission.PermissionCheckHandler`

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-auth</artifactId>
</dependency>
```

## 制約

thread_context_handler より後ろに配置すること
本ハンドラではスレッドコンテキスト上に設定されたリクエストIDとユーザIDをもとに認可チェックを行うため、
thread_context_handler より後ろに本ハンドラを配置する必要がある。

forwarding_handler より後ろに配置すること
内部フォーワードが行われた際に、フォーワード先のリクエストID（ 内部リクエストID ）をもとに
認可チェックを行いたい場合は、 forwarding_handler より後ろに本ハンドラを配置する必要がある。
合わせて、 thread_context_handler の `attributes` に `InternalRequestIdAttribute` を追加すること。

http_error_handler より後ろに配置すること
認可チェックエラーの場合に表示するエラーページを指定するため、
http_error_handler より後ろに本ハンドラを配置する必要がある。

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

## 権限がない場合に表示するエラーページを指定する

権限がない場合に表示するエラーページは、HTTPエラー制御ハンドラで指定する。
指定方法は、 HttpErrorHandler_DefaultPage を参照。

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
