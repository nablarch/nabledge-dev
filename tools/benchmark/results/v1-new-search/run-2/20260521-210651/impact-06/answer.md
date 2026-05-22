Step 5で回答を生成します。

**結論**: スケールアウト環境では **DBストア** または **Redisストア** を選ぶのが適切。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウト時に追加の工夫が必要。HIDDENストアはクライアントサイド保存のため冗長化時に暗号化キーの明示設定が必要。

**根拠**: 各ストアの特徴と選択基準は以下の通り。

---

## 各ストアの特徴

### DBストア（保存先: データベースのテーブル）
- APサーバが停止してもセッション変数の復元が可能（ローリングメンテナンス対応）
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は**後勝ち**（先に保存されたデータは消失）
- **スケールアウト適性**: 高い。DB が共有リソースとなるため APサーバを増減できる

### HIDDENストア（保存先: クライアントサイド / hiddenタグ）
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、セッションデータはそれぞれのスレッドに紐付けて保存される
- **スケールアウト時の注意点**: デフォルトではAPサーバごとに異なる暗号化キーを自動生成するため、冗長化環境では別サーバが復号に失敗するケースがある。全APサーバで共通のキーを明示的に設定する必要がある:

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

### HTTPセッションストア（保存先: APサーバのヒープ領域）
- 認証情報のようなアプリケーション全体で頻繁に使用する情報の保持に適している
- **APサーバ毎に情報を保持するため、スケールアウト時に工夫が必要**
- 通常は以下のいずれかの対処が必要になる:
  1. ロードバランサーでスティッキーセッションを有効にする
  2. APサーバのセッションレプリケーション機能を使用する
  3. APサーバのHTTPセッション保存先をNoSQLにする
- 1・2はTwelve-Factor Appの廃棄容易性の点で劣り、2・3はAPサーバ依存となる
- 大量データを保存するとヒープ領域を圧迫する恐れがある

### Redisストア（保存先: Redis / Lettuceアダプタ使用）
- 特徴はDBストアと同じ（保存先が異なるだけ）
- DBストアと比べた追加メリット:
  - セッション情報を保存するためのテーブルを事前に用意する必要がない
  - 有効期限が切れたセッション情報はRedisが自動削除（削除バッチが不要）
- 本番環境では Sentinel を使用した Master-Replica 構成や Cluster 構成に対応

---

## ストアの選択基準

| 用途 | 推奨ストア |
|------|-----------|
| 入力〜確認〜完了画面間で入力情報を保持（複数タブ不可） | DBストア |
| 入力〜確認〜完了画面間で入力情報を保持（複数タブ許容） | HIDDENストア |
| 認証情報の保持 | DBストアまたはHTTPセッションストア |

## 注意点

- HTTPセッションストアを使用していると、そのままではAPサーバをステートレスにできない。スケールアウトを前提とした設計では、セッションストアの有効期間保存先をDBに変更するなど、HTTPセッション非依存の機能に切り替えることが推奨される。
- HIDDENストアを使用する場合は、冗長化環境では暗号化キーの明示設定が必須。

参照: libraries-session-store.json:s2, libraries-session-store.json:s16, libraries-session-store.json:s12, adapters-redisstore-lettuce-adaptor.json:s5, adapters-redisstore-lettuce-adaptor.json:s6, adapters-redisstore-lettuce-adaptor.json:s15, libraries-stateless-web-app.json:s1, libraries-stateless-web-app.json:s2

---