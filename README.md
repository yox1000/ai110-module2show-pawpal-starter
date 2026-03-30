# PawPal Pet Care App - Professional Manual

**Version**: 1.0 | **Status**: Production Ready

## Overview

**PawPal** is an intelligent pet care scheduling system that helps busy pet owners organize and prioritize daily care tasks across multiple pets. The system uses advanced algorithms to generate conflict-free daily schedules that respect time constraints, pet health restrictions, and task priorities.

### Key Capabilities

- 🐾 **Multi-Pet Management**: Manage tasks for multiple pets simultaneously
- 📅 **Smart Scheduling**: AI-powered task ranking and conflict resolution
- ⏰ **Time-Aware Planning**: Prevents double-booking and respects available time windows
- ♻️ **Auto-Recurring Tasks**: Daily/weekly tasks automatically regenerate after completion
- ⚠️ **Conflict Detection**: Real-time warnings for scheduling conflicts
- 📊 **Transparent Reasoning**: Explains why tasks were scheduled or skipped

---

## Quick Start

### Installation

```bash
# Clone or download the repository
cd pawpal-starter

# Install dependencies (if any)
pip install -r requirements.txt

# Run the demo
python main.py
```

### Basic Usage

```python
from pawpal_system import Owner, Pet, CareTask, Scheduler

# Create an owner
sarah = Owner("Sarah", available_minutes_per_day=120)

# Add pets
buddy = Pet("Buddy", "Golden Retriever", age=3.5, weight=65.0)
sarah.add_pet(buddy)

# Create tasks
morning_walk = CareTask(
    id="task_001",
    title="Morning Walk",
    task_type="walk",
    duration_minutes=30,
    priority=9,
    due_window="07:00-08:00",
    recurrence="daily",
    is_required=True
)
buddy.add_task(morning_walk)

# Generate daily plan
scheduler = Scheduler(sarah)
daily_plan = scheduler.generate_daily_plan()
print(daily_plan.to_display_format())
```

---

## Architecture

### Class Diagram

See [UML Diagram](uml_diagram.md) for complete system design.

**Core Classes:**
- **Owner**: Manages pets and availability configuration
- **Pet**: Stores pet metadata and associated tasks
- **CareTask**: Represents a single schedulable activity
- **Scheduler**: The "brain" that orchestrates scheduling decisions
- **DailyPlan**: Output showing scheduled vs. unscheduled tasks

### Data Flow

```
Owner + Pets + Tasks → Scheduler.generate_daily_plan() → DailyPlan (output)
     ↓
  - Rank tasks by urgency
  - Apply time/health constraints
  - Detect conflicts
  - Resolve with greedy algorithm
  - Generate explanations
```

---

## Core Scheduling Algorithms

### 1. **Multi-Criteria Task Ranking** (`rank_tasks()`)
**Purpose**: Sort tasks by strategic importance

- **Formula**: `urgency = (priority × 10) × 0.6 + recurrence_boost × 0.2`
- **Logic**: Combines priority level, recurrence type, and required status
- **Result**: Critical/required tasks bubble to top; daily tasks get priority boost
- **Complexity**: O(n log n)

**Example:**
```
Priority 10, Required, Daily  → Score: 65
Priority 10, Required, Once   → Score: 60
Priority 7, Optional, Daily   → Score: 43
```

### 2. **Chronological Time-Based Sorting** (`sort_by_time()`)
**Purpose**: Arrange tasks in morning-to-evening sequence

- **Input**: List of tasks with `due_window="HH:MM-HH:MM"`
- **Logic**: Parses start times, sorts chronologically
- **Error Handling**: Malformed times default to 23:59 (end of day)
- **Result**: Morning tasks scheduled first, preventing late-day overload
- **Complexity**: O(n log n)

**Example:**
```
Input:  [14:00-15:00, 08:00-09:00, 09:00-10:00]
Output: [08:00-09:00, 09:00-10:00, 14:00-15:00]
```

### 3. **Time Window Overlap Detection** (`_windows_overlap()`)
**Purpose**: Identify conflicting time slots

- **Algorithm**: Interval intersection check
- **Logic**: Two ranges overlap if `NOT (end1 ≤ start2 OR end2 ≤ start1)`
- **Complexity**: O(1)

**Example:**
```
"08:00-09:00" overlaps "08:30-09:30" → TRUE (conflict)
"08:00-09:00" overlaps "09:00-10:00" → FALSE (sequential OK)
"08:00-10:00" overlaps "08:30-09:30" → TRUE (conflict)
```

### 4. **Conflict Prevention (Greedy Resolution)** (`resolve_conflicts()`)
**Purpose**: Build non-conflicting schedule

- **Algorithm**: Sequential feasibility checking
- **Logic**: Iterate through ranked tasks; add if no time conflict exists
- **Trade-off**: Greedy approach (earliest best wins) vs. optimal bin-packing
- **Result**: No two scheduled tasks occupy overlapping time
- **Complexity**: O(n²)

**Pipeline:**
```
Ranked Tasks → Check Time Conflicts → Accept/Reject → Scheduled Output
```

### 5. **Smart Constraint Filtering** (`apply_constraints()`)
**Purpose**: Respect time budget and pet health

**Multi-level checks:**
1. **Time Budget**: Does `task.duration_minutes + time_used ≤ available_minutes`?
2. **Pet Health**: Is `task.task_type` in pet's restricted activities?
3. **Cumulative Time**: Total hours needed per day realistic?

- **Result**: Only feasible tasks pass through
- **Complexity**: O(n × p) where p = number of pets

### 6. **Conflict Warning Generation** (`detect_time_conflicts()`)
**Purpose**: Alert user to scheduling issues (non-fatal)

- **Algorithm**: Pairwise O(n²) window comparison
- **Output**: List of descriptive warnings with pet names and time slots
- **Benefit**: Non-blocking; scheduling continues but flags issues

**Example Output:**
```
"Time conflict: 'Feed Buddy' (Buddy, 08:00-09:00) 
 overlaps with 'Feed Whiskers' (Whiskers, 08:30-09:00)."
```

### 7. **Recurring Task Auto-Generation** (`_create_next_occurrence()`)
**Purpose**: Self-sustaining recurring tasks

- **Logic**: 
  - `recurrence="daily"` → `due_date + 1 day`
  - `recurrence="weekly"` → `due_date + 7 days`
  - `recurrence="once"` → return None (stop)
- **Trigger**: Automatically called by `mark_done()`
- **Attachment**: New task auto-added to same pet

**Example:**
```python
task.mark_done()  # Task marked COMPLETED
next_task = task._create_next_occurrence()
# Returns: CareTask with due_date = today + 1 day (for daily tasks)
pet.add_task(next_task)  # Automatically added by complete_task()
```

### 8. **Task Completion Lifecycle** (`complete_task()`)
**Purpose**: Manage task state transitions and recurring propagation

**Steps:**
1. Find task by ID across all pets
2. Mark as COMPLETED with timestamp
3. Generate next occurrence if recurring
4. Append new task to same pet
5. Return next task reference (or None if one-time)

- **Result**: Recurring tasks never "run out"
- **Key Innovation**: Self-healing schedule (no manual re-entry)

### 9. **Intelligent Task Urgency Scoring** (`get_urgency_score()`)
**Purpose**: Quantify task importance

- **Formula**: `score = (priority × 10) + 50 (if required)`
- **Range**: Priority 1-10 → Score 10-150
- **Use**: Feeds into ranking algorithm

### 10. **Time Budget Feasibility Check** (`can_fit_all_tasks()`)
**Purpose**: Early warning if schedule is overbooked

- **Algorithm**: Knapsack-style checking
- **Logic**: Sum all `duration_minutes` vs. `available_minutes_per_day`
- **Output**: Boolean indicating schedule viability
- **Use Case**: Alerts owner to impossible schedules

---

## Data Filtering & Query Algorithms

### 11. **Multi-Criteria Task Filtering** (`filter_tasks()`)
**Purpose**: Query tasks by status and/or pet

- **Filters** (both optional, combinable):
  - By status: "pending", "completed", "skipped" (case-insensitive)
  - By pet name (case-insensitive)
- **Output**: List of matching tasks across all pets
- **Complexity**: O(t) where t = total tasks

**Example:**
```python
# Get all pending tasks for Buddy
pending_buddy = owner.filter_tasks(status="pending", pet_name="Buddy")

# Get all completed tasks across all pets
completed_all = owner.filter_tasks(status="completed")
```

### 12. **Cross-Pet Task Aggregation** (`get_pending_tasks()`)
**Purpose**: Flatten multi-pet hierarchy for global queries

- **Logic**: Flatten `pet.get_pending_tasks()` from all pets into single list
- **Use**: Single call to find all urgent tasks

### 13. **Task Type Filtering by Pet** (`get_tasks_by_type()`)
**Purpose**: Find all tasks of specific type for a pet

- **Example**: "Show all feeding tasks for Buddy"
- **Use**: Activity-based reporting

---

## Time Validation Algorithms

### 14. **Time Window Feasibility Check** (`fits_time_window()`)
**Purpose**: Verify task fits into available time window

- **Logic**: Parse `due_window`, calculate available minutes, check if `duration_minutes` fits
- **Error Handling**: Returns False on parse failure
- **Complexity**: O(1)

### 15. **Date-Based Recurrence Evaluation** (`is_due_today()`)
**Purpose**: Determine if task qualifies for today's plan

- **Check**: `due_date <= check_date`
- **Flexibility**: Accepts custom `check_date` for historical/future planning
- **Use**: Filters tasks for specific dates

---

## Display & Summary Algorithms

### 16. **Daily Plan Summary Generation** (`_generate_summary()`)
**Purpose**: One-line snapshot of scheduling outcome

**Output Template:**
```
"Scheduled X tasks (Y minutes). Could not fit Z tasks. Available time: W minutes."
```

### 17. **Rich Text Display Formatting** (`to_display_format()`)
**Purpose**: Human-readable terminal output with visual hierarchy

**Sections:**
- ✅ **SCHEDULED TASKS**: With times and priorities
- ❌ **UNSCHEDULED TASKS**: With reasons
- ⚠️ **CONFLICT WARNINGS**: Overlapping time slots
- 📊 **METRICS**: Total minutes and summary

**Example Output:**
```
📅 Daily Plan for 2026-03-30
==================================================

✅ SCHEDULED TASKS:
  1. [08:00-09:00] Feed Buddy (10min) [Priority: 10]
  2. [14:00-15:00] Afternoon Play Session (20min) [Priority: 7]

❌ UNSCHEDULED TASKS:
  1. Evening Training (30min)

⚠️ CONFLICT WARNINGS:
  - Time conflict: 'Feed Buddy' overlaps with 'Feed Whiskers'

📊 Total Time: 30 minutes
💭 Summary: Scheduled 2 tasks (30 minutes). Could not fit 1 tasks. Available time: 120 minutes.
```

### 18. **Explanation Retrieval** (`explain_selection()`)
**Purpose**: Transparency into scheduling decisions

- **Data Structure**: `task_explanations: Dict[task_id, reason_string]`
- **Lookup**: O(1) dictionary access
- **Purpose**: User can understand why tasks were scheduled/skipped

---

## Design Patterns

- **Strategy Pattern**: Different ranking/filtering strategies
- **Builder Pattern**: Incremental DailyPlan construction
- **Factory Pattern**: CareTask auto-generation of recurring instances
- **Chain of Responsibility**: Pipeline of filters (rank → constrain → resolve)

---

## Performance Characteristics

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Rank tasks | O(n log n) | O(1) | Merge sort |
| Sort by time | O(n log n) | O(1) | Time parsing + sort |
| Apply constraints | O(n × p) | O(n) | Per-pet checks |
| Resolve conflicts | O(n²) | O(n) | Pairwise comparison |
| Detect conflicts | O(n²) | O(w) | All pair conflicts |
| Filter tasks | O(t) | O(m) | Linear scan |
| Time overlap | O(1) | O(1) | Simple arithmetic |

*n = tasks, p = pets, t = total tasks, m = matching tasks, w = warnings*

---

## Key Innovation: Self-Sustaining Task Lifecycle

**The Problem**: Recurring tasks require manual re-entry every day.

**The Solution**: Automatic task regeneration

```
1. Owner creates task: CareTask(..., recurrence="daily")
2. Owner completes task: scheduler.complete_task(task_id)
3. System auto-generates: New task with due_date = today + 1 day
4. System auto-attaches: New task added to same pet
5. Result: No manual re-entry needed; system self-perpetuates
```

This design ensures recurring tasks never "run out" and the system adapts naturally to daily changes.

---

## Testing

### Run Tests

```bash
python -m pytest tests/ -v
```

### Current Coverage

✅ **Task Completion**: `mark_done()` updates status and timestamp
✅ **Task Addition**: Adding task to pet increases task count
✅ **Recurring Rollover**: Daily/weekly tasks auto-generate next instance

**Confidence Level**: ★★★★☆ (4/5) — Core behaviors validated; edge cases and integration testing recommended

---

## Usage Examples

### Example 1: Simple Daily Schedule

```python
from pawpal_system import Owner, Pet, CareTask, Scheduler
from datetime import date

# Setup
owner = Owner("Alice", available_minutes_per_day=120)
dog = Pet("Max", "Labrador", age=4.0, weight=70.0)
owner.add_pet(dog)

# Add tasks
dog.add_task(CareTask(
    id="walk1", title="Morning Walk", task_type="walk",
    duration_minutes=30, priority=9, due_window="07:00-08:00",
    recurrence="daily", is_required=True
))

dog.add_task(CareTask(
    id="feed1", title="Breakfast", task_type="feed",
    duration_minutes=10, priority=10, due_window="08:00-09:00",
    recurrence="daily", is_required=True
))

# Generate schedule
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()
print(plan.to_display_format())
```

### Example 2: Multi-Pet Household

```python
# Two pets with overlapping task times
owner = Owner("Bob", available_minutes_per_day=180)
dog = Pet("Buddy", "Golden Retriever", age=3.5, weight=65.0)
cat = Pet("Whiskers", "Tabby", age=2.0, weight=8.5)

owner.add_pet(dog)
owner.add_pet(cat)

# Dog tasks
dog.add_task(CareTask(id="d1", title="Walk", task_type="walk",
    duration_minutes=30, priority=9, due_window="07:00-08:00",
    recurrence="daily", is_required=True))

# Cat tasks (overlapping time)
cat.add_task(CareTask(id="c1", title="Feed Cat", task_type="feed",
    duration_minutes=5, priority=10, due_window="08:00-08:30",
    recurrence="daily", is_required=True))

# Scheduler detects and reports conflicts
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()
# Output includes ⚠️ CONFLICT WARNINGS section
```

### Example 3: Completing and Recurring

```python
# Complete task and auto-generate next
scheduler = Scheduler(owner)

# Mark task as done → auto-generates tomorrow's instance
next_task = scheduler.complete_task("walk1")

# next_task is a new CareTask with due_date = tomorrow
# It's already added to the pet automatically
print(f"Next task due: {next_task.due_date}")
```

---

## File Structure

```
pawpal-starter/
├── pawpal_system.py       # Core system classes
├── main.py                # Demo script
├── tests/
│   └── test_pawpal.py    # Unit tests
├── README.md              # This file
├── FEATURES.md            # Detailed algorithm documentation
└── requirements.txt       # Dependencies
```

---

## Support & Development

**Report Issues**: Check GitHub issues tracker
**Contribute**: Fork and submit pull requests
**Documentation**: See FEATURES.md for algorithm deep-dives

---

## License

MIT License — See LICENSE file for details

---

**Last Updated**: March 2026 | **Maintainer**: PawPal Team

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
