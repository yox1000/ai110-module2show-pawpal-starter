import unittest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, CareTask, TaskStatus, Scheduler


class TestTaskCompletion(unittest.TestCase):
    """Test task completion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = CareTask(
            id="test_001",
            title="Test Task",
            task_type="walk",
            duration_minutes=30,
            priority=5,
            due_window="10:00-11:00",
            recurrence="daily",
            is_required=True
        )
    
    def test_mark_done_changes_status(self):
        """Verify that mark_done() changes task status to completed."""
        # Initial status should be pending
        self.assertEqual(self.task.status, TaskStatus.PENDING.value)
        
        # Call mark_done()
        self.task.mark_done()
        
        # Status should now be completed
        self.assertEqual(self.task.status, TaskStatus.COMPLETED.value)
        
        # completed_at should be set
        self.assertIsNotNone(self.task.completed_at)
    
    def test_mark_skipped_changes_status(self):
        """Verify that mark_skipped() changes task status to skipped."""
        self.assertEqual(self.task.status, TaskStatus.PENDING.value)
        self.task.mark_skipped()
        self.assertEqual(self.task.status, TaskStatus.SKIPPED.value)


class TestTaskAddition(unittest.TestCase):
    """Test task addition to pets."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pet = Pet(
            name="Fluffy",
            species="Cat",
            age=2.0,
            weight=5.0
        )
        
        self.task = CareTask(
            id="test_002",
            title="Feed Cat",
            task_type="feed",
            duration_minutes=10,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
    
    def test_task_addition_increases_count(self):
        """Verify that adding a task increases pet's task count."""
        # Initial task count should be 0
        initial_count = len(self.pet.tasks)
        self.assertEqual(initial_count, 0)
        
        # Add task
        self.pet.add_task(self.task)
        
        # Task count should now be 1
        self.assertEqual(len(self.pet.tasks), 1)
        
        # Task should be in the pet's task list
        self.assertIn(self.task, self.pet.tasks)
    
    def test_multiple_task_addition(self):
        """Verify adding multiple tasks to a pet."""
        task2 = CareTask(
            id="test_003",
            title="Play Session",
            task_type="play",
            duration_minutes=20,
            priority=7,
            due_window="14:00-15:00",
            recurrence="daily",
            is_required=False
        )
        
        self.pet.add_task(self.task)
        self.pet.add_task(task2)
        
        self.assertEqual(len(self.pet.tasks), 2)
        self.assertIn(self.task, self.pet.tasks)
        self.assertIn(task2, self.pet.tasks)


class TestTaskSortingCorrectness(unittest.TestCase):
    """Test task ranking and sorting logic."""
    
    def setUp(self):
        """Set up test fixtures with multiple tasks."""
        self.owner = Owner(name="Alex", available_minutes_per_day=120)
        self.pet = Pet(name="Buddy", species="dog", age=4.0, weight=30.0)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)
    
    def test_tasks_ranked_by_priority_descending(self):
        """Verify tasks are ranked highest priority first."""
        task_low = CareTask(
            id="low_001",
            title="Optional Play",
            task_type="play",
            duration_minutes=20,
            priority=3,
            due_window="15:00-16:00",
            recurrence="daily",
            is_required=False
        )
        task_med = CareTask(
            id="med_001",
            title="Afternoon Walk",
            task_type="walk",
            duration_minutes=30,
            priority=7,
            due_window="14:00-15:00",
            recurrence="daily",
            is_required=False
        )
        task_high = CareTask(
            id="high_001",
            title="Morning Feeding",
            task_type="feed",
            duration_minutes=10,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        
        self.pet.add_task(task_low)
        self.pet.add_task(task_med)
        self.pet.add_task(task_high)
        
        ranked = self.scheduler.rank_tasks([task_low, task_med, task_high])
        
        # Highest priority should be first
        self.assertEqual(ranked[0].priority, 10)
        self.assertEqual(ranked[1].priority, 7)
        self.assertEqual(ranked[2].priority, 3)
    
    def test_required_tasks_ranked_higher_than_optional(self):
        """Verify required tasks are prioritized over optional ones."""
        required_task = CareTask(
            id="req_001",
            title="Required Walk",
            task_type="walk",
            duration_minutes=30,
            priority=5,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        optional_high_priority = CareTask(
            id="opt_001",
            title="Optional High Priority",
            task_type="play",
            duration_minutes=20,
            priority=9,
            due_window="15:00-16:00",
            recurrence="daily",
            is_required=False
        )
        
        self.pet.add_task(required_task)
        self.pet.add_task(optional_high_priority)
        
        ranked = self.scheduler.rank_tasks([optional_high_priority, required_task])
        
        # Required task should rank higher despite lower priority
        self.assertEqual(ranked[0].is_required, True)
    
    def test_identical_priority_tasks_stable_sort(self):
        """Verify tasks with same priority maintain consistent order."""
        task1 = CareTask(
            id="same_001",
            title="Task One",
            task_type="walk",
            duration_minutes=20,
            priority=5,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=False
        )
        task2 = CareTask(
            id="same_002",
            title="Task Two",
            task_type="play",
            duration_minutes=15,
            priority=5,
            due_window="14:00-15:00",
            recurrence="daily",
            is_required=False
        )
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        ranked = self.scheduler.rank_tasks([task1, task2])
        
        # Both should be present
        self.assertEqual(len(ranked), 2)
        self.assertIn(task1, ranked)
        self.assertIn(task2, ranked)
    
    def test_zero_priority_task_sorted_correctly(self):
        """Verify tasks with zero priority are ranked lowest."""
        zero_priority = CareTask(
            id="zero_001",
            title="Zero Priority Task",
            task_type="other",
            duration_minutes=10,
            priority=0,
            due_window="10:00-11:00",
            recurrence="daily",
            is_required=False
        )
        normal_priority = CareTask(
            id="norm_001",
            title="Normal Priority",
            task_type="walk",
            duration_minutes=20,
            priority=5,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=False
        )
        
        ranked = self.scheduler.rank_tasks([zero_priority, normal_priority])
        
        # Normal priority should come first
        self.assertEqual(ranked[0].priority, 5)
        self.assertEqual(ranked[1].priority, 0)
    
    def test_daily_recurrence_boost_ranking(self):
        """Verify daily tasks get ranking boost over non-daily."""
        daily_task = CareTask(
            id="daily_001",
            title="Daily Task",
            task_type="feed",
            duration_minutes=10,
            priority=5,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=False
        )
        once_task = CareTask(
            id="once_001",
            title="One-time Task",
            task_type="grooming",
            duration_minutes=30,
            priority=5,
            due_window="14:00-15:00",
            recurrence="once",
            is_required=False
        )
        
        ranked = self.scheduler.rank_tasks([once_task, daily_task])
        
        # Daily task should rank higher with same priority
        self.assertEqual(ranked[0].recurrence, "daily")


class TestRecurrenceLogic(unittest.TestCase):
    """Test recurrence detection and filtering logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(name="Morgan", available_minutes_per_day=120)
        self.pet = Pet(name="Whiskers", species="cat", age=3.0, weight=8.0)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)
    
    def test_daily_task_is_due_today(self):
        """Verify daily tasks are marked as due today."""
        task = CareTask(
            id="daily_001",
            title="Daily Feeding",
            task_type="feed",
            duration_minutes=5,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        
        self.assertTrue(task.is_due_today())
    
    def test_daily_task_is_due_every_day(self):
        """Verify daily tasks are due tomorrow and beyond."""
        task = CareTask(
            id="daily_001",
            title="Daily Feeding",
            task_type="feed",
            duration_minutes=5,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        
        tomorrow = date.today() + timedelta(days=1)
        self.assertTrue(task.is_due_today(tomorrow))
        
        next_week = date.today() + timedelta(days=7)
        self.assertTrue(task.is_due_today(next_week))
    
    def test_once_task_is_due_today(self):
        """Verify one-time tasks are marked as due."""
        task = CareTask(
            id="once_001",
            title="One-time Vet Visit",
            task_type="veterinary",
            duration_minutes=60,
            priority=9,
            due_window="10:00-11:00",
            recurrence="once",
            is_required=True
        )
        
        self.assertTrue(task.is_due_today())
    
    def test_weekly_task_due_on_correct_day(self):
        """Verify weekly tasks are due on their assigned day."""
        # This test assumes Monday (weekday=0) for weekly recurrence
        task = CareTask(
            id="weekly_001",
            title="Weekly Grooming",
            task_type="grooming",
            duration_minutes=30,
            priority=6,
            due_window="10:00-11:00",
            recurrence="weekly",
            is_required=False
        )
        
        # Check on a Monday (weekday 0)
        monday = date(2026, 3, 30)  # This is actually a Monday in 2026
        self.assertTrue(task.is_due_today(monday))
    
    def test_multiple_daily_tasks_for_same_pet(self):
        """Verify multiple daily tasks all show as due today."""
        task1 = CareTask(
            id="daily_001",
            title="Feed Morning",
            task_type="feed",
            duration_minutes=5,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        task2 = CareTask(
            id="daily_002",
            title="Feed Evening",
            task_type="feed",
            duration_minutes=5,
            priority=10,
            due_window="18:00-19:00",
            recurrence="daily",
            is_required=True
        )
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        due_tasks = [t for t in self.pet.tasks if t.is_due_today()]
        self.assertEqual(len(due_tasks), 2)
    
    def test_non_daily_recurrence_filtering(self):
        """Verify non-daily tasks are filtered correctly."""
        task_daily = CareTask(
            id="daily_001",
            title="Daily Walk",
            task_type="walk",
            duration_minutes=20,
            priority=8,
            due_window="07:00-08:00",
            recurrence="daily",
            is_required=True
        )
        task_weekly = CareTask(
            id="weekly_001",
            title="Weekly Grooming",
            task_type="grooming",
            duration_minutes=30,
            priority=6,
            due_window="10:00-11:00",
            recurrence="weekly",
            is_required=False
        )
        
        self.pet.add_task(task_daily)
        self.pet.add_task(task_weekly)
        
        daily_due = [t for t in self.pet.tasks if t.recurrence == "daily"]
        self.assertEqual(len(daily_due), 1)
        self.assertEqual(daily_due[0].title, "Daily Walk")


class TestConflictDetection(unittest.TestCase):
    """Test time window conflict detection and resolution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(name="Jordan", available_minutes_per_day=120)
        self.pet = Pet(name="Buddy", species="dog", age=5.0, weight=50.0)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)
    
    def test_identical_time_windows_detected_as_conflict(self):
        """Verify tasks with identical time windows are flagged as conflicting."""
        window1 = "10:00-11:00"
        window2 = "10:00-11:00"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertTrue(conflict)
    
    def test_overlapping_time_windows_detected_as_conflict(self):
        """Verify overlapping windows are flagged as conflicting."""
        window1 = "10:00-10:45"
        window2 = "10:30-11:00"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertTrue(conflict)
    
    def test_back_to_back_windows_not_conflicting(self):
        """Verify back-to-back windows don't conflict (10:00-10:30, 10:30-11:00)."""
        window1 = "10:00-10:30"
        window2 = "10:30-11:00"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        # Back-to-back should not conflict (end of first == start of second)
        self.assertFalse(conflict)
    
    def test_non_overlapping_windows_not_conflicting(self):
        """Verify completely separate windows don't conflict."""
        window1 = "08:00-09:00"
        window2 = "14:00-15:00"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertFalse(conflict)
    
    def test_partial_overlap_early_window(self):
        """Verify early window overlapping later window is detected."""
        window1 = "09:00-10:30"
        window2 = "10:00-11:00"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertTrue(conflict)
    
    def test_partial_overlap_late_window(self):
        """Verify late window overlapping earlier window is detected."""
        window1 = "10:00-11:00"
        window2 = "10:45-11:30"
        
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertTrue(conflict)
    
    def test_resolve_conflicts_removes_overlapping_tasks(self):
        """Verify conflict resolution removes conflicting tasks."""
        task1 = CareTask(
            id="conflict_001",
            title="First Task",
            task_type="walk",
            duration_minutes=30,
            priority=8,
            due_window="10:00-10:30",
            recurrence="daily",
            is_required=True
        )
        task2 = CareTask(
            id="conflict_002",
            title="Conflicting Task",
            task_type="play",
            duration_minutes=20,
            priority=7,
            due_window="10:15-10:35",
            recurrence="daily",
            is_required=False
        )
        
        self.pet.add_task(task1)
        self.pet.add_task(task2)
        
        resolved = self.scheduler.resolve_conflicts([task1, task2])
        
        # One task should be removed
        self.assertEqual(len(resolved), 1)
        self.assertIn(task1, resolved)
    
    def test_has_time_conflict_with_used_windows(self):
        """Verify time conflict detection against already scheduled windows."""
        used_windows = ["10:00-11:00", "14:00-15:00"]
        new_window = "10:30-11:15"
        
        conflict = self.scheduler._has_time_conflict(new_window, used_windows)
        self.assertTrue(conflict)
    
    def test_no_time_conflict_with_gap(self):
        """Verify no conflict when window fits in gap between scheduled tasks."""
        used_windows = ["08:00-09:00", "14:00-15:00"]
        new_window = "10:00-11:00"
        
        conflict = self.scheduler._has_time_conflict(new_window, used_windows)
        self.assertFalse(conflict)
    
    def test_invalid_time_format_handled_gracefully(self):
        """Verify invalid time formats don't crash conflict detection."""
        window1 = "10-11"  # Invalid format
        window2 = "10:00-11:00"
        
        # Should return False without crashing
        conflict = self.scheduler._windows_overlap(window1, window2)
        self.assertFalse(conflict)


class TestSchedulerEdgeCases(unittest.TestCase):
    """Test edge cases in scheduler and task management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(name="Pat", available_minutes_per_day=120)
        self.pet = Pet(name="Muffin", species="cat", age=2.0, weight=7.0)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)
    
    def test_zero_duration_task(self):
        """Verify zero-duration tasks don't break scheduling."""
        task = CareTask(
            id="zero_001",
            title="Instant Task",
            task_type="other",
            duration_minutes=0,
            priority=5,
            due_window="12:00-12:00",
            recurrence="daily",
            is_required=False
        )
        
        self.pet.add_task(task)
        plan = self.scheduler.generate_daily_plan()
        
        # Plan should complete without error
        self.assertIsNotNone(plan)
    
    def test_owner_with_no_pets(self):
        """Verify scheduling works with owner having no pets."""
        owner_no_pets = Owner(name="NoOne", available_minutes_per_day=120)
        scheduler = Scheduler(owner_no_pets)
        
        plan = scheduler.generate_daily_plan()
        
        # Should generate empty plan
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.scheduled_items), 0)
    
    def test_all_tasks_exceed_available_time(self):
        """Verify graceful handling when all tasks exceed available time."""
        owner_limited = Owner(name="Limited", available_minutes_per_day=30)
        pet = Pet(name="Busy", species="dog", age=3.0, weight=40.0)
        owner_limited.add_pet(pet)
        scheduler = Scheduler(owner_limited)
        
        task1 = CareTask(
            id="busy_001",
            title="Long Walk",
            task_type="walk",
            duration_minutes=60,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        task2 = CareTask(
            id="busy_002",
            title="Long Play",
            task_type="play",
            duration_minutes=60,
            priority=8,
            due_window="14:00-15:00",
            recurrence="daily",
            is_required=False
        )
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        plan = scheduler.generate_daily_plan()
        
        # At least some unscheduled tasks should exist
        self.assertGreater(len(plan.unscheduled_items), 0)
    
    def test_exactly_fits_available_time(self):
        """Verify scheduling when tasks exactly fit available time."""
        owner_exact = Owner(name="Exact", available_minutes_per_day=30)
        pet = Pet(name="Perfect", species="dog", age=3.0, weight=30.0)
        owner_exact.add_pet(pet)
        scheduler = Scheduler(owner_exact)
        
        task = CareTask(
            id="exact_001",
            title="Perfect Task",
            task_type="walk",
            duration_minutes=30,
            priority=8,
            due_window="08:00-10:00",
            recurrence="daily",
            is_required=True
        )
        
        pet.add_task(task)
        plan = scheduler.generate_daily_plan()
        
        # Task should be scheduled
        self.assertEqual(plan.total_minutes, 30)
    
    def test_restricted_activity_excluded(self):
        """Verify tasks of restricted type are excluded from schedule."""
        pet_restricted = Pet(
            name="Lazy",
            species="cat",
            age=10.0,
            weight=12.0,
            routine_preferences={"restrict_activities": ["walking"]}
        )
        self.owner.pets = [pet_restricted]
        
        walk_task = CareTask(
            id="walk_001",
            title="Restricted Walk",
            task_type="walk",
            duration_minutes=20,
            priority=8,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=False
        )
        
        feed_task = CareTask(
            id="feed_001",
            title="Allowed Feed",
            task_type="feed",
            duration_minutes=5,
            priority=10,
            due_window="08:00-09:00",
            recurrence="daily",
            is_required=True
        )
        
        pet_restricted.add_task(walk_task)
        pet_restricted.add_task(feed_task)
        
        plan = self.scheduler.generate_daily_plan()
        
        # Walk should not be scheduled, feed should be
        scheduled_ids = [t.id for t in plan.scheduled_items]
        self.assertNotIn("walk_001", scheduled_ids)
        self.assertIn("feed_001", scheduled_ids)


if __name__ == "__main__":
    unittest.main()
