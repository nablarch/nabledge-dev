**結論**: `SystemRepository.get("コンポーネント名")` を使用して、XMLのコンポーネント設定ファイルに定義したコンポーネントを取得できます。

**根拠**:

コンポーネント定義（XMLファイル）:
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
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get()` の引数には、XMLの `component` 要素の `name` 属性に設定した値を指定します。

**注意点**:
- 取得できるのはシングルトンのオブジェクトです。取得するたびに新しいインスタンスが生成されるわけではありません。
- システムリポジトリには事前にDIコンテナの情報が設定されている必要がありますが、Nablarchが提供する `ServletContextListener` 実装クラスや独立型アプリケーションの起動クラスが自動的に行うため、通常は個別実装不要です。
- ネストして定義したコンポーネントも、リポジトリ上はグローバル領域に保持されるため、`"親名.子名"` の形式で取得できます。

参照: libraries-repository.json:s25, libraries-repository.json:s24