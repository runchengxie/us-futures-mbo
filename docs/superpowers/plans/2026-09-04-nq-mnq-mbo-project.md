# NQ/MNQ MBO Research Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a safe, testable Python project that estimates Databento costs for five years of CME NQ/MNQ MBO data and explores explicitly bounded small windows.

**Architecture:** Keep configuration, API boundary, quote logic, and exploration logic in separate modules. The CLI reads YAML and environment variables, calls Databento only after validation, and emits structured JSON suitable for saving in a report.

**Tech Stack:** Python 3.11+, `databento`, `pydantic`, `PyYAML`, `python-dotenv`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-09-04-nq-mnq-mbo-project-design.md`

## Global Constraints

- Dataset is `GLBX.MDP3`; default schema is `mbo`.
- Default dates are `2021-09-04` through `2026-09-04`.
- API keys are read from `DATABENTO_API_KEY` and never committed or printed.
- Five-year MBO downloads are never implicit; quote and exploration are separate commands.
- Tests must run without network access.

---

### Task 1: Project scaffold and dependency boundary

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/us_futures_mbo/__init__.py`
- Create: `config/quote.yaml`
- Create: `tests/__init__.py`

**Interfaces:**
- Produces an installable package and test command for later tasks.

- [ ] **Step 1: Write the failing test**

Create a smoke test that imports `us_futures_mbo` and asserts the package exposes `__version__`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_package.py -q`
Expected: FAIL because the package and test file are not yet present.

- [ ] **Step 3: Write minimal implementation**

Add package metadata, dependencies, ignored secrets/data/cache patterns, an example environment file, and the default YAML configuration.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_package.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add .gitignore .env.example pyproject.toml src tests config; git commit -m "chore: scaffold NQ MNQ MBO project"`

### Task 2: Configuration model and validation

**Files:**
- Create: `src/us_futures_mbo/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Produces `QuoteConfig.from_yaml(path)`, `QuoteConfig.from_mapping(mapping)`, and `QuoteConfig.to_request_kwargs()`.

- [ ] **Step 1: Write the failing tests**

Test default dates/symbols/schema, reject an end date before start, reject schema values other than `mbo`, and preserve `stype_in` in the request mapping.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -q`
Expected: FAIL with import or missing-model errors.

- [ ] **Step 3: Write minimal implementation**

Use a small Pydantic model with explicit fields: `dataset`, `schema`, `symbols`, `stype_in`, `start`, `end`. Parse ISO dates/timestamps and validate ordering, non-empty symbols, and the supported schema.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add src/us_futures_mbo/config.py tests/test_config.py; git commit -m "feat: validate Databento quote configuration"`

### Task 3: Databento API boundary and quote result

**Files:**
- Create: `src/us_futures_mbo/databento_client.py`
- Create: `src/us_futures_mbo/quote.py`
- Create: `tests/test_quote.py`

**Interfaces:**
- `DatabentoGateway(api_key: str)` owns the SDK client.
- `DatabentoGateway.get_cost(**request_kwargs) -> dict` delegates to `metadata.get_cost`.
- `quote_cost(config: QuoteConfig, gateway: DatabentoGateway) -> dict` returns request parameters plus normalized `cost_usd`, `billable_size_bytes`, and raw-response keys when available.

- [ ] **Step 1: Write the failing tests**

Use a recording fake gateway, not a network mock, to assert the quote passes dataset/schema/symbols/stype/date arguments and normalizes a representative Databento response without including the API key.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_quote.py -q`
Expected: FAIL because the gateway and quote function do not exist.

- [ ] **Step 3: Write minimal implementation**

Read the key only in `DatabentoGateway`; call `db.Historical(api_key)` and `metadata.get_cost`. Normalize mappings or SDK response objects defensively, converting byte counts and costs to JSON-safe values. Raise a clear configuration error when the key is empty.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_quote.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add src/us_futures_mbo/databento_client.py src/us_futures_mbo/quote.py tests/test_quote.py; git commit -m "feat: add Databento cost quote"`

### Task 4: CLI and bounded exploration

**Files:**
- Create: `src/us_futures_mbo/cli.py`
- Create: `src/us_futures_mbo/explore.py`
- Create: `tests/test_explore.py`
- Modify: `pyproject.toml`

**Interfaces:**
- CLI commands: `python -m us_futures_mbo.cli quote --config config/quote.yaml` and `python -m us_futures_mbo.cli explore --start ... --end ...`.
- `explore_window(config, gateway) -> dict` requires an explicit bounded window and returns schema/field/record summary.

- [ ] **Step 1: Write the failing tests**

Test that exploration rejects a window longer than 24 hours unless `--allow-large-window` is provided, and that its structured output contains the requested symbols and schema.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_explore.py -q`
Expected: FAIL because exploration and CLI do not exist.

- [ ] **Step 3: Write minimal implementation**

Add argparse subcommands, dotenv loading, JSON output, safe error messages, and a Databento historical metadata/data preview that does not write raw data by default. Register console scripts in `pyproject.toml`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_explore.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add src/us_futures_mbo/cli.py src/us_futures_mbo/explore.py tests/test_explore.py pyproject.toml; git commit -m "feat: add quote and bounded exploration CLI"`

### Task 5: Documentation and live quote attempt

**Files:**
- Create: `README.md`
- Create: `reports/.gitkeep`
- Modify: `config/quote.yaml`

**Interfaces:**
- Documents installation, environment setup, quote command, bounded exploration command, expected output, data licensing, and MNQ launch-date limitation.

- [ ] **Step 1: Write the documentation checks**

Add a test that README mentions `DATABENTO_API_KEY`, `metadata.get_cost`, `GLBX.MDP3`, `mbo`, and the no-raw-download default.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_readme.py -q`
Expected: FAIL because README does not exist.

- [ ] **Step 3: Write the documentation and run live probe**

Document commands and run the full five-year quote only if `DATABENTO_API_KEY` is already set in the environment. Save only sanitized quote JSON under `reports/`; if absent or rejected, report the exact non-secret reason and leave a ready-to-run command.

- [ ] **Step 4: Run all verification**

Run: `python -m pytest -q` and `python -m us_futures_mbo.cli quote --config config/quote.yaml --help`
Expected: all tests pass and CLI help exits 0.

- [ ] **Step 5: Commit**

Run: `git add README.md reports config/quote.yaml tests/test_readme.py; git commit -m "docs: document Databento research workflow"`
