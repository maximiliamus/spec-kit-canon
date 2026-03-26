---
description: Initialize or amend the project constitution from the canon constitution template, keeping dependent prompts and templates aligned.
handoffs: 
  - label: Build Specification
    agent: speckit.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are maintaining the project constitution at `.specify/memory/constitution.md`.

This preset ships a canon constitution baseline at
`.specify/presets/canon-core/templates/constitution-template.md`. Unlike the
stock Spec Kit placeholder scaffold, this file is already a fully written
constitution body and uses only four approved metadata placeholders:
`[PROJECT_NAME]`, `[CONSTITUTION_VERSION]`, `[RATIFICATION_DATE]`, and
`[LAST_AMENDED_DATE]`. The bundled baseline also contains derived canon-path
tokens `CANON_ROOT` and `CANON_TOC` that must be resolved from configuration
before writing project files. Treat it as the structural and wording baseline
for this project family.

The bundled baseline's Section 6 branch type rows, branch scope rows, and
example branch names are seed scaffolding only. They are NOT the source of
truth and MUST be regenerated from `.specify/extensions/canon/canon-config.yml`
for every constitution run before either project file is written.

The project-local working template remains
`.specify/templates/constitution-template.md`. Keep that file synchronized with
the bundled preset baseline and with the active constitution so future project
bootstrap and recovery operations use the canon version instead of the stock
placeholder scaffold. In that template file, preserve the same four approved
placeholders rather than replacing them with project-specific values.
That placeholder rule applies only to the four approved metadata placeholders;
Section 6 branch lists and example branch names in the project-local template
must be concrete config-derived content.

Your goals are to:

1. Initialize or repair `.specify/templates/constitution-template.md` from the
   bundled preset baseline when needed, including rendering Section 6 branch
   rows and examples from config.
2. Initialize or repair the configured canon root `CANON_ROOT`, including
   `CANON_TOC`, when it is missing.
3. Initialize `.specify/memory/constitution.md` from
   `.specify/templates/constitution-template.md` if it is missing.
4. Apply any user-requested amendments while preserving the canon-oriented
   structure unless the user explicitly asks to change that structure.
5. Keep `.specify/templates/constitution-template.md` synchronized with the
   updated constitution when the amendment becomes the new project baseline.
6. Validate that dependent templates, prompts, and docs remain aligned.

Follow this execution flow:

1. Load `.specify/presets/canon-core/templates/constitution-template.md`.
   - Treat it as the authoritative bundled baseline for section order,
     terminology, and default wording.
   - If it is missing, stop and report that the `canon-core` preset install is
     incomplete.

2. Load `.specify/templates/constitution-template.md` if it exists.
   - This is the project-local template that Spec Kit bootstrap logic reads.
   - If it is missing, initialize it from the bundled preset baseline, then
     immediately replace the bundled Section 6 type rows, scope rows, and
     example branch names with config-rendered content before using it as the
     project template.
   - If it still contains the generic placeholder scaffold or has drifted in a
     way that conflicts with the canon baseline, repair it before proceeding.
   - Treat a Section 6 mismatch against config as template drift even when the
     rest of the template is structurally valid.

3. Load `.specify/presets/canon-core/templates/canon-toc-template.md`.
   - Use it as the bundled starter for `CANON_TOC`.
   - If it is missing, stop and report that the `canon-core` preset install is
     incomplete.

4. Load project configuration for constitution-driven values:
   - Primary project config source:
     `.specify/extensions/canon/canon-config.yml`.
   - Fallback defaults source:
     `.specify/extensions/canon/extension.yml` under
     `config.defaults.project.name`,
     `config.defaults.canon.root`,
     `config.defaults.branching.types`, and
     `config.defaults.branching.scopes`.
   - Legacy fallback defaults source for backward compatibility:
     `config.defaults.branching.areas`.
   - If the project config file is missing but the extension defaults exist,
     initialize `.specify/extensions/canon/canon-config.yml` from those
     defaults before continuing.
   - Treat `.specify/extensions/canon/canon-config.yml` as the project source
     of truth for project identity, canon root, branch type configuration, and
     branch scope configuration after it has been initialized.
   - Do NOT use the bundled preset template as a source for branch type rows,
     branch scope rows, or example branch names.
   - Project config fields:
     - `project.name`: human-readable project name used for constitution title
       and canon TOC title
     - `canon.root`: repo-relative canon root directory used to initialize the
       canon baseline and render canon paths in the constitution
     - `branching.types`: list of configured branch type rows for Section 6
     - `branching.scopes`: list of configured branch scope rows for Section 6
   - If `branching.scopes` is missing but `branching.areas` exists, treat
     `branching.areas` as a legacy alias, migrate the project config to
     `branching.scopes`, and continue using the migrated values as the source
     of truth.
   - Validate that `project.name`, if present, is a non-empty string after
     trimming whitespace.
   - Validate that `canon.root`, if present, is a non-empty repo-relative path
     after trimming whitespace. Normalize it to forward slashes with no
     trailing slash.
   - Resolve derived canon paths:
     - `CANON_ROOT`: normalized `canon.root`
     - `CANON_TOC`: `CANON_ROOT/_toc.md`
   - Each type entry must be an object with:
     - `code`: lowercase branch prefix token suitable for `<type>`
     - `classification`: exact Section 5 change-classification label mapped by
       the type table
   - Each scope entry must be an object with:
     - `code`: lowercase branch segment token suitable for `<scope>`
     - `description`: human-readable description for the constitution table
   - Validate that at least one type and one scope are configured.
   - Validate that type codes are unique, match `^[a-z0-9-]+$`, and that
     classifications are non-empty and match one of the allowed Section 5
     change classifications exactly.
   - Validate that scope codes are unique, match `^[a-z0-9-]+$`, and that
     descriptions are non-empty.
   - Resolve the exact ordered Section 6 type rows and scope rows that will be
     rendered into both `.specify/templates/constitution-template.md` and
     `.specify/memory/constitution.md`.
   - Resolve example branch names from the configured type and scope codes.
     These examples MUST be regenerated from config during constitution
     creation, not copied from the bundled preset baseline.
   - If the user requests a project rename, update
     `.specify/extensions/canon/canon-config.yml` first and then regenerate the
     constitution from it.
   - If the user requests a canon root relocation or rename, update
     `.specify/extensions/canon/canon-config.yml` first and then regenerate the
     constitution from it.
   - If the user requests branch type additions, removals, renames, or
     classification changes, update
     `.specify/extensions/canon/canon-config.yml` first and then regenerate the
     constitution from it.
   - If the user requests branch scope additions, removals, renames, or
     description changes, update `.specify/extensions/canon/canon-config.yml`
     first and then regenerate the constitution from it.
   - Do NOT preserve stale hardcoded type or scope rows when config says
     otherwise.

5. Ensure the canon root exists:
   - Required canon root path: `CANON_ROOT`.
   - Required canon TOC path: `CANON_TOC`.
   - If `CANON_ROOT` does not exist, create it.
   - If `CANON_TOC` does not exist, initialize it from the canon TOC template.
   - If `_toc.md` already exists, preserve its linked content unless the user
     explicitly asks to restructure canon.
   - Keep `CANON_TOC` H1 synchronized with the resolved `PROJECT_NAME`.

6. Load `.specify/memory/constitution.md` if it exists.
   - If it does not exist, start from the already re-rendered template content.
   - If it exists, use it as the current state and compare it against the
     template to detect project drift or missing sections.

7. Resolve the approved metadata placeholders for the concrete constitution:
   - `[PROJECT_NAME]`:
     - If the user explicitly provides or changes the project name, update
       `.specify/extensions/canon/canon-config.yml` and use that value.
     - Otherwise first use `.specify/extensions/canon/canon-config.yml`
       `project.name` if it is present and non-empty.
     - If config does not contain a usable project name yet, derive it from the
       existing constitution title if present.
     - Otherwise derive it from the main project README title.
     - Otherwise derive it from the repository directory name.
     - Persist the resolved project name back into
       `.specify/extensions/canon/canon-config.yml` so future constitution
       updates use the config value first.
   - `[CONSTITUTION_VERSION]`:
     - If an existing constitution already has a version, use that as the base
       and bump it according to the amendment rules below.
     - If no prior version exists, initialize it to `1.2`, which is the
       bundled canon baseline version for this preset, unless the user
       explicitly provides a different starting version.
   - `[RATIFICATION_DATE]`:
     - Preserve the existing ratification date if one is already recorded.
     - If migrating an older constitution that only has `Last Updated`, reuse
       that existing date as the first recorded ratification date unless the
       user provides a better historical date.
     - If no prior date exists, use today's date.
   - `[LAST_AMENDED_DATE]`:
     - If you are making substantive changes, set it to today's date.
     - If you are only initializing from the template with no amendments, use
       the ratification date.
     - If an existing constitution is preserved without content changes, keep
       its current last-amended or last-updated date.

8. Determine the requested operation:
   - If user input is empty and the memory constitution is missing, initialize
     it from `.specify/templates/constitution-template.md`.
   - If user input is empty and the memory constitution already exists, make no
     content changes unless you find obvious structural drift that should be
     repaired to match the template.
   - If user input requests amendments, apply them to the current constitution
     while using the template as the structural baseline.

9. Preserve the canon-specific structure unless the user explicitly requests a
   structural change:
   - Keep the template title format `# [PROJECT_NAME] Constitution`, and use
     the resolved project name in `.specify/memory/constitution.md`.
   - Keep the metadata header format
     `> Version: ... | Ratified: ... | Last Amended: ...`.
   - Keep the numbered section model and canon-specific terminology such as
     `Canon`, `drift`, `canon updates`, and `vibecoding` unless the user asks
     to rename them.
   - Keep exact command names, workflow sequences, and file paths aligned with
     the current project naming.
   - Keep the canon root path aligned with configured `canon.root`, resolved as
     `CANON_ROOT`.
   - Keep `CANON_TOC` as the canon entry point.
   - Replace `CANON_ROOT` and `CANON_TOC` tokens in both the template and the
     concrete constitution with the resolved configured paths.
   - Re-render Section 6 from config on every constitution write, including
     first-time initialization, repair-only runs, and amendment runs.
   - Render the Section 6 type table from
     `.specify/extensions/canon/canon-config.yml`.
   - Render the Section 6 scope table from
     `.specify/extensions/canon/canon-config.yml`.
   - Replace the hardcoded type rows in both the template and the concrete
     constitution with the configured rows in the same order as the config.
   - Replace the hardcoded scope rows in both the template and the concrete
     constitution with the configured rows in the same order as the config.
   - Render the type table in this exact markdown shape:
     - Header row: `| Type | Map to Change Classification |`
     - Separator row: `| ---- | ---------------------------- |`
     - Data row format: `| \`<code>\` | <classification> |`
   - Render the table in this exact markdown shape:
     - Header row: `| Scope | Description |`
     - Separator row: `| ---- | ----------- |`
     - Data row format: `| \`<code>\` | <description> |`
   - Render the example branch names as concrete human-readable examples, not
     as `<type>` / `<scope>` placeholders.
   - Example branch names are illustrative only; the type and scope tables
     remain the source of truth.
   - Prefer examples that use configured type and scope codes and read like
     realistic branch names such as `feature-api-add-capability`.
   - In `.specify/templates/constitution-template.md`, leave only the four
     approved metadata placeholders unresolved. The Section 6 tables and
     examples must already be filled with config-derived content.

10. Apply amendments carefully:
   - Prefer targeted edits over broad rewrites.
   - Preserve valid existing text that is not being changed.
   - If a requested change affects workflow rules, branch taxonomy, change
     classification, or canon source-of-truth rules, update all related sections
     consistently.
   - If a requested change is ambiguous, resolve it from repo context first and
     use `TODO(<FIELD_NAME>): explanation` only when critical information is
     truly unavailable.

11. Versioning:
   - PATCH: wording clarifications, examples, typo fixes, or non-semantic
     refinements.
   - MINOR: new rule, new section, new workflow step, or material expansion of
     existing governance.
   - MAJOR: incompatible policy reversal, removed rule, redefined authority, or
     changed source-of-truth model.
   - If content changes, set `Last Amended` to today in ISO format
     `YYYY-MM-DD`; otherwise preserve the existing value.
   - Explain the version bump rationale in the final response.

12. Consistency propagation checklist:
   - Read `.specify/templates/plan-template.md` and ensure any constitution
     checks or workflow constraints still match.
   - Read `.specify/templates/spec-template.md` for required spec sections and
     terminology alignment.
   - Read `.specify/templates/tasks-template.md` for task expectations that are
     constitution-driven.
   - Read any checked-in `speckit.*` command override sources if present and
     verify they still reflect the constitution.
   - Read relevant runtime guidance docs such as `README.md` when constitution
     changes affect documented workflow or terminology.

13. Write results:
   - Ensure `CANON_ROOT` exists.
   - Ensure `CANON_TOC` exists with a resolved project title.
   - Ensure `.specify/extensions/canon/canon-config.yml` exists and reflects
     the intended project name, canon root, branch type list, and branch scope
     list.
   - Write the updated concrete constitution to `.specify/memory/constitution.md`.
   - Write the project baseline template to
     `.specify/templates/constitution-template.md` so future initialization uses
     the updated canon version instead of the stock placeholder scaffold.
   - Before writing either constitution file, replace the bundled preset's
     Section 6 type rows, scope rows, and example branch names with the rows and
     examples resolved from `.specify/extensions/canon/canon-config.yml`.
   - In `.specify/templates/constitution-template.md`, preserve exactly these
     placeholder tokens and no others:
     `[PROJECT_NAME]`, `[CONSTITUTION_VERSION]`, `[RATIFICATION_DATE]`,
     `[LAST_AMENDED_DATE]`.
   - Do NOT leave those placeholders unresolved in
     `.specify/memory/constitution.md`.
   - Do NOT leave `CANON_ROOT` or `CANON_TOC` unresolved in either
     `.specify/templates/constitution-template.md` or
     `.specify/memory/constitution.md`.

14. Validation before final output:
   - `CANON_ROOT` exists.
   - `CANON_TOC` exists and has an H1 title matching the resolved project
     name.
   - `.specify/extensions/canon/canon-config.yml` exists and contains the
     effective project name, canon root, branch type list, and branch scope
     list.
   - The Section 6 type table matches the configured branch types exactly.
   - The Section 6 scope table matches the configured branch scopes exactly.
   - The Section 6 example branch names use configured type and scope codes
     rather than stale bundled preset examples.
   - `.specify/memory/constitution.md` is a concrete constitution with no
     unresolved placeholders.
   - `.specify/templates/constitution-template.md` preserves only the four
     approved metadata placeholders listed above.
   - Heading hierarchy and numbered sections remain coherent.
   - Version and date line is internally consistent.
   - Terminology, command names, and file paths are consistent with the rest of
     the repo.
   - `.specify/templates/constitution-template.md` and
     `.specify/memory/constitution.md` are intentionally synchronized at the
     body level, with placeholderized metadata in the template and resolved
     metadata in memory.

15. Output a final summary to the user with:
    - Whether the canon root was initialized or repaired.
    - Whether the constitution was initialized, repaired, or amended.
    - Version change and bump rationale.
    - Files synchronized, including whether the project-local template was
      repaired from the bundled preset baseline.
    - Whether `CANON_TOC` was created or updated.
    - Which branch strategy config source was used and whether
      `.specify/extensions/canon/canon-config.yml` was created or updated.
    - Whether the project name came from explicit input, existing config,
      existing constitution, README title, or repository directory name.
    - Which configured canon root was used and whether it came from explicit
      input, existing config, or extension defaults.
    - The resolved source used for `PROJECT_NAME`, `CONSTITUTION_VERSION`,
      `RATIFICATION_DATE`, and `LAST_AMENDED_DATE`.
    - Any follow-up items requiring manual review.
    - Suggested commit message (for example
      `docs: update constitution baseline for canon workflow`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template unless the user explicitly
  requests a structural change.
- Keep the concrete section numbering and separator lines if they exist in the
  template.
- Keep the four approved metadata placeholders only in the template copy, not
  in the generated memory constitution.
- Keep branch type and scope configuration in
  `.specify/extensions/canon/canon-config.yml` as the project source of truth.
  Do not let the constitution drift from it.
- Keep `project.name` in `.specify/extensions/canon/canon-config.yml` as the
  preferred project-name source after initialization.
- Keep `canon.root` in `.specify/extensions/canon/canon-config.yml` as the
  preferred canon-root source after initialization.
- Keep the canon TOC starter minimal. Do not invent canon documents or links
  that do not exist yet.
- Wrap long lines for readability where practical, but do not introduce awkward
  formatting.
- Keep a single blank line between sections.
- Avoid trailing whitespace.
- Use ASCII only.

If the user supplies partial updates (for example one workflow rule revision),
still perform validation and version decision steps.

Do not prepend HTML sync reports or other metadata blocks that are not already
part of the concrete constitution format.

Do not invent a new constitution structure. Always derive from the existing
project constitution, the bundled preset baseline, and the project-local
constitution template.
