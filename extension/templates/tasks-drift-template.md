# Task Drift Report

**Branch**: `[branch]`
**Source Tasks**: `[FEATURE_DIR]/tasks.md`
**Spec Context**: `[FEATURE_DIR]/spec.md`
**Resolution Status**: `[classified|resolved]`

Use globally incrementing `TD-XXX` identifiers across all sections. Keep only tasks with drift kind `ADDED`, `UPDATED`, or `CANCELED`.

## Added Tasks

### TD-001 - [added task title]
- Drift Kind: `ADDED`
- Original Task Ref: `-`
- Summary: [one-sentence WHAT-level summary of the implemented task]
- Why It Drifted: [why this work has no matching task in tasks.md]
- Evidence:
  - `[path/to/file]` - [what changed and why it belongs to this task]
  - `[path/to/another-file]` - [supporting evidence]
- Potential Spec Impact: [brief note for downstream spec drift analysis]

## Updated Tasks

### TD-002 - [updated task title]
- Drift Kind: `UPDATED`
- Original Task Ref: `T0XX`
- Summary: [one-sentence WHAT-level summary of the implemented task]
- Planned vs Actual: [how the implementation differs from the original task]
- Evidence:
  - `[path/to/file]` - [what changed and why it differs from the plan]
  - `[path/to/another-file]` - [supporting evidence]
- Potential Spec Impact: [brief note for downstream spec drift analysis]

## Canceled Tasks

### TD-003 - [canceled task title]
- Drift Kind: `CANCELED`
- Original Task Ref: `T0YY`
- Summary: [one-sentence summary of the task that was not implemented]
- Why It Was Classified Canceled: [why the task is absent or was removed]
- Evidence:
  - `[path/to/planned-file-or-context]` - [expected or removed implementation evidence]
  - `[path/to/related-file]` - [supporting evidence]
- Potential Spec Impact: [brief note for downstream spec drift analysis]
