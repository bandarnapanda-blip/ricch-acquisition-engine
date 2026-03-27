# WORKFLOW: /plan
# File: .agent/workflows/plan.md
# Trigger: User types /plan OR task touches more than one file

---

When this workflow is triggered, follow this exact sequence.
Do NOT write application code until the user types "Approve".

---

## STEP 1 — DISCOVERY

Read the relevant files before forming any opinion.
Use search to find:
- Which files are involved in this task
- Current function signatures and return types
- Existing DB table structure if relevant
- Any existing tests for the affected area

State what you found. Do not assume.

---

## STEP 2 — REQUIREMENT ANALYSIS

List exactly what the user asked for.
Clarify any ambiguity with ONE question if needed.
State which agents/divisions are involved.

---

## STEP 3 — WRITE Implementation_Plan.md

Create this file in the project root.
Structure it exactly like this:

```
# Implementation Plan: [Feature Name]
## Date: [today]
## Requested by: Khalil
## Agents involved: [list]

### Phase 1: Setup & Dependencies
- [ ] What needs to be installed or configured first

### Phase 2: Backend / Database
- [ ] Supabase schema changes (if any)
- [ ] Python file changes
- [ ] New functions needed

### Phase 3: Frontend / UI
- [ ] React component changes
- [ ] API hook changes
- [ ] New endpoints needed in api.py

### Phase 4: Agent Integration
- [ ] Which Division pipeline steps are affected
- [ ] Validation requirements (Vex sign-off needed?)
- [ ] Silas trigger changes (if any)

### Phase 5: Testing & Verification
- [ ] How to confirm this works
- [ ] What could break
- [ ] Rollback plan if something goes wrong

### Files to modify:
- file1.py — what changes and why
- file2.tsx — what changes and why

### Files NOT to touch:
- List any files that must be preserved exactly
```

---

## STEP 4 — PAUSE

After writing the plan, say exactly this:

"Implementation_Plan.md is ready. Does this plan look correct?
Type **Approve** to begin Phase 1, or tell me what to change."

Do not write any code until "Approve" is received.

---

## STEP 5 — EXECUTE (after Approve)

Execute one phase at a time.
After each phase, report what was done and ask to continue.
Never skip phases.
Never modify files outside the plan without asking first.
