# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Recent scheduler upgrades add safer and more realistic planning behavior:

- Time ordering: tasks can be sorted by due-window start time.
- Task filtering: tasks can be filtered by status and/or pet name.
- Recurring rollover: completing a `daily` or `weekly` task auto-creates the next occurrence.
- Conflict warnings: overlapping task windows are detected and reported as warnings (non-fatal).

## Testing PawPal+

Run the test suite with:

```bash
python -m pytest
```

Current tests cover core model behaviors, including:

- Marking tasks complete (status and completion timestamp updates)
- Adding tasks to a pet
- Recurring rollover behavior (`daily` creates next-day tasks, `weekly` creates next-week tasks)

Confidence Level: `★★★★☆` (4/5) based on passing core behavior tests, with room to add broader edge-case and integration coverage.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
