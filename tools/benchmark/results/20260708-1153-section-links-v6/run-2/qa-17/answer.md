**結論**: `SystemRepository.get("コンポーネント名")` を呼び出すことで、登録済みコンポーネントを取得できます。文字列設定値は `SystemRepository.getString()`、真偽値は `SystemRepository.getBoolean()` で取得します。

**根拠**:

コンポーネント定義ファイルで `name` 属性を設定しておき、その名前を指定して取得します。

コンポーネント定義（XML）:
```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

取得例:
```java
// SystemRepository#get を使用して取得する
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結して取得する
Component2 component2 = SystemRepository.get("component.component2");
```

型ごとの取得メソッド:

| メソッド | 用途 |
|---|---|
| `SystemRepository.get(String name)` | 任意の型のコンポーネントを取得（見つからない場合は null） |
| `SystemRepository.getObject(String name)` | コンポーネントを `Object` 型で取得 |
| `SystemRepository.getString(String name)` | 文字列の設定値を取得 |
| `SystemRepository.getBoolean(String name)` | 真偽値の設定値を取得 |

**注意点**:
- システムリポジトリには事前に `SystemRepository.load(new DiContainer(loader))` でDIコンテナの情報を設定しておく必要があります。ただし、この登録処理はNablarchが提供する ServletContextListener の実装クラスや独立型アプリケーションの起動クラスが行うため、通常は個別実装不要です。
- `SystemRepository.get()` で指定した型と登録済みコンポーネントの型が一致しない場合は `ClassCastException` がスローされます。

参照:
- システムリポジトリ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-repository.md
  DIコンテナの情報をシステムリポジトリに設定する
  システムリポジトリからオブジェクトを取得する