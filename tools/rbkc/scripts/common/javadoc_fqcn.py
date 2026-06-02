"""Shared FQCN normalisation for :java:extdoc: roles (Issue #363).

Both create (javadoc.py) and verify (verify.py) import this module so that
the same normalisation is applied in both directions (§3-1 single-source
principle).
"""
from __future__ import annotations


def class_fqcn(fqcn: str) -> str | None:
    """Normalise a raw :java:extdoc: FQCN to a class-level FQCN.

    Returns the class FQCN string, or ``None`` if the FQCN refers to a
    package (last segment is lowercase with no parentheses) — these have
    no corresponding .java file and are scope-out (quadrant 3(b)).

    Normalisation steps (applied in order):

    1. Strip ``#method`` suffix  (Javadoc anchor form).
    2. Strip ``.<init>(args)``   (docutils constructor form).
    3. If ``(`` is present → method-level RST dot-notation.
       Find the dot before the opening ``(``; if the segment after that dot
       starts with a lowercase letter it is the method name — strip it.
    4. If the last two dot-segments are both uppercase-initial → inner class.
       Strip the last segment (one level only; Nablarch inner classes are at
       most one level deep).
    5. If the last segment starts with lowercase → package reference → None.

    JDK classes (``java.*``, ``jakarta.*``, ``javax.*``) are returned
    unchanged; the caller is responsible for filtering them out.
    """
    # Step 1: strip #method suffix
    fqcn = fqcn.split("#")[0]

    # Step 2: strip .<init>(...) constructor suffix
    idx = fqcn.find(".<init>")
    if idx != -1:
        fqcn = fqcn[:idx]

    # Step 3: method-level RST dot-notation — FQCN contains '('
    if "(" in fqcn:
        paren_idx = fqcn.index("(")
        prefix = fqcn[:paren_idx]  # e.g. 'pkg.ClassName.methodName'
        dot_idx = prefix.rfind(".")
        if dot_idx == -1:
            return None  # degenerate — no class boundary
        method_name = prefix[dot_idx + 1:]
        if method_name and method_name[0].islower():
            # lowercase-initial segment → method name, strip it
            fqcn = prefix[:dot_idx]
        else:
            # uppercase-initial segment before '(' — treat as class (e.g. <T>)
            fqcn = prefix

    # Step 4: inner class — last two segments both uppercase-initial
    parts = fqcn.split(".")
    if (
        len(parts) >= 2
        and parts[-1] and parts[-1][0].isupper()
        and parts[-2] and parts[-2][0].isupper()
    ):
        fqcn = ".".join(parts[:-1])

    # Step 5: package-level — last segment is lowercase-initial, no parens
    parts = fqcn.split(".")
    if parts[-1] and parts[-1][0].islower():
        return None

    return fqcn
