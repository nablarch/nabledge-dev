#!/usr/bin/env python3
"""Generate expected test values independently from kc source code.

This script implements the classification, splitting, and ID generation
logic from scratch based on the documented specifications. It does NOT
import any kc module. The output is a JSON file containing all expected
values that E2E tests assert against.

Usage:
    python generate_expected.py <repo_root> <output_path>
"""
import os
import re
import sys
import json
import hashlib
from collections import Counter

# ============================================================
# Constants (copied from spec, NOT imported from step2_classify.py)
# ============================================================

SPLIT_SECTION_THRESHOLD = 2
LINE_GROUP_THRESHOLD = 400

RST_MAPPING = [
    ("application_framework/application_framework/batch/nablarch_batch", "processing-pattern", "nablarch-batch"),
    ("application_framework/application_framework/batch/jsr352", "processing-pattern", "jakarta-batch"),
    ("application_framework/application_framework/batch/", "processing-pattern", "nablarch-batch"),
    ("application_framework/application_framework/web_service/rest", "processing-pattern", "restful-web-service"),
    ("application_framework/application_framework/web_service/http_messaging", "processing-pattern", "http-messaging"),
    ("application_framework/application_framework/web_service/", "processing-pattern", "restful-web-service"),
    ("application_framework/application_framework/web/", "processing-pattern", "web-application"),
    ("application_framework/application_framework/messaging/mom", "processing-pattern", "mom-messaging"),
    ("application_framework/application_framework/messaging/db", "processing-pattern", "db-messaging"),
    ("application_framework/application_framework/handlers/", "component", "handlers"),
    ("application_framework/application_framework/batch/jBatchHandler", "component", "handlers"),
    ("application_framework/application_framework/libraries/", "component", "libraries"),
    ("application_framework/adaptors/", "component", "adapters"),
    ("development_tools/testing_framework/", "development-tools", "testing-framework"),
    ("development_tools/toolbox/", "development-tools", "toolbox"),
    ("development_tools/java_static_analysis/", "development-tools", "java-static-analysis"),
    ("application_framework/application_framework/blank_project/", "setup", "blank-project"),
    ("application_framework/application_framework/configuration/", "setup", "configuration"),
    ("application_framework/setting_guide/", "setup", "setting-guide"),
    ("application_framework/application_framework/cloud_native/", "setup", "cloud-native"),
    ("about_nablarch/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch_architecture/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch/", "about", "about-nablarch"),
    ("migration/", "about", "migration"),
    ("release_notes/", "about", "release-notes"),
    ("biz_samples/", "about", "about-nablarch"),
    ("application_framework/application_framework/messaging/", "processing-pattern", "db-messaging"),
    ("examples/", "about", "about-nablarch"),
    ("external_contents/", "about", "about-nablarch"),
    ("inquiry/", "about", "about-nablarch"),
    ("jakarta_ee/", "about", "about-nablarch"),
    ("nablarch_api/", "about", "about-nablarch"),
    ("releases/", "about", "release-notes"),
    ("terms_of_use/", "about", "about-nablarch"),
    ("application_framework/application_framework/", "about", "about-nablarch"),
    ("application_framework/", "about", "about-nablarch"),
    ("development_tools/", "development-tools", "testing-framework"),
]

MD_MAPPING = {
    "Nablarchバッチ処理パターン.md": ("guide", "nablarch-patterns"),
    "Nablarchでの非同期処理.md": ("guide", "nablarch-patterns"),
    "Nablarchアンチパターン.md": ("guide", "nablarch-patterns"),
}

XLSX_MAPPING = {
    "Nablarch機能のセキュリティ対応表.xlsx": ("check", "security-check"),
}


# ============================================================
# Step 1: List sources
# ============================================================

def list_sources(repo: str, version: str) -> list:
    sources = []

    # RST
    rst_base = os.path.join(repo, f".lw/nab-official/v{version}/nablarch-document/ja/")
    if os.path.exists(rst_base):
        for root, dirs, files in os.walk(rst_base):
            dirs[:] = [d for d in dirs if not d.startswith("_")]
            for f in sorted(files):
                if f.endswith(".rst"):
                    rel = os.path.relpath(os.path.join(root, f), repo)
                    sources.append({"path": rel, "format": "rst", "filename": f})

    # MD
    pattern_dir = os.path.join(
        repo, ".lw/nab-official/v6/nablarch-system-development-guide/"
        "Nablarchシステム開発ガイド/docs/nablarch-patterns/")
    for f in ["Nablarchバッチ処理パターン.md", "Nablarchでの非同期処理.md", "Nablarchアンチパターン.md"]:
        fp = os.path.join(pattern_dir, f)
        if os.path.exists(fp):
            sources.append({"path": os.path.relpath(fp, repo), "format": "md", "filename": f})

    # Security Excel
    xlsx_path = os.path.join(
        repo, ".lw/nab-official/v6/nablarch-system-development-guide/"
        "Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx")
    if os.path.exists(xlsx_path):
        sources.append({"path": os.path.relpath(xlsx_path, repo),
                        "format": "xlsx", "filename": "Nablarch機能のセキュリティ対応表.xlsx"})

    # Release notes Excel
    releases_dir = os.path.join(repo, f".lw/nab-official/v{version}/nablarch-document/ja/releases/")
    if os.path.exists(releases_dir):
        for f in sorted(os.listdir(releases_dir)):
            if f.endswith(".xlsx"):
                sources.append({"path": os.path.relpath(os.path.join(releases_dir, f), repo),
                                "format": "xlsx", "filename": f})

    return sources


# ============================================================
# Step 2: Classify
# ============================================================

def classify_rst(path: str):
    marker = "nablarch-document/ja/"
    idx = path.find(marker)
    if idx < 0:
        return None, None, None
    rel_path = path[idx + len(marker):]

    if rel_path == "index.rst":
        return "about", "about-nablarch", ""

    for pattern, type_, category in RST_MAPPING:
        if pattern in rel_path:
            return type_, category, pattern

    return None, None, None


def title_to_section_id(title: str) -> str:
    ascii_id = re.sub(r'[^a-zA-Z0-9-]', '', title.replace(' ', '-')).lower().strip('-')
    ascii_id = re.sub(r'-+', '-', ascii_id)
    if ascii_id and len(ascii_id) >= 3:
        return ascii_id[:50]
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    return f"sec-{h}"


def generate_id(filename: str, format: str, category: str = None,
                source_path: str = None, matched_pattern: str = None) -> str:
    if format == "xlsx" and filename in XLSX_MAPPING:
        return category

    if format == "rst":
        base_name = filename.replace(".rst", "")
    elif format == "md":
        base_name = filename.replace(".md", "")
    elif format == "xlsx":
        base_name = filename.replace(".xlsx", "")
    else:
        base_name = filename

    if base_name == "index" and source_path and matched_pattern is not None:
        marker = "nablarch-document/ja/"
        marker_idx = source_path.find(marker)
        if marker_idx >= 0:
            rst_rel = source_path[marker_idx + len(marker):]
            pattern_clean = matched_pattern.rstrip("/")
            if not pattern_clean:
                base_name = "top"
            else:
                pat_idx = rst_rel.find(pattern_clean)
                if pat_idx >= 0:
                    remainder = rst_rel[pat_idx + len(pattern_clean):].strip("/")
                    if remainder == "index.rst":
                        base_name = os.path.basename(pattern_clean)
                    else:
                        dir_part = os.path.dirname(remainder)
                        base_name = dir_part.replace("/", "-").replace("_", "-")

    if category:
        return f"{category}-{base_name}"
    return base_name


def classify_excel_by_pattern(filename: str):
    if filename.endswith("-releasenote.xlsx"):
        return ("releases", "releases")
    return None


def analyze_rst_sections(content: str) -> list:
    lines = content.splitlines()
    sections = []
    for i in range(len(lines) - 1):
        if re.match(r'^-{5,}$', lines[i + 1]):
            title = lines[i].strip()
            sections.append({'title': title, 'start_line': i, 'level': 'h2'})

    if sections:
        sections[0]['start_line'] = 0

    for i in range(len(sections)):
        start = sections[i]['start_line']
        end = sections[i + 1]['start_line'] if i + 1 < len(sections) else len(lines)
        sections[i]['end_line'] = end
        sections[i]['line_count'] = end - start

    return sections


def analyze_h3_subsections(content: str, h2_start: int, h2_end: int) -> list:
    lines = content.splitlines()
    subsections = []
    h3_pattern = re.compile(r'^[\^~+*.]{5,}$')

    for i in range(h2_start, h2_end - 1):
        if i + 1 < len(lines):
            if h3_pattern.match(lines[i + 1]) and not re.match(r'^[-=]{5,}$', lines[i + 1]):
                subsections.append({'title': lines[i].strip(), 'start_line': i, 'level': 'h3'})

    for i in range(len(subsections)):
        start = subsections[i]['start_line']
        end = subsections[i + 1]['start_line'] if i + 1 < len(subsections) else h2_end
        subsections[i]['end_line'] = end
        subsections[i]['line_count'] = end - start

    return subsections


def expand_large_sections(sections: list, content: str) -> list:
    expanded = []
    for section in sections:
        if section['line_count'] > LINE_GROUP_THRESHOLD:
            h3_subs = analyze_h3_subsections(content, section['start_line'], section['end_line'])
            if h3_subs:
                if h3_subs[0]['start_line'] > section['start_line']:
                    h3_subs[0]['start_line'] = section['start_line']
                    h3_subs[0]['line_count'] = h3_subs[0]['end_line'] - h3_subs[0]['start_line']
                expanded.extend(h3_subs)
            else:
                expanded.append(section)
        else:
            expanded.append(section)
    return expanded


def group_sections_by_lines(sections: list) -> list:
    if not sections:
        return []
    groups = []
    current_group = []
    current_count = 0
    for section in sections:
        new_total = current_count + section['line_count']
        if current_group and new_total > LINE_GROUP_THRESHOLD:
            groups.append(current_group)
            current_group = [section]
            current_count = section['line_count']
        else:
            current_group.append(section)
            current_count = new_total
    if current_group:
        groups.append(current_group)
    return groups


def generate_split_entries(base_entry: dict, groups: list) -> list:
    result = []
    base_id = base_entry['id']
    type_ = base_entry['type']
    category = base_entry['category']
    total_parts = len(groups)
    used_ids = set()

    for part_num, group in enumerate(groups, 1):
        section_id = title_to_section_id(group[0]['title'])
        original_section_id = section_id
        counter = 2
        while section_id in used_ids:
            section_id = f"{original_section_id}-{counter}"
            counter += 1
        used_ids.add(section_id)
        split_id = f"{base_id}--{section_id}"

        start_line = group[0]['start_line']
        end_line = group[-1]['end_line']
        section_titles = [s['title'] for s in group]

        result.append({
            **base_entry,
            'id': split_id,
            'base_name': base_id,
            'output_path': f"{type_}/{category}/{split_id}.json",
            'assets_dir': f"{type_}/{category}/assets/{split_id}/",
            'section_range': {
                'start_line': start_line,
                'end_line': end_line,
                'sections': section_titles,
            },
            'split_info': {
                'is_split': True,
                'part': part_num,
                'total_parts': total_parts,
                'original_id': base_id,
                'group_line_count': sum(s['line_count'] for s in group),
            },
        })
    return result


def dedup_ids(classified: list, repo: str) -> list:
    """Deduplicate IDs by adding ancestor directory names."""
    id_counts = Counter(e['id'] for e in classified)
    dup_ids = {k for k, v in id_counts.items() if v > 1}
    if not dup_ids:
        return classified

    for dup_id in dup_ids:
        group = [e for e in classified if e['id'] == dup_id]

        resolved_depth = None
        for depth in range(1, 6):
            suffixes = []
            for e in group:
                d = os.path.dirname(os.path.join(repo, e['source_path']))
                for _ in range(depth - 1):
                    d = os.path.dirname(d)
                suffixes.append(os.path.basename(d))
            if len(set(suffixes)) == len(group):
                resolved_depth = depth
                break

        if resolved_depth is None:
            raise ValueError(f"Cannot dedup {dup_id}")

        for e in group:
            d = os.path.dirname(os.path.join(repo, e['source_path']))
            for _ in range(resolved_depth - 1):
                d = os.path.dirname(d)
            suffix = os.path.basename(d)
            old_id = e['id']

            if '--' in old_id and 'split_info' in e:
                base, split_sfx = old_id.split('--', 1)
                new_id = f"{base}-{suffix}--{split_sfx}"
            else:
                new_id = f"{old_id}-{suffix}"

            e['id'] = new_id
            e['base_name'] = new_id.split('--')[0] if 'split_info' in e else new_id
            e['output_path'] = e['output_path'].replace(f"{old_id}.json", f"{new_id}.json")
            e['assets_dir'] = e['assets_dir'].replace(f"assets/{old_id}/", f"assets/{new_id}/")
            if 'split_info' in e:
                e['split_info']['original_id'] = f"{e['split_info']['original_id']}-{suffix}"

    # Verify
    id_counts2 = Counter(e['id'] for e in classified)
    still_dup = {k for k, v in id_counts2.items() if v > 1}
    if still_dup:
        raise ValueError(f"Dedup failed: {still_dup}")

    return classified


def classify_all(sources: list, repo: str) -> list:
    classified = []

    for source in sources:
        fmt = source["format"]
        filename = source["filename"]
        path = source["path"]

        type_ = category = matched_pattern = None
        if fmt == "rst":
            type_, category, matched_pattern = classify_rst(path)
        elif fmt == "md":
            if filename in MD_MAPPING:
                type_, category = MD_MAPPING[filename]
        elif fmt == "xlsx":
            if filename in XLSX_MAPPING:
                type_, category = XLSX_MAPPING[filename]
            else:
                result = classify_excel_by_pattern(filename)
                if result:
                    type_, category = result

        if type_ is None or category is None:
            continue

        file_id = generate_id(filename, fmt, category,
                              source_path=path, matched_pattern=matched_pattern)
        classified.append({
            "source_path": path,
            "format": fmt,
            "filename": filename,
            "type": type_,
            "category": category,
            "id": file_id,
            "base_name": file_id,
            "output_path": f"{type_}/{category}/{file_id}.json",
            "assets_dir": f"{type_}/{category}/assets/{file_id}/",
        })

    # Split
    final = []
    for entry in classified:
        if entry["format"] != "rst":
            final.append(entry)
            continue

        full_path = os.path.join(repo, entry["source_path"])
        if not os.path.exists(full_path):
            final.append(entry)
            continue

        with open(full_path, encoding="utf-8") as f:
            content = f.read()

        sections = analyze_rst_sections(content)
        if len(sections) >= SPLIT_SECTION_THRESHOLD:
            expanded = expand_large_sections(sections, content)
            groups = group_sections_by_lines(expanded)
            split_entries = generate_split_entries(entry, groups)
            final.extend(split_entries)
        else:
            final.append(entry)

    # Dedup
    final = dedup_ids(final, repo)

    return final


# ============================================================
# CC Mock rules (expected knowledge content)
# ============================================================

def mock_phase_b_knowledge(file_id: str, entry: dict) -> dict:
    """Generate expected Phase B knowledge output for a file."""
    if 'section_range' in entry:
        sections = entry['section_range'].get('sections', [])
        n_sections = len(sections)  # all sections (including empty strings)
        if n_sections == 0:
            n_sections = 5
    else:
        n_sections = 5

    sec_ids = [f"sec-{i}" for i in range(n_sections)]
    return {
        "id": file_id,
        "title": f"Title for {file_id}",
        "no_knowledge_content": False,
        "official_doc_urls": [f"https://nablarch.github.io/docs/LATEST/doc/{file_id}"],
        "processing_patterns": [],
        "index": [
            {"id": sid, "title": f"Section {i}", "hints": [f"hint-{file_id}-{i}"]}
            for i, sid in enumerate(sec_ids)
        ],
        "sections": {
            sid: f"Content for {file_id} section {sid}"
            for sid in sec_ids
        },
    }


def mock_phase_b_trace(file_id: str, entry: dict) -> dict:
    """Generate expected Phase B trace output."""
    knowledge = mock_phase_b_knowledge(file_id, entry)
    return {
        "file_id": file_id,
        "generated_at": "TIMESTAMP",
        "sections": [
            {"section_id": e["id"], "source_heading": e["title"],
             "heading_level": "h2", "h3_split": False,
             "h3_split_reason": "mock"}
            for e in knowledge["index"]
        ],
    }


def mock_phase_e_knowledge(file_id: str, entry: dict) -> dict:
    """Generate expected Phase E (fix) output — same as B with '-fixed' suffix."""
    k = mock_phase_b_knowledge(file_id, entry)
    k["sections"] = {
        sid: f"{content}-fixed"
        for sid, content in k["sections"].items()
    }
    return k


# ============================================================
# Merge logic (expected merge output)
# ============================================================

def compute_merged_files(catalog_entries: list, knowledge_fn=None) -> dict:
    """Compute expected merged knowledge files.

    Returns:
        {merged_id: merged_knowledge_dict}
    """
    if knowledge_fn is None:
        knowledge_fn = mock_phase_b_knowledge
    # Group split entries
    split_groups = {}
    non_split = []
    for e in catalog_entries:
        if 'split_info' in e and e['split_info'].get('is_split'):
            oid = e['split_info']['original_id']
            split_groups.setdefault(oid, []).append(e)
        else:
            non_split.append(e)

    merged = {}

    # Split groups
    for oid, parts in split_groups.items():
        parts.sort(key=lambda p: p['split_info']['part'])
        first_knowledge = knowledge_fn(parts[0]['id'], parts[0])

        merged_knowledge = {
            "id": oid,
            "title": first_knowledge["title"],
            "official_doc_urls": [],
        }

        # Merge urls (dedup, preserve order)
        seen_urls = set()
        urls = []
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for url in pk.get("official_doc_urls", []):
                if url not in seen_urls:
                    seen_urls.add(url)
                    urls.append(url)
        merged_knowledge["official_doc_urls"] = urls

        # Merge processing_patterns (union, dedup, preserve order)
        seen_pp = set()
        pp_list = []
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for pp in pk.get("processing_patterns", []):
                if pp not in seen_pp:
                    seen_pp.add(pp)
                    pp_list.append(pp)
        merged_knowledge["processing_patterns"] = pp_list

        # Merge index: part-sequential order, dedup by id, merge hints
        merged_index = []
        seen_ids = {}
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for entry in pk.get("index", []):
                sid = entry["id"]
                if sid not in seen_ids:
                    seen_ids[sid] = len(merged_index)
                    merged_index.append({"id": sid, "title": entry["title"],
                                         "hints": list(entry.get("hints", []))})
                else:
                    existing_entry = merged_index[seen_ids[sid]]
                    existing_hints = set(existing_entry["hints"])
                    for h in entry.get("hints", []):
                        if h not in existing_hints:
                            existing_entry["hints"].append(h)
                            existing_hints.add(h)
        merged_knowledge["index"] = merged_index

        # Merge sections
        merged_sections = {}
        for p in parts:
            pk = knowledge_fn(p['id'], p)
            for sid, content in pk.get("sections", {}).items():
                content = content.replace(f"assets/{p['id']}/", f"assets/{oid}/")
                if sid not in merged_sections:
                    merged_sections[sid] = content
                else:
                    merged_sections[sid] += "\n\n" + content
        merged_knowledge["sections"] = merged_sections

        merged[oid] = merged_knowledge

    # Non-split
    for e in non_split:
        k = knowledge_fn(e['id'], e)
        merged[e['id']] = k

    return merged


# ============================================================
# Main: generate all expected values
# ============================================================

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <repo_root> <output_path>")
        sys.exit(1)

    repo = os.path.abspath(sys.argv[1])
    output_path = sys.argv[2]

    # Step 1: List sources
    sources = list_sources(repo, "6")
    print(f"Sources: {len(sources)}")

    # Step 2: Classify + split + dedup
    catalog_entries = classify_all(sources, repo)
    print(f"Catalog entries: {len(catalog_entries)}")

    ids = [e['id'] for e in catalog_entries]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[k for k,v in Counter(ids).items() if v>1]}"
    print(f"Unique IDs: {len(set(ids))} (no duplicates)")

    # Compute derived values
    split_entries = [e for e in catalog_entries if 'split_info' in e]
    non_split_entries = [e for e in catalog_entries if 'split_info' not in e]
    split_groups = {}
    for e in split_entries:
        oid = e['split_info']['original_id']
        split_groups.setdefault(oid, []).append(e)

    merged_files = compute_merged_files(catalog_entries)
    pp_type_merged = set()
    for e in catalog_entries:
        if e['type'] == 'processing-pattern':
            if 'split_info' in e:
                pp_type_merged.add(e['split_info']['original_id'])
            else:
                pp_type_merged.add(e['id'])

    f_target = len(merged_files) - len(pp_type_merged)

    # Phase B expected knowledge for each entry
    expected_knowledge_cache = {}
    for e in catalog_entries:
        expected_knowledge_cache[e['id']] = mock_phase_b_knowledge(e['id'], e)

    # Phase B expected traces
    expected_traces = {}
    for e in catalog_entries:
        expected_traces[e['id']] = mock_phase_b_trace(e['id'], e)

    # Phase E expected (fixed) knowledge
    expected_fixed_cache = {}
    for e in catalog_entries:
        expected_fixed_cache[e['id']] = mock_phase_e_knowledge(e['id'], e)

    # index.toon expected lines
    index_entries = []
    for mid, mk in sorted(merged_files.items()):
        # Find the catalog entry for type/category
        entry = None
        for e in catalog_entries:
            base = e.get('base_name', e['id'])
            if base == mid or e['id'] == mid:
                entry = e
                break
            if 'split_info' in e and e['split_info']['original_id'] == mid:
                entry = e
                break
        if entry:
            type_ = entry['type']
            category = entry['category']
            pp = category if type_ == 'processing-pattern' else ''
            path = f"{type_}/{category}/{mid}.json"
            title = mk['title'].replace(',', '、')
            index_entries.append(f"  {title}, {type_}, {category}, {pp}, {path}")

    # Persistent error 24 base_names -> split IDs
    persistent_error_base_names = [
        "adapters-doma_adaptor", "adapters-redisstore_lettuce_adaptor",
        "blank-project-CustomizeDB", "blank-project-setup_ContainerWeb",
        "cloud-native-aws_distributed_tracing", "db-messaging-multiple_process",
        "handlers-SessionStoreHandler", "handlers-csrf_token_verification_handler",
        "handlers-thread_context_handler", "java-static-analysis-java_static_analysis",
        "libraries-bean_validation", "libraries-database",
        "libraries-failure_log", "libraries-log",
        "libraries-service_availability", "libraries-tag",
        "libraries-tag_reference", "mom-messaging-feature_details",
        "nablarch-batch-architecture", "restful-web-service-architecture",
        "testing-framework-02_entityUnitTestWithNablarchValidation",
        "testing-framework-batch",
        "testing-framework-guide-development-guide-05-UnitTestGuide-02-RequestUnitTest",
        "toolbox-NablarchOpenApiGenerator",
    ]

    split_ids_24 = []
    for bn in persistent_error_base_names:
        matched = [e['id'] for e in catalog_entries if e.get('base_name') == bn]
        split_ids_24.extend(matched)

    # Build output
    output = {
        "params": {
            "N": len(catalog_entries),
            "U": len(set(ids)),
            "M": len(merged_files),
            "F_TARGET": f_target,
            "split_entries": len(split_entries),
            "non_split_entries": len(non_split_entries),
            "split_groups": len(split_groups),
            "pp_type_merged": len(pp_type_merged),
            "split_ids_24": split_ids_24,
            "split_ids_24_count": len(split_ids_24),
        },
        "catalog_entries": catalog_entries,
        "expected_knowledge_cache": expected_knowledge_cache,
        "expected_traces": {k: v for k, v in expected_traces.items()},
        "expected_fixed_cache": expected_fixed_cache,
        "expected_merged_knowledge": {k: v for k, v in merged_files.items()},
        "expected_index_toon_header": f"# Nabledge-6 Knowledge Index\n\nfiles[{len(merged_files)},]{{title,type,category,processing_patterns,path}}:",
        "expected_index_toon_entry_count": len(merged_files),
    }

    # Summary
    print(f"\nParameters:")
    for k, v in output["params"].items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
        else:
            print(f"  {k}: {v}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
