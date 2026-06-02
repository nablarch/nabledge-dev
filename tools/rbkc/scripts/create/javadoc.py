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

from scripts.common.javadoc_fqcn import class_fqcn as _class_fqcn


def fqcn_to_file_id(fqcn: str) -> str:
    """Convert class FQCN to file_id.

    nablarch.common.dao.UniversalDao → javadoc-nablarch-common-dao-UniversalDao
    """
    return "javadoc-" + fqcn.replace(".", "-")


# ---------------------------------------------------------------------------
# FQCN extraction from RST
# ---------------------------------------------------------------------------

# Matches :java:extdoc:`DisplayText <FQCN>` using partition logic:
# The FQCN is everything between the first `<` and the last `>` in the backtick.
# We use a simple regex on the raw RST text (not docutils AST) for the
# collection pass — precision of the FQCN boundary is handled by _class_fqcn.
_EXTDOC_RE = re.compile(
    r":java:extdoc:`([^`]+)`"
)


def _extract_fqcns(rst_text: str) -> set[str]:
    """Extract nablarch.* class FQCNs from RST text.

    Handles display-text form (:java:extdoc:`DisplayText <FQCN>`) and
    bare form (:java:extdoc:`FQCN`).  Method/constructor suffixes are
    stripped to return class FQCNs only.
    """
    fqcns: set[str] = set()
    for m in _EXTDOC_RE.finditer(rst_text):
        raw = m.group(1).strip()
        # Display-text form: use partition (first <) to avoid <init> confusion
        if "<" in raw and raw.rstrip().endswith(">"):
            _, _, fqcn_part = raw.partition("<")
            fqcn_part = fqcn_part.rstrip(">").strip()
        else:
            fqcn_part = raw
        cls = _class_fqcn(fqcn_part)
        if cls is not None and cls.startswith("nablarch."):
            fqcns.add(cls)
    return fqcns


def collect_fqcns(version: str, repo_root: Path) -> set[str]:
    """Scan all RST files for the given version and return nablarch.* class FQCNs."""
    from scripts.common.sources import _source_roots
    fqcns: set[str] = set()
    for src_root in _source_roots(version, repo_root):
        if not src_root.exists():
            continue
        for rst_path in src_root.rglob("*.rst"):
            text = rst_path.read_text(encoding="utf-8", errors="replace")
            fqcns.update(_extract_fqcns(text))
    return fqcns


# ---------------------------------------------------------------------------
# Artifact resolution (FQCN → groupId:artifactId:version)
# ---------------------------------------------------------------------------

def _load_bom_artifacts(bom_pom: Path) -> list[tuple[str, str, str]]:
    """Parse BOM POM and return [(groupId, artifactId, version), ...]."""
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
    mapping = {"6": "6u3", "5": "5u26"}
    return mapping.get(version, version)


def _get_bom_pom(version: str, repo_root: Path) -> Path | None:
    bom_ver = _bom_version(version)
    m2_root = Path.home() / ".m2" / "repository"
    pom_path = (
        m2_root / "com/nablarch/profile/nablarch-bom" / bom_ver
        / f"nablarch-bom-{bom_ver}.pom"
    )
    if pom_path.exists():
        return pom_path
    _mvn_get(f"com.nablarch.profile:nablarch-bom:{bom_ver}:pom")
    return pom_path if pom_path.exists() else None


def _mvn_get(artifact_spec: str, classifier: str = "") -> bool:
    cmd = ["mvn", "dependency:get", f"-Dartifact={artifact_spec}", "-q"]
    if classifier:
        cmd.append(f"-Dclassifier={classifier}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"WARN javadoc: mvn dependency:get failed for {artifact_spec}: "
            f"{result.stderr.strip()[:200]}",
            file=sys.stderr,
        )
        return False
    return True


# ---------------------------------------------------------------------------
# sources.jar download and .java extraction
# ---------------------------------------------------------------------------

def _sources_jar_path(group_id: str, artifact_id: str, version: str) -> Path:
    m2_root = Path.home() / ".m2" / "repository"
    group_path = group_id.replace(".", "/")
    jar_name = f"{artifact_id}-{version}-sources.jar"
    return m2_root / group_path / artifact_id / version / jar_name


def _fetch_sources_jars(version: str, repo_root: Path) -> dict[str, Path]:
    """Download sources.jar for all BOM artifacts and return {artifactId: jar_path}."""
    bom_pom = _get_bom_pom(version, repo_root)
    if bom_pom is None:
        print(f"WARN javadoc: could not locate BOM POM for version {version}", file=sys.stderr)
        return {}

    artifacts = _load_bom_artifacts(bom_pom)
    result: dict[str, Path] = {}
    for group_id, artifact_id, art_ver in artifacts:
        jar_path = _sources_jar_path(group_id, artifact_id, art_ver)
        if not jar_path.exists():
            _mvn_get(f"{group_id}:{artifact_id}:{art_ver}", classifier="sources")
        if jar_path.exists():
            result[artifact_id] = jar_path
    return result


def _extract_java_files(
    sources_jars: dict[str, Path],
    fqcns: set[str],
    extract_dir: Path,
) -> dict[str, Path]:
    """Extract .java source files matching fqcns from sources jars.

    Returns {class_fqcn: java_path} for each successfully extracted class.
    """
    fqcn_to_relpath: dict[str, str] = {
        fqcn: fqcn.replace(".", "/") + ".java"
        for fqcn in fqcns
    }
    remaining: dict[str, str] = dict(fqcn_to_relpath)
    found: dict[str, Path] = {}

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

    return found


# ---------------------------------------------------------------------------
# Javadoc MD → Knowledge JSON conversion
# ---------------------------------------------------------------------------

def _parse_javadoc_md(md_text: str, file_id: str = "") -> dict:
    """Parse jar-generated Javadoc Markdown into the RBKC JSON schema.

    Javadoc MD structure:
        # class ClassName           → title
        [preamble text]             → top-level content
        ## フィールドの詳細         → Section(level=2)
        ## コンストラクタの詳細    → Section(level=2)
        ## メソッドの詳細          → Section(level=2)
        ### methodName              → Section(level=3)
            ```java ...```          → content
            description text        → content (appended)
    """
    lines = md_text.splitlines()
    title = ""
    top_content_lines: list[str] = []
    sections: list[dict] = []

    state = "before_title"
    current_section: dict | None = None
    current_content_lines: list[str] = []

    def _flush_section() -> None:
        nonlocal current_section, current_content_lines
        if current_section is not None:
            current_section["content"] = "\n".join(current_content_lines).strip()
            sections.append(current_section)
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

    # Assign sequential section ids
    for i, s in enumerate(sections, start=1):
        s["id"] = f"s{i}"

    result: dict = {
        "title": title,
        "content": top_content,
        "no_knowledge_content": False,
        "sections": sections,
    }
    if file_id:
        result["id"] = file_id
    return result


# ---------------------------------------------------------------------------
# jar runner
# ---------------------------------------------------------------------------

def _run_converter_jar(java_path: Path, jar_path: Path) -> str | None:
    """Run source-to-document-converter.jar on a .java file."""
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
    """Write docs MD for a Javadoc knowledge file."""
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

    Returns javadoc_map {class_fqcn: file_id} for successfully generated files.
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
    fqcn_to_java = _extract_java_files(sources_jars, fqcns, extract_dir)
    print(
        f"javadoc_generate: {len(fqcn_to_java)} / {len(fqcns)} FQCNs resolved",
        file=sys.stderr,
    )

    javadoc_map: dict[str, str] = {}
    print(
        f"javadoc_generate: converting {len(fqcn_to_java)} classes...",
        file=sys.stderr,
    )
    for cls_fqcn, java_path in fqcn_to_java.items():
        file_id = fqcn_to_file_id(cls_fqcn)
        out_json = output_dir / "javadoc" / f"{file_id}.json"
        if out_json.exists():
            javadoc_map[cls_fqcn] = file_id
            continue

        md_text = _run_converter_jar(java_path, jar_path)
        if md_text is None:
            continue

        data = _parse_javadoc_md(md_text, file_id=file_id)
        _write_json(data, file_id, output_dir)
        _write_docs_md(data, file_id, docs_dir)
        javadoc_map[cls_fqcn] = file_id

    print(
        f"javadoc_generate: complete — {len(javadoc_map)} knowledge files written",
        file=sys.stderr,
    )
    return javadoc_map
