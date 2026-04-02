# Canon Drift Plan

**Branch**: `[branch]`
**Drift Source**: `[SPEC_DRIFT]`
**Status**: `[draft|applied]`
**Canon Root**: `[CANON_ROOT]`

Use globally incrementing `CD-XXX` identifiers across all sections. Each entry should reference the originating `SD-XXX` item and, where possible, the related `TD-XXX` item.

## Accepted Entries

### CD-001 - [accepted canon change title]
- Status: `ACCEPTED`
- Spec Drift Ref: `SD-001`
- Task Drift Ref: `TD-001`
- Canon Target: `[CANON_ROOT]/[file].md § [section heading]`
- Change Type: `add|modify|remove`
- Why Canon Changes: [missing behavior, outdated canon, new entity/field, or terminology gap]
- Proposed Canon Text:

```md
[authoritative present-tense canon text]
```

- Notes: [cross-references, new heading, or TOC implications]

## Rejected Entries

### CD-002 - [rejected canon change title]
- Status: `REJECTED`
- Spec Drift Ref: `SD-002`
- Task Drift Ref: `TD-002`
- Canon Target: `[CANON_ROOT]/[file].md § [section heading]` or `-`
- Change Type: `-`
- Rejection Reason: [already covered by canon, below canon abstraction level, duplicate, or out of scope]
- Notes: [optional clarification]
