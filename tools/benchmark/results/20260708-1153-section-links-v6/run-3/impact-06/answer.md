**結論:** スケールアウト環境では **DBストア** または **Redisストア** を選ぶのが基本方針です。HTTPセッションストアはAPサーバごとに状態を持つためそのままではスケールアウトできず、HIDDENストアはクライアントサイド保存のためサーバ状態に依存しませんが、冗長化時に暗号化キーの明示的な設定が必要です。

---

**根拠:**

**各ストアの特徴一覧**

| ストア | 保存先 | スケールアウト | ヒープ | 並行アクセス |
|--------|--------|--------------|--------|------------|
| DBストア | DBテーブル | ◎ そのまま可 | 圧迫しない | 後勝ち（先のデータ消失） |
| HIDDENストア | クライアント（hidden タグ） | ◎ ただし要設定 | 圧迫しない | スレッドごとに独立保存 |
| HTTPセッションストア | APサーバのヒープ | △ 工夫が必要 | 大量データで圧迫リスク | 後勝ち（先のデータ消失） |
| Redisストア | Redis | ◎ そのまま可 | 圧迫しない | DBストアと同じ |

**DBストア**

DBテーブルに保存するため、APサーバが停止してもセッション変数を復元できます。APサーバのヒープを圧迫しません。期限切れセッションを削除するバッチが別途必要です。

**HIDDENストア**

hidden タグを使ってクライアントサイドで保持するため、APサーバに状態を持ちません。複数タブでの操作を許容できます。ただし、**APサーバが冗長化されている場合は暗号化キーを明示的に設定する必要があります**。デフォルトでは各APサーバが独自にキーを自動生成するため、別サーバで復号に失敗するケースがあります。

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

**HTTPセッションストア**

APサーバのヒープに保存するため、APサーバ毎に情報を保持します。スケールアウトを行う際に工夫が必要となります。具体的には①スティッキーセッション、②APサーバのセッションレプリケーション、③HTTPセッション保存先をNoSQLに変更するといった対処が必要ですが、①②は廃棄容易性の観点で劣り、②③はAPサーバ依存となります。

**Redisストア**（アダプタで追加）

保存先が異なるだけで特徴はDBストアと同じです。DBストアと比べてセッション情報保存用のテーブルを事前に用意する必要がなく、有効期限切れのセッション情報はRedisが自動削除するためバッチも不要です。

**注意点:**

- **有効期間の管理**: デフォルトではセッションの有効期間はHTTPセッションに保存されます。完全にAPサーバをステートレスにするには、`DbManagedExpiration` に差し替えてDBに保存するか、Redisストアを使用してRedisに保存する設定が必要です。
- DBストア・HTTPセッションストアは同一セッションへの並行アクセス時に後勝ちとなるため（先に保存されたデータは消失）、設計上の考慮が必要です。

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
- Redisストア(Lettuce)アダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-redisstore-lettuce-adaptor.md
  有効期限の管理方法