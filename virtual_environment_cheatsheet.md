# Virtual Environment Cheatsheet

---

## Creating a Virtual Environment

```bash
# Navigate to your project folder first
cd path/to/your/project

# Create a virtual environment named venv
python -m venv venv

# Or with a specific Python version via pyenv
pyenv local 3.12
python -m venv venv
```

---

## Activating & Deactivating

```bash
# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate (same for all)
deactivate
```

**How to know it's active:**
Your terminal prompt will show the environment name in brackets like:
```
(venv) harsh@Mac project %
```

---

## Installing Packages

```bash
# Always activate first, then install
pip install package-name

# Install from requirements.txt
pip install -r requirements.txt

# Save current packages to requirements.txt
pip freeze > requirements.txt
```

---

## Common Errors & Fixes

### `command not found: python`
```bash
# Try python3 instead
python3 -m venv venv
```

### `zsh: command not found: venv-name`
You forgot to activate the environment first:
```bash
source venv/bin/activate
```

### Packages installed but still `ModuleNotFoundError`
The environment is not active. Check your prompt — if you don't see `(venv)` at the start, activate it first.

### Wrong Python version inside the environment
```bash
# Check which python is being used
which python
python --version

# If wrong, delete and recreate with correct version
deactivate
rm -rf venv
pyenv local 3.12
python -m venv venv
source venv/bin/activate
```

### `pip: command not found`
```bash
# Use python -m pip instead
python -m pip install package-name
```

### Environment not activating after closing terminal
Virtual environments don't persist between terminal sessions. You must activate every time you open a new terminal:
```bash
cd path/to/your/project
source venv/bin/activate
```

### Accidentally installed packages globally (forgot to activate)
```bash
# Check if env is active — if not, activate it
source venv/bin/activate

# Reinstall the package inside the env
pip install package-name
```

---

## Checking What's Installed

```bash
# List all installed packages
pip list

# Check specific package
pip show package-name

# Check which python is active
which python

# Check python version
python --version
```

---

## Quick Checklist When Something Breaks

1. Is the environment active? → Check for `(venv)` in prompt
2. Are you in the right folder? → `pwd` to check
3. Is the right Python version being used? → `python --version`
4. Is the package actually installed? → `pip list`
5. Did you open a new terminal and forget to activate? → `source venv/bin/activate`

---

## Your Project Environments

| Project | Folder | Environment Name | Activate Command |
|---|---|---|---|
| Phase 1 | data-engineering/Phase-1 | venv | `source venv/bin/activate` |
| Phase 2 | data-engineering/Phase-2 | dbt-env | `source dbt-env/bin/activate` |
| Phase 3 | data-engineering/Phase-3 | venv | `source venv/bin/activate` |

---

## One Rule to Remember

> **Always activate your virtual environment before doing anything in a project.**
> Close terminal → open terminal → activate → then work.
