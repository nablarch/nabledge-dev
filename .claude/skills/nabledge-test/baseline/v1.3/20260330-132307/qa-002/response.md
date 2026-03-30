**結論**: `ListSearchInfo`を継承したFormクラスと`DbAccessSupport`の`search`メソッド、そして`nbs:listSearchResult`タグを組み合わせることでページング付き一覧検索を実装できます。

ListSearchInfo継承フォーム → DbAccessSupport#search呼び出し → nbs:listSearchResultタグで表示。ページングはフレームワークが自動処理。

参照: `biz-samples-03_ListSearchResult.json#s3`, `web-application-03_listSearch.json#s1`
