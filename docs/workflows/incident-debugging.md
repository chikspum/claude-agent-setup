# Incident Debugging

Workflow for debugging failures in the hybrid agent loop.

## Common Failure Classes

- Claude changed files outside scope
- Claude claimed checks passed when they were not rerun
- environment tooling was missing
- docs drifted away from real code
- the task was too large or ambiguous for one execution pass

## Response Pattern

1. Record the failing brief and resulting diff.
2. Identify whether the failure was planning, execution, or validation.
3. Patch minor defects directly when that is cheaper.
4. Narrow the next brief instead of repeating the same prompt.
5. Record the failure mode in the quality scorecard if it recurs.
