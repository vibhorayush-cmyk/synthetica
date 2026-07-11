# Contributing to Synthetica

Thank you for improving Synthetica.

## Setup

Follow the [development guide](docs/development.md), run backend tests, then
run frontend tests, typecheck, and build before submitting a pull request.

## Branches and commits

- Use focused branch names such as `feat/banking-scenarios` or
  `fix/export-path-validation`.
- Write imperative, scoped commit messages such as `feat: add retail template`.
- Keep unrelated formatting or refactors out of feature changes.

## Pull request checklist

- [ ] Describe the motivation and implementation.
- [ ] Add or update tests.
- [ ] Run `python -m pytest`.
- [ ] Run `npm run typecheck` and `npm run build` in `frontend` when UI changes.
- [ ] Update documentation for API, plugin, or configuration changes.
- [ ] Do not commit generated exports, secrets, or local environments.

## Plugin contributions

Implement the plugin contract, expose complete frontend metadata, validate
configuration, register scenarios and quality rules, and provide tests for
relationships and export behavior. See [docs/plugins.md](docs/plugins.md).

## Code quality

Use strict TypeScript, typed Python, focused components/services, PEP 8 style,
and accessible UI patterns. Preserve backwards-compatible API behavior unless a
change is explicitly proposed and documented.
