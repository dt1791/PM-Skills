#!/usr/bin/env python3
"""
Generate Cursor sub-agent files from PM Skills.

Creates one agent per skill in:
- {plugin}/agents/{skill-name}.md  (plugin distribution)
- .cursor/agents/{skill-name}.md    (repo-level Cursor usage)

Author: Paweł Huryn — The Product Compass Newsletter (https://www.productcompass.pm)
"""

from __future__ import annotations

import re
from pathlib import Path


def parse_yaml_frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in content[3:end].strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^(\S+):\s*(.+)$', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            result[key] = value
    return result


def title_case(name: str) -> str:
    acronyms = {
        "prd": "PRD",
        "okrs": "OKRs",
        "okr": "OKR",
        "icp": "ICP",
        "gtm": "GTM",
        "swot": "SWOT",
        "pestle": "PESTLE",
        "ost": "OST",
        "jtbd": "JTBD",
        "wwa": "WWA",
        "wwas": "WWAs",
        "nda": "NDA",
        "sql": "SQL",
        "ab": "A/B",
        "tam": "TAM",
        "sam": "SAM",
        "som": "SOM",
        "nps": "NPS",
    }
    parts = []
    for part in name.split("-"):
        parts.append(acronyms.get(part.lower(), part.capitalize()))
    return " ".join(parts)


def render_agent(plugin: str, skill_name: str, description: str) -> str:
    skill_path = f"{plugin}/skills/{skill_name}/SKILL.md"
    label = title_case(skill_name)
    return f"""---
name: {skill_name}
description: {description}
model: inherit
---

You are a specialized product management sub-agent for **{label}**.

## Before starting

Read and follow the full skill definition at `{skill_path}`. Apply every framework, template, step, and instruction from that skill exactly.

## When invoked

1. Read the skill file and understand the user's request in context.
2. Ask clarifying questions if required inputs are missing.
3. Execute the skill workflow step by step.
4. Produce well-structured markdown output as specified in the skill.
5. Save substantial outputs to appropriately named markdown files when the skill requires it.

Stay focused on this skill's domain. Do not improvise alternative frameworks unless the skill explicitly allows it.
"""


def collect_skills(base_path: Path) -> list[tuple[str, str, str, str]]:
    skills: list[tuple[str, str, str, str]] = []
    for skill_md in sorted(base_path.glob("pm-*/skills/*/SKILL.md")):
        plugin = skill_md.parts[-4]
        skill_name = skill_md.parts[-2]
        frontmatter = parse_yaml_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = frontmatter.get("name", skill_name)
        description = frontmatter.get("description", "")
        if not description:
            raise ValueError(f"Missing description in {skill_md}")
        if name != skill_name:
            raise ValueError(
                f"Name mismatch in {skill_md}: frontmatter '{name}' != directory '{skill_name}'"
            )
        skills.append((plugin, skill_name, name, description))
    return skills


def write_agent(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    base_path = Path(__file__).resolve().parent
    skills = collect_skills(base_path)
    created = 0
    updated = 0

    for plugin, skill_name, _, description in skills:
        content = render_agent(plugin, skill_name, description)

        plugin_agent = base_path / plugin / "agents" / f"{skill_name}.md"
        if write_agent(plugin_agent, content):
            if plugin_agent.stat().st_size == len(content.encode("utf-8")):
                created += 1
            else:
                updated += 1

        cursor_agent = base_path / ".cursor" / "agents" / f"{skill_name}.md"
        if write_agent(cursor_agent, content):
            created += 1

    print(f"Processed {len(skills)} skills")
    print(f"Wrote {created} new/updated agent files")
    print(f"Plugin agents: {len(skills)} in pm-*/agents/")
    print(f"Cursor agents: {len(skills)} in .cursor/agents/")


if __name__ == "__main__":
    main()
