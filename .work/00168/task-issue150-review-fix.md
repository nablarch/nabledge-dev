# タスク: Issue #150 レビュー指摘対応

## 状況

`150-fix-phase-c-failures` ブランチのレビューで以下の問題が発見された。

| ID | 深刻度 | 問題 | 影響 |
|---|---|---|---|
| P1 | CRITICAL | splitファイルのキャッシュリネーム失敗 → merge全件スキップ | skill JSON 125/343件、docs MD 82件、index.toon 296件が"not yet created" |
| P2 | HIGH | skill JSONのcross-fileリンクにtype/categoryパスが欠落 | 別ディレクトリへの参照174件がリンク切れ |
| P3 | MEDIUM | 空コミット `9b926a0` | コミットメッセージと実態が不一致 |
| P4 | MEDIUM | verify_integrity.py にV2,V4,V5,V6,V16,V17チェックが欠落 | P1,P2が検出されなかった |
| P5 | LOW | .pr/00150/ 未作成 | 方針転換の記録がない |

## P1の根本原因（3つの原因が重なっている）

**原因A — rename_split_filesの実装ミス**: キャッシュJSON内の `split_info` を読もうとするが、`split_info` はカタログにしかない → リネーム0件。

**原因B — biz_samplesのキャッシュ未移動**: カタログは `guide/biz-samples/biz-samples-*` に更新済みだが、キャッシュファイルは `about/about-nablarch/about-nablarch-*` のまま（18ファイル）。

**原因C — 5件のoriginal_id変更**: step2のID生成ロジック変更で以下の5件のoriginal_idが変わった:

| 旧original_id (キャッシュ) | 新original_id (カタログ) |
|---|---|
| `testing-framework-rest` | `testing-framework-rest-02_RequestUnitTest` |
| `testing-framework-batch` | `testing-framework-batch-02_RequestUnitTest` |
| `testing-framework-send_sync` | `testing-framework-send_sync-02_RequestUnitTest` |
| `testing-framework-rest` | `testing-framework-rest-03_DealUnitTest` |
| `testing-framework-batch` | `testing-framework-batch-03_DealUnitTest` |
| `testing-framework-send_sync` | `testing-framework-send_sync-03_DealUnitTest` |

注: 旧original_idの`testing-framework-rest`/`batch`/`send_sync`はそれぞれ02と03の2つの新IDに分岐している（旧IDのdedup処理で同名ファイルが存在していた）。

## 前提

- ブランチ: `150-fix-phase-c-failures` 上で作業
- 作業ディレクトリ: `tools/knowledge-creator/`
- 現状テスト: `python -m pytest tests/ut/ -q` → 154 passed, 7 skipped
- **実行順**: Task 1 → 2 → 3 → 4 → 5 → 6 → 7（順序厳守）

---

## Task 1: P1修正 — rename_split_files の全面書き直し

### 戦略

カタログの `section_range.sections[0]`（最初のh2見出し）に旧 `_title_to_section_id()` を適用して旧ファイル名を復元する。290/296件で成功することを確認済み。残り6件は原因Cの手動マッピングテーブルで対応。biz_samples（原因B）は旧type/category/original_idに逆変換してから同じロジックを適用する。

### Step 1-1: `scripts/migrate_section_ids.py` を修正

以下の変更を行う。

**1. `_title_to_section_id_legacy` 関数を追加** (ファイル先頭のimport群の後):

```python
def _title_to_section_id_legacy(title):
    """Reproduce the old _title_to_section_id logic for reverse mapping."""
    import hashlib
    ascii_id = re.sub(r'[^a-zA-Z0-9-]', '', title.replace(' ', '-')).lower().strip('-')
    ascii_id = re.sub(r'-+', '-', ascii_id)
    if ascii_id and len(ascii_id) >= 3:
        return ascii_id[:50]
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    return f"sec-{h}"
```

**2. 定数テーブルを追加**:

```python
_ORIGINAL_ID_REMAP_REVERSE = {
    "testing-framework-rest-02_RequestUnitTest": "testing-framework-rest",
    "testing-framework-batch-02_RequestUnitTest": "testing-framework-batch",
    "testing-framework-send_sync-02_RequestUnitTest": "testing-framework-send_sync",
    "testing-framework-rest-03_DealUnitTest": "testing-framework-rest",
    "testing-framework-batch-03_DealUnitTest": "testing-framework-batch",
    "testing-framework-send_sync-03_DealUnitTest": "testing-framework-send_sync",
}
```

**3. `rename_non_split_biz_samples` 関数を追加**:

```python
def rename_non_split_biz_samples(knowledge_cache_dir, catalog_path, stats):
    """Move biz_samples non-split cache files from old to new path."""
    catalog = load_json(catalog_path)
    moved = 0
    for fi in catalog.get("files", []):
        if fi.get("split_info", {}).get("is_split"):
            continue
        if fi["category"] != "biz-samples":
            continue
        new_path = os.path.join(knowledge_cache_dir, fi["output_path"])
        if os.path.exists(new_path):
            continue
        old_id = fi["id"].replace("biz-samples-", "about-nablarch-")
        old_path = os.path.join(knowledge_cache_dir, "about", "about-nablarch", f"{old_id}.json")
        if not os.path.exists(old_path):
            print(f"  WARNING: biz_samples non-split not found: {old_path}")
            continue
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        data = load_json(new_path)
        data["id"] = fi["id"]
        write_json(new_path, data)
        moved += 1
    stats["biz_samples_nonsplit_moved"] = moved
    print(f"  Moved {moved} biz_samples non-split files")
```

**4. `rename_split_files` 関数を全置換**:

```python
def rename_split_files(knowledge_cache_dir, catalog_path, stats):
    """Rename split cache files to match new catalog output_paths.

    For each catalog split entry:
    1. Reconstruct old filename: {old_original_id}--{_title_to_section_id_legacy(first_heading)}.json
    2. Handle biz_samples (type/category changed) via reverse mapping
    3. Handle 5 original_id changes via _ORIGINAL_ID_REMAP_REVERSE
    4. Verify old file exists, rename to new output_path, update id field
    """
    catalog = load_json(catalog_path)
    renamed = 0
    skipped = 0
    errors = []

    for fi in catalog.get("files", []):
        si = fi.get("split_info")
        if not si or not si.get("is_split"):
            continue

        new_output_path = fi["output_path"]
        new_path = os.path.join(knowledge_cache_dir, new_output_path)
        if os.path.exists(new_path):
            skipped += 1
            continue

        original_id = si["original_id"]
        type_ = fi["type"]
        category = fi["category"]

        # Reverse-map to old type/category/original_id
        old_type, old_category, old_original_id = type_, category, original_id
        if category == "biz-samples":
            old_type, old_category = "about", "about-nablarch"
            old_original_id = original_id.replace("biz-samples-", "about-nablarch-")
        if original_id in _ORIGINAL_ID_REMAP_REVERSE:
            old_original_id = _ORIGINAL_ID_REMAP_REVERSE[original_id]

        # Reconstruct old suffix
        sections = fi.get("section_range", {}).get("sections", [])
        first_heading = sections[0] if sections else ""
        old_suffix = _title_to_section_id_legacy(first_heading)

        # Try exact match, then dedup suffixes (-2, -3, ...)
        old_dir = os.path.join(knowledge_cache_dir, old_type, old_category)
        old_path = os.path.join(old_dir, f"{old_original_id}--{old_suffix}.json")
        if not os.path.exists(old_path):
            found = False
            for counter in range(2, 10):
                candidate = os.path.join(old_dir, f"{old_original_id}--{old_suffix}-{counter}.json")
                if os.path.exists(candidate):
                    old_path = candidate
                    found = True
                    break
            if not found:
                errors.append(f"{old_original_id}--{old_suffix} (for {new_output_path})")
                continue

        # Execute rename
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)

        # Update id field
        data = load_json(new_path)
        new_file_id = os.path.basename(new_path).replace(".json", "")
        data["id"] = new_file_id
        write_json(new_path, data)

        # Rename assets directory
        old_basename = os.path.basename(old_path).replace(".json", "")
        old_assets = os.path.join(os.path.dirname(old_path), "assets", old_basename)
        new_assets = os.path.join(os.path.dirname(new_path), "assets", new_file_id)
        if os.path.isdir(old_assets):
            os.makedirs(os.path.dirname(new_assets), exist_ok=True)
            if os.path.exists(new_assets):
                shutil.rmtree(new_assets)
            shutil.move(old_assets, new_assets)
            for sid in list(data.get("sections", {}).keys()):
                data["sections"][sid] = data["sections"][sid].replace(
                    f"assets/{old_basename}/", f"assets/{new_file_id}/")
            write_json(new_path, data)

        renamed += 1

    stats["renamed"] = renamed
    stats["skipped"] = skipped
    if errors:
        print(f"  WARNING: {len(errors)} files not found:")
        for e in errors[:10]:
            print(f"    {e}")
    print(f"  Renamed {renamed}, skipped {skipped} (already correct)")
```

**5. `migrate_biz_samples_content` 関数を追加**:

```python
def migrate_biz_samples_content(knowledge_cache_dir, catalog_path, stats):
    """Update section IDs in biz_samples JSONs (still in old kebab-case)."""
    catalog = load_json(catalog_path)
    updated = 0
    for fi in catalog.get("files", []):
        if fi["category"] != "biz-samples":
            continue
        path = os.path.join(knowledge_cache_dir, fi["output_path"])
        if not os.path.exists(path):
            continue
        data = load_json(path)
        if data.get("no_knowledge_content"):
            continue
        changed = migrate_file_content(data)
        if changed:
            write_json(path, data)
            updated += 1
    stats["biz_content_updated"] = updated
    print(f"  Updated section IDs in {updated} biz_samples files")
```

**6. `main()` の実行順序を修正**:

```python
def main():
    # ... 既存のパス設定 ...

    stats = {}

    # Phase 1: biz_samples 非splitファイルの移動
    print("Phase 1: Move biz_samples non-split files...")
    rename_non_split_biz_samples(knowledge_cache_dir, catalog_path, stats)

    # Phase 2: 全splitファイルのリネーム（biz_samples split含む）
    print("Phase 2: Rename split files...")
    rename_split_files(knowledge_cache_dir, catalog_path, stats)

    # Phase 3: biz_samples のJSON中身セクションID更新
    print("Phase 3: Update biz_samples section IDs...")
    migrate_biz_samples_content(knowledge_cache_dir, catalog_path, stats)

    # Phase 4: 既存のmigrate_file_content（セクションID変換）は
    #          biz_samples以外のファイルについてはすでに実行済み。
    #          ここでは全ファイルに対して再実行して検証を兼ねる。
    print("Phase 4: Verify all files...")
    # ... 既存のverify() 呼び出し ...
```

### 検証

```bash
cd tools/knowledge-creator
python scripts/migrate_section_ids.py

# 1. 全ファイルが存在する
python3 -c "
import json, os
cat = json.load(open('.cache/v6/catalog.json'))
missing = [f['id'] for f in cat['files'] if not os.path.exists(f'.cache/v6/knowledge/{f[\"output_path\"]}')]
print(f'Missing: {len(missing)}/{len(cat[\"files\"])}')
assert len(missing) == 0, f'{len(missing)} missing: {missing[:5]}'
print('OK')
"

# 2. 旧形式ファイルが残っていない
python3 -c "
import glob
old = [p for p in glob.glob('.cache/v6/knowledge/**/*.json', recursive=True)
       if '/assets/' not in p and '--sec-' in p]
print(f'Old --sec- files: {len(old)}')
assert len(old) == 0, f'{len(old)} remain'
print('OK')
"

# 3. 全セクションIDがs{N}形式
python3 -c "
import glob, json, re
pat = re.compile(r'^s\d+$')
bad = 0
for p in glob.glob('.cache/v6/knowledge/**/*.json', recursive=True):
    if '/assets/' in p: continue
    d = json.load(open(p))
    if d.get('no_knowledge_content'): continue
    for sid in d.get('sections',{}).keys():
        if not pat.match(sid): bad += 1
print(f'Non-sequential: {bad}')
assert bad == 0
print('OK')
"
```

### コミット

```
fix: rewrite rename_split_files with old filename reconstruction

- Reconstruct old filenames via _title_to_section_id_legacy()
- Handle biz_samples path change (about→guide, about-nablarch→biz-samples)
- Handle 5 original_id changes with explicit remap table
- Move biz_samples non-split files
- Update biz_samples section IDs (were still kebab-case)

Fixes P1: 218 missing merged files.
Part of #150
```

---

## Task 2: P2修正 — skill JSONのcross-fileリンクパス

### 修正

**ファイル**: `scripts/phase_f_finalize.py` の `_make_cross_file_link` メソッド

変更前（L249付近）:
```python
if output_type == 'skill_json':
    return f"{to_file_id}.json{anchor}"
```

変更後:
```python
if output_type == 'skill_json':
    from_type, from_cat = self.file_type_category.get(from_file_id, ('', ''))
    to_type, to_cat = self.file_type_category.get(to_file_id, ('', ''))
    from_dir = f"{self.ctx.knowledge_dir}/{from_type}/{from_cat}"
    to_path = f"{self.ctx.knowledge_dir}/{to_type}/{to_cat}/{to_file_id}.json"
    rel = os.path.relpath(to_path, from_dir)
    return f"{rel}{anchor}"
```

### テスト期待値の修正

**ファイル**: `tests/ut/test_phase_f_links.py`

P2修正でskill_jsonのcross-fileリンクが`file_id.json`から相対パスに変わるため、テスト4箇所の期待値を更新する。テストのsetupでは`current-file`が`component/handlers`、`other-file`が`component/adapters`なので、相対パスは`../adapters/other-file.json`になる。

1. `test_ref_external_skill_json` (L201):
   - 変更前: `assert result == "[external_label](other-file.json#s2)"`
   - 変更後: `assert result == "[external_label](../adapters/other-file.json#s2)"`

2. `test_ref_external_skill_json_no_section` (L207):
   - 変更前: `assert result == "[external_no_section](other-file.json)"`
   - 変更後: `assert result == "[external_no_section](../adapters/other-file.json)"`

3. `test_doc_link_skill_json` (L227):
   - 変更前: `assert result == "[path/to/other](other-file.json)"`
   - 変更後: `assert result == "[path/to/other](../adapters/other-file.json)"`

4. `test_doc_link_with_display_text` (L233):
   - 変更前: `assert result == "[Other Doc](other-file.json)"`
   - 変更後: `assert result == "[Other Doc](../adapters/other-file.json)"`

### 検証

```bash
cd tools/knowledge-creator
python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
from phase_f_finalize import PhaseFFinalize
from run import Context
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='test')
pf = PhaseFFinalize(ctx, dry_run=True)
pf.file_type_category = {
    'about-nablarch-big_picture': ('about', 'about-nablarch'),
    'about-nablarch-architecture': ('about', 'about-nablarch'),
    'handlers-jaxrs_bean_validation_handler': ('component', 'handlers'),
}
# 同一ディレクトリ
link = pf._make_cross_file_link('about-nablarch-big_picture', 'about-nablarch-architecture', None, 'skill_json')
assert link == 'about-nablarch-architecture.json', f'Got: {link}'
# 別ディレクトリ
link = pf._make_cross_file_link('about-nablarch-big_picture', 'handlers-jaxrs_bean_validation_handler', 's1', 'skill_json')
assert link == '../../component/handlers/handlers-jaxrs_bean_validation_handler.json#s1', f'Got: {link}'
print('OK')
"
```

### コミット

```
fix: use relative paths for skill JSON cross-file links

Fixes P2: 174 broken links.
Part of #150
```

---

## Task 3: Phase M再実行

```bash
cd tools/knowledge-creator
python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_m_finalize import PhaseMFinalize
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='fix')
PhaseMFinalize(ctx).run()
"
```

### 検証

```bash
cd tools/knowledge-creator
python3 -c "
import glob, json
skill = [p for p in glob.glob('../../.claude/skills/nabledge-6/knowledge/**/*.json', recursive=True) if '/assets/' not in p]
docs = glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True)
toon = open('../../.claude/skills/nabledge-6/knowledge/index.toon').read()
not_yet = sum(1 for l in toon.splitlines() if 'not yet created' in l)
print(f'Skill JSONs: {len(skill)} (>=300)')
print(f'Docs MDs:    {len(docs)} (>=250)')
print(f'not_yet:     {not_yet} (==0)')
assert len(skill) >= 300 and len(docs) >= 250 and not_yet == 0
print('ALL OK')
"
```

### コミット

```
fix: regenerate all outputs after P1/P2 fixes

Part of #150
```

---

## Task 4: P4修正 — verify_integrity.py にV2,V4,V5,V6,V16,V17を追加

**ファイル**: `scripts/verify_integrity.py`

以下の6関数を追加し、`main()` から呼び出す。関数の完全なコードはこのドキュメントの末尾「付録A」に記載。

追加する関数:
- `check_v2_doc_anchors(docs_dir, results)` — docs内anchor先存在
- `check_v4_skill_asset_links(knowledge_dir, results)` — skill JSONアセット存在
- `check_v5_skill_internal_anchors(knowledge_dir, results)` — skill JSON内部参照存在
- `check_v6_skill_crossfile_links(knowledge_dir, results)` — skill JSONクロスファイル存在
- `check_v16_biz_samples(catalog_path, results)` — biz_samples配置
- `check_v17_catalog_labels(catalog_path, repo_root, results)` — ラベル実在

`main()` に追加:
```python
check_v2_doc_anchors(docs_dir, results)
check_v4_skill_asset_links(knowledge_dir, results)
check_v5_skill_internal_anchors(knowledge_dir, results)
check_v6_skill_crossfile_links(knowledge_dir, results)
catalog_path = os.path.join(kc_root, ".cache/v6/catalog.json")
check_v16_biz_samples(catalog_path, results)
check_v17_catalog_labels(catalog_path, repo_root, results)
```

### 検証

```bash
cd tools/knowledge-creator
python scripts/verify_integrity.py
# 期待: 0 FAIL
```

### コミット

```
fix: add V2/V4/V5/V6/V16/V17 to verify_integrity.py

Part of #150
```

---

## Task 5: P3 — 空コミット削除

```bash
git rebase -i 9b926a0^
# 9b926a0 の行を "drop" に変更
git push --force-with-lease origin 150-fix-phase-c-failures
```

---

## Task 6: P5 — .pr/00150/ 作成

`.pr/00150/notes.md`:
```markdown
# Issue #150: Phase C不合格の根本原因修正

## 方針転換
元のIssue: 3ファイルの個別修正。
実際: 根本原因対応（セクションID連番化、processing_patterns廃止、Phase G廃止、biz_samplesリマップ）。
同時解決: #149, #151, #166。

## レビュー指摘修正
- P1: splitリネーム失敗 → title_to_section_id復元で旧ファイル名を再構築
- P2: skill JSON cross-fileリンクパス欠落 → 相対パス計算
- P4: verify_integrity.pyチェック欠落 → V2/V4/V5/V6/V16/V17追加
```

### コミット
```
docs: add .pr/00150/ work notes
Part of #150
```

---

## Task 7: 最終検証

```bash
cd tools/knowledge-creator
echo "=== Unit Tests ===" && python -m pytest tests/ut/ -q
echo "=== Integrity ===" && python scripts/verify_integrity.py
echo "=== Cross-file links (V6) ===" && python3 -c "
import glob, json, os, re
skill_dir = '../../.claude/skills/nabledge-6/knowledge'
broken = 0
total = 0
for p in glob.glob(f'{skill_dir}/**/*.json', recursive=True):
    if '/assets/' in p: continue
    data = json.load(open(p))
    json_dir = os.path.dirname(p)
    for sid, content in data.get('sections', {}).items():
        for m in re.finditer(r'\[([^\]]*)\]\(([^)]+\.json)(?:#([^)]*))?\)', content):
            tf = m.group(2)
            if tf.startswith('http'): continue
            total += 1
            if not os.path.exists(os.path.normpath(os.path.join(json_dir, tf))):
                broken += 1
print(f'Cross-file links: {total}, broken: {broken}')
assert broken == 0, f'{broken} broken'
print('OK')
"
echo "=== Counts ===" && python3 -c "
import glob, json
s = len([p for p in glob.glob('../../.claude/skills/nabledge-6/knowledge/**/*.json', recursive=True) if '/assets/' not in p])
d = len(glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True))
n = sum(1 for l in open('../../.claude/skills/nabledge-6/knowledge/index.toon').read().splitlines() if 'not yet created' in l)
print(f'Skill:{s} Docs:{d} NotYet:{n}')
assert s >= 300 and d >= 250 and n == 0, 'FAIL'
print('ALL OK')
"
```

### 期待結果

- UT: 154+ passed, 0 failed
- verify_integrity.py: 以下のV3/V7 FAILは本タスクのスコープ外の既存問題として許容。P1/P2に起因するFAILがゼロであること。
  - V3 FAIL 1件: `testing-framework-guide-...-02-RequestUnitTest`のasset（merge時のassets名がsplit IDを含む既存問題）
  - V7 FAIL 1件: `setting-guide-ManagingEnvironmentalConfiguration`のタイトル比較（toon解析のカンマ変換バグ）
  - V10/V11 WARN: 未解決RSTリンク（ソースRSTに存在しない架空ラベルへの参照）
- Cross-file links (V6手動検証): 0 broken
- Skill JSON: >=300, Docs MD: >=250, not_yet_created: 0

---

## 付録A: verify_integrity.py 追加関数

```python
def check_v2_doc_anchors(docs_dir, results):
    """V2: docs内 [text](file.md#anchor) のanchor先が実在する"""
    fails = []
    link_re = re.compile(r'(?<!!\[)\[([^\]]+)\]\(([^)#]+\.md)#([^)]+)\)')
    for md_path in glob.glob(f"{docs_dir}/**/*.md", recursive=True):
        content = open(md_path, encoding="utf-8").read()
        src_dir = os.path.dirname(md_path)
        for m in link_re.finditer(content):
            file_part, anchor = m.group(2), m.group(3)
            if file_part.startswith("http"):
                continue
            target_path = os.path.normpath(os.path.join(src_dir, file_part))
            if not os.path.exists(target_path):
                continue
            target_content = open(target_path, encoding="utf-8").read()
            heading_ids = set()
            for hm in re.finditer(r'^##\s+(.+)$', target_content, re.MULTILINE):
                h = hm.group(1).strip()
                hid = re.sub(r'[^\w\s-]', '', h).strip().lower().replace(' ', '-')
                heading_ids.add(hid)
            if anchor not in heading_ids:
                rel = os.path.relpath(md_path, docs_dir)
                fails.append(f"  {rel} -> {file_part}#{anchor}: anchor not in target")
    results["V2"] = ("FAIL", fails) if fails else ("OK", [])


def check_v4_skill_asset_links(knowledge_dir, results):
    """V4: skill JSON内 assets/ リンク先が実在する"""
    fails = []
    for p in glob.glob(f"{knowledge_dir}/**/*.json", recursive=True):
        if "/assets/" in p: continue
        data = load_json(p)
        json_dir = os.path.dirname(p)
        for sid, content in data.get("sections", {}).items():
            for m in re.finditer(r'[!\[]\[?[^\]]*\]\((assets/[^)]+)\)', content):
                if not os.path.exists(os.path.join(json_dir, m.group(1))):
                    fails.append(f"  {data.get('id','')}#{sid}: {m.group(1)}")
    results["V4"] = ("FAIL", fails) if fails else ("OK", [])


def check_v5_skill_internal_anchors(knowledge_dir, results):
    """V5: skill JSON内 (#section_id) が同一ファイル内に存在する"""
    fails = []
    for p in glob.glob(f"{knowledge_dir}/**/*.json", recursive=True):
        if "/assets/" in p: continue
        data = load_json(p)
        sids = set(data.get("sections", {}).keys())
        for sid, content in data.get("sections", {}).items():
            for m in re.finditer(r'\(#([^)]+)\)', content):
                if m.group(1) not in sids:
                    fails.append(f"  {data.get('id','')}#{sid} -> #{m.group(1)}")
    results["V5"] = ("FAIL", fails) if fails else ("OK", [])


def check_v6_skill_crossfile_links(knowledge_dir, results):
    """V6: skill JSON内 [text](path/file.json#sid) のターゲットが実在する"""
    fails = []
    link_re = re.compile(r'\[([^\]]*)\]\(([^)]+\.json)(?:#([^)]*))?\)')
    for p in glob.glob(f"{knowledge_dir}/**/*.json", recursive=True):
        if "/assets/" in p: continue
        data = load_json(p)
        json_dir = os.path.dirname(p)
        for sid, content in data.get("sections", {}).items():
            for m in link_re.finditer(content):
                target_file, anchor = m.group(2), m.group(3)
                if target_file.startswith("http"): continue
                target_abs = os.path.normpath(os.path.join(json_dir, target_file))
                if not os.path.exists(target_abs):
                    fails.append(f"  {data.get('id','')}#{sid} -> {target_file}: not found")
                elif anchor:
                    td = load_json(target_abs)
                    if anchor not in td.get("sections", {}):
                        fails.append(f"  {data.get('id','')}#{sid} -> {target_file}#{anchor}: section missing")
    results["V6"] = ("FAIL", fails[:20]) if fails else ("OK", [])
    if fails and len(fails) > 20:
        results["V6"] = ("FAIL", fails[:20] + [f"  ... and {len(fails)-20} more"])


def check_v16_biz_samples(catalog_path, results):
    """V16: biz_samplesがguide/biz-samplesに配置されている"""
    if not os.path.exists(catalog_path):
        results["V16"] = ("FAIL", ["  catalog.json not found"])
        return
    catalog = load_json(catalog_path)
    fails = []
    for fi in catalog.get("files", []):
        if "biz_samples" in fi.get("source_path", ""):
            if fi["type"] != "guide" or fi["category"] != "biz-samples":
                fails.append(f"  {fi['id']}: in {fi['type']}/{fi['category']}")
    results["V16"] = ("FAIL", fails) if fails else ("OK", [])


def check_v17_catalog_labels(catalog_path, repo_root, results):
    """V17: section_mapのrst_labelsがソースRSTに実在する"""
    if not os.path.exists(catalog_path):
        results["V17"] = ("FAIL", ["  catalog.json not found"])
        return
    catalog = load_json(catalog_path)
    fails = []
    checked = 0
    for fi in catalog.get("files", []):
        source = os.path.join(repo_root, fi.get("source_path", ""))
        if not os.path.exists(source): continue
        src_content = open(source, encoding="utf-8").read()
        src_labels = set(re.findall(r'^\.\.\s+_([a-z0-9_-]+):', src_content, re.MULTILINE))
        for sm in fi.get("section_map", []):
            for label in sm.get("rst_labels", []):
                checked += 1
                if label not in src_labels:
                    fails.append(f"  {fi['id']}: '{label}' not in source")
    results["V17"] = ("FAIL", fails[:10]) if fails else ("OK", [f"  {checked} labels verified"])
```
