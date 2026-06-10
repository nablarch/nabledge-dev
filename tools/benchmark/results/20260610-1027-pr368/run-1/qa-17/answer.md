**結論**: `SystemRepository.get(name)` メソッドを使い、コンポーネント設定ファイルで指定した `name` 属性の値を引数に渡してコンポーネントを取得します。

**根拠**:

コンポーネント設定ファイル（XML）でコンポーネントを定義します。

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component">
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

アプリケーションコードから以下のように取得します。

```java
// SystemRepository#get を使用して取得する
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストした component は、親の名前と自身の名前を "." で連結して取得する
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get(String name)` の仕様：
- 指定した名前のコンポーネントを返す
- コンポーネントが見つからなかった場合は `null` を返す
- 型引数 `<T>` と登録されたコンポーネントの型が一致しない場合は `ClassCastException` がスローされる

文字列設定値を取得したい場合は `SystemRepository.getString(name)` も使えます。

**注意点**:
- `SystemRepository.get()` を呼び出す前に、事前にDIコンテナの情報をシステムリポジトリに設定しておく必要があります（通常はNablarchが提供する `ServletContextListener` の実装クラスや起動クラスが自動的に行います）。
- DIコンテナで管理されるインスタンスはシングルトンです。取得のたびに新しいインスタンスが生成されるわけではありません。

参照: libraries-repository.json:s25, libraries-repository.json:s24, javadoc-nablarch-core-repository-SystemRepository.json:s11