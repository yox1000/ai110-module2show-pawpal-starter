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


class TestRecurringTaskCompletion(unittest.TestCase):
    """Test automatic creation of next recurring task instance."""

    def setUp(self):
        """Set up recurring-task test fixtures."""
        self.owner = Owner(name="Alex", available_minutes_per_day=90)
        self.pet = Pet(name="Mochi", species="dog", age=4.0, weight=30.0)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)

    def test_daily_task_completion_creates_next_day_instance(self):
        """Completing a daily task should create a new pending task for tomorrow."""
        today = date.today()
        task = CareTask(
            id="daily_001",
            title="Daily Walk",
            task_type="walk",
            duration_minutes=20,
            priority=9,
            due_window="07:00-08:00",
            recurrence="daily",
            is_required=True,
            due_date=today,
        )
        self.pet.add_task(task)

        next_task = self.scheduler.complete_task("daily_001")

        self.assertIsNotNone(next_task)
        self.assertEqual(task.status, TaskStatus.COMPLETED.value)
        self.assertEqual(next_task.status, TaskStatus.PENDING.value)
        self.assertEqual(next_task.due_date, today + timedelta(days=1))
        self.assertIn(next_task, self.pet.tasks)

    def test_weekly_task_completion_creates_next_week_instance(self):
        """Completing a weekly task should create a new pending task for next week."""
        today = date.today()
        task = CareTask(
            id="weekly_001",
            title="Weekly Grooming",
            task_type="grooming",
            duration_minutes=30,
            priority=6,
            due_window="10:00-11:00",
            recurrence="weekly",
            is_required=False,
            due_date=today,
        )
        self.pet.add_task(task)

        next_task = self.scheduler.complete_task("weekly_001")

        self.assertIsNotNone(next_task)
        self.assertEqual(task.status, TaskStatus.COMPLETED.value)
        self.assertEqual(next_task.due_date, today + timedelta(days=7))
        self.assertIn(next_task, self.pet.tasks)


if __name__ == "__main__":
    unittest.main()
