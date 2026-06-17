**結論**: `SystemRepository.get("コンポーネント名")` を使って、コンポーネント設定ファイルの `component` 要素に設定した `name` 属性の値を指定することでコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイル (xml) でコンポーネントに名前を付けて登録します:

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

**注意点**:
- `SystemRepository.get()` で取得できるオブジェクトは**シングルトン**です。取得のたびに新しいインスタンスが生成されるわけではありません。プロトタイプと勘違いすると、あるリクエストでユーザAの入力値をコンポーネントに設定し、別のユーザBのリクエストでその値を使用するなどの重大な不具合を起こす危険があります。
- アプリケーション内のどこからでも取得できるよう、事前に `SystemRepository.load()` でDIコンテナ情報が設定されている必要がありますが、この処理はNablarchが提供するServletContextListenerや独立型アプリケーションの起動クラスが行うため、通常は個別に実装する必要はありません。

参照: libraries-repository.json:s25, libraries-repository.json:s24