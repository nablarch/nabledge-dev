**結論**: `SystemRepository.get("コンポーネント名")` を呼び出すことで、コンポーネント設定ファイル(xml)に定義した `name` 属性の値を指定してオブジェクトを取得できます。

**根拠**:

コンポーネント設定ファイルに以下のように定義します：

```xml
<component name="sampleComponent" class="sample.SampleComponent" />

<component name="component" class="sample.Component" >
  <property name="component2">
    <component name="component2" class="sample.Component2" />
  </property>
</component>
```

アプリケーションコードからの取得例：

```java
// SystemRepository#get を使用して取得する。
SampleComponent sample = SystemRepository.get("sampleComponent");

// ネストしたcomponentは、親の名前と自身の名前を"."で連結して取得する。
Component2 component2 = SystemRepository.get("component.component2");
```

**事前準備**: システムリポジトリには事前にDIコンテナの情報をロードしておく必要があります。通常はNablarchが提供するServletContextListenerや独立型アプリケーションの起動クラスが自動的に行うため、個別実装は不要です。手動でロードする場合の例：

```java
XmlComponentDefinitionLoader loader
    = new XmlComponentDefinitionLoader("web-boot.xml");
SystemRepository.load(new DiContainer(loader));
```

**注意点**: 取得されるオブジェクトは **シングルトン** です。取得のたびに新しいインスタンスが生成されるわけではないため、リクエスト固有の情報をコンポーネントに保持しないでください。マルチスレッド環境で複数リクエストが同じインスタンスを共有するため、ユーザーAの入力値が別のユーザーBのリクエストで参照されるような重大な不具合につながります。

参照: `libraries-repository.json:s25`, `libraries-repository.json:s24`, `libraries-repository.json:s7`