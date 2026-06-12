Step 5: 回答を生成します。

---

**結論**: 入力→確認→完了画面間のセッション変数保持は、**複数タブでの操作を許容しない**場合は**DBストア**、**許容する**場合は**HIDDENストア**を使用する。

---

**根拠**:

公式の選択基準は以下の通り。

| 用途 | セッションストア |
|---|---|
| 入力→確認→完了（複数タブ **不可**） | DBストア |
| 入力→確認→完了（複数タブ **可**） | HIDDENストア |

**DBストアの特徴**:
- セッション変数をデータベース上のテーブル（`USER_SESSION`）に保存
- ローリングメンテナンスでサーバが停止してもセッション変数を復元可能
- 同一セッションを複数スレッドが処理した場合は**後勝ち**（先のデータは消失）

**HIDDENストアの特徴**:
- クライアントサイドにhiddenタグでセッション変数を引き回す
- 複数タブでの操作を許容できる（各タブのセッション変数が独立して保存される）
- JSPに `<n:hiddenStore>` タグを配置する必要がある

```jsp
<n:form>
  <!--
    name属性にはHiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

セッションストアに格納するオブジェクトは**FormではなくEntity**にすること。FormはバリデーションME前の信頼できない値を含む可能性があるため、セキュリティリスクが高まる。

---

**注意点**:

**HIDDENストア使用時のハンドラ配置制約**:
- `SessionStoreHandler` は **マルチパートリクエストハンドラより後ろ**に配置すること（リクエストパラメータにアクセスするため）
- **内部フォーワードハンドラより前**に配置すること（後ろに配置すると内部フォワード時に最新のセッション変数を取得できない）

**HIDDENストア使用時の冗長構成**:
- デフォルトの暗号化キーはAPサーバごとに自動生成されるため、冗長化環境では**別サーバで復号に失敗**するケースがある。冗長構成では明示的にAESキーを設定すること。

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

**改竄検知時の動作の違い**:
- HIDDENストア: 改竄検知時にHTTP 400 (`HttpErrorResponse`) を送出
- DBストア等その他のストア: 復号処理時の例外をそのまま送出

参照: libraries-session-store.json:s16, libraries-session-store.json:s9, libraries-session-store.json:s12, handlers-SessionStoreHandler.json:s3, handlers-SessionStoreHandler.json:s6

---