Step 5–7: セクション内容をもとに回答を生成し、Verify します。

---

**結論**: スケールアウト環境では **DBストア・HIDDENストア・Redisストア** のいずれかを選択する。HTTPセッションストアはAPサーバごとに状態を持つため、スケールアウト時に追加の工夫（スティッキーセッション等）が必要となり、基本的に選択肢から外れる。

---

**根拠**:

### 各ストアの特徴と比較

| ストア | 保存先 | スケールアウト適性 | 主な特徴 |
|--------|--------|--------------------|----------|
| DBストア | データベース（テーブル） | ◎ | ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能。ヒープ非消費。同一セッションの複数スレッド実行は後勝ち。 |
| HIDDENストア | クライアントサイド（hiddenタグ） | ◎ | APサーバに状態を持たないため自然にスケールアウト対応。複数タブでの画面操作を許容できる。ヒープ非消費。ただし冗長化時は暗号化キーの明示設定が必要（後述）。 |
| HTTPセッションストア | APサーバのヒープ領域 | △ | **APサーバごとに情報を保持するため、スケールアウト時に工夫が必要**。認証情報のような頻繁に使う情報の保持には適しているが、大量データを保存するとヒープ圧迫の恐れあり。 |
| Redisストア | Redis（Lettuceアダプタ） | ◎ | 保存先が異なるだけで特徴はDBストアと同じ。有効期限はRedisのTTL機能で自動管理されるため、期限切れセッション削除用のバッチが不要。 |

### スケールアウト環境での3つの選択肢

**1. DBストア（推奨）**
入力～確認～完了画面間で入力情報を保持する用途（複数タブ不要な場合）や認証情報の保持に適する。

**2. HIDDENストア（複数タブが必要な場合）**
入力情報をクライアントサイドに保持するため、APサーバの台数に依存しない。ただし、APサーバが冗長化されている場合、デフォルトでは**サーバごとに異なる暗号化キーが自動生成される**ため、別サーバでのリクエスト処理時に復号に失敗するケースがある。これを防ぐには、全APサーバで共通の暗号化キーを明示的に設定する必要がある。

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

**3. Redisストア**
DBストアと同じ特性を持ちつつ、セッション有効期限はRedisのTTL機能が自動管理する（有効期限切れキーは自動削除）。DBストアと異なり、期限切れセッションを削除するバッチを別途用意する必要がない。

```shell
# 例: pttlコマンドでセッション有効期限を確認
127.0.0.1:6379> pttl "nablarch.session.8b00bce5-d19f-4f63-b1fe-d14ecca9a4f6"
(integer) 879774
```

### 有効期間の保存先にも注意

セッションの**有効期間**は、デフォルトで `HttpSessionManagedExpiration` を使用するため、HTTPセッションに保存される。DBストアやRedisストアを使用する場合でもこの設定が残ったままだとHTTPセッション依存が残る。完全にステートレスにするには、ハンドラの `expiration` プロパティを `DbManagedExpiration` に差し替えてデータベースに保存するか、Redisストアの場合はRedisのTTL機能を使用する。

---

**注意点**:
- `libraries-stateless-web-app.json` が示す通り、HTTPセッションに依存したままスケールアウトするには「スティッキーセッション」「セッションレプリケーション」「NoSQL保存先変更」のいずれかの対処が必要で、いずれもTwelve-Factor Appの廃棄容易性の点で劣る、またはAPサーバ依存となる。
- 検索条件・検索結果一覧・画面表示項目・エラーメッセージはセッションストアに保存しない（リクエストスコープで受け渡す）。

参照: `libraries-session-store.json:s16`, `libraries-session-store.json:s12`, `libraries-stateless-web-app.json:s1`, `handlers-SessionStoreHandler.json:s9`, `adapters-redisstore-lettuce-adaptor.json:s15`

---