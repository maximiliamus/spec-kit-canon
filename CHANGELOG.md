# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-05

### Added

- Initial release of the `spec-kit-canon` extension.
- Added comprehensive drift orchestration pipeline commands:
  - `speckit.canon.drift`: Standard canon drift orchestration.
  - `speckit.canon.drift-reverse`: Reverse-engineer task drift.
  - `speckit.canon.drift-detect`: Detect spec-level drift.
  - `speckit.canon.drift-resolve`: Resolve outstanding drift items.
  - `speckit.canon.drift-implement`: Execute deferred alignment work.
  - `speckit.canon.drift-reconcile`: Infer canon gaps.
  - `speckit.canon.drift-analyze`: Analyze canon and produce repair candidates.
  - `speckit.canon.drift-canonize`: Apply accepted canon entries.
- Added vibecoding-specific drift orchestration pipeline commands:
  - `speckit.canon.vibecode-specify`: Autonomous vibecoding sessions.
  - `speckit.canon.vibecode-drift`: Vibecoding drift orchestration with a direct analyze review gate.
  - `speckit.canon.vibecode-drift-reverse`: Vibecoding task drift reverse-engineering.
  - `speckit.canon.vibecode-drift-detect`: Vibecoding spec-level drift detection.
  - `speckit.canon.vibecode-drift-reconcile`: Vibecoding canon gap inference.
  - `speckit.canon.vibecode-drift-analyze`: Vibecoding entrypoint for the shared draft canon analysis review.
  - `speckit.canon.vibecode-drift-canonize`: Apply vibecoding canon plans.
  - `speckit.canon.vibecode-drift-express`: Express vibecoding drift-to-canon pipeline.
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
