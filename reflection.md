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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff my scheduler makes is using a lightweight, greedy approach: it ranks tasks by urgency, schedules what fits, and flags overlapping time windows with warnings instead of running a full optimization search for the best global schedule.

This tradeoff is reasonable for this scenario because it keeps the system simple, fast, and explainable for a daily pet-care planner, while still giving useful feedback about conflicts without crashing or requiring complex optimization logic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
