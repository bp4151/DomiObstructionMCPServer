# Open Source Best Practices Guide

This document lists recommended practices for running this repository as a healthy open source project, including **branch protection rules**, documentation, community, security, and automation. Use it as a checklist and reference.

---

## 1. Documentation & Discoverability

| Practice | Description | Status / Action |
|----------|-------------|-----------------|
| **README** | Clear project name, description, install/run instructions, and links to more docs. | ✅ Present; keep updated. |
| **LICENSE** | Visible license file (e.g. `LICENSE` or `LICENSE.md`) in repo root. | ✅ Present (MIT). |
| **CONTRIBUTING.md** | How to contribute: branching, PR process, code style, how to run tests. | Add in repo root. |
| **CODE_OF_CONDUCT.md** | Community standards (e.g. Contributor Covenant). | Add in repo root or `.github/`. |
| **CHANGELOG.md** | Human-readable list of notable changes per version. | Add and update with each release. |
| **SECURITY.md** | How to report vulnerabilities and supported versions. | Add (see Security section). |
| **Issue / PR templates** | Standardized templates so issues and PRs include needed context. | Add under `.github/`. |
| **API or user docs** | Links from README to server/client docs (e.g. `../server/README_SERVER.md`, `../client/README_CLIENT.md`). | ✅ Referenced in README. |

---

## 2. Branch Protection Rules

Configure branch protection on the **default branch** (e.g. `main` or `master`) so that changes go through review and CI. Below are concrete recommendations.

### Where to configure (GitHub)

**Settings → Repository → General → Default branch**  
Set the default branch (e.g. `main`).

**Settings → Repository → Code and automation → Branches → Add branch protection rule**  
Create a rule for the default branch (e.g. `main`).

### Recommended settings

| Setting | Recommendation | Why |
|--------|----------------|-----|
| **Branch name pattern** | `main` (or `master`) | Protects only the default branch; use a second rule for `release/*` if needed. |
| **Require a pull request before merging** | ✅ Enabled | No direct pushes; all changes go through PRs. |
| **Required approvals** | At least **1** (2 for larger teams) | Ensures a second pair of eyes. |
| **Dismiss stale pull request approvals when new commits are pushed** | ✅ Enabled | New commits require a fresh review. |
| **Require review from Code Owners** | ✅ Enabled (if using CODEOWNERS) | CODEOWNERS must approve when their paths change. |
| **Require status checks to pass before merging** | ✅ Enabled | Merge only when CI (lint, tests) succeeds. |
| **Require branches to be up to date before merging** | Optional (✅ if CI is fast) | Reduces merge skew; can be disabled if CI is slow. |
| **Require conversation resolution before merging** | ✅ Enabled | All review comments must be resolved. |
| **Require signed commits** | Optional | Improves integrity; needs contributors to have signing set up. |
| **Require linear history** | ✅ Recommended | Enforces squash or rebase; keeps history clean. |
| **Do not allow bypassing the above settings** | ✅ For org repos | Prevents admins from bypassing (use with care). |
| **Allow force pushes** | ❌ Disable | Prevents rewriting protected branch history. |
| **Allow deletions** | ❌ Disable | Prevents accidental deletion of the default branch. |
| **Restrict who can push to matching branches** | Optional | Leave empty to allow all contributors with write access to open PRs; restrict only if you need a smaller set of pushers. |

### Summary: minimal branch protection rule (GitHub UI)

- **Branch name pattern:** `main`
- **Require a pull request:** Yes, with at least 1 approval
- **Dismiss stale pull request approvals when new commits are pushed:** Yes
- **Require review from Code Owners:** Yes
- **Require status checks to pass:** Yes (select your CI workflow, e.g. “lint”, “test”)
- **Require conversation resolution:** Yes
- **Require linear history:** Yes (or “Allow squash merging” as default)
- **Do not allow force pushes:** Yes
- **Do not allow branch deletion:** Yes

### Allowing contributions from forks

- **Allow fork pull requests:** In the same branch protection rule, under “Rules applied to everyone including administrators”, do **not** restrict pushes by actor; then in **Settings → General**, ensure “Allow fork pull requests” (or similar) is enabled so external contributors can open PRs from their forks. Branch protection will still require approvals and status checks for those PRs.

---

## 3. Issue and Pull Request Templates

| Item | Location | Purpose |
|------|----------|--------|
| **Issue template** | `.github/ISSUE_TEMPLATE/` | Bug report, feature request, or generic issue so submitters include environment, steps, and context. |
| **PR template** | `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md` | Checklist (e.g. tests added, docs updated, CHANGELOG) and link to related issue. |
| **Config** | `.github/ISSUE_TEMPLATE/config.yml` | Optional; customizes issue template chooser. |

Example PR template contents: link to issue, type of change, checklist (tests, docs, CHANGELOG), and any deployment notes.

---

## 4. Code of Conduct

- Add **CODE_OF_CONDUCT.md** in the repo root (or in `.github/`).
- Use a standard such as [Contributor Covenant](https://www.contributor-covenant.org/) (v2.1 or later).
- Optionally add a contact method (e.g. email or GitHub username) for conduct reports.
- Reference it in README and CONTRIBUTING.

---

## 5. Contributing Guide (CONTRIBUTING.md)

Include at least:

- How to clone, install dependencies, and run the project (or link to README/server docs).
- How to propose changes: create a branch, open an issue first for large changes, open a PR against the default branch.
- Code/style expectations: formatter (e.g. Ruff, Black), linter, type checks; “run `make lint` / `uv run ...` before submitting”.
- That PRs should pass CI and require review (point to branch protection).
- How to update docs and CHANGELOG when relevant.
- Link to CODE_OF_CONDUCT and LICENSE.

---

## 6. Security

| Practice | Description |
|----------|-------------|
| **SECURITY.md** | Add at repo root. Describe supported versions, how to report vulnerabilities (e.g. private email or GitHub Security Advisories), and expected response. |
| **Dependency updates** | Enable Dependabot (or Renovate): **Settings → Code security and analysis → Dependabot → Enable**; add `.github/dependabot.yml` for schedule and groups if desired. |
| **Vulnerability alerts** | Enable “Dependabot alerts” so you see known vulnerabilities in dependencies. |
| **Secrets** | Never commit secrets; use repo or environment secrets in CI; consider `gitleaks` or GitHub secret scanning. |
| **Supply chain** | For published packages, consider signed commits/tags and provenance (e.g. GitHub Actions build attestations). |

---

## 7. CI/CD and Quality

| Practice | Description |
|----------|-------------|
| **Lint and test on PR** | Run linter and tests on every PR (e.g. GitHub Actions); require these as status checks in branch protection. |
| **Single source of truth** | Reuse the same commands in CI that CONTRIBUTING asks contributors to run locally (e.g. `uv run ruff check`, `uv run pytest`). |
| **Cache dependencies** | In CI, cache `uv` / pip caches to speed up runs. |
| **Matrix (optional)** | If the project supports multiple Python versions or OSes, run tests in a matrix. |
| **No direct push to default** | Rely on branch protection; all changes via PR. |

---

## 8. Releases and Versioning

| Practice | Description |
|----------|-------------|
| **Semantic versioning** | Use [SemVer](https://semver.org/) (e.g. `v1.2.3`) for tags and releases. |
| **CHANGELOG** | Maintain CHANGELOG.md (e.g. Keep a Changelog format); update with each release. |
| **Git tags** | Tag releases (e.g. `git tag v1.0.0`); push tags so GitHub Releases can use them. |
| **Release notes** | For each release, add a short summary and “what’s changed” (can be generated from CHANGELOG or PRs). |
| **Automation** | Optional: GitHub Action to create a release and upload assets when a version tag is pushed. |

---

## 9. Repository Settings (GitHub)

| Setting | Recommendation |
|---------|----------------|
| **Default branch** | `main` (or `master`); set in Settings → General. |
| **Description & topics** | Short description and topics (e.g. `mcp`, `wprdc`, `pittsburgh`) for discoverability. |
| **Website** | Link to docs or live app if applicable. |
| **Issues** | Enable issues; use labels (e.g. `bug`, `enhancement`, `good first issue`). |
| **Discussions** | Optional; useful for Q&A and ideas without opening issues. |
| **Wiki** | Optional; only if you prefer wiki over `/docs` in repo. |
| **Forking** | Allow forks so external contributors can open PRs. |
| **Merge methods** | Prefer “Squash and merge” or “Rebase and merge” if you require linear history. |

---

## 10. Dependency and Code Health

| Practice | Description |
|----------|-------------|
| **Pin versions** | Lock file (e.g. `uv.lock`) and pinned dependencies in Dockerfiles for reproducible builds. |
| **Dependabot / Renovate** | Automated dependency PRs; group minor/patch updates to reduce noise. |
| **License compliance** | Ensure dependencies’ licenses are compatible with your LICENSE (e.g. MIT); add a simple license check in CI if needed. |
| **Deprecation policy** | In CONTRIBUTING or README, state how long old behavior will be supported when you make breaking changes. |

---

## 11. Community and Maintenance

| Practice | Description |
|----------|-------------|
| **Respond to issues/PRs** | Aim for a first response within a few days; close stale issues with a polite message. |
| **Labels** | Use `good first issue`, `help wanted`, `priority: high` (or similar) to guide contributors. |
| **Stale bot** | Optional: GitHub Action to mark or close stale issues/PRs with a comment. |
| **Single maintainer** | If solo, state in README how contributions are welcomed and that response times may vary. |

---

## 12. Quick Checklist

- [ ] Branch protection on default branch (PR required, approvals, status checks, no force push)
- [ ] CODEOWNERS with repo owner (or team) for entire repo
- [ ] CONTRIBUTING.md with how to run and submit changes
- [ ] CODE_OF_CONDUCT.md (e.g. Contributor Covenant)
- [ ] SECURITY.md for vulnerability reporting and supported versions
- [ ] Issue and PR templates under `.github/`
- [ ] CHANGELOG.md and SemVer tags for releases
- [ ] CI runs lint and tests; required as status checks
- [ ] Dependabot (or similar) enabled; dependency alerts on
- [ ] README and LICENSE up to date and easy to find

This list focuses on practices that work well for most open source projects; adjust to your project size and hosting platform (e.g. GitHub, GitLab, or others).
