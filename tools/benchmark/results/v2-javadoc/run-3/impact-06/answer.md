必要なセクションを読み終えました。回答を生成します。

---

**結論**: APサーバを複数台にスケールアウトする場合、**DBストア**または**Redisストア**を選択する。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウト時に工夫が必要で、HIDDENストアは入力画面間の一時保持用途に限定した使い方となる。

**根拠**:

### 各ストアの特徴一覧

| ストア | 保存先 | スケールアウト適性 | 用途 |
|--------|--------|-------------------|------|
| DBストア | DBテーブル | ○ 対応済み | 認証情報、入力情報保持（複数タブ不可） |
| HIDDENストア | クライアントサイド | △ 要暗号化キー設定 | 入力～確認～完了画面間（複数タブ可） |
| HTTPセッションストア | APサーバのヒープ | × 工夫が必要 | 認証情報（スケールアウト非推奨） |
| Redisストア | Redis | ○ 対応済み | DBストアと同等用途 |

---

#### DBストア
データベース上のテーブルに保存する。

- APサーバが停止してもセッション変数の復元が可能（ローリングメンテナンス対応）
- APサーバのヒープ領域を圧迫しない
- 同一セッションの複数スレッド実行時は後勝ち（先のデータは消失）
- 期限切れセッション情報を削除するバッチが別途必要

#### HIDDENストア
`hidden` タグでクライアントサイドに保持する。

- 複数タブでの画面操作を許容できる
- APサーバが冗長化されている場合、**暗号化キーを明示的に設定する必要がある**。デフォルトはAPサーバ内で自動生成されたキーを使用するため、APサーバごとに異なるキーとなり復号に失敗するケースがある。

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv" value="NOj5OUN+GlyGYTc6FM0+nw==" />
        </component>
      </property>
    </component>
  </property>
</component>
```

#### HTTPセッションストア
APサーバのヒープ領域に保存する。

- APサーバ毎に情報を保持するため、**スケールアウト時に工夫が必要**
- 大量データを保存するとヒープ領域を圧迫するおそれがある
- 認証情報のようなアプリケーション全体で頻繁に使用する情報の保持に適しているが、スケールアウト構成には不向き

#### Redisストア（Lettuceアダプタ）
Redisに保存する。

- 保存先が異なるだけで**特徴はDBストアと同じ**
- セッション情報保存用テーブルを事前に用意する必要がない
- 有効期限が切れたセッション情報はRedisが自動削除するため、削除バッチが不要

---

### スケールアウトのための追加設定

セッションストアの**有効期間はデフォルトではHTTPセッションに保存される**。DBストアを選択してもこのデフォルト設定のままでは有効期間の管理にHTTPセッションが使われてしまう。APサーバをステートレスにするには、`SessionStoreHandler` の `expiration` プロパティを `DbManagedExpiration` に差し替えて有効期間をデータベースに保存する必要がある。

```xml
<component name="sessionStoreHandler" class="nablarch.common.web.session.SessionStoreHandler">
  <property name="expiration" ref="expiration" />
  <!-- その他のプロパティは省略 -->
</component>

<component name="expiration" class="nablarch.common.web.session.DbManagedExpiration">
  <property name="dbManager">
    <component class="nablarch.core.db.transaction.SimpleDbTransactionManager">
      <property name="dbTransactionName" value="expirationTransaction"/>
    </component>
  </property>
</component>
```

Redisストアを使用する場合は、RedisネイティブのTTL機能で有効期限が管理されるためこの設定は不要。

**注意点**:
- HTTPセッションストアを使った認証情報の保持は、スケールアウト構成には向かない。認証情報はDBストアを推奨する。
- `SESSION_OBJECT` カラムは有効期間をDBで管理する場合にNull許容で定義する必要がある（ログアウト時にNullレコードが登録される）。

参照: `component/libraries/libraries-session-store.json:s16`, `component/libraries/libraries-session-store.json:s17`, `component/libraries/libraries-stateless-web-app.json:s1`, `component/libraries/libraries-session-store.json:s12`, `component/adapters/adapters-redisstore-lettuce-adaptor.json:s15`, `component/handlers/handlers-SessionStoreHandler.json:s9`

---