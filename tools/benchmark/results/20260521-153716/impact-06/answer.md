Step 5: 回答を生成します。

**結論**: スケールアウト構成では **DBストア** または **Redisストア** を選ぶ。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウト時に問題が生じる。HIDDENストアも使用可能だが、冗長化時に暗号化キーの明示設定が必要となる。

---

Step 6: 検証を実施します。

抽出するNablarch固有クレーム:
1. 「DBストアはAPサーバ停止時もセッション変数を復元できる」→ s16に直接記述あり ✓
2. 「HTTPセッションストアはスケールアウト時に工夫が必要」→ s16に直接記述あり ✓
3. 「HIDDENストアは冗長化時に暗号化キーの明示設定が必要」→ s12に直接記述あり ✓
4. 「RedisストアはDBストアと同じ特徴」→ s16のTipに直接記述あり ✓
5. 「Redisは期限切れセッションを自動削除しバッチ不要」→ s15に直接記述あり ✓
6. 「DBストアは定期的な削除バッチが必要」→ s8のTipに直接記述あり ✓
7. 「有効期間はデフォルトでHTTPセッションに保存される」→ s17に直接記述あり ✓
8. 「DbManagedExpirationで有効期間をDBに保存できる」→ s9に直接記述あり ✓

**verify_result = PASS**

---

以下が最終回答です。

---

**結論**: スケールアウト構成では **DBストア** または **Redisストア** を選ぶ。HTTPセッションストアはAPサーバ毎に情報を保持するためスケールアウトに工夫が必要となる。HIDDENストアも利用可能だが、AP冗長化時に暗号化キーの明示設定が必要。

**根拠**:

### 各ストアの特徴と比較

| ストア | 保存先 | スケールアウト適性 | 特徴 |
|--------|--------|-------------------|------|
| **DBストア** | データベース上のテーブル | ✅ 適している | ローリングメンテナンス等でAPサーバが停止してもセッション変数を復元可能。ヒープ領域を圧迫しない。同一セッションの並行処理は後勝ち。 |
| **Redisストア** | Redis | ✅ 適している | 保存先が異なるだけでDBストアと同じ特徴。Redisの有効期限機能により期限切れセッションが自動削除されるため、削除バッチが不要。 |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | ⚠️ 条件付き | AP冗長化時は暗号化/復号キーを明示設定しないとAPサーバごとに異なるキーが生成されて復号失敗になる。複数タブ操作を許容できる。ヒープを圧迫しない。 |
| **HTTPセッションストア** | APサーバのヒープ領域 | ❌ 不向き | APサーバ毎に情報を保持するためスケールアウト時に工夫が必要。大量データでヒープを圧迫するリスクもある。 |

### HIDDENストアを冗長化環境で使う場合の設定

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

### セッション有効期間の保存先にも注意

セッションの有効期間はデフォルトでHTTPセッションに保存される。スケールアウト時は `DbManagedExpiration` に切り替えてデータベースに保存する必要がある。

```
handlers-SessionStoreHandler の expiration プロパティ
→ DbManagedExpiration に差し替え
```

**注意点**:
- DBストアを使う場合、`USER_SESSION` テーブルの作成が必要。また期限切れセッションを定期的に削除するバッチも別途必要となる（Redisストアはこのバッチが不要）。
- デフォルトでHTTPセッションに依存している機能は「セッションストア」以外にも「2重サブミット防止」「スレッドコンテキスト変数管理ハンドラ」「HTTPリライトハンドラ」「hidden暗号化」があるため、スケールアウト対応時はこれらも合わせて確認が必要。

参照: `libraries-session-store.json:s16`, `libraries-session-store.json:s12`, `libraries-stateless-web-app.json:s1`, `libraries-stateless-web-app.json:s2`, `adapters-redisstore-lettuce-adaptor.json:s15`, `handlers-SessionStoreHandler.json:s9`, `libraries-session-store.json:s17`, `libraries-session-store.json:s8`

---