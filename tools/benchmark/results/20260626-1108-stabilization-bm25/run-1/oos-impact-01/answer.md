**結論**: NablarchはOAuth2やOpenID Connectを含む認証機能をフレームワークとして組み込んでいません。認証はプロジェクト要件によって仕様が異なるため、プロジェクト側で実装する必要があります。

**根拠**:
Nablarchのウェブアプリケーション機能詳細には以下の通り明示されています。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

つまり、OAuth2 / OpenID ConnectによるIDプロバイダー連携の処理（認可コードフローの実装、トークン検証、ユーザー情報取得など）はすべてプロジェクトで実装します。

認証後の**セッション管理**（認証情報の保持）については、Nablarchが提供するセッションストアを利用できます。

```xml
<!-- セッションストアの設定例（DBストア使用） -->
<component name="sessionManager" class="nablarch.common.web.session.SessionManager">
  <property name="defaultStoreName" value="db"/>
  <property name="availableStores">
    <list>
      <component-ref name="dbStore" />
    </list>
  </property>
</component>
```

なお、認証とは別に**認可（権限チェック）**については、Nablarchが `PermissionCheckHandler` による認可チェック機能を提供しています。OAuth2で認証されたユーザーの権限管理にこの仕組みを活用することは可能です。

**注意点**:
- OAuth2/OpenID Connectの実装（Spring Security OAuth2等のライブラリ活用を含む）はプロジェクト責任で行うため、Nablarchとの統合方法（セッションへの認証情報格納タイミング、ハンドラキューへの組み込み方）はプロジェクトで設計する必要があります。
- セッションストアにOAuth2のトークン情報を保持する場合、DBストアを使用すると期限切れセッションが残留するため、定期削除の仕組みが別途必要です。

参照:
- `web-application-feature-details.json:s13`（認証）
- `web-application-feature-details.json:s14`（認可チェック）
- `libraries-session-store.json:s2`、`s8`（セッションストア）
- `handlers-permission-check-handler.json:s4`（認可チェックハンドラ）