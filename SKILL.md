---
name: openclaw-cron-standard
version: 0.1.0
description: Standardize OpenClaw cron wrappers and prompts to a safe shared contract. Use when auditing or fixing cron jobs that rely on ClankerHive claims, result JSON artifacts, cron delivery status, or wrapper scripts. Prevent stale result files, duplicate-run confusion, and claim-string drift by enforcing a single wrapper and prompt pattern.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["python3"] }
    }
  }
---

# openclaw-cron-standard

Use this skill when cleaning up or designing OpenClaw cron jobs.

## Standard contract

For cron wrappers:

1. Clear the old result artifact before a new run.
2. Claim through one shared helper.
3. If the claim reports `ALREADY_CLAIMED`, print that sentinel, exit 0, and do not write a result artifact.
4. Only write a result JSON for a real execution or a real failure.
5. Keep result artifacts as the source of truth for real runs, not duplicate-run guards.

For cron prompts:

1. Run the wrapper first.
2. If it prints `ALREADY_CLAIMED`, reply only with `NO_REPLY`.
3. Only then read the result JSON.
4. Never read a stale artifact after a duplicate-claim guard path.

For cron health and debug tooling:

1. Treat `/root/.openclaw/cron/jobs.json` as the job definition store.
2. Read live runtime state from `/root/.openclaw/cron/jobs-state.json`.
3. Do not rely on embedded `job.state` in `jobs.json`; it may be empty or stale.
4. Report missing entries from `jobs-state.json` separately from jobs that have never run.

For cron delivery configuration:

1. Infer the expected delivery mode from the job contract.
2. Use `delivery.mode: "announce"` for jobs that rely on reply-text delivery.
3. Use `delivery.mode: "none"` only for jobs that send explicitly through the `message` tool or are intentionally silent.
4. Do not bulk-normalize every job to `delivery.mode: "none"` unless each job has been migrated away from reply-text delivery.

## Why this matters

The fragile failure mode is usually contract drift across three places:

- wrapper behavior
- prompt behavior
- claim string expectations such as `already claimed` vs `already-claimed`
- runtime state location
- delivery mode expectations

That drift can turn a healthy duplicate-run guard into a fake failure or a silent not-delivered run.

## Preferred implementation shape

Use a small shared helper module for:

- `prepare_result_path(...)`
- `claim_or_exit(...)`
- `run(...)`

Keep wrapper-specific business logic outside the shared helper.

## Audit checklist

- no result artifact written on `ALREADY_CLAIMED`
- stale result file is removed before each run
- prompts check the sentinel before reading the artifact
- health/debug tools read `jobs-state.json`, not embedded `job.state`
- reply-delivery jobs use `delivery.mode: "announce"`
- explicit `message`-tool or intentionally silent jobs use `delivery.mode: "none"`
- validator passes after edits
- dead scratch wrappers and tmp scripts are removed if unreferenced

## Good migration order

1. Patch the wrapper contract first.
2. Patch the live cron prompt second.
3. Patch the job delivery contract.
4. Validate health tooling against `jobs-state.json`.
5. Validate with the cron validator.
6. Remove dead one-off scripts after reference checks.

## Scope guidance

This skill is for cron wrapper standardization, not for changing the business logic of a cron job unless that logic is required to fit the contract.
