**結論**: スケールアウト環境では **DBストア** または **Redisストア** を選択するのが適切です。HTTPセッションストアはAPサーバごとに状態を持つためスケールアウト時に別途対処が必要になります。HIDDENストアはクライアントサイド保存なので複数APサーバでも動作しますが、冗長化時は暗号化キーの明示設定が必要です。

---

**根拠**:

### 各ストアの特長一覧

| ストア | 保存先 | スケールアウト適性 | ヒープ影響 |
|--------|--------|-------------------|------------|
| DBストア | DBテーブル | ◎ 適している | なし |
| Redisストア | Redis | ◎ 適している | なし |
| HIDDENストア | クライアント（hiddenタグ） | ○ 使用可能（要注意） | なし |
| HTTPセッションストア | APサーバのヒープ | △ 工夫が必要 | 大量データで圧迫の恐れ |

### DBストア
- ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 複数APサーバ間でDBを共有するためスケールアウト環境でも特別な設定不要

### Redisストア（Lettuceアダプタ使用）
- 特徴はDBストアと同じ（保存先がRedisになるだけ）
- DBストアと違い、セッション情報を保存するテーブルを事前に用意する必要がない
- 有効期限が切れたセッション情報はRedisの仕組みで自動削除されるため、削除用バッチが不要
- Sentinel使用のMaster-Replica構成、Cluster構成にも対応

### HIDDENストア
- クライアントサイド（hiddenタグ）に保存するためAPサーバにセッション状態を持たない
- 複数タブでの画面操作を許容できる
- ただし冗長化構成では**後述の注意点**あり

### HTTPセッションストア
- APサーバのヒープ領域に保存するため、そのままではスケールアウトができない
- 対処方法として以下が考えられるが、いずれも欠点がある：
  1. ロードバランサーでスティッキーセッションを有効にする
  2. APサーバのセッションレプリケーション機能を使用する
  3. APサーバのHTTPセッション保存先をNoSQLにする
  - 1・2はTwelve-Factor Appの廃棄容易性の点で劣り、2・3はAPサーバ依存となる

---

**注意点**:

**HIDDENストアの暗号化キー設定（冗長化時必須）**

HIDDENストアはデフォルトでAPサーバ内で共通の暗号化キーを自動生成しますが、**APサーバが冗長化されている場合、サーバごとに異なるキーを生成するため復号に失敗するケースがあります**。冗長化環境では明示的にキーを統一設定してください：

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

**有効期間の保存先（スケールアウト時のさらなる注意）**

セッションの有効期間はデフォルトでHTTPセッションに保存されています。DBストアを使用していてもHTTPセッションに有効期間が残るため、完全なステートレス化にはDBへの保存先変更も検討してください。

参照: component/libraries/libraries-session-store.json:s16, component/libraries/libraries-session-store.json:s2, component/libraries/libraries-session-store.json:s12, component/libraries/libraries-session-store.json:s17, component/libraries/libraries-stateless-web-app.json:s1, component/adapters/adapters-redisstore-lettuce-adaptor.json:s5, component/adapters/adapters-redisstore-lettuce-adaptor.json:s6, component/adapters/adapters-redisstore-lettuce-adaptor.json:s15