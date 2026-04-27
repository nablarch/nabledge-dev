# タスク: catalog.json の sources 消失バグ修正

## 問題

`catalog.json`の`sources`フィールドが空（`[]`）になっている。

**原因**: `step2_classify.py`がcatalog.jsonを書き出す際に、全フィールドをゼロから組み立てて丸ごと上書きしている。

**影響**:
- `setup.sh`がcatalog.jsonの`sources`を読んでリポジトリをcloneする → 0件cloneされる
- `knowledge_meta.py`の差分検知が動かない → 差分リジェネ不可

## 前提

- ブランチ: `153-verify-r2-fabrication`（`origin/main`にリベース済み）
- 作業ディレクトリ: `tools/knowledge-creator/`
- ベースライン: 154 passed, 7 skipped
- **実行順**: Task 1 → 2 → 3 → 4 → 5 → 6（順序厳守）

---

## Task 1: catalog.jsonのsources復元 + setup.sh実行

sourcesが空だと`setup.sh`がリポジトリをcloneできず、以降の全タスク（テスト含む）が動かない。最初に復元する。

### Step 1-1: sources復元

```bash
cd tools/knowledge-creator
python3 -c "
import json
catalog = json.load(open('.cache/v6/catalog.json'))
catalog['sources'] = [
    {
        'repo': 'https://github.com/nablarch/nablarch-document',
        'branch': 'main',
        'commit': 'eb1ea136c20e325ebbd4b15ba552fbbc47169bec'
    },
    {
        'repo': 'https://github.com/Fintan-contents/nablarch-system-development-guide',
        'branch': 'main',
        'commit': '3c34cc3a75da0c4ce85620d8002f1c004f2bb753'
    }
]
with open('.cache/v6/catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
print('OK')
"
```

### Step 1-2: ユーザーにsetup.sh実行を依頼

以下のメッセージをユーザーに伝えて、setup.shの実行を依頼する:

```
catalog.jsonのsourcesを復元しました。
リポジトリのクローンが必要なため、setup.shの実行をお願いします。

cd /path/to/nabledge-dev
bash setup.sh

完了したら教えてください。
```

**setup.sh完了を確認してからTask 2に進む。**

### 検証

```bash
cd tools/knowledge-creator
python3 -c "
import json, os
catalog = json.load(open('.cache/v6/catalog.json'))
assert len(catalog['sources']) == 2
print(f'sources: {len(catalog[\"sources\"])} repos')
# .lw がcloneされていること
assert os.path.isdir('../../.lw/nab-official/v6/nablarch-document'), '.lw not cloned'
assert os.path.isdir('../../.lw/nab-official/v6/nablarch-system-development-guide'), '.lw not cloned'
print('OK')
"
```

---

## Task 2: テスト作成

**ファイル**: `tests/ut/test_catalog_sources.py` を新規作成

```python
"""Test that step2_classify preserves catalog.json fields other than files."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import load_json, write_json


class TestStep2PreservesCatalogFields:
    """step2 must only update 'files', preserving all other fields."""

    def test_sources_preserved_after_step2(self, ctx):
        """sources field is not overwritten by step2."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-03-08T01:00:00+09:00",
            "sources": [
                {"repo": "https://github.com/nablarch/nablarch-document",
                 "branch": "main", "commit": "abc123"},
                {"repo": "https://github.com/Fintan-contents/nablarch-system-development-guide",
                 "branch": "main", "commit": "def456"},
            ],
            "files": []
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        assert len(catalog["sources"]) == 2
        assert catalog["sources"][0]["repo"] == "https://github.com/nablarch/nablarch-document"
        assert catalog["sources"][0]["commit"] == "abc123"
        assert catalog["sources"][1]["repo"] == "https://github.com/Fintan-contents/nablarch-system-development-guide"

    def test_generated_at_preserved_after_step2(self, ctx):
        """generated_at is not overwritten by step2."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-01-01T00:00:00Z",
            "sources": [],
            "files": []
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        assert catalog["generated_at"] == "2026-01-01T00:00:00Z"

    def test_files_updated_after_step2(self, ctx):
        """files field is updated with new classification results."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-01-01T00:00:00Z",
            "sources": [{"repo": "test", "branch": "main", "commit": "x"}],
            "files": [{"id": "old-file"}]
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        file_ids = [f["id"] for f in catalog["files"]]
        assert "old-file" not in file_ids
        assert len(catalog["sources"]) == 1
        assert catalog["sources"][0]["repo"] == "test"

    def test_first_run_without_existing_catalog(self, ctx):
        """First run creates catalog.json with empty sources and correct files."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        if os.path.exists(ctx.classified_list_path):
            os.remove(ctx.classified_list_path)

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        assert os.path.exists(ctx.classified_list_path)
        catalog = load_json(ctx.classified_list_path)
        assert "files" in catalog
        assert "version" in catalog
        assert "sources" in catalog
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_catalog_sources.py -q --tb=short
# 期待: 4 passed（退行防止テスト。現状のstep2でもGREENになる）
```

---

## Task 3: step2_classify.pyの修正

**ファイル**: `scripts/step2_classify.py`

L657-670を変更。

変更前:
```python
        # Generate output — preserve sources from existing catalog
        existing = {}
        if os.path.exists(self.ctx.classified_list_path):
            try:
                existing = load_json(self.ctx.classified_list_path)
            except (json.JSONDecodeError, OSError):
                pass

        output = {
            "version": self.ctx.version,
            "generated_at": existing.get("generated_at", datetime.utcnow().isoformat() + "Z"),
            "sources": existing.get("sources", []),
            "files": classified
        }
```

変更後:
```python
        # Update only the files field in existing catalog
        if os.path.exists(self.ctx.classified_list_path):
            try:
                output = load_json(self.ctx.classified_list_path)
            except (json.JSONDecodeError, OSError):
                output = {"version": self.ctx.version, "sources": []}
        else:
            output = {"version": self.ctx.version, "sources": []}
        output["files"] = classified
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_catalog_sources.py -q --tb=short
# 期待: 4 passed
python -m pytest tests/ut/ -q --tb=short 2>&1 | tail -3
# 期待: 158 passed, 7 skipped
```

---

## Task 4: modeディレクトリ移動、test_test_mode.pyのskip削除

### 問題

- `tests/ut/mode/`（`batch.json`, `largest3.json`）は`kc gen --test batch.json`で実行時に使われるリソースでUTのテストデータではない → `tests/e2e/mode/`に移動
- `test_test_mode.py`の`REPO_ROOT`算出にバグがあり常にskipされている
- `batch.json`内の4件のファイルIDが#150のbiz_samplesリマップで変わった

### Step 4-1: modeディレクトリを移動

```bash
cd tools/knowledge-creator
cp -r tests/ut/mode tests/e2e/mode
git add tests/e2e/mode
git rm -r tests/ut/mode
```

（`git mv`はcross-device linkエラーで失敗するため`cp` + `git add` + `git rm`を使う）

### Step 4-2: step2_classify.pyのパス参照を更新

**ファイル**: `scripts/step2_classify.py` L46

変更前:
```python
    test_file_path = os.path.join(repo_path, "tools/knowledge-creator/tests/mode", test_file_name)
```

変更後:
```python
    test_file_path = os.path.join(repo_path, "tools/knowledge-creator/tests/e2e/mode", test_file_name)
```

### Step 4-3: test_test_mode.pyのskip削除とパス修正

**ファイル**: `tests/ut/test_test_mode.py`

L10-14を変更:

変更前:
```python
# Get real repository path
TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(os.path.dirname(TOOL_DIR))

sys.path.insert(0, TOOL_DIR)
```

変更後:
```python
# Get real repository path
# __file__ = tests/ut/test_test_mode.py → knowledge-creator is 2 levels up
KC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_ROOT = os.path.dirname(os.path.dirname(KC_DIR))
TOOL_DIR = KC_DIR

sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))
```

L42-45のskipマーカーを削除（この4行をまるごと削除）:
```python
pytestmark = pytest.mark.skipif(
    not os.path.exists(f"{REPO_ROOT}/.lw/nab-official/v6"),
    reason="Requires real repository with source files"
)
```

L119とL174のmodeパス参照を更新:

変更前:
```python
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/tests/mode/batch.json"
```
変更後:
```python
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/tests/e2e/mode/batch.json"
```

変更前:
```python
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/tests/mode/largest3.json"
```
変更後:
```python
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/tests/e2e/mode/largest3.json"
```

### Step 4-4: batch.jsonのファイルIDを#150のbiz_samplesリマップに合わせて更新

**ファイル**: `tests/e2e/mode/batch.json`

以下の4件を変更:

| 変更前 | 変更後 |
|---|---|
| `about-nablarch-0101_PBKDF2PasswordEncryptor` | `biz-samples-0101_PBKDF2PasswordEncryptor` |
| `about-nablarch-0401_ExtendedDataFormatter` | `biz-samples-0401_ExtendedDataFormatter` |
| `about-nablarch-0402_ExtendedFieldType` | `biz-samples-0402_ExtendedFieldType` |
| `about-nablarch-OnlineAccessLogStatistics` | `biz-samples-OnlineAccessLogStatistics` |

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_test_mode.py -v --tb=short
# 期待: 7 passed, 0 skipped
```

---

## Task 5: 最終検証

```bash
cd tools/knowledge-creator

echo "=== UT ===" && python -m pytest tests/ut/ -q

echo "=== sources ===" && python3 -c "
import json
catalog = json.load(open('.cache/v6/catalog.json'))
print(f'sources: {len(catalog[\"sources\"])} repos')
for s in catalog['sources']:
    print(f'  {s[\"repo\"]} ({s[\"branch\"]}, {s[\"commit\"][:12]})')
assert len(catalog['sources']) == 2
print('OK')
"
```

### 期待結果

- UT: 165 passed, **0 skipped**, 0 failed
- catalog.json sources: 2 repos

### コミット

```
fix: step2 must only update files field in catalog.json

step2_classify was rebuilding the entire catalog.json object from
scratch, requiring it to manually preserve sources and generated_at.
This caused sources to be lost when the existing catalog happened to
have empty sources.

Changed to load existing catalog.json and only replace the files field.
Also restored the correct sources (2 repos) in catalog.json.

Additionally:
- Move tests/ut/mode/ to tests/e2e/mode/ (runtime resource, not UT data)
- Fix REPO_ROOT path bug in test_test_mode.py and remove skip marker
- Update batch.json file IDs for #150 biz_samples remap

Part of #153
```
