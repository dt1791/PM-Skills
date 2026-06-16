#!/usr/bin/env python3
"""
Generate self-contained Cursor sub-agents for pm-product-discovery skills.

Each agent embeds the full skill workflow so it executes completely when invoked.
Agents include discovery sequence metadata (Stage 0–4) where applicable.

Author: Paweł Huryn — The Product Compass Newsletter (https://www.productcompass.pm)
"""

from __future__ import annotations

import re
from pathlib import Path

PLUGIN = "pm-product-discovery"
SKILLS_DIR = Path(PLUGIN) / "skills"
AGENT_DIRS = [Path(PLUGIN) / "agents", Path(".cursor") / "agents"]

SEQUENCE = {
    "validate-problem": "Stage 0 — run FIRST before any discovery or ideation",
    "brainstorm-ideas-new": "Stage 1 — divergent ideation (new product)",
    "brainstorm-ideas-existing": "Stage 1 — divergent ideation (existing product)",
    "identify-assumptions-new": "Stage 2 — assumption mapping (new product)",
    "identify-assumptions-existing": "Stage 2 — assumption mapping (existing product)",
    "prioritize-assumptions": "Stage 3 — focus and triage assumptions",
    "brainstorm-experiments-new": "Stage 4 — validation experiments (new product)",
    "brainstorm-experiments-existing": "Stage 4 — validation experiments (existing product)",
}

NEXT_STEPS = {
    "validate-problem": (
        "- **GO** → `/brainstorm-ideas-new` or `/brainstorm-ideas-existing`, or run `/discover`\n"
        "- **PAUSE** → `/interview-script`, then return to `/validate-problem`\n"
        "- **STOP** → explore pivot with value proposition work"
    ),
    "brainstorm-ideas-new": (
        "→ `/identify-assumptions-new` on your top 3–5 ideas, or run `/discover` for the full cycle"
    ),
    "brainstorm-ideas-existing": (
        "→ `/identify-assumptions-existing` on your top 3–5 ideas, or run `/discover` for the full cycle"
    ),
    "identify-assumptions-new": "→ `/prioritize-assumptions` to rank and plan tests",
    "identify-assumptions-existing": "→ `/prioritize-assumptions` to rank and plan tests",
    "prioritize-assumptions": (
        "→ `/brainstorm-experiments-new` or `/brainstorm-experiments-existing` for top assumptions"
    ),
    "brainstorm-experiments-new": (
        "→ `/metrics-dashboard` to track experiments, or `/create-prd` if validation succeeds"
    ),
    "brainstorm-experiments-existing": (
        "→ `/metrics-dashboard` to track experiments, or `/create-prd` if validation succeeds"
    ),
    "opportunity-solution-tree": "→ `/brainstorm-ideas-existing` or `/identify-assumptions-existing` on top solutions",
    "analyze-feature-requests": "→ `/prioritize-features` or `/identify-assumptions-existing` on top themes",
    "prioritize-features": "→ `/identify-assumptions-existing` or `/create-prd` for top-ranked features",
    "interview-script": "→ run interviews, then `/summarize-interview` on transcripts",
    "summarize-interview": "→ `/opportunity-solution-tree` or `/identify-assumptions-existing` with insights",
    "metrics-dashboard": "→ monitor experiments defined in `/brainstorm-experiments-*`",
}


def parse_skill(path: Path) -> tuple[dict[str, str], str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError(f"Missing frontmatter: {path}")
    end = content.find("---", 3)
    if end == -1:
        raise ValueError(f"Unclosed frontmatter: {path}")

    fm_text = content[3:end]
    frontmatter: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_key, current_lines
        if current_key is not None:
            value = " ".join(line.strip() for line in current_lines if line.strip())
            frontmatter[current_key] = value.strip().strip('"').strip("'")
        current_key = None
        current_lines = []

    for raw_line in fm_text.split("\n"):
        line = raw_line.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue

        key_match = re.match(r"^(\S+):\s*(.*)$", line)
        if key_match:
            flush()
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            if value in (">", "|", ""):
                continue
            current_lines = [value.strip().strip('"').strip("'")]
        elif current_key and (line.startswith("  ") or line.startswith("\t")):
            current_lines.append(line.strip())

    flush()

    body = content[end + 3 :].strip()
    return frontmatter, body


def title_case(name: str) -> str:
    acronyms = {"ost": "OST", "jtbd": "JTBD", "okr": "OKR", "okrs": "OKRs", "prd": "PRD"}
    return " ".join(acronyms.get(p.lower(), p.capitalize()) for p in name.split("-"))


def build_description(skill_name: str, base_description: str) -> str:
    stage = SEQUENCE.get(skill_name)
    if stage:
        return f"{stage}. {base_description} Invoke with /{skill_name}."
    return f"{base_description} Invoke with /{skill_name}."


def render_agent(skill_name: str, description: str, body: str) -> str:
    label = title_case(skill_name)
    stage_line = ""
    if skill_name in SEQUENCE:
        stage_line = f" ({SEQUENCE[skill_name]})"

    next_step = NEXT_STEPS.get(skill_name, "→ continue discovery with the next relevant sub-agent")

    return f"""---
name: {skill_name}
description: {description}
model: inherit
---

You are the **{label}** sub-agent{stage_line} for product discovery.

## Execution rules

- Execute the **entire workflow below** from start to finish in a single run.
- Follow every step and stage in order. **Do not skip steps** or stop at an outline.
- Produce the **complete output artifact** (tables, reports, plans) before finishing.
- If the user provides files, read them first. Use web search when market context is needed.
- Ask clarifying questions only when required inputs are genuinely missing.
- Save substantial output as a markdown file in the workspace.

## After completing

Suggest the next step in the discovery sequence:

{next_step}

---

{body}
"""


def render_discover_orchestrator() -> str:
    return """---
name: discover
description: Run the full product discovery cycle in sequence — ideation, assumption mapping, prioritization, and experiment design. Stage 1–4 orchestrator. Invoke with /discover after /validate-problem.
model: inherit
---

You are the **Discover** sub-agent — the full product discovery orchestrator (Stages 1–4).

## Execution rules

- Run the complete discovery cycle below **in sequence**. Do not skip stages.
- Pause at each checkpoint for user input before continuing.
- If problem validation has not been done, recommend `/validate-problem` first.
- Save the final discovery plan as a markdown file in the workspace.

## Discovery sequence

### Step 1: Understand context

Determine whether this is an **existing product** (continuous discovery) or a **new product** (initial discovery).

Ask:
- What are you exploring?
- What do you already know? (research, feedback, data)
- What decisions will this discovery inform?

Accept context from uploaded files, links, or conversation.

### Step 2: Brainstorm ideas (Stage 1)

Apply **brainstorm-ideas-existing** or **brainstorm-ideas-new**:
- Generate ideas from PM, Designer, and Engineer perspectives
- Present the top 10 ideas with brief rationale
- **Checkpoint**: ask user to select 3–5 ideas to carry forward

### Step 3: Identify assumptions (Stage 2)

For each selected idea, apply **identify-assumptions-existing** or **identify-assumptions-new**:
- Surface assumptions across risk categories (Value, Usability, Viability, Feasibility; plus GTM/Strategy/Team for new products)
- Compile a master assumption list

### Step 4: Prioritize assumptions (Stage 3)

Apply **prioritize-assumptions**:
- Map assumptions on Impact × Risk matrix
- Identify leap-of-faith assumptions
- **Checkpoint**: confirm top assumptions to validate

### Step 5: Design experiments (Stage 4)

Apply **brainstorm-experiments-existing** or **brainstorm-experiments-new**:
- Design 1–2 experiments per critical assumption
- Include success criteria, timeline, and effort
- Sequence experiments by dependency

### Step 6: Create discovery plan

Compile everything into a **Discovery Plan** document with:
- Ideas explored and selected
- Critical assumptions table (Impact, Uncertainty, Priority)
- Validation experiments table (Method, Success Criteria, Effort, Timeline)
- Discovery timeline (week-by-week)
- Decision framework (if X succeeds → Y; if fails → pivot/kill)

Save as `Discovery-Plan-[topic].md`.

### Step 7: Offer next steps

- `/create-prd` for the top validated idea
- `/interview-script` to supplement experiments
- `/metrics-dashboard` to track experiment results
- `/write-stories` to break down an MVP
"""


def main() -> None:
    base = Path(__file__).resolve().parent
    skills_dir = base / SKILLS_DIR
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))

    agents: dict[str, str] = {}
    for skill_path in skill_files:
        skill_name = skill_path.parent.name
        frontmatter, body = parse_skill(skill_path)
        name = frontmatter.get("name", skill_name)
        if name != skill_name:
            raise ValueError(f"Name mismatch: {skill_path}")
        description = build_description(skill_name, frontmatter.get("description", ""))
        agents[skill_name] = render_agent(skill_name, description, body)

    agents["discover"] = render_discover_orchestrator()

    for agent_dir in AGENT_DIRS:
        agent_dir.mkdir(parents=True, exist_ok=True)
        for skill_name, content in agents.items():
            (agent_dir / f"{skill_name}.md").write_text(content, encoding="utf-8")

    print(f"Generated {len(agents)} discovery sub-agents in:")
    for agent_dir in AGENT_DIRS:
        print(f"  - {agent_dir}/")
    print("\nDiscovery sequence:")
    print("  /validate-problem → /brainstorm-ideas-* → /identify-assumptions-*")
    print("  → /prioritize-assumptions → /brainstorm-experiments-*")
    print("\nOr run the full cycle: /discover")


if __name__ == "__main__":
    main()
