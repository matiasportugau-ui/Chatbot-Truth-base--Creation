"""
Markdown Parser Utility

Extracts system instructions and documentation from Markdown files.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class MarkdownParser:
    """Parser for Markdown instruction files"""

    def __init__(self):
        pass

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse Markdown file and extract structured sections"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            sections = self._extract_sections(content)
            code_blocks = self._extract_code_blocks(content)
            lists = self._extract_lists(content)

            result = {
                "full_text": content,
                "sections": sections,
                "code_blocks": code_blocks,
                "lists": lists,
                "metadata": self._extract_metadata(content),
            }

            logger.info(f"Successfully parsed Markdown file: {file_path.name}")
            return result

        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            raise

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections based on headers"""
        sections = {}
        current_section = "introduction"
        current_content = []

        lines = content.split("\n")
        for line in lines:
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = self._normalize_section_name(title)
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _normalize_section_name(self, title: str) -> str:
        """Normalize section name to lowercase with underscores"""
        normalized = re.sub(r"[^\w\s]", "", title.lower())
        normalized = re.sub(r"\s+", "_", normalized)
        return normalized

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from Markdown"""
        code_blocks = []
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            language = match.group(1) or "text"
            code = match.group(2).strip()
            code_blocks.append({"language": language, "code": code})

        return code_blocks

    def _extract_lists(self, content: str) -> Dict[str, List[str]]:
        """Extract lists (ordered and unordered) from Markdown"""
        lists = {"unordered": [], "ordered": []}

        lines = content.split("\n")
        current_list = []
        list_type = None

        for line in lines:
            if re.match(r"^[-*+]\s+", line):
                if list_type != "unordered" and current_list:
                    lists[list_type].extend(current_list)
                    current_list = []
                list_type = "unordered"
                item = re.sub(r"^[-*+]\s+", "", line).strip()
                current_list.append(item)
            elif re.match(r"^\d+\.\s+", line):
                if list_type != "ordered" and current_list:
                    lists[list_type].extend(current_list)
                    current_list = []
                list_type = "ordered"
                item = re.sub(r"^\d+\.\s+", "", line).strip()
                current_list.append(item)
            else:
                if current_list:
                    lists[list_type].extend(current_list)
                    current_list = []
                list_type = None

        if current_list:
            lists[list_type].extend(current_list)

        return lists

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from frontmatter or content"""
        metadata = {}

        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")

        if "version" in content.lower():
            version_match = re.search(r"version[:\s]+([\d.]+)", content, re.IGNORECASE)
            if version_match:
                metadata["version"] = version_match.group(1)

        return metadata

    def extract_system_instructions(self, content: str) -> str:
        """Extract system instructions section from content"""
        patterns = [
            r"#\s*INSTRUCCIONES\s*(.*?)(?=#|\Z)",
            r"#\s*SYSTEM\s*INSTRUCTIONS\s*(.*?)(?=#|\Z)",
            r"```\s*instructions?\s*\n(.*?)```",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return content

    def extract_commands(self, content: str) -> List[Dict[str, str]]:
        """Extract special commands (e.g., /estado, /checkpoint)"""
        commands = []
        pattern = r"[-*]\s*`?/(\w+)`?\s*[→-]\s*(.+?)(?=\n|$)"
        matches = re.finditer(pattern, content, re.MULTILINE)

        for match in matches:
            command = match.group(1)
            description = match.group(2).strip()
            commands.append({"command": command, "description": description})

        return commands
