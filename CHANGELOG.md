# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-29

### Added

- Initial release of the `spec-kit-canon` extension.
- Added comprehensive drift orchestration pipeline commands:
  - `speckit.canon.drift`: Standard canon drift orchestration.
  - `speckit.canon.drift-detect`: Detect spec-level drift.
  - `speckit.canon.drift-reconcile`: Infer canon gaps.
  - `speckit.canon.drift-analyze`: Analyze canon and produce repair candidates.
  - `speckit.canon.drift-canonize`: Apply accepted canon entries.
  - `speckit.canon.drift-repair`: Repair canon post-analysis.
  - `speckit.canon.drift-resolve`: Resolve outstanding drift items.
  - `speckit.canon.drift-reverse`: Reverse-engineer task drift.
- Added Vibecode-specific drift orchestration pipeline commands:
  - `speckit.canon.vibecode-drift`: Fully autonomous drift orchestration.
  - `speckit.canon.vibecode-drift-detect`: Vibecode spec-level drift detection.
  - `speckit.canon.vibecode-drift-reconcile`: Vibecode canon gap inference.
  - `speckit.canon.vibecode-drift-canonize`: Apply vibecode canon plans.
  - `speckit.canon.vibecode-drift-reverse`: Vibecode task drift reverse-engineering.
  - `speckit.canon.vibecode-specify`: Autonomous specification sessions.
- Initial release of the `canon-core` preset with core Spec Kit command overrides:
  - `speckit.specify`
  - `speckit.clarify`
  - `speckit.checklist`
  - `speckit.plan`
  - `speckit.tasks`
  - `speckit.analyze`
  - `speckit.implement`
  - `speckit.constitution`
- Added shared automation skills:
  - `bumping-spec-kit-canon-version`: Centralized version management for canon packages.
  - `syncing-spec-kit-canon-core-preset`: Marker-aware upstream merge automation.
  - `testing-spec-kit-canon-extension`: Automated extension verification workflow.
- Established GitHub Actions workflow for automated release packaging and publishing.
- Bootstrapped documentation and project structure for the canon ecosystem.

[0.1.0]: https://github.com/maximiliamus/spec-kit-canon/releases/tag/v0.1.0
