# ハンドラによる認可チェック

## 機能概要

> **重要**: アプリケーション要件が合致する場合のみ使用すること。DBでリクエスト単位の権限データを管理するため、細かいデータ設計が必要で、開発生産性低下や運用負荷が高まる可能性がある。単純なデータ構造で権限管理したい場合は [role_check](libraries-role_check.md) も選択肢とすること。

:ref:`permission_check_handler` をハンドラキューに設定することで、リクエスト単位で認可チェックを行うことができる。

権限設定の概念モデル:

![権限設定の概念モデル](../../knowledge/component/libraries/assets/libraries-permission_check/conceptual_model.png)

- **グループ**: 部署など組織単位での権限割り当てに使用
- **認可チェック単位**: 複数リクエストをまとめた認可チェックの最小単位。ウェブの場合は画面イベント（リクエスト）が複数紐付く。例: ユーザ登録 → 入力初期表示・確認ボタン・登録ボタン・戻るボタン
- グループとユーザ、グループと認可チェック単位の関連設定でグループ単位の権限を設定可能
- ユーザに直接認可チェック単位を設定することで、特定ユーザへのイレギュラーな権限付与に対応可能

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-auth</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-auth-jdbc</artifactId>
</dependency>
```

## 認可チェックを使うための設定

DBテーブル構成:

| テーブル名 | カラム | 備考 |
|---|---|---|
| グループ | グループID(PK): 文字列型 | |
| システムアカウント | ユーザID(PK): 文字列型, ユーザIDロック状態: 文字列型, 有効日From: 文字列型, 有効日To: 文字列型 | ロック状態: 0=未ロック/0以外=ロック済。有効日: yyyyMMdd形式（デフォルトFrom=19000101, To=99991231） |
| グループシステムアカウント | グループID(PK), ユーザID(PK), 有効日From(PK), 有効日To | 有効日: yyyyMMdd形式（デフォルトFrom=19000101, To=99991231） |
| 認可チェック単位 | 認可チェック単位ID(PK): 文字列型 | |
| 認可チェック単位リクエスト | 認可チェック単位ID(PK), リクエストID(PK): 文字列型 | |
| グループ権限 | グループID(PK), 認可チェック単位ID(PK) | |
| システムアカウント権限 | ユーザID(PK), 認可チェック単位ID(PK) | |

`BasicPermissionFactory` をコンポーネント定義に追加し、:ref:`permission_check_handler` に設定する（コンポーネント名は任意）。初期化が必要なため `BasicApplicationInitializer` の `initializeList` に追加すること。

```xml
<component name="permissionFactory" class="nablarch.common.permission.BasicPermissionFactory">
  <property name="groupTableSchema">
    <component class="nablarch.common.permission.schema.GroupTableSchema"/>
  </property>
  <property name="systemAccountTableSchema">
    <component class="nablarch.common.permission.schema.SystemAccountTableSchema"/>
  </property>
  <property name="groupSystemAccountTableSchema">
    <component class="nablarch.common.permission.schema.GroupSystemAccountTableSchema"/>
  </property>
  <property name="permissionUnitTableSchema">
    <component class="nablarch.common.permission.schema.PermissionUnitTableSchema"/>
  </property>
  <property name="permissionUnitRequestTableSchema">
    <component class="nablarch.common.permission.schema.PermissionUnitRequestTableSchema"/>
  </property>
  <property name="groupAuthorityTableSchema">
    <component class="nablarch.common.permission.schema.GroupAuthorityTableSchema"/>
  </property>
  <property name="systemAccountAuthorityTableSchema">
    <component class="nablarch.common.permission.schema.SystemAccountAuthorityTableSchema"/>
  </property>
  <property name="dbManager" ref="permissionCheckDbManager"/>
  <property name="businessDateProvider" ref="businessDateProvider"/>
</component>
```

```xml
<component name="initializer" class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="permissionFactory"/>
    </list>
  </property>
</component>
```

## サーバサイドで認可チェックを行う

:ref:`permission_check_handler` によりスレッドコンテキストに `Permission` が設定される。`PermissionUtil.getPermission` で取得して認可チェックを行う。

```java
Permission permission = PermissionUtil.getPermission();
if (permission.permit("/action/user/unlock")) {
    // 認可チェックがOKの場合の処理
}
```

## 権限に応じて画面表示を制御する

権限の有無でボタン・リンクの非表示（非活性）を制御する場合はカスタムタグ :ref:`tag-submit_display_control` を使用する。

## 権限データにアクセスする

本機能は認可チェックのみを提供しており、権限データへの直接アクセス機能は提供しない。特定グループに属するユーザ一覧取得など権限データへのアクセスが必要な場合は :ref:`universal_dao` でSQLを作成して対応すること。

## 拡張例

なし。
