# Contributing to AgriSecure

Thank you for your interest in contributing to AgriSecure! 🌾  
We welcome contributions of all kinds — bug reports, feature requests, documentation improvements, and code.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Branching Strategy](#branching-strategy)
- [Code Style Guidelines](#code-style-guidelines)
- [Reporting Issues](#reporting-issues)
- [Submitting Pull Requests](#submitting-pull-requests)

---

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
By participating, you are expected to uphold this code. Please report unacceptable behaviour to the project maintainers.

---

## 🛠️ How to Contribute

### 1. Fork the repository

Click the **Fork** button at the top right of the [repository page](https://github.com/hselinustaoglu/agri-secure) to create your own copy.

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/agri-secure.git
cd agri-secure
```

### 3. Add the upstream remote

```bash
git remote add upstream https://github.com/hselinustaoglu/agri-secure.git
```

### 4. Keep your fork up to date

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## 🌿 Branching Strategy

Use descriptive branch names with a prefix that reflects the type of change:

| Prefix | Use case |
|--------|----------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `chore/` | Maintenance tasks (deps, config) |
| `refactor/` | Code refactoring without behaviour change |
| `test/` | Adding or improving tests |

Example:

```bash
git checkout -b feat/farmer-sms-advisory
```

---

## ✏️ Code Style Guidelines

### Python (backend services)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Use [Black](https://black.readthedocs.io/) for formatting: `black .`
- Use [Ruff](https://docs.astral.sh/ruff/) for linting: `ruff check .`
- Type hints are encouraged for all function signatures.
- Write docstrings for public functions and classes.

### JavaScript / TypeScript (frontend & SMS gateway)

- Follow the project's ESLint configuration.
- Use [Prettier](https://prettier.io/) for formatting.
- Prefer TypeScript over plain JavaScript.
- Use functional React components with hooks.

### General

- Keep commits small and focused — one logical change per commit.
- Write meaningful commit messages using [Conventional Commits](https://www.conventionalcommits.org/) style:
  ```
  feat(farmer-service): add phone number validation
  fix(market-service): correct price aggregation query
  docs(readme): update setup instructions
  ```

---

## 🐛 Reporting Issues

Before opening a new issue, please:
1. Search [existing issues](https://github.com/hselinustaoglu/agri-secure/issues) to avoid duplicates.
2. Use the appropriate issue template (bug report or feature request) when available.
3. Provide as much detail as possible:
   - Steps to reproduce (for bugs)
   - Expected vs. actual behaviour
   - Screenshots or logs where relevant
   - Environment details (OS, Python/Node version, Docker version)

---

## 🔀 Submitting Pull Requests

1. Ensure your branch is up to date with `main`.
2. Run all linters and tests locally before pushing:
   ```bash
   # Python
   black . && ruff check . && pytest

   # Node.js
   npm run lint && npm test
   ```
3. Open a Pull Request against the `main` branch of this repository.
4. Fill in the PR template completely — describe what changed and why.
5. Reference the related issue using `Closes #<issue-number>` in the PR description.
6. Request a review from `@hselinustaoglu`.
7. Address all review feedback before merging.

---

Thank you for helping make AgriSecure better! 🚀
