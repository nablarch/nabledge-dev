"""Phase G: Resolve Links

Resolve RST cross-references to Markdown links after all knowledge files are generated.
"""

import os
import re
import json
from glob import glob
from .common import load_json, write_json
from .logger import get_logger


class PhaseGResolveLinks:
    def __init__(self, ctx):
        self.ctx = ctx
        self.label_index = {}  # label -> (file_id, section_id)
        self.doc_index = {}    # rst_path -> file_id
        self.logger = get_logger()

    def _validate_file_id(self, file_id):
        """Validate file_id contains only safe characters.

        Args:
            file_id: File identifier to validate

        Returns:
            file_id if valid

        Raises:
            ValueError: If file_id contains unsafe characters
        """
        self.logger = get_logger()
        if not file_id:
            raise ValueError("file_id cannot be empty")

        # Reject absolute paths, parent directory refs (..), backslashes
        if file_id.startswith('/') or '..' in file_id or '\\' in file_id:
            raise ValueError(f"Unsafe file_id (path traversal risk): {file_id}")

        # Allow alphanumeric, underscore, hyphen, forward slash (for nested paths)
        if not re.match(r'^[a-zA-Z0-9_/-]+$', file_id):
            raise ValueError(f"Invalid characters in file_id: {file_id}")

        return file_id

    def _build_label_index(self):
        """Scan all knowledge files to build global label index."""
        self.logger.info("  Building label index...")

        # Get all knowledge JSON files
        pattern = f"{self.ctx.knowledge_dir}/**/*.json"
        json_files = glob(pattern, recursive=True)

        for json_path in json_files:
            knowledge = load_json(json_path)
            file_id = knowledge.get("id")
            if not file_id:
                continue

            # Extract labels from trace.internal_labels if available
            trace_path = f"{self.ctx.trace_dir}/{file_id}.json"
            if os.path.exists(trace_path):
                trace = load_json(trace_path)
                internal_labels = trace.get("internal_labels", [])
                for label in internal_labels:
                    # Try to map label to section_id
                    # For now, assume label matches section_id or is file-level
                    section_id = self._find_section_for_label(knowledge, label)

                    # Index both underscore and hyphen versions for flexibility
                    self.label_index[label] = (file_id, section_id)
                    label_underscore = label.replace("-", "_")
                    label_hyphen = label.replace("_", "-")
                    if label_underscore != label:
                        self.label_index[label_underscore] = (file_id, section_id)
                    if label_hyphen != label:
                        self.label_index[label_hyphen] = (file_id, section_id)

            # Also index the file_id itself as a label (for file-level references)
            # Map common label patterns to file_id
            # Index both underscore and hyphen versions for flexibility
            file_label_underscore = file_id.replace("-", "_")
            file_label_hyphen = file_id.replace("_", "-")
            self.label_index[file_label_underscore] = (file_id, None)
            self.label_index[file_label_hyphen] = (file_id, None)
            self.label_index[file_id] = (file_id, None)

        self.logger.debug(f"    Indexed {len(self.label_index)} labels")

    def _find_section_for_label(self, knowledge, label):
        """Find section_id that matches a label."""
        # Try multiple conversion strategies
        sections = knowledge.get("sections", {})

        # Try as-is
        if label in sections:
            return label

        # Try kebab-case (underscores to hyphens)
        section_id_hyphen = label.replace("_", "-")
        if section_id_hyphen in sections:
            return section_id_hyphen

        # Try snake_case (hyphens to underscores)
        section_id_underscore = label.replace("-", "_")
        if section_id_underscore in sections:
            return section_id_underscore

        # If not found, return None (file-level reference)
        return None

    def _build_doc_index(self):
        """Build index of RST paths to file_ids."""
        self.logger.info("  Building doc index...")

        # This requires knowledge of the source file structure
        # For now, use a simple heuristic based on file_id
        classified = load_json(self.ctx.classified_list_path)
        for fi in classified["files"]:
            file_id = fi["id"]
            source_path = fi.get("source_path", "")
            if source_path:
                # Extract relative path from source (remove extension)
                rst_path = source_path.replace(".rst", "").replace(".md", "")
                self.doc_index[rst_path] = file_id

                # Also index without leading path components for relative path matching
                # E.g., "application_framework/configuration/database" -> "configuration/database", "database"
                path_parts = rst_path.split("/")
                for i in range(len(path_parts)):
                    partial_path = "/".join(path_parts[i:])
                    if partial_path not in self.doc_index:
                        self.doc_index[partial_path] = file_id

        self.logger.debug(f"    Indexed {len(self.doc_index)} document paths")

    def _resolve_ref(self, match, current_file_id):
        """Resolve :ref:`...` to Markdown link."""
        full_match = match.group(0)

        # Parse :ref:`text <label>` or :ref:`label`
        # Pattern: :ref:`display <label>` or :ref:`label`
        ref_with_text = re.match(r':ref:`([^<>`]+)\s*<([^>`]+)>`', full_match)
        ref_plain = re.match(r':ref:`([^>`]+)`', full_match)

        if ref_with_text:
            display_text = ref_with_text.group(1).strip()
            label = ref_with_text.group(2).strip()
        elif ref_plain:
            label = ref_plain.group(1).strip()
            display_text = None
        else:
            return full_match  # Keep as-is if parse fails

        # Look up label in index
        if label in self.label_index:
            target_file_id, section_id = self.label_index[label]

            if target_file_id == current_file_id and section_id:
                # Internal reference
                link = f"#{section_id}"
            else:
                # External reference
                # Calculate relative path
                link = self._calculate_relative_path(current_file_id, target_file_id)
                if section_id:
                    link += f"#{section_id}"

            # Use display_text if provided, otherwise use label
            text = display_text if display_text else label
            return f"[{text}]({link})"
        else:
            # Label not found - keep as-is for now
            return full_match

    def _resolve_doc(self, match, current_file_id):
        """Resolve :doc:`...` to Markdown link."""
        full_match = match.group(0)

        # Parse :doc:`text <path>` or :doc:`path`
        doc_with_text = re.match(r':doc:`([^<>`]+)\s*<([^>`]+)>`', full_match)
        doc_plain = re.match(r':doc:`([^>`]+)`', full_match)

        if doc_with_text:
            display_text = doc_with_text.group(1).strip()
            doc_path = doc_with_text.group(2).strip()
        elif doc_plain:
            doc_path = doc_plain.group(1).strip()
            display_text = None
        else:
            return full_match

        # Normalize doc_path (remove .. and .)
        # Simple normalization: remove ../ prefix
        normalized_path = doc_path
        while normalized_path.startswith("../"):
            normalized_path = normalized_path[3:]
        normalized_path = normalized_path.lstrip("./")

        # Look up doc_path in index (try both original and normalized)
        target_file_id = self.doc_index.get(doc_path) or self.doc_index.get(normalized_path)
        if target_file_id:
            link = self._calculate_relative_path(current_file_id, target_file_id)
            text = display_text if display_text else doc_path
            return f"[{text}]({link})"
        else:
            # Path not found - keep as-is
            return full_match

    def _resolve_download(self, match, current_file_id):
        """Resolve :download:`text<path>` to assets link."""
        full_match = match.group(0)

        # Parse :download:`text <path>` or :download:`text<path>` (with/without space)
        download_match = re.match(r':download:`([^<>`]+)\s*<([^>`]+)>`', full_match)
        if not download_match:
            return full_match

        display_text = download_match.group(1).strip()
        file_path = download_match.group(2).strip()

        # Validate file_path for path traversal risks
        if file_path.startswith('/') or '..' in file_path or '\\' in file_path:
            # Suspicious path - keep as-is rather than generating unsafe asset path
            return full_match

        # Extract filename
        filename = os.path.basename(os.path.normpath(file_path))

        # Validate current_file_id before using in path
        try:
            validated_id = self._validate_file_id(current_file_id)
        except ValueError:
            # Invalid file_id - keep original syntax
            return full_match

        # Format as assets link
        return f"[{display_text}](assets/{validated_id}/{filename})"

    def _resolve_java_extdoc(self, match):
        """Resolve :java:extdoc:`...` - keep as-is since already in official_doc_urls."""
        # For now, keep the RST syntax as it will be handled separately
        # In final output, these should be converted to inline code
        full_match = match.group(0)

        # Parse :java:extdoc:`text <class>` or :java:extdoc:`class`
        java_with_text = re.match(r':java:extdoc:`([^<>`]+)\s*<([^>`]+)>`', full_match)
        java_plain = re.match(r':java:extdoc:`([^>`]+)`', full_match)

        if java_with_text:
            display_text = java_with_text.group(1).strip()
            class_name = java_with_text.group(2).strip()
        elif java_plain:
            class_name = java_plain.group(1).strip()
            display_text = None
        else:
            return full_match

        # Extract simple class name if no display_text
        if not display_text:
            simple_name = class_name.split(".")[-1]
            if "#" in simple_name:
                simple_name = simple_name.split("#")[0]
            display_text = simple_name

        return f"`{display_text}`"

    def _calculate_relative_path(self, from_file_id, to_file_id):
        """Calculate relative path from one file to another."""
        # Validate file IDs before using in paths
        try:
            self._validate_file_id(from_file_id)
            self._validate_file_id(to_file_id)
        except ValueError as e:
            self.logger.warning(f"  Warning: Invalid file_id in path calculation: {e}")
            return f"{to_file_id}.md"  # Return simple path anyway

        # Simple implementation: assume flat structure for now
        # TODO: Implement proper relative path calculation based on file structure
        if '/' in from_file_id or '/' in to_file_id:
            self.logger.warning(f"  Warning: Relative path calculation for nested files not yet fully supported")

        return f"{to_file_id}.md"

    def _resolve_section_links(self, content, file_id):
        """Resolve all RST links in section content."""
        # Resolve :ref: links
        content = re.sub(
            r':ref:`[^`]+`',
            lambda m: self._resolve_ref(m, file_id),
            content
        )

        # Resolve :doc: links
        content = re.sub(
            r':doc:`[^`]+`',
            lambda m: self._resolve_doc(m, file_id),
            content
        )

        # Resolve :download: links
        content = re.sub(
            r':download:`[^<>`]+<[^>`]+>`',
            lambda m: self._resolve_download(m, file_id),
            content
        )

        # Resolve :java:extdoc: links
        content = re.sub(
            r':java:extdoc:`[^`]+`',
            lambda m: self._resolve_java_extdoc(m),
            content
        )

        return content

    def _resolve_knowledge_file(self, json_path):
        """Resolve links in a single knowledge file."""
        knowledge = load_json(json_path)
        file_id = knowledge.get("id")

        # Resolve links in each section
        sections = knowledge.get("sections", {})
        for section_id, content in sections.items():
            sections[section_id] = self._resolve_section_links(content, file_id)

        return knowledge

    def run(self):
        """Execute Phase G: Link Resolution."""
        self.logger.info("\n=== Phase G: Link Resolution ===")

        # Build indices
        self._build_label_index()
        self._build_doc_index()

        # Create output directory
        resolved_dir = self.ctx.knowledge_resolved_dir
        os.makedirs(resolved_dir, exist_ok=True)

        # Process all knowledge files
        pattern = f"{self.ctx.knowledge_dir}/**/*.json"
        json_files = glob(pattern, recursive=True)

        resolved_count = 0
        for json_path in json_files:
            try:
                resolved_knowledge = self._resolve_knowledge_file(json_path)

                # Write to resolved directory (maintain structure)
                rel_path = os.path.relpath(json_path, self.ctx.knowledge_dir)
                output_path = os.path.join(resolved_dir, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                write_json(output_path, resolved_knowledge)
                resolved_count += 1
            except Exception as e:
                self.logger.error(f"  Error resolving {json_path}: {e}")

        self.logger.info(f"\nResolved links in {resolved_count} files")
        self.logger.info(f"Output: {resolved_dir}")

        return {
            "resolved_count": resolved_count,
            "output_dir": resolved_dir
        }
