# Alignment Tasks

**Branch**: `[branch]`
**Source Spec Drift**: `[FEATURE_DIR]/spec.drift.md`
**Status**: `pending|in-progress|implemented`

Use globally incrementing `TA-XXX` identifiers across all sections. Use
standard Spec Kit task checkboxes: `- [ ]` for incomplete and `- [X]` for
complete.

Status meaning:

- `pending`: no TA-XXX tasks in scope are checked yet
- `in-progress`: some but not all TA-XXX tasks in scope are checked
- `implemented`: all TA-XXX tasks in scope are checked

Each deferred-alignment group is anchored to a spec drift item (`SD-XXX`).
Individual implementation tasks inside that group use `TA-XXX` identifiers.

## Deferred Alignment

### Spec Drift SD-004 - [title]
- Spec Drift Ref: `SD-004`
- Task Drift Ref: `TD-004`
- Status: `pending|in-progress|implemented`
- Spec Requirement: [short requirement from spec.drift.md]
- Reason Deferred: [why the implementation fix was deferred]
- Tasks:
  - [ ] TA-001 Implement the missing behavior in src/...
  - [ ] TA-002 [P] Add regression coverage in tests/...
