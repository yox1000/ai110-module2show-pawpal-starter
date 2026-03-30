from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date, time, timedelta
from enum import Enum




class TaskStatus(Enum):
    """Enumeration for task status values."""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """Enumeration for types of care tasks."""
    WALK = "walk"
    FEED = "feed"
    MEDICATION = "medication"
    PLAY = "play"
    GROOMING = "grooming"
    TRAINING = "training"
    VETERINARY = "veterinary"
    OTHER = "other"


@dataclass
class Pet:
    """Represents a pet that needs care."""
    name: str
    species: str
    age: float
    weight: float
    health_notes: str = ""
    routine_preferences: Dict = field(default_factory=dict)
    tasks: List['CareTask'] = field(default_factory=list)

    def update_pet_info(self, **kwargs):
        """Update pet information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_health_note(self, note: str):
        """Add a health note to the pet's record."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.health_notes += f"\n[{timestamp}] {note}"

    def get_care_context(self) -> Dict:
        """Return a summary of pet's care context."""
        pending_tasks = [t for t in self.tasks if t.status == TaskStatus.PENDING.value]
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "health_notes": self.health_notes,
            "pending_tasks_count": len(pending_tasks),
            "routine_preferences": self.routine_preferences
        }

    def add_task(self, task: 'CareTask'):
        """Add a task to this pet."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List['CareTask']:
        """Get all pending tasks for this pet."""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING.value]

    def get_tasks_by_type(self, task_type: str) -> List['CareTask']:
        """Get all tasks of a specific type."""
        return [t for t in self.tasks if t.task_type == task_type]



@dataclass
class CareTask:
    """Represents a care task to be scheduled."""
    id: str
    title: str
    task_type: str
    duration_minutes: int
    priority: int
    due_window: str  # Format: "HH:MM-HH:MM" (e.g., "08:00-12:00")
    recurrence: str  # "daily", "weekly", "once", etc.
    is_required: bool
    due_date: date = field(default_factory=date.today)
    status: str = TaskStatus.PENDING.value
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def edit_task(self, **kwargs):
        """Update task attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ["id", "created_at"]:
                setattr(self, key, value)

    def mark_done(self) -> Optional['CareTask']:
        """Mark task complete and create the next recurring instance if applicable."""
        self.status = TaskStatus.COMPLETED.value
        self.completed_at = datetime.now()
        return self._create_next_occurrence()

    def mark_skipped(self):
        """Mark task as skipped."""
        self.status = TaskStatus.SKIPPED.value

    def is_due_today(self, check_date: Optional[date] = None) -> bool:
        """Check if task is due today based on recurrence."""
        if check_date is None:
            check_date = date.today()

        return self.due_date <= check_date

    def fits_time_window(self, start_time: str, end_time: str) -> bool:
        """Check if task fits within a time window (format: HH:MM)."""
        try:
            task_start, task_end = self.due_window.split("-")
            window_start = datetime.strptime(start_time, "%H:%M").time()
            window_end = datetime.strptime(end_time, "%H:%M").time()
            task_start_time = datetime.strptime(task_start, "%H:%M").time()
            task_end_time = datetime.strptime(task_end, "%H:%M").time()
            
            # Check if task window overlaps with available window
            available_duration = (
                datetime.combine(date.today(), window_end) -
                datetime.combine(date.today(), window_start)
            ).total_seconds() / 60
            
            return self.duration_minutes <= available_duration
        except ValueError:
            return False

    def get_urgency_score(self) -> int:
        """Calculate urgency based on priority and required status."""
        score = self.priority * 10
        if self.is_required:
            score += 50
        return score

    def _create_next_occurrence(self) -> Optional['CareTask']:
        """Return the next pending instance for daily/weekly tasks, or None for non-recurring ones."""
        recurrence = self.recurrence.lower().strip()
        if recurrence == "daily":
            next_due_date = self.due_date + timedelta(days=1)
        elif recurrence == "weekly":
            next_due_date = self.due_date + timedelta(days=7)
        else:
            return None

        return CareTask(
            id=f"{self.id}__next_{next_due_date.isoformat()}",
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_window=self.due_window,
            recurrence=self.recurrence,
            is_required=self.is_required,
            due_date=next_due_date,
        )



class Owner:
    """Represents a pet owner."""

    def __init__(self, name: str, available_minutes_per_day: int):
        """Initialize an owner profile with availability and pet storage."""
        self.name: str = name
        self.available_minutes_per_day: int = available_minutes_per_day
        self.preferences: Dict = {}
        self.notes: str = ""
        self.pets: List[Pet] = []

    def update_profile(self, **kwargs):
        """Update owner profile information."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != "pets":
                setattr(self, key, value)

    def set_availability(self, minutes: int):
        """Set available minutes per day."""
        self.available_minutes_per_day = minutes

    def set_preferences(self, preferences: Dict):
        """Set owner preferences."""
        self.preferences.update(preferences)

    def add_pet(self, pet: Pet):
        """Add a pet to owner's profile."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]
        return len(self.pets) < len(self.pets)

    def get_all_tasks(self) -> Dict[str, List[CareTask]]:
        """Get all tasks across all pets."""
        all_tasks = {}
        for pet in self.pets:
            all_tasks[pet.name] = pet.tasks
        return all_tasks

    def filter_tasks(
        self,
        status: Optional[str] = None,
        pet_name: Optional[str] = None,
    ) -> List[CareTask]:
        """Return tasks matching optional status and/or pet-name filters."""
        normalized_status = status.lower().strip() if isinstance(status, str) else None
        normalized_pet_name = pet_name.lower().strip() if isinstance(pet_name, str) else None

        filtered_tasks: List[CareTask] = []
        for pet in self.pets:
            if normalized_pet_name and pet.name.lower() != normalized_pet_name:
                continue

            for task in pet.tasks:
                if normalized_status and task.status.lower() != normalized_status:
                    continue
                filtered_tasks.append(task)

        return filtered_tasks

    def get_pending_tasks(self) -> List[CareTask]:
        """Get all pending tasks across all pets."""
        pending = []
        for pet in self.pets:
            pending.extend(pet.get_pending_tasks())
        return pending

    def get_total_task_time_needed(self) -> int:
        """Calculate total minutes needed for all pending tasks."""
        total = 0
        for task in self.get_pending_tasks():
            total += task.duration_minutes
        return total

    def can_fit_all_tasks(self) -> bool:
        """Check if owner has enough time for all pending tasks."""
        return self.get_total_task_time_needed() <= self.available_minutes_per_day




class Scheduler:
    """The "Brain" that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner):
        """Initialize scheduler rules and scoring weights for an owner."""
        self.owner: Owner = owner
        self.available_time: int = owner.available_minutes_per_day
        self.priority_rules: Dict = {"required": 100, "high": 80, "medium": 50, "low": 20}
        self.constraint_rules: Dict = {"time_window": True, "pet_health": True}
        self.scoring_weights: Dict = {"priority": 0.6, "recurrence": 0.2, "duration": 0.2}
        self.task_explanations: Dict[str, str] = {}
        self.conflict_warnings: List[str] = []

    def generate_daily_plan(self, target_date: Optional[date] = None) -> 'DailyPlan':
        """Generate an optimized daily plan for all pets."""
        if target_date is None:
            target_date = date.today()

        self.task_explanations = {}
        self.conflict_warnings = []

        # Get all tasks due today
        all_tasks = self.owner.get_pending_tasks()
        due_tasks = [t for t in all_tasks if t.is_due_today(target_date)]

        # Rank and filter tasks
        ranked_tasks = self.rank_tasks(due_tasks)
        feasible_tasks = self.apply_constraints(ranked_tasks, self.available_time)
        self.conflict_warnings = self.detect_time_conflicts(feasible_tasks)
        scheduled_tasks = self.resolve_conflicts(feasible_tasks)

        # Create daily plan
        plan = DailyPlan(target_date.strftime("%Y-%m-%d"))
        for task in scheduled_tasks:
            plan.add_scheduled_item(task, task.due_window)

        # Add unscheduled tasks
        unscheduled = [t for t in ranked_tasks if t not in scheduled_tasks]
        plan.unscheduled_items = unscheduled
        plan.reasoning_summary = self._generate_summary(scheduled_tasks, unscheduled)
        plan.conflict_warnings = self.conflict_warnings

        return plan

    def rank_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Sort tasks by urgency and importance."""
        def calculate_score(task: CareTask) -> float:
            urgency = task.get_urgency_score()
            recurrence_boost = 0.5 if task.recurrence == "daily" else 0.2
            return urgency * self.scoring_weights["priority"] + recurrence_boost
        
        return sorted(tasks, key=calculate_score, reverse=True)

    def sort_by_time(self, tasks: List[CareTask]) -> List[CareTask]:
        """Sort tasks by due-window start time so earlier tasks come first."""
        def get_start_time(task: CareTask) -> time:
            try:
                start_str = task.due_window.split("-")[0].strip()
                return datetime.strptime(start_str, "%H:%M").time()
            except (ValueError, IndexError):
                return time(23, 59)

        return sorted(tasks, key=get_start_time)

    def apply_constraints(self, tasks: List[CareTask], available_minutes: int) -> List[CareTask]:
        """Filter tasks based on constraints (time, health, etc.)."""
        feasible = []
        time_used = 0

        for task in tasks:
            # Check if fits in available time
            if time_used + task.duration_minutes > available_minutes:
                continue

            # Check pet health constraints
            pet = self._find_pet_for_task(task)
            if pet and "restrict_activities" in pet.routine_preferences:
                if task.task_type in pet.routine_preferences["restrict_activities"]:
                    continue

            feasible.append(task)
            time_used += task.duration_minutes
            self.task_explanations[task.id] = f"Scheduled (time: {task.duration_minutes}min)"

        return feasible

    def resolve_conflicts(self, tasks: List[CareTask]) -> List[CareTask]:
        """Handle overlapping tasks and resource conflicts."""
        # Simple conflict resolution: ensure no overlapping time windows
        scheduled = []
        used_windows = []

        for task in tasks:
            if not self._has_time_conflict(task.due_window, used_windows):
                scheduled.append(task)
                used_windows.append(task.due_window)
            else:
                self.task_explanations[task.id] = "Skipped due to time conflict"

        return scheduled

    def explain_selection(self, task: CareTask) -> str:
        """Provide reasoning for scheduling decision."""
        return self.task_explanations.get(
            task.id,
            f"Task '{task.title}' - Priority: {task.priority}, Required: {task.is_required}"
        )

    def detect_time_conflicts(self, tasks: List[CareTask]) -> List[str]:
        """Detect overlapping due windows and return lightweight warning strings."""
        warnings: List[str] = []
        for i, first_task in enumerate(tasks):
            for second_task in tasks[i + 1:]:
                if not self._windows_overlap(first_task.due_window, second_task.due_window):
                    continue

                first_pet = self._find_pet_for_task(first_task)
                second_pet = self._find_pet_for_task(second_task)
                first_pet_name = first_pet.name if first_pet else "Unknown pet"
                second_pet_name = second_pet.name if second_pet else "Unknown pet"

                warnings.append(
                    f"Time conflict: '{first_task.title}' ({first_pet_name}, {first_task.due_window}) "
                    f"overlaps with '{second_task.title}' ({second_pet_name}, {second_task.due_window})."
                )
        return warnings

    def complete_task(self, task_id: str) -> Optional[CareTask]:
        """Complete a task by id and append the next recurring instance to the same pet."""
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.id == task_id:
                    next_task = task.mark_done()
                    if next_task is not None:
                        pet.add_task(next_task)
                    return next_task
        return None

    def _find_pet_for_task(self, task: CareTask) -> Optional[Pet]:
        """Find which pet a task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet
        return None

    def _has_time_conflict(self, due_window: str, used_windows: List[str]) -> bool:
        """Check if due window conflicts with already scheduled windows."""
        for window in used_windows:
            if self._windows_overlap(due_window, window):
                return True
        return False

    def _windows_overlap(self, window1: str, window2: str) -> bool:
        """Check if two time windows overlap."""
        try:
            start1, end1 = window1.split("-")
            start2, end2 = window2.split("-")
            
            start1_time = datetime.strptime(start1, "%H:%M").time()
            end1_time = datetime.strptime(end1, "%H:%M").time()
            start2_time = datetime.strptime(start2, "%H:%M").time()
            end2_time = datetime.strptime(end2, "%H:%M").time()
            
            return not (end1_time <= start2_time or end2_time <= start1_time)
        except ValueError:
            return False

    def _generate_summary(self, scheduled: List[CareTask], unscheduled: List[CareTask]) -> str:
        """Generate a summary of the scheduling decisions."""
        total_minutes = sum(t.duration_minutes for t in scheduled)
        return (
            f"Scheduled {len(scheduled)} tasks ({total_minutes} minutes). "
            f"Could not fit {len(unscheduled)} tasks. "
            f"Available time: {self.available_time} minutes."
        )




class DailyPlan:
    """Represents a scheduled daily plan for pet care."""

    def __init__(self, date: str):
        """Initialize an empty daily plan for the given date."""
        self.date: str = date
        self.scheduled_items: List[CareTask] = []
        self.unscheduled_items: List[CareTask] = []
        self.total_minutes: int = 0
        self.reasoning_summary: str = ""
        self.conflict_warnings: List[str] = []

    def add_scheduled_item(self, task: CareTask, time: str):
        """Add a task to the schedule."""
        self.scheduled_items.append(task)
        self.recalculate_totals()

    def remove_item(self, task_id: str):
        """Remove a task from the schedule."""
        self.scheduled_items = [t for t in self.scheduled_items if t.id != task_id]
        self.recalculate_totals()

    def recalculate_totals(self):
        """Recalculate total scheduled time."""
        self.total_minutes = sum(t.duration_minutes for t in self.scheduled_items)

    def to_display_format(self) -> str:
        """Format plan as a readable string."""
        lines = [f"\n📅 Daily Plan for {self.date}", "=" * 50]
        
        if self.scheduled_items:
            lines.append("\n✅ SCHEDULED TASKS:")
            for i, task in enumerate(self.scheduled_items, 1):
                lines.append(
                    f"  {i}. [{task.due_window}] {task.title} "
                    f"({task.duration_minutes}min) [Priority: {task.priority}]"
                )
        else:
            lines.append("\n✅ SCHEDULED TASKS: None")

        if self.unscheduled_items:
            lines.append("\n❌ UNSCHEDULED TASKS:")
            for i, task in enumerate(self.unscheduled_items, 1):
                lines.append(f"  {i}. {task.title} ({task.duration_minutes}min)")
        
        lines.append(f"\n📊 Total Time: {self.total_minutes} minutes")

        if self.conflict_warnings:
            lines.append("\n⚠️ CONFLICT WARNINGS:")
            for warning in self.conflict_warnings:
                lines.append(f"  - {warning}")

        lines.append(f"\n💭 Summary: {self.reasoning_summary}")
        
        return "\n".join(lines)

    def get_explanations(self) -> Dict[str, str]:
        """Get explanations for scheduling decisions."""
        explanations = {}
        for task in self.scheduled_items:
            explanations[task.id] = f"✓ Scheduled for {task.due_window}"
        for task in self.unscheduled_items:
            explanations[task.id] = "✗ Could not fit in available time"
        return explanations

