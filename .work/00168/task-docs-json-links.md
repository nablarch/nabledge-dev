# タスク: 閲覧用MDのリンク修正

## 問題

閲覧用MD（docs/）内のcross-fileリンクが全て `.json` ファイルを指しており、リンク切れになっている。

- docs MD内の全1,455件のパス付きリンクのうち **1,361件が `.json` リンク**
- docs MDディレクトリにJSONファイルは存在しない → **全件リンク切れ**
- verify_integrity.py V1は `.md` リンクのみチェック → `.md`リンクが0件のためOKを返していた

### 原因

`_generate_docs`がskill JSONを読んでdocs MDを生成するが、skill JSONにはすでに`_generate_skill_json`で`:ref:`/`:doc:`が `.json` リンクに変換済みのテキストが入っている。`_resolve_rst_links('docs_md')`は残存RST構文のみ変換するので、変換済みの`.json`リンクはそのまま残る。

### 追加で発見した問題

28件のリンクが `no_knowledge_content` ファイル（目次ページ等）を指している。これらはdocs MDが生成されないため、`.json`→`.md`変換してもリンク先MDが存在しない。

## 前提

- ブランチ: `150-fix-phase-c-failures`
- 作業ディレクトリ: `tools/knowledge-creator/`
- **実行順**: Task 1 → 2 → 3 → 4 → 5（順序厳守）

---

## Task 1: _generate_docsに.json→.md変換を追加

### Step 1-1: `_convert_json_to_md_links`メソッドを追加

**ファイル**: `scripts/phase_f_finalize.py`

`_convert_asset_paths`メソッドの直後（`_generate_docs`の前）に追加:

```python
    @staticmethod
    def _convert_json_to_md_links(content):
        """Convert .json cross-file links to .md for browsable docs.

        Skill JSON contains links like [text](path/file.json#anchor).
        Docs MD should link to [text](path/file.md#anchor) instead.
        Asset paths (containing 'assets/') are not converted.
        """
        def replacer(m):
            prefix = m.group(1)   # [text](
            path = m.group(2)     # path/file.json
            anchor = m.group(3)   # #anchor or empty
            if 'assets/' in path:
                return m.group(0)
            return f"{prefix}{path[:-5]}.md{anchor})"

        return re.sub(r'(\[[^\]]*?\]\()([^)]*?\.json)((?:#[^)]*)?)\)', replacer, content)
```

### Step 1-2: `_generate_docs`のループ内で呼び出す

L414の後に1行追加:

変更前 (L411-415):
```python
                # Get section content, convert asset paths and resolve RST links
                section_content = knowledge.get("sections", {}).get(sid, "")
                section_content = self._convert_asset_paths(section_content, fi)
                section_content = self._resolve_rst_links(section_content, fi["id"], 'docs_md')
                md_lines.append(section_content)
```

変更後:
```python
                # Get section content, convert asset paths and resolve RST links
                section_content = knowledge.get("sections", {}).get(sid, "")
                section_content = self._convert_asset_paths(section_content, fi)
                section_content = self._resolve_rst_links(section_content, fi["id"], 'docs_md')
                section_content = self._convert_json_to_md_links(section_content)
                md_lines.append(section_content)
```

---

## Task 2: no_knowledge_contentファイルのdocs MD生成

`no_knowledge_content`ファイルへのリンクが28件あり、docs MDが生成されないためリンク切れになる。タイトルと公式URLのみのMDを生成して、リンク先として機能させる。

**ファイル**: `scripts/phase_f_finalize.py`

`_generate_docs`メソッド内のL391-393を変更:

変更前:
```python
            knowledge = load_json(json_path)
            if knowledge.get("no_knowledge_content") is True:
                continue
            md_lines = [f"# {knowledge['title']}", ""]
```

変更後:
```python
            knowledge = load_json(json_path)
            if knowledge.get("no_knowledge_content") is True:
                # Generate minimal MD with title and official URL for link targets
                md_lines = [f"# {knowledge['title']}", ""]
                urls = knowledge.get("official_doc_urls", [])
                if urls:
                    if len(urls) == 1:
                        link = f"[{knowledge['title']}]({urls[0]})"
                    else:
                        link = " ".join(f"[{i + 1}]({u})" for i, u in enumerate(urls))
                    md_lines.append(f"**公式ドキュメント**: {link}")
                    md_lines.append("")
                md_content = "\n".join(md_lines)
                type_ = fi["type"]
                category = fi["category"]
                file_id = fi["id"]
                md_dir = f"{self.ctx.docs_dir}/{type_}/{category}"
                os.makedirs(md_dir, exist_ok=True)
                if not self.dry_run:
                    write_file(f"{md_dir}/{file_id}.md", md_content)
                generated += 1
                continue
            md_lines = [f"# {knowledge['title']}", ""]
```

---

## Task 3: verify_integrity.py V1を全リンク対象に拡大

**ファイル**: `scripts/verify_integrity.py`

`check_v1_doc_links`の正規表現を`.md`限定から全ファイルリンク対象に変更。

変更前:
```python
def check_v1_doc_links(knowledge_dir, docs_dir, results):
    """V1: docs内 [text](file.md) リンク先が実在する"""
    fails = []
    md_files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)
    link_re = re.compile(r'(?<!!\[)\[([^\]]+)\]\(([^)#]+\.md)\)')
    for md_path in md_files:
        content = open(md_path, encoding="utf-8").read()
        for m in link_re.finditer(content):
            target = m.group(2)
            if target.startswith("http"):
                continue
            # Resolve relative to the MD file's directory
            abs_target = os.path.normpath(os.path.join(os.path.dirname(md_path), target))
            if not os.path.exists(abs_target):
                fails.append(f"  {os.path.relpath(md_path, docs_dir)}: broken link to {target}")
    results["V1"] = ("FAIL", fails) if fails else ("OK", [])
```

変更後:
```python
def check_v1_doc_links(knowledge_dir, docs_dir, results):
    """V1: docs内の全リンク先ファイルが実在する"""
    fails = []
    md_files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)
    # Match all links [text](path) and ![text](path), excluding anchor-only (#xxx)
    link_re = re.compile(r'!?\[[^\]]*?\]\(([^)#][^)]*)\)')
    for md_path in md_files:
        content = open(md_path, encoding="utf-8").read()
        for m in link_re.finditer(content):
            target = m.group(1)
            if target.startswith("http"):
                continue
            # Resolve relative to the MD file's directory
            abs_target = os.path.normpath(os.path.join(os.path.dirname(md_path), target))
            if not os.path.exists(abs_target):
                rel = os.path.relpath(md_path, docs_dir)
                fails.append(f"  {rel}: broken link to {target}")
    results["V1"] = ("FAIL", fails[:20]) if fails else ("OK", [])
    if fails and len(fails) > 20:
        results["V1"] = ("FAIL", fails[:20] + [f"  ... and {len(fails) - 20} more"])
```

---

## Task 4: Phase M再実行

```bash
cd tools/knowledge-creator
python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
from run import Context
from phase_m_finalize import PhaseMFinalize
ctx = Context(version='6', repo=os.path.abspath('../..'), concurrency=1, run_id='doclinks')
PhaseMFinalize(ctx).run()
"
```

### 検証

```bash
cd tools/knowledge-creator

# 1. docs MD内に .json リンクが0件であること
python3 -c "
import glob, re
docs_dir = '../../.claude/skills/nabledge-6/docs'
json_links = 0
for p in glob.glob(f'{docs_dir}/**/*.md', recursive=True):
    content = open(p).read()
    for m in re.finditer(r'\[[^\]]*?\]\([^)]*?\.json[^)]*\)', content):
        if 'http' not in m.group(0):
            json_links += 1
print(f'.json links in docs MD: {json_links}')
assert json_links == 0, f'{json_links} .json links remain'
print('OK')
"

# 2. docs MDの全リンクがリンク先存在すること
python3 -c "
import glob, re, os
docs_dir = '../../.claude/skills/nabledge-6/docs'
broken = 0
total = 0
for p in glob.glob(f'{docs_dir}/**/*.md', recursive=True):
    content = open(p).read()
    md_dir = os.path.dirname(p)
    for m in re.finditer(r'!?\[[^\]]*?\]\(([^)#][^)]*)\)', content):
        target = m.group(1)
        if target.startswith('http'): continue
        total += 1
        abs_t = os.path.normpath(os.path.join(md_dir, target))
        if not os.path.exists(abs_t):
            broken += 1
            if broken <= 5:
                print(f'  BROKEN: {os.path.relpath(p, docs_dir)} -> {target}')
print(f'Total links: {total}, broken: {broken}')
assert broken == 0, f'{broken} broken links'
print('OK')
"

# 3. docs MD数（no_knowledge_content分が追加）
python3 -c "
import glob
docs = glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True)
print(f'Docs MDs: {len(docs)} (expected: 339 = 296 + 43 nkc)')
assert len(docs) >= 335
print('OK')
"

# 4. verify_integrity.py 全チェック
python scripts/verify_integrity.py

# 5. UT
python -m pytest tests/ut/ -q
```

---

## Task 5: 最終検証

```bash
cd tools/knowledge-creator
echo "=== UT ===" && python -m pytest tests/ut/ -q
echo "=== Integrity ===" && python scripts/verify_integrity.py
echo "=== Counts ===" && python3 -c "
import glob
s = len([p for p in glob.glob('../../.claude/skills/nabledge-6/knowledge/**/*.json', recursive=True) if '/assets/' not in p])
d = len(glob.glob('../../.claude/skills/nabledge-6/docs/**/*.md', recursive=True))
n = sum(1 for l in open('../../.claude/skills/nabledge-6/knowledge/index.toon').read().splitlines() if 'not yet created' in l)
print(f'Skill:{s} Docs:{d} NotYet:{n}')
assert s >= 300 and d >= 335 and n == 0
print('ALL OK')
"
```

### 期待結果

- UT: 154+ passed, 0 failed
- verify_integrity.py: 0 FAIL, 15+ OK, 2 WARN
- Docs MD: >=335件（296 + 43 no_knowledge_content）
- docs MD内の `.json` リンク: 0件
- docs MD内の全リンク: 0件broken

### コミット

```
fix: convert .json links to .md in browsable docs, generate nkc placeholder MDs

- Add _convert_json_to_md_links() to convert skill JSON cross-file links
  (.json) to docs MD links (.md) in _generate_docs
- Generate minimal docs MD for no_knowledge_content files (title + official URL)
  so that cross-file links to these files are not broken (28 links)
- Expand V1 check to verify all link types, not just .md links

Fixes 1,361 broken .json links in browsable docs.
Part of #150
```
