# Issues Found in energy_system.py

Line numbers refer to the original file. Sources: `pylint_before.txt` (6.14/10), `bandit_before.txt` (1 medium), `flake8_before.txt` (12 findings).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `eval()` on user input | Security (Bandit B307, Pylint W0123) | 63 | The prompt result is passed to `eval`, so any Python expression runs on the machine. Confirmed by entering `__import__('os').getcwd()`, which executed. Malformed input also crashes the program with a traceback. | Replaced with a `parse_units` helper using `float()`, rejecting non-finite values, with `try/except ValueError` in `main`. Prompt text updated since expressions are no longer accepted. |
| Mutable default argument `history=[]` | Bug (Pylint W0102) | 12 | The list is created once and shared across every call, so history leaks between calls. The "Readings stored so far: 3" output only worked because of this bug. | Default changed to `None` and the list is created inside the function. `main` now owns its own `history` list and passes it in. |
| Bare `except:` | Bug (Pylint W0702, Flake8 E722) | 44 | Catches every exception, including `KeyboardInterrupt`, and hides real errors by silently resetting `meters` to `{}`. | Catch only `OSError` and `json.JSONDecodeError`. |
| Files opened without `with` and without encoding | Resource handling (Pylint R1732, W1514) | 42, 48 | `load_meter_data` never closes its file. Encoding depends on the operating system. | Used `with open(..., encoding="utf-8")` with `json.load` and `json.dump`. |
| Negative readings accepted | Logic (no tool reported it) | 12-15, 55 | A reading of -50 for M-03 was stored and produced a bill of -192.50. | `record_reading` raises `ValueError` for negative units, and `main` handles it. The M-03 bill line was removed because the meter is never created. |
| Global statements and shared mutable state | Design (Pylint W0603) | 27, 40 | `raise_rates` and `load_meter_data` modify module-level variables, making behaviour order-dependent and hard to test. | `meters` is passed as an argument, `raise_rates` returns new rates, and `load_meter_data` returns the dict. |
| Unused import `sys` | Style (Pylint W0611, Flake8 F401) | 2 | Dead import. | Removed. |
| Unnecessary `elif` after `return` | Style (Pylint R1705) | 19 | Redundant branching in the billing function. | Rewrote `compute_bill` as three computed slabs multiplied by their rates. This also removed the 88-character line. |
| Old-style `%` string formatting | Style (Pylint C0209) | 59, 60, 66 | Prefer f-strings. | Converted to f-strings. |
| Missing docstrings | Style (Pylint C0114, C0116) | 1, 12, 17, 26, 32, 39, 47, 52 | No module or function documentation. | Added a module docstring and a docstring for every function. |
| Lines over 79 characters | Style (Flake8 E501) | 24, 62 | Line 24 is 88 characters and line 62 is 86 characters. Pylint did not flag these because its limit is 100. | Line 24 removed by the `compute_bill` rewrite. Line 62 shortened by the new prompt wording. |
| Wrong blank-line spacing | Style (Flake8 E302, E305) | 12, 17, 26, 32, 39, 47, 52, 68 | Only one blank line between top-level definitions and before the final call. | Two blank lines everywhere. `main()` placed under an `if __name__ == "__main__":` guard. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.14/10 | 10 |
| Bandit | 1 issue (Medium) | 0 issues |
| Flake8 | 12 findings | 0 findings |
