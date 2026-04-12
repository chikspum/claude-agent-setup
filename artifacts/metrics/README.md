# Metrics Summary

This directory holds machine-readable summaries derived from run logs and validation artifacts.

Current intent:

- provide a compact operational snapshot for internal-team review
- complement markdown artifacts, not replace them
- make production-readiness checks easier to automate later

## Commands

- regenerate: `python3 scripts/generate_metrics_summary.py`
- verify drift: `python3 scripts/generate_metrics_summary.py --check`
