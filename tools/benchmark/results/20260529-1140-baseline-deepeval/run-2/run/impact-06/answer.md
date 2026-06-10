**結論**: APサーバを複数台にスケールアウトする場合、**DBストア**または**Redisストア(Lettuce)アダプタ**を選択するのが適切です。HTTPセッションストアはそのままではスケールアウトに対応できません。HIDDENストアはクライアントサイドに保存するため技術的にはスケールアウト可能ですが、冗長化環境では暗号化キーの明示的な設定が必要です。

---

**根拠**: 各ストアの特徴と選択基準

#### DBストア（保存先：データベース上のテーブル）

- ローリングメンテナンス等でAPサーバが停止した場合でも**セッション変数の復元が可能**
- APサーバのヒープ領域を圧迫しない
- APサーバ間でセッションを共有できるため、スケールアウトに対応可能
- 同一セッションの処理が複数スレッドで実行された場合、**後勝ちとなる**（先に保存されたセッションのデータは消失する）

#### Redisストア（Lettuce）アダプタ（保存先：Redis）

- **特徴はDBストアと同じ**（保存先が異なるだけ）
- セッション情報を保存するためのテーブルを事前に用意する必要がない
- **有効期限が切れたセッション情報は自動的に削除**されるため、削除バッチを用意する必要がない
- Sentinel（Master-Replica構成）やCluster構成のRedisに接続可能

#### HIDDENストア（保存先：クライアントサイド）

- `hidden`タグを使用して画面間でセッション変数を引き回す
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- ⚠️ **冗長化環境での注意点**: デフォルトではAPサーバごとに異なる暗号化キーを自動生成するため、**復号に失敗するケースがある**。冗長化している場合は暗号化キーを明示的に統一する必要がある：

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

#### HTTPセッションストア（保存先：APサーバのヒープ領域）

- 認証情報のようなアプリケーション全体で頻繁に使用する情報の保持に適している
- ⚠️ **APサーバ毎に情報を保持するため、スケールアウトを行う際に工夫が必要**
- 一般的な対処法：(1) ロードバランサーでスティッキーセッションを有効にする、(2) APサーバのセッションレプリケーション機能を使用する、(3) APサーバのHTTPセッション保存先をNoSQLにする。ただし (1)(2) は廃棄容易性の点で劣り、(2)(3) はAPサーバ依存となる

---

**注意点**

- セッションの有効期間はデフォルトでHTTPセッションに保存されている。スケールアウト構成でDBストアを使用する場合、**有効期間もデータベースに保存する設定**（`DbManagedExpiration`）に切り替えることで、完全にHTTPセッションへの依存をなくすことができる
- Redisストアを使用する場合は有効期限をRedisのTTL機能で管理するため、この問題は発生しない

---

| ストア | スケールアウト対応 | APサーバ停止時のセッション復元 | ヒープ圧迫 |
|---|---|---|---|
| DBストア | ✅ | ✅ | なし |
| Redisストア | ✅ | ✅ | なし |
| HIDDENストア | ✅（要暗号化キー統一） | ✅ | なし |
| HTTPセッションストア | ❌（要工夫） | ❌ | あり |

参照: libraries-session-store.json:s16, libraries-session-store.json:s17, libraries-session-store.json:s2, libraries-session-store.json:s12, adapters-redisstore-lettuce-adaptor.json:s5, adapters-redisstore-lettuce-adaptor.json:s6, adapters-redisstore-lettuce-adaptor.json:s15, libraries-stateless-web-app.json:s1

---