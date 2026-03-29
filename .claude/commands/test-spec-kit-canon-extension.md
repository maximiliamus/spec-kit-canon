# Testing Spec Kit Canon Extension

Use the Claude skill at `.claude/skills/testing-spec-kit-canon-extension`.

Supported command flags:

- `--script sh`
- `--script ps`
- `--restart`

Default behavior:

- continue the existing workflow when the saved progress is not complete
- restart from scratch automatically when the saved workflow is already complete
- restart from scratch immediately when `--restart` is passed

Pass any provided flags through to the shared skill and let the skill prepare
the workflow state before executing the current step.

Follow that skill exactly.

Do not duplicate the workflow in this command file.
