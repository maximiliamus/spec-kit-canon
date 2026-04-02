# Spec Drift Report

**Branch**: `[branch]`
**Source Task Drift**: `[FEATURE_DIR]/tasks.drift.md`
**Spec Source**: `[FEATURE_DIR]/spec.md`
**Resolution Status**: `[unresolved|resolved]`

Use globally incrementing `SD-XXX` identifiers across all sections. Every finding must reference its originating `TD-XXX` item.

## Undocumented Features

### SD-001 - [undocumented feature title]
- Status: `ACCEPTED`
- Category: `Undocumented feature`
- Task Drift Ref: `TD-001`
- Spec Reference: `-`
- Implementation Evidence:
  - `[path/to/file]` - [observable behavior]
- Spec Expectation: [what spec.md currently says, or that it is silent]
- Observed Behavior: [what the implementation actually does]
- Canon Impact: [why this matters at canon level]

## Behavioral Deviations

### SD-002 - [behavioral deviation title]
- Status: `UNRESOLVED|IMPL-REJECTED|ACCEPTED`
- Category: `Behavioral deviation`
- Task Drift Ref: `TD-002`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [observable behavior]
- Spec Expectation: [what spec.md requires]
- Observed Behavior: [what the implementation actually does]
- Canon Impact: [why the deviation matters for canon]

## New Entities Or Fields

### SD-003 - [new entity or field title]
- Status: `ACCEPTED`
- Category: `New entity or field`
- Task Drift Ref: `TD-003`
- Spec Reference: `[FEATURE_DIR]/data-model.md § [section]` or `-`
- Implementation Evidence:
  - `[path/to/file]` - [new model, field, or data shape]
- Spec Expectation: [what the current spec or data model defines]
- Observed Behavior: [what new entity or field exists in implementation]
- Canon Impact: [why canon should capture it]

## Removed Or Skipped Requirements

### SD-004 - [removed or skipped requirement title]
- Status: `UNRESOLVED|IMPL-REJECTED|REJECTED`
- Category: `Removed or skipped requirement`
- Task Drift Ref: `TD-004`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [absence, deletion, or contradictory behavior]
- Spec Expectation: [what spec.md still requires]
- Observed Behavior: [what is missing or no longer implemented]
- Canon Impact: [why this changes canon or why it is out of scope]

## Terminology Drift

### SD-005 - [terminology drift title]
- Status: `ACCEPTED|UNRESOLVED|IMPL-REJECTED`
- Category: `Terminology drift`
- Task Drift Ref: `TD-005`
- Spec Reference: `[FEATURE_DIR]/spec.md § [section]`
- Implementation Evidence:
  - `[path/to/file]` - [current term in code]
- Spec Expectation: [term used in spec]
- Observed Behavior: [term used in implementation]
- Canon Impact: [why terminology alignment matters]

## Resolution

Include this section only when the file is fully resolved, whether that happened during detect, during resolve, or immediately in vibecoding workflows that skip the resolve step.

| Drift ID | Task Drift Ref | Terminal Status | Resolution Action | Updated Artifact | Notes |
|----------|----------------|-----------------|-------------------|---------------------|-------|
| SD-001 | TD-001 | ACCEPTED | Accepted as authoritative behavior | `-` | No further action |
| SD-002 | TD-002 | SPEC-ACCEPTED | Implementation updated to match specification | `[path/to/file]` | Fixed in code |
| SD-003 | TD-003 | IMPL-ACCEPTED | Specification updated to match implementation | `SD-003 in [FEATURE_DIR]/spec.drift.md` | No code change required |
| SD-004 | TD-004 | REJECTED | Excluded from canon consideration | `-` | Below canon abstraction level |
