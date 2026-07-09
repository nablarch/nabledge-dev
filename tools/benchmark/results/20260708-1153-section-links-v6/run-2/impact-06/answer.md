**結論**: スケールアウト時はDBストアまたはRedisストアを選択する。HTTPセッションストアはAPサーバごとに状態を持つためスケールアウトには不向きで使用する場合に追加の工夫が必要となる。HIDDENストアはクライアントサイドに保存するため基本的にスケールアウト対応だが、デフォルトの暗号化設定では冗長化時に復号失敗が起きるため注意が必要。

---

**根拠**:

### 各ストアの特徴と選択基準

| ストア | 保存先 | スケールアウト適合性 | 主な特徴 |
|---|---|---|---|
| DBストア | データベース上のテーブル | ◎ | ローリングメンテナンス等でサーバ停止後もセッション変数の復元が可能。ヒープ圧迫なし。複数スレッド同時実行時は後勝ち |
| HIDDENストア | クライアントサイド（hiddenタグ経由） | △（要設定） | 複数タブの画面操作を許容できる。ヒープ圧迫なし。デフォルトの暗号化キーはサーバごとに異なるため冗長化時に復号失敗のリスクあり |
| HTTPセッションストア | APサーバのヒープ領域 | △（要工夫） | APサーバ毎に情報を保持するためスケールアウト時に工夫が必要 |
| Redisストア（Lettuceアダプタ） | Redis | ◎ | DBストアと同様の特徴。有効期限切れセッションはRedisが自動削除（バッチ不要）。Sentinel/Cluster構成に対応 |

---

### スケールアウト時にHTTPセッションを使うと何が問題になるか

HTTPセッションはAPサーバで状態を持つため、スケールアウトには以下いずれかの対処が必要となる。

1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する
3. APサーバのHTTPセッション保存先をNoSQLにする

1・2は [Twelve-Factor App](https://12factor.net/ja/) の廃棄容易性の点で劣り、2・3はAPサーバ依存となる。

---

### 有効期間の管理とステートレス化

セッションの有効期間は**デフォルトではHTTPセッションに保存**される。DBストアを使っていても有効期間がHTTPセッションに残るため、APサーバを完全にステートレスにするには `SessionStoreHandler` の `expiration` プロパティを `DbManagedExpiration` に変更する必要がある。

```xml
<component name="sessionStoreHandler" class="nablarch.common.web.session.SessionStoreHandler">
  <!-- その他の設定は省略 -->
  <property name="expiration" ref="expiration" />
</component>

<component name="expiration" class="nablarch.common.web.session.DbManagedExpiration">
  <property name="dbManager">
    <component class="nablarch.core.db.transaction.SimpleDbTransactionManager">
      <property name="dbTransactionName" value="expirationTransaction"/>
    </component>
  </property>
</component>
```

---

### HIDDENストアで冗長化する場合の注意

デフォルトではAPサーバごとに異なる暗号化キーが自動生成されるため、異なるサーバで復号に失敗するケースがある。冗長化する場合は暗号化キーを明示的に統一する必要がある。

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

---

### 用途別の選択基準

| 用途 | 推奨ストア |
|---|---|
| 入力～確認～完了画面の入力情報保持（複数タブ不許容） | DBストア |
| 入力～確認～完了画面の入力情報保持（複数タブ許容） | HIDDENストア |
| 認証情報の保持 | DBストアまたはHTTPセッションストア |

---

**注意点**:
- DBストアおよびHTTPセッションストアは複数スレッドで同一セッションが同時処理された場合、後勝ちになる（先に保存されたデータが消失する）
- RedisストアはDBストアを選択した場合と比較して、セッション情報保存用のテーブルを事前に用意する必要がない点と、有効期限切れセッションを削除するためのバッチが不要な点がメリット
- Redisストアの Redis 構成（単一・Master-Replica・Cluster）は環境設定値 `nablarch.lettuce.clientType` で切り替えられる

---

参照:
- セッションストア
  .claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md
  セッション変数の保存先を選択できる
  セッションストアの特長と選択基準
  HIDDENストアの暗号化設定をカスタマイズする
  有効期間の管理方法
- Webアプリケーションをステートレスにする
  .claude/skills/nabledge-6/docs/component/libraries/libraries-stateless-web-app.md
  基本的な考え方
  HTTPセッションに依存している機能
- セッション変数保存ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-SessionStoreHandler.md
  有効期間をデータベースに保存する
- Redisストア(Lettuce)アダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md
  Redis の構成に合わせて設定する
  構成ごとに用意されたクライアントクラス
  有効期限の管理方法