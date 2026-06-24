#!/usr/bin/env python3
"""Generate OKF-style Obsidian notes for ALL Milano tasks (POC).

Reads life/tasks/milano_active_tasks.yaml and writes one Markdown note per task
into poc/obsidian_okf_milano/tasks/, plus a regenerated index.md.

Re-runnable: overwrites generated task notes and index.md each time.
Run from the repo root:  python3 poc/obsidian_okf_milano/generate_notes.py
"""
import os, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "life", "tasks", "milano_active_tasks.yaml")
OUT = os.path.join(ROOT, "poc", "obsidian_okf_milano")
TASKS = os.path.join(OUT, "tasks")
STAMP = "2026-06-25"

CHECKBOX_FIELDS = {"acceptance_criteria", "next_actions"}
BULLET_FIELDS = [
    ("context", "Context"),
    ("scope", "Scope"),
    ("inputs", "Inputs"),
    ("current_state", "Current state"),
    ("tooling_notes", "Tooling notes"),
    ("expected_outputs", "Expected outputs"),
    ("failure_modes_to_avoid", "Failure modes to avoid"),
    ("acceptance_criteria", "Acceptance criteria"),
    ("next_actions", "Next actions"),
]


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def wl(ref):
    """ref id -> Obsidian wikilink string for frontmatter list."""
    return q(f"[[{ref}]]")


def render_requirement_spec(spec):
    out = ["## Requirement"]
    for k, v in spec.items():
        label = k.replace("_", " ")
        if isinstance(v, list) and v and isinstance(v[0], dict):
            # table (e.g. bar0_size_map)
            cols = list(v[0].keys())
            out.append(f"\n**{label}:**\n")
            out.append("| " + " | ".join(cols) + " |")
            out.append("|" + "|".join(["---"] * len(cols)) + "|")
            for row in v:
                out.append("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
        elif isinstance(v, list):
            out.append(f"\n**{label}:**")
            for item in v:
                out.append(f"- {item}")
        elif isinstance(v, dict):
            out.append(f"\n**{label}:**")
            for kk, vv in v.items():
                if isinstance(vv, list):
                    out.append(f"- {kk.replace('_',' ')}: {', '.join(map(str, vv))}")
                else:
                    out.append(f"- {kk.replace('_',' ')}: {vv}")
        else:
            out.append(f"- **{label}:** {v}")
    return "\n".join(out) + "\n"


def render_task(t):
    tid = t["id"]
    comp = t.get("component_ref")
    fm = ["---", "type: task", f"id: {tid}", f"title: {q(t.get('title',''))}",
          f"area: {t.get('area','')}", f"project: {t.get('project_ref','-')}"]
    if comp:
        fm.append(f"component: {q('[[' + comp + ']]')}")
    fm += [f"status: {t.get('status','')}", f"priority: {t.get('priority','')}",
           f"progress: {t.get('progress_percent') or 0}"]
    if t.get("tags"):
        fm.append("tags: [" + ", ".join(t["tags"]) + "]")
    if t.get("related_task_refs"):
        fm.append("related_tasks: [" + ", ".join(wl(r) for r in t["related_task_refs"]) + "]")
    if t.get("depends_on"):
        fm.append("depends_on: [" + ", ".join(wl(r) for r in t["depends_on"]) + "]")
    if t.get("related_project_refs"):
        fm.append("related_projects: [" + ", ".join(t["related_project_refs"]) + "]")
    if t.get("evidence_refs"):
        fm.append("evidence: [" + ", ".join(t["evidence_refs"]) + "]")
    fm += [f"confidence: {t.get('confidence','')}",
           f"needs_user_review: {str(t.get('needs_user_review', False)).lower()}",
           f"updated: {STAMP}", "---", ""]

    body = [f"# {t.get('title','')}", ""]
    one = f"{t.get('status','')} · {t.get('priority','')} priority · {t.get('progress_percent') or 0}%"
    body += [f"> [!summary] Status", f"> **{one}**", ""]

    if isinstance(t.get("requirement_spec"), dict):
        body.append(render_requirement_spec(t["requirement_spec"]))

    for key, label in BULLET_FIELDS:
        items = t.get(key)
        if not items:
            continue
        body.append(f"## {label}")
        check = "- [ ] " if key in CHECKBOX_FIELDS else "- "
        for item in items:
            body.append(f"{check}{item}")
        body.append("")

    # Links
    links = ["## Links"]
    if comp:
        links.append(f"- Component: [[{comp}]]")
    for r in t.get("related_task_refs", []):
        links.append(f"- Related: [[{r}]]")
    for r in t.get("depends_on", []):
        links.append(f"- Depends on: [[{r}]]")
    for r in t.get("related_issue_refs", []):
        links.append(f"- Issue: [[{r}]]")
    links.append("- Index: [[index]]")
    body += links + [""]

    body += ["## History", f"- **{STAMP}** — Generated from `life/tasks/milano_active_tasks.yaml`.", ""]
    return "\n".join(fm) + "\n".join(body) + "\n"


STATUS_ORDER = ["in_progress", "todo", "planned", "deferred", "completed"]


def render_index(tasks, updated_at):
    by = {}
    for t in tasks:
        by.setdefault(t.get("status", "other"), []).append(t)
    lines = ["---", "type: index", "title: Milano Tasks — Index",
             "description: OKF index / map of content for the Milano task POC (all tasks).",
             "project: project_milano", "component: component_milano_pcie",
             "tags: [okf, index, milano]", f"updated: {STAMP}", "---", "",
             "# Milano Tasks — Index", "",
             f"All {len(tasks)} Milano tasks, generated from `life/tasks/milano_active_tasks.yaml` "
             f"(source `updated_at: {updated_at}`). Component hub: [[component_milano_pcie]]. "
             "For a live filterable view open [`milano_tasks.base`](milano_tasks.base).", ""]
    for st in STATUS_ORDER + [s for s in by if s not in STATUS_ORDER]:
        group = by.get(st)
        if not group:
            continue
        lines.append(f"## {st}  ({len(group)})")
        lines.append("")
        lines.append("| Task | Priority | Progress |")
        lines.append("|------|----------|----------|")
        for t in group:
            lines.append(f"| [[{t['id']}]] | {t.get('priority','')} | {t.get('progress_percent') or 0}% |")
        lines.append("")
    return "\n".join(lines)


def main():
    doc = yaml.safe_load(open(SRC))
    tasks = doc.get("tasks", [])
    os.makedirs(TASKS, exist_ok=True)
    for t in tasks:
        with open(os.path.join(TASKS, t["id"] + ".md"), "w") as f:
            f.write(render_task(t))
    with open(os.path.join(OUT, "index.md"), "w") as f:
        f.write(render_index(tasks, doc.get("updated_at")))
    print(f"Generated {len(tasks)} task notes + index.md")


if __name__ == "__main__":
    main()
