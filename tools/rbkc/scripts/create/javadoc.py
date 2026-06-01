"""Javadoc knowledge file generator (Issue #363).

Generates knowledge JSON files for Nablarch API classes referenced via
:java:extdoc: roles in RST source files.

Pipeline (called from run.py create before RST conversion):
    1. Scan all RST files to collect nablarch.* FQCNs from :java:extdoc:
    2. Download sources.jar for each artifact via mvn dependency:get
    3. Extract .java files from sources.jar
    4. Run source-to-document-converter.jar on each .java file → Javadoc MD
    5. Convert Javadoc MD to knowledge JSON schema and write to output_dir/javadoc/
    6. Generate docs MD to docs_dir/javadoc/
    7. Return javadoc_map (FQCN → file_id)

Public API:
    javadoc_generate(version, repo_root, output_dir, docs_dir) -> dict[str, str]
        Returns {fqcn: file_id} for all successfully generated files.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# FQCN extraction from RST
# ---------------------------------------------------------------------------

# Matches :java:extdoc:`DisplayText <nablarch.some.Class>` or
# :java:extdoc:`nablarch.some.Class` (no angle brackets)
_EXTDOC_RE = re.compile(
    r":java:extdoc:`[^`]*?<([^>`]+)>`|:java:extdoc:`([^`<>]+)`"
)


def _extract_fqcns(rst_text: str) -> set[str]:
    """Extract nablarch.* FQCNs from RST text.

    FQCNs may include method suffixes like:
      nablarch.common.dao.UniversalDao.insert(java.lang.Object)
    Strip everything after the first '(' and keep the class part only.
    """
    fqcns: set[str] = set()
    for m in _EXTDOC_RE.finditer(rst_text):
        raw = (m.group(1) or m.group(2) or "").strip()
        # Strip method/field suffix: keep up to the first '(' or space
        class_part = raw.split("(")[0].strip()
        if class_part.startswith("nablarch."):
            # Further strip trailing method ref like .methodName after the class
            # heuristic: last segment is class if it starts with uppercase
            fqcns.add(class_part)
    return fqcns


def collect_fqcns(version: str, repo_root: Path) -> set[str]:
    """Scan all RST files for the given version and return nablarch.* FQCNs."""
    from scripts.common.sources import _source_roots  # type: ignore[attr-defined]
    fqcns: set[str] = set()
    for src_root in _source_roots(version, repo_root):
        if not src_root.exists():
            continue
        for rst_path in src_root.rglob("*.rst"):
            text = rst_path.read_text(encoding="utf-8", errors="replace")
            fqcns.update(_extract_fqcns(text))
    return fqcns


# ---------------------------------------------------------------------------
# FQCN → file_id
# ---------------------------------------------------------------------------

def fqcn_to_file_id(fqcn: str) -> str:
    """Convert FQCN to file_id.

    nablarch.common.dao.UniversalDao → javadoc-nablarch-common-dao-UniversalDao
    """
    return "javadoc-" + fqcn.replace(".", "-")


# ---------------------------------------------------------------------------
# Artifact resolution (FQCN → groupId:artifactId:version)
# ---------------------------------------------------------------------------

def _load_bom_artifacts(bom_pom: Path) -> list[tuple[str, str, str]]:
    """Parse BOM POM and return [(groupId, artifactId, version), ...].

    Uses stdlib xml.etree since lxml is not a project dependency.
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(str(bom_pom))
    root = tree.getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    artifacts = []
    for dep in root.findall(".//m:dependencyManagement/m:dependencies/m:dependency", ns):
        g = dep.find("m:groupId", ns)
        a = dep.find("m:artifactId", ns)
        v = dep.find("m:version", ns)
        if g is not None and a is not None and v is not None:
            artifacts.append((g.text.strip(), a.text.strip(), v.text.strip()))
    return artifacts


def _bom_version(version: str) -> str:
    """Map Nablarch version string to BOM artifact version."""
    mapping = {
        "6": "6u3",
        "5": "5u26",
    }
    return mapping.get(version, version)


def _get_bom_pom(version: str, repo_root: Path) -> Path | None:
    """Return path to the BOM POM from the local Maven repository."""
    bom_ver = _bom_version(version)
    m2_root = Path.home() / ".m2" / "repository"
    pom_path = m2_root / "com/nablarch/profile/nablarch-bom" / bom_ver / f"nablarch-bom-{bom_ver}.pom"
    if pom_path.exists():
        return pom_path
    # Download BOM POM
    _mvn_get(f"com.nablarch.profile:nablarch-bom:{bom_ver}:pom")
    return pom_path if pom_path.exists() else None


def _mvn_get(artifact_spec: str, classifier: str = "") -> bool:
    """Run mvn dependency:get to fetch an artifact to local .m2 cache.

    For sources jars, artifact_spec must include the classifier suffix:
    ``groupId:artifactId:version:jar:sources``

    Returns True on success.
    """
    if classifier:
        # Maven dependency:get requires the full coordinate with packaging+classifier:
        # groupId:artifactId:version → groupId:artifactId:version:jar:sources
        full_spec = f"{artifact_spec}:jar:{classifier}"
    else:
        full_spec = artifact_spec
    cmd = [
        "mvn", "dependency:get",
        f"-Dartifact={full_spec}",
        "-q",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"WARN javadoc: mvn dependency:get failed for {full_spec}: "
            f"{result.stderr.strip()[:200]}",
            file=sys.stderr,
        )
        return False
    return True


# ---------------------------------------------------------------------------
# sources.jar download and .java extraction
# ---------------------------------------------------------------------------

def _sources_jar_path(group_id: str, artifact_id: str, version: str) -> Path:
    """Return the expected local .m2 path for a sources jar."""
    m2_root = Path.home() / ".m2" / "repository"
    group_path = group_id.replace(".", "/")
    jar_name = f"{artifact_id}-{version}-sources.jar"
    return m2_root / group_path / artifact_id / version / jar_name


def _fetch_sources_jars(
    version: str, repo_root: Path
) -> dict[str, Path]:
    """Download sources.jar for all BOM artifacts and return {artifactId: jar_path}.

    Only artifacts with successfully downloaded sources.jar are included.
    """
    bom_pom = _get_bom_pom(version, repo_root)
    if bom_pom is None:
        print(f"WARN javadoc: could not locate BOM POM for version {version}", file=sys.stderr)
        return {}

    artifacts = _load_bom_artifacts(bom_pom)
    result: dict[str, Path] = {}

    for group_id, artifact_id, art_ver in artifacts:
        jar_path = _sources_jar_path(group_id, artifact_id, art_ver)
        if not jar_path.exists():
            spec = f"{group_id}:{artifact_id}:{art_ver}"
            _mvn_get(spec, classifier="sources")
        if jar_path.exists():
            result[artifact_id] = jar_path

    return result


def _extract_java_files(
    sources_jars: dict[str, Path],
    fqcns: set[str],
    extract_dir: Path,
) -> dict[str, Path]:
    """Extract .java source files matching fqcns from sources jars.

    Returns {fqcn: java_path} for each successfully extracted class.
    Note: A single FQCN may contain a method suffix; we strip it to get the
    class path.  Multiple FQCNs mapping to the same class are deduplicated.
    """
    # Build a set of unique class FQCNs (strip method refs)
    class_fqcns: set[str] = set()
    for fqcn in fqcns:
        class_fqcns.add(_class_fqcn(fqcn))

    # Map class FQCN → expected .java relative path
    # e.g. nablarch.common.dao.UniversalDao → nablarch/common/dao/UniversalDao.java
    fqcn_to_relpath: dict[str, str] = {
        fqcn: fqcn.replace(".", "/") + ".java"
        for fqcn in class_fqcns
    }

    remaining: dict[str, str] = dict(fqcn_to_relpath)  # fqcn → rel path (not yet found)
    found: dict[str, Path] = {}  # fqcn → extracted absolute path

    for artifact_id, jar_path in sources_jars.items():
        if not remaining:
            break
        try:
            with zipfile.ZipFile(jar_path, "r") as zf:
                zip_names = set(zf.namelist())
                to_extract = {
                    fqcn: rel for fqcn, rel in list(remaining.items())
                    if rel in zip_names
                }
                for fqcn, rel in to_extract.items():
                    dest = extract_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(zf.read(rel))
                    found[fqcn] = dest
                    del remaining[fqcn]
        except (zipfile.BadZipFile, OSError) as e:
            print(f"WARN javadoc: could not read {jar_path}: {e}", file=sys.stderr)

    for fqcn in remaining:
        print(f"WARN javadoc: .java not found in any sources.jar: {fqcn}", file=sys.stderr)

    # Build fqcn → java_path for all original FQCNs (including method-suffixed ones)
    result: dict[str, Path] = {}
    for fqcn in fqcns:
        cls = _class_fqcn(fqcn)
        if cls in found:
            result[fqcn] = found[cls]
    return result


def _class_fqcn(fqcn: str) -> str:
    """Strip method/field suffix from a FQCN to get the class FQCN.

    nablarch.common.dao.UniversalDao.insert → nablarch.common.dao.UniversalDao
    (heuristic: last segment starting with uppercase = class boundary)
    """
    parts = fqcn.split(".")
    # Find last segment starting with uppercase — that's the class
    for i, part in enumerate(parts):
        if part and part[0].isupper():
            return ".".join(parts[: i + 1])
    return fqcn


# ---------------------------------------------------------------------------
# Javadoc MD → Knowledge JSON conversion
# ---------------------------------------------------------------------------

def _parse_javadoc_md(md_text: str) -> dict:
    """Parse jar-generated Javadoc Markdown into the RBKC JSON schema.

    Javadoc MD structure:
        # class ClassName           → title
        [preamble text]             → top-level content
        ## フィールドの詳細         → Section(level=2)
        ## コンストラクタの詳細    → Section(level=2)
        ## メソッドの詳細          → Section(level=2)
        ### methodName              → Section(level=3)
            ```java ...```          → content
            description text       → content (appended)

    Each section dict includes "id" (s1, s2, ...) as required by index.py.
    """
    lines = md_text.splitlines()
    title = ""
    top_content_lines: list[str] = []
    raw_sections: list[dict] = []  # no id yet

    state = "before_title"  # before_title | top_content | in_section
    current_section: dict | None = None
    current_content_lines: list[str] = []

    def _flush_section():
        nonlocal current_section, current_content_lines
        if current_section is not None:
            current_section["content"] = "\n".join(current_content_lines).strip()
            raw_sections.append(current_section)
            current_section = None
            current_content_lines = []

    for line in lines:
        if state == "before_title":
            if line.startswith("# "):
                title = line[2:].strip()
                state = "top_content"
            continue

        if state == "top_content":
            if line.startswith("## "):
                _flush_section()
                current_section = {"title": line[3:].strip(), "level": 2}
                current_content_lines = []
                state = "in_section"
            else:
                top_content_lines.append(line)
            continue

        if state == "in_section":
            if line.startswith("### "):
                _flush_section()
                current_section = {"title": line[4:].strip(), "level": 3}
                current_content_lines = []
            elif line.startswith("## "):
                _flush_section()
                current_section = {"title": line[3:].strip(), "level": 2}
                current_content_lines = []
            else:
                current_content_lines.append(line)

    _flush_section()

    top_content = "\n".join(top_content_lines).strip()

    # Assign sequential ids as required by index.py
    sections = []
    for idx, sec in enumerate(raw_sections, start=1):
        sec["id"] = f"s{idx}"
        sections.append(sec)

    return {
        "title": title,
        "content": top_content,
        "no_knowledge_content": False,
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# jar runner
# ---------------------------------------------------------------------------

def _run_converter_jar(java_path: Path, jar_path: Path) -> str | None:
    """Run source-to-document-converter.jar on a .java file.

    Returns the Markdown output as a string, or None on failure.
    """
    result = subprocess.run(
        ["java", "-jar", str(jar_path), str(java_path)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        print(
            f"WARN javadoc: converter jar failed for {java_path}: "
            f"{result.stderr.strip()[:200]}",
            file=sys.stderr,
        )
        return None
    return result.stdout


# ---------------------------------------------------------------------------
# Write JSON and docs MD
# ---------------------------------------------------------------------------

def _write_json(data: dict, file_id: str, output_dir: Path) -> None:
    out_path = output_dir / "javadoc" / f"{file_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_docs_md(data: dict, file_id: str, docs_dir: Path) -> None:
    """Write minimal docs MD for a Javadoc knowledge file.

    The docs MD lives at docs_dir/javadoc/{file_id}.md and is rendered
    from the JSON data directly (same format as docs.py _render_full but
    without asset-link rewriting, since Javadoc files have no assets).
    """
    title = data.get("title", "")
    lines = [f"# {title}", ""] if title else []

    top_content = data.get("content", "")
    if top_content:
        lines.append(top_content)
        lines.append("")

    for section in data.get("sections", []):
        sec_title = section.get("title", "")
        sec_content = section.get("content", "")
        level = section.get("level", 2)
        hashes = "#" * max(1, int(level))
        lines.append(f"{hashes} {sec_title}")
        lines.append("")
        if sec_content:
            lines.append(sec_content)
            lines.append("")

    out_path = docs_dir / "javadoc" / f"{file_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def javadoc_generate(
    version: str,
    repo_root: Path,
    output_dir: Path,
    docs_dir: Path,
) -> dict[str, str]:
    """Generate Javadoc knowledge files for all nablarch.* :java:extdoc: references.

    Steps:
        1. Collect FQCNs from RST corpus
        2. Fetch sources.jar for each BOM artifact
        3. Extract .java files for referenced FQCNs
        4. Run converter jar → Javadoc MD
        5. Convert Javadoc MD → knowledge JSON + docs MD
        6. Return javadoc_map {fqcn: file_id}

    Only runs for versions "5" and "6"; returns empty dict for other versions.
    """
    if version not in ("5", "6"):
        return {}

    jar_path = Path(__file__).parents[2] / "lib" / "source-to-document-converter-0.0.1.jar"
    if not jar_path.exists():
        print(f"WARN javadoc: converter jar not found: {jar_path}", file=sys.stderr)
        return {}

    print(f"javadoc_generate: scanning RST for FQCNs (v{version})...", file=sys.stderr)
    fqcns = collect_fqcns(version, repo_root)
    print(f"javadoc_generate: found {len(fqcns)} FQCNs", file=sys.stderr)

    if not fqcns:
        return {}

    print("javadoc_generate: fetching sources.jar artifacts...", file=sys.stderr)
    sources_jars = _fetch_sources_jars(version, repo_root)
    print(f"javadoc_generate: {len(sources_jars)} sources.jar available", file=sys.stderr)

    extract_dir = repo_root / ".tmp" / "javadoc-sources" / f"v{version}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    print("javadoc_generate: extracting .java files...", file=sys.stderr)
    fqcn_to_java: dict[str, Path] = _extract_java_files(sources_jars, fqcns, extract_dir)
    print(
        f"javadoc_generate: {len(fqcn_to_java)} / {len(fqcns)} FQCNs resolved",
        file=sys.stderr,
    )

    javadoc_map: dict[str, str] = {}
    unique_classes: dict[str, Path] = {}  # class_fqcn → java_path (deduplicated)
    for fqcn, java_path in fqcn_to_java.items():
        cls = _class_fqcn(fqcn)
        unique_classes[cls] = java_path

    print(
        f"javadoc_generate: converting {len(unique_classes)} unique classes...",
        file=sys.stderr,
    )
    for cls_fqcn, java_path in unique_classes.items():
        file_id = fqcn_to_file_id(cls_fqcn)
        out_json = output_dir / "javadoc" / f"{file_id}.json"
        if out_json.exists():
            # Already generated (e.g. incremental run); still register in map
            javadoc_map[cls_fqcn] = file_id
            continue

        md_text = _run_converter_jar(java_path, jar_path)
        if md_text is None:
            continue

        data = _parse_javadoc_md(md_text)
        data["id"] = file_id
        _write_json(data, file_id, output_dir)
        _write_docs_md(data, file_id, docs_dir)
        javadoc_map[cls_fqcn] = file_id

    # Map all original FQCNs (including method-suffixed) to their class file_id.
    # Also include class FQCNs directly so that inline_inline() can look them up
    # by both the full method FQCN and by the class FQCN after stripping method suffix.
    result: dict[str, str] = {}
    for fqcn in fqcns:
        cls = _class_fqcn(fqcn)
        if cls in javadoc_map:
            result[fqcn] = javadoc_map[cls]
    # Add class FQCNs directly (for inline_inline() class_fqcn lookup)
    for cls_fqcn, file_id in javadoc_map.items():
        result.setdefault(cls_fqcn, file_id)

    print(
        f"javadoc_generate: complete — {len(javadoc_map)} knowledge files written",
        file=sys.stderr,
    )
    return result
