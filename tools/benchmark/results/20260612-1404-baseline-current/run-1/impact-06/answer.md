**結論**: スケールアウト環境では**DBストア**または**Redisストア**を選ぶべきです。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウト時に工夫が必要であり、HIDDENストアはサーバ間共有の問題はないものの用途が入力データの画面間受け渡しに限定されます。

**根拠**:

Nablarchが提供するセッション変数の保存先は標準3種類＋Redisアダプタの計4種類です。

---

**① DBストア（データベース上のテーブル）**

| 特長 | 内容 |
|---|---|
| スケールアウト | ✅ 全APサーバが同一DBを参照するため、共有が容易 |
| APサーバ停止時 | ✅ ローリングメンテナンス等でAPサーバが停止しても復元可能 |
| ヒープ消費 | ✅ APサーバのヒープを圧迫しない |
| 並行アクセス | ⚠ 同一セッションが複数スレッドで処理された場合は後勝ち（先のデータが消失する） |
| 運用 | ⚠ 有効期限切れセッション削除バッチが必要 |

有効期間をデフォルトのHTTPセッションではなくDBに保存する設定（`DbManagedExpiration`）にすると、HTTPセッション非依存でのスケールアウトが実現できます。

---

**② HIDDENストア（クライアントサイド）**

| 特長 | 内容 |
|---|---|
| スケールアウト | ✅ クライアント側に保存するためAPサーバ間の共有不要 |
| 用途 | 入力～確認～完了画面間での入力データ保持（複数タブ許容時） |
| ヒープ消費 | ✅ APサーバのヒープを圧迫しない |
| 注意 | サーバが冗長化されている場合、暗号化キーを明示的に設定しないと復号失敗が起きる |

スケールアウト環境でHIDDENストアを使用する場合は、APサーバごとに自動生成される暗号化キーではなく、**全APサーバで共通のキーを明示設定**することが必要です：

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

**③ HTTPセッションストア（APサーバのヒープ領域）**

| 特長 | 内容 |
|---|---|
| スケールアウト | ❌ APサーバ毎に情報を保持するため、スケールアウト時に工夫が必要 |
| 用途 | 認証情報等、アプリ全体で頻繁に使用する情報の保持に適している |
| ヒープ消費 | ⚠ 大量データを保存するとヒープを圧迫する恐れがある |

スケールアウトするには、ロードバランサーのスティッキーセッション、セッションレプリケーション、またはHTTPセッション保存先のNoSQL化が必要ですが、これらはいずれも廃棄容易性の点で劣るかAPサーバ依存となります。

---

**④ Redisストア（Lettuceアダプタ）**

| 特長 | 内容 |
|---|---|
| スケールアウト | ✅ DBストアと同様の特徴（保存先が異なるだけ） |
| テーブル準備 | ✅ 事前にテーブルを用意する必要がない |
| 有効期限管理 | ✅ Redisの有効期限機能を使用するため、削除バッチが不要 |
| 構成 | 単一・Master-Replica・Cluster構成に対応 |

---

**選択基準まとめ**

| 用途 | 推奨ストア |
|---|---|
| 入力データの画面間保持（複数タブ許容しない）| DBストア |
| 入力データの画面間保持（複数タブ許容する）| HIDDENストア（暗号化キー共通設定必須） |
| 認証情報の保持 | DBストアまたはHTTPセッションストア |
| スケールアウト環境全般 | DBストアまたはRedisストア |

**注意点**: セッションストアのデフォルト有効期間保存先はHTTPセッションです。完全なステートレス化（HTTPセッション非依存）を実現するには、`DbManagedExpiration` または Redisストアを使用して有効期間もHTTPセッション外に保存する設定が必要です。

参照: libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-stateless-web-app.json:s1, adapters-redisstore-lettuce-adaptor.json:s15