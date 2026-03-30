# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

- A user should be able to add their pet and owner details so the planner has the right context for daily care decisions.
- A user should be able to create and update care tasks (like walks, feeding, or medication) with duration and priority so the scheduler can choose what to include.
- A user should be able to generate and review today’s care plan so they can see what to do, in what order, and why those tasks were selected.

**a. Initial design**

My initial UML design used six main classes with clear separation between data, task management, and scheduling logic:

- `Owner`: stores owner profile data such as available time and preferences that influence planning.
- `Pet`: stores pet-specific context (name, type, routine/health notes) used to guide care decisions.
- `CareTask`: represents one care activity with attributes like duration, priority, recurrence, and status.
- `TaskManager`: handles task CRUD operations and prepares filtered task lists (for example, tasks due today).
- `Scheduler`: applies constraints and priority rules to select and order tasks into a realistic daily schedule.
- `DailyPlan`: stores the generated schedule output (scheduled tasks, unscheduled tasks, totals, and explanation summary) for display in the app.

**b. Design changes**

Yes, the design changed during implementation. I originally planned a separate `TaskManager`, but I removed it to keep the model simpler and avoid duplicating responsibilities. I moved task filtering and aggregation into `Owner` and kept scheduling decisions in `Scheduler`.

I also added `due_date` to `CareTask` and recurrence rollover behavior so completed daily/weekly tasks automatically generate the next instance. Finally, I extended `DailyPlan` with conflict warnings so the UI can surface overlapping windows as guidance instead of treating them as fatal errors.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers available minutes per day, task urgency (priority + required flag), recurrence, due-window overlap, and pet-specific restrictions from `routine_preferences` (for example, restricted activities).

I treated time availability and required/high-priority tasks as the highest-priority constraints because missing essentials like feeding or medication is worse than skipping optional enrichment. After that, I used due windows and overlap checks to keep the output realistic and explainable.

**b. Tradeoffs**

One tradeoff my scheduler makes is using a lightweight, greedy approach: it ranks tasks by urgency, schedules what fits, and flags overlapping time windows with warnings instead of running a full optimization search for the best global schedule.

This tradeoff is reasonable for this scenario because it keeps the system simple, fast, and explainable for a daily pet-care planner, while still giving useful feedback about conflicts without crashing or requiring complex optimization logic.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot in three ways: brainstorming class responsibilities, generating method skeletons, and accelerating targeted refactors/tests.

The most effective Copilot features for building the scheduler were:

- Inline Chat inside methods (for example, quickly drafting `sort_by_time` and conflict-detection helpers).
- Copilot Chat for converting design intent into concrete method signatures and test cases.
- In-editor completions for repetitive code patterns (dataclass fields, table-display dicts, and test setup blocks).

The most helpful prompts were specific and bounded, such as: “add a method that filters tasks by status and pet name,” “create non-fatal conflict detection warnings,” and “write tests for daily/weekly recurrence rollover.”

**b. Judgment and verification**

One suggestion I modified was introducing extra manager-layer complexity for task handling. I rejected a heavy abstraction and kept the architecture cleaner: `Owner`/`Pet` hold state, `Scheduler` computes decisions, and `DailyPlan` stores output.

I verified AI suggestions by running the terminal demo (`main.py`), checking outputs for sorted order/conflict warnings, and running unit tests for completion and recurrence behavior. I only kept suggestions that fit the existing class boundaries and passed those checks.

Using separate chat sessions for different phases (UML/design, backend logic, Streamlit wiring, testing/reflection) helped me stay organized because each session had a narrow objective and less context noise. That made it easier to compare AI ideas against the current phase goals instead of mixing architecture and implementation concerns.

My key “lead architect” lesson is that AI is best used as a fast implementation partner, not the decision-maker. I got better results when I set clear boundaries, required method-level accountability, and used tests plus runtime checks to validate every major suggestion.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion state changes, task addition to pets, and recurring rollover behavior for both daily and weekly tasks. I also validated sorting, filtering, and conflict-warning behavior through terminal runs in `main.py`.

These tests were important because they cover the highest-risk scheduler behaviors: state transitions, recurrence correctness, and whether the system produces usable planning output without crashing when tasks overlap.

**b. Confidence**

I am moderately high confidence (`4/5`) that the current scheduler works correctly for the supported flows because core tests pass and terminal/UI behavior is consistent with the design.

If I had more time, I would test malformed time windows, tasks spanning midnight, duplicate task IDs, timezone/date-boundary behavior, and larger task sets to evaluate performance and fairness of the greedy prioritization strategy.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the architecture staying clean while features expanded: domain state in `Owner`/`Pet`/`CareTask`, decision logic in `Scheduler`, and display output in `DailyPlan` and Streamlit UI.

**b. What you would improve**

In another iteration, I would improve schedule optimization beyond greedy ranking (for example, search-based or scoring optimization), add task editing/completion actions directly in the UI, and increase automated test coverage for edge cases and integration paths.

**c. Key takeaway**

A key takeaway is that strong results come from treating AI as an accelerator while keeping architectural ownership. Defining boundaries first, then using AI for targeted implementation and verification, produced faster progress without losing design clarity.
