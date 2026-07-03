# MCTP IP Jarvis Loop 100-Turn Adaptive Run Summary

Status: paused_pending_approval

Run ID: `mctp_ip_jarvis_loop_20260703_100turn_adaptive_run`

Target thread: `019f1dce-6a25-7eb3-9f54-2b6c9d5291f9` (`MCTP IP 개발`)

This run continues from the completed 10-turn dry run and tests adaptive prompt generation: each next prompt should be derived from the previous result and should move the mission forward without crossing approval gates.

Initial verdict inherited from the 10-turn run: `go-with-approval-gates`.

## Current Status

Completed turns: `2/100`

Previous pause reason: Turn 1 reached the approval gate. The target thread identified the next bounded mission-progress action as creating one OAG verification/evidence dispatch for `CON_APB_CSR_CDC` / `OBL_CONFIG_APB_CDC`.

Brian approved this gate with: `승인 함`

Current allowed scope:

- Create one bounded OAG verification dispatch for `CON_APB_CSR_CDC` / `OBL_CONFIG_APB_CDC`
- Generate fresh APB CSR evidence
- Generate receipt
- Run only the minimum verification needed for that bounded dispatch

Still forbidden:

- Closure/signoff
- `oag.decide` final closure
- Git stage/commit/push
- Unrelated RTL/TB edits
- Broad random regression unless Brian expands scope
- Static CDC/RDC signoff
- Timing/STA

## Turn 1 Result

The target thread produced a minimal fresh verification dispatch scope proposal:

- Contract: `CON_APB_CSR_CDC`
- Primary obligation: `OBL_CONFIG_APB_CDC`
- Adjacent only if needed: `CON_IRQ_COUNTER_STATUS`
- Evidence to refresh: APB response decode, APB write/read side-effect rules, counter/status clear priority, descriptor ownership side effects, reset/default APB-visible state
- Candidate checks: lint/structural review, directed APB CSR simulation, targeted formal/property check if already available, evidence freshness scan
- Exclusions: release signoff, static CDC/RDC signoff, timing/STA, unrelated RTL/TB edits, broad random regression unless Brian expands scope

## Previous Approval

Previous approval was granted by Brian with: `승인 함`

## Turn 2 Result

Turn 2 did not complete the approved bounded dispatch.

Incident:

- The target thread checked `python3 formal/run_formal.py --help`.
- That command unexpectedly executed the full formal script.
- Three formal jobs passed, but formal output files changed before an OAG dispatch/receipt existed.
- No dispatch, evidence record, or receipt was created.
- The bounded `CON_APB_CSR_CDC` dispatch result is therefore `inconclusive`, not pass.

Changed formal output scope reported by target thread:

- `formal/formal_status.json`
- `formal/formal_apb_counter_priority.log`
- `formal/formal_axi_read_body.log`
- `formal/formal_axi_write_ingress.log`
- `formal/runs/formal_apb_counter_priority/*`
- `formal/runs/formal_axi_read_body/*`
- `formal/runs/formal_axi_write_ingress/*`

Controller local verification:

- `git diff --stat -- formal` reported 37 formal files changed.
- Target repo also has pre-existing OAG/RTL dirty state; no rollback was performed.

## Current Approval Needed

```text
Brian, approve proceeding from the current worktree by treating the accidental formal rerun as quarantined pre-dispatch evidence, then creating a fresh bounded OAG dispatch/receipt for `CON_APB_CSR_CDC` only?
```

## Controller Lesson

When a handoff is newer than contract evidence, route to fresh verification dispatch before integration or closure.

Additional lesson from Turn 2:

Never probe repo-local execution scripts with `--help` unless the script is known argparse-safe; inspect the file first or use documented commands only.
