"""Survey literalinclude / include usage across all versions.

Count: #occurrences, options used, target file existence, lines option
complexity, shim implementation adequacy.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path("/home/tie303177/work/nabledge/work2/.lw/nab-official")

DIRECTIVE_RE = re.compile(
    r"^(\s*)\.\.\s+(literalinclude|include)::\s*(.+?)\s*$", re.MULTILINE
)
OPTION_RE = re.compile(r"^(\s+):([a-zA-Z_-]+):(.*)$")


def survey() -> None:
    occurrences = []
    for v_dir in sorted(ROOT.glob("v*")):
        if not v_dir.is_dir():
            continue
        v = v_dir.name
        for p in v_dir.rglob("*.rst"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            lines = text.splitlines()
            for i, line in enumerate(lines):
                m = DIRECTIVE_RE.match(line)
                if not m:
                    continue
                indent, name, arg = m.groups()
                # Collect options on immediately following indented lines.
                options: dict[str, str] = {}
                j = i + 1
                base_indent = len(indent) + 3  # at least ".. " + 3
                while j < len(lines):
                    l2 = lines[j]
                    if not l2.strip():
                        j += 1
                        continue
                    om = OPTION_RE.match(l2)
                    if not om:
                        break
                    opt_indent, opt_name, opt_val = om.groups()
                    if len(opt_indent) <= len(indent):
                        break
                    options[opt_name] = opt_val.strip()
                    j += 1
                occurrences.append({
                    "version": v,
                    "file": str(p.relative_to(ROOT)),
                    "line": i + 1,
                    "directive": name,
                    "arg": arg.strip(),
                    "options": options,
                })
    # Summarize
    by_version_directive = Counter()
    option_names = Counter()
    total_options = 0
    for o in occurrences:
        by_version_directive[(o["version"], o["directive"])] += 1
        for k in o["options"]:
            option_names[k] += 1
            total_options += 1

    print(f"# Total directive occurrences: {len(occurrences)}\n")
    print("## By version × directive")
    for k, n in sorted(by_version_directive.items()):
        print(f"- {k[0]} / {k[1]}: {n}")
    print(f"\n## Option names (total option uses: {total_options})")
    for k, n in option_names.most_common():
        print(f"- :{k}: {n}")

    # Examples per option
    print("\n## Example occurrences with non-trivial options")
    non_trivial = [o for o in occurrences if o["options"] and o["directive"] == "literalinclude"]
    for o in non_trivial[:10]:
        print(f"- {o['version']} :: {o['file']}:{o['line']} arg={o['arg']!r}")
        for k, v in o["options"].items():
            print(f"    :{k}: {v!r}")


if __name__ == "__main__":
    survey()
