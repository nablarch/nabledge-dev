Step 4で読み込んだセクション内容をもとに回答を生成します。

---

**結論**: スケールアウト時は **DBストア** または **Redisストア(Lettuce)** を選ぶのが基本方針です。HTTPセッションストアはAPサーバ毎に状態を持つためスケールアウト時に工夫が必要で、HIDDENストアは冗長化時に暗号化キーの明示設定が必要です。

**根拠**:

### 各ストアの特徴とスケールアウト適合性

| ストア | 保存先 | スケールアウト時の注意点 |
|---|---|---|
| **DBストア** | データベース上のテーブル | 問題なし（APサーバ非依存） |
| **Redisストア** | Redis | 問題なし（DBストアと同じ特徴） |
| **HIDDENストア** | クライアントサイド（hiddenタグ） | APサーバ冗長化時に暗号化キーの明示設定が必要 |
| **HTTPセッションストア** | APサーバのヒープ | スケールアウト時に工夫が必要 |

---

### HTTPセッションの問題

HTTPセッションはAPサーバで状態を持つため、そのままではスケールアウトができません。通常、以下のいずれかの対処が必要ですが、いずれも課題があります:

1. ロードバランサーでスティッキーセッションを有効にする
2. APサーバのセッションレプリケーション機能を使用する（廃棄容易性の点で劣る）
3. APサーバのHTTPセッション保存先をNoSQLにする（APサーバ依存）

---

### DBストアの特徴

- データベース上のテーブルに保存
- ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 期限切れのセッション情報は定期的に削除するバッチが必要

---

### Redisストア(Lettuce)アダプタの特徴

DBストアと同じ特性に加えて、以下のメリットがあります:

- セッション情報保存用のテーブルを事前に準備する必要がない
- 有効期限が切れたセッション情報は**自動的に削除**されるため、削除バッチが不要
- Sentinel(Master-Replica構成)やCluster構成にも対応可能

---

### HIDDENストアの注意点

複数タブでの画面操作を許容できるメリットがありますが、**APサーバが冗長化されている場合**は注意が必要です。デフォルトではAPサーバごとに異なる暗号化キーが自動生成されるため、復号に失敗するケースがあります。冗長化環境ではキーを明示的に設定する必要があります:

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv"  value="NOj5OUN+GlyGYTc6FM0+nw==" />
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
| 入力〜確認〜完了画面間のデータ保持（複数タブ不要） | DBストア |
| 入力〜確認〜完了画面間のデータ保持（複数タブ許容） | HIDDENストア（冗長化時はキー明示設定必須） |
| 認証情報の保持 | DBストア または HTTPセッションストア |

**注意点**: HTTPセッションストアをAPサーバのヒープに依存させたままスケールアウトするには工夫が必要です。ステートレスなAPサーバを実現するには、セッションストアの有効期間保存先もHTTPセッションからデータベースに変更する必要があります（デフォルトではHTTPセッションに保存）。

参照: `libraries-session-store.json:s2`, `libraries-session-store.json:s12`, `libraries-session-store.json:s16`, `libraries-stateless-web-app.json:s1`, `adapters-redisstore-lettuce-adaptor.json:s5`, `adapters-redisstore-lettuce-adaptor.json:s6`

---