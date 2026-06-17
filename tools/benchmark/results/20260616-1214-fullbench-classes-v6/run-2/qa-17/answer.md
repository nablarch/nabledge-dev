**結論**: `SystemRepository.get("コンポーネント名")` を使用して、コンポーネント設定ファイル（XML）に登録されたコンポーネントを取得できます。

**根拠**:

コンポーネント設定ファイルで `name` 属性を付けて定義したコンポーネントを、`SystemRepository.get()` で名前を指定して取得します。

コンポーネント定義（XML）:
```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

取得例（Java）:
```java
// SystemRepository#getを使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結し取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

`SystemRepository.get(String name)` の仕様：
- 型パラメータ `<T>` で返却型を指定する
- コンポーネントが見つからなかった場合は `null` を返す
- 型引数 `<T>` がリポジトリに登録されたコンポーネントの型と一致しない場合は `ClassCastException` がスローされる

文字列設定値を取得する場合は `SystemRepository.getString(String name)`、真偽値は `SystemRepository.getBoolean(String name)` も使用できます。

**注意点**:
- システムリポジトリには事前にDIコンテナの情報が設定されている必要があります（通常はNablarchが提供するServletContextListenerや起動クラスが実施するため、個別実装は不要）。
- DIコンテナで管理されるインスタンスはシングルトンです。プロトタイプと勘違いしてリクエスト固有のデータをコンポーネントに保持すると、複数ユーザー間でデータが混在する重大な不具合が発生します。スレッドセーフな設計が必要です。

参照: `libraries-repository.json:s25`, `javadoc-nablarch-core-repository-SystemRepository.json:s11`