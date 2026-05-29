セクション内容をもとに回答を生成します。

---

**結論**: スケールアウト環境では **DBストア** または **Redisストア** を選ぶのが基本方針です。HTTPセッションストアはAPサーバごとに状態を持つため工夫が必要で、HIDDENストアは暗号化キーを明示的に統一する必要があります。

---

**根拠**

## 各ストアの特徴と選択基準

### 1. DBストア（保存先: データベース）

- ローリングメンテナンス等でAPサーバが停止しても、セッション変数を復元できる
- APサーバのヒープ領域を圧迫しない
- 同一セッションへの複数スレッド同時アクセスは**後勝ち**（先のデータは消失）
- **スケールアウトに最適**。どのAPサーバがリクエストを受けても同じDBを参照するため、追加設定不要

### 2. HIDDENストア（保存先: クライアントサイド hidden タグ）

- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 同一セッションへの複数スレッド同時アクセスは、スレッドごとにデータが保存される
- **スケールアウト時の注意**: APサーバが冗長化されている場合、サーバごとに異なる暗号化キーを自動生成するため、復号に失敗するケースがある。この場合は暗号化/復号キーを**全サーバで明示的に統一して設定**する必要がある

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

### 3. HTTPセッションストア（保存先: APサーバのヒープ）

- 認証情報のようにアプリケーション全体で頻繁に使用する情報の保持に適している
- **APサーバごとに情報を保持するため、スケールアウトを行う際に工夫が必要**
- 大量データを保存するとヒープ領域を圧迫する恐れがある
- 同一セッションへの複数スレッド同時アクセスは**後勝ち**

スケールアウトで使う場合、従来は以下の対処が必要だった（Twelve-Factor App の廃棄容易性の観点で劣る/APサーバ依存になる）:
1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使う
3. APサーバのHTTPセッション保存先をNoSQLにする

Nablarchでは代わりに「セッションの有効期限保存先をDBに変更」することで、HTTPセッション依存を排除できる（`DbManagedExpiration` への切り替え）。

### 4. Redisストア（Lettuce アダプタ使用）

- **特徴はDBストアと同じ**（保存先がRedisになるだけ）
- Redisの有効期限（TTL）の仕組みを使って自動削除されるため、**有効期限切れセッションを削除するバッチが不要**
- Redis構成に合わせて3種類のクライアントクラスを選択できる:
  - `LettuceSimpleRedisClient`: 単一Redisインスタンスへの直接接続
  - `LettuceMasterReplicaRedisClient`: Master-Replica構成（Sentinel経由も対応）
  - `LettuceClusterRedisClient`: Cluster構成

Redisでのセッション保存キー形式:
```shell
127.0.0.1:6379> keys *
1) "nablarch.session.8b00bce5-d19f-4f63-b1fe-d14ecca9a4f6"
```

---

## 用途別の選択基準

| 用途 | 推奨ストア |
|------|-----------|
| 入力〜確認〜完了間の入力情報保持（複数タブ禁止） | DBストア |
| 入力〜確認〜完了間の入力情報保持（複数タブ許容） | HIDDENストア |
| 認証情報の保持 | DBストア または HTTPセッションストア |

---

**注意点**

- **セッションの有効期間はデフォルトでHTTPセッションに保存される**。スケールアウト環境でHTTPセッション依存を完全になくすには、有効期間の保存先もDBに変更する必要がある（`DbManagedExpiration` に切り替え）
- 検索条件・検索結果一覧・画面表示項目・エラーメッセージはセッションストアに保存しないことが推奨されている
- HTTPセッションに依存している機能はセッションストア以外にも複数あるため（二重サブミット防止、スレッドコンテキスト変数管理ハンドラ等）、完全なステートレス化には各機能の切り替えが必要

参照: `libraries-session-store.json:s16`, `libraries-session-store.json:s12`, `libraries-stateless-web-app.json:s1`, `adapters-redisstore-lettuce-adaptor.json:s6`, `adapters-redisstore-lettuce-adaptor.json:s15`

---