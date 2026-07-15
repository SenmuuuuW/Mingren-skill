# Manual host evaluation

Use this procedure to compare host behavior without calling a model from this repository.

1. Start a clean conversation with no earlier task context.
2. Install or load the generated Skill bundle, using `SKILL.md` as the entry instruction and making its required references available.
3. Run each `user_input` from `host_cases.yaml` exactly as written.
4. Record the observed lens selection, safety decision, language, response structure, and any prohibited behavior.
5. Score the response with `quality-rubric.md` and compare it with every required and forbidden behavior in the case.
6. Mark all failures using the product failure taxonomy; do not silently reinterpret a failed expectation.
7. Keep the prompt and loaded bundle unchanged between host or model comparisons.

This repository does not claim these manual cases have been executed. Record an actual run only after observing the host output.

## Result template

```yaml
host: ""
host_model_version: ""
date: "YYYY-MM-DD"
case_id: ""
result: pass | partial | fail
score: null
failures: []
notes: ""
```
