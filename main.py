from pawpal_system import Owner, Pet, CareTask, Scheduler


def main():
    """Demonstrate the PawPal pet care system."""
    
    # Create an Owner
    owner = Owner(
        name="Sarah",
        available_minutes_per_day=120
    )
    owner.set_preferences({
        "morning_person": True,
        "prefers_grouped_tasks": True
    })
    print(f"👤 Owner: {owner.name}")
    print(f"⏰ Available daily: {owner.available_minutes_per_day} minutes\n")
    
    # Create Pets
    dog = Pet(
        name="Buddy",
        species="Golden Retriever",
        age=3.5,
        weight=65.0,
        health_notes="Healthy, loves outdoor activities",
        routine_preferences={"preferred_walk_time": "morning", "max_play_session": 30}
    )
    
    cat = Pet(
        name="Whiskers",
        species="Tabby Cat",
        age=2.0,
        weight=8.5,
        health_notes="Sensitive stomach - special diet",
        routine_preferences={"feeding_times": ["08:00", "18:00"], "restrict_activities": ["walking"]}
    )
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    print(f"🐾 Pets: {', '.join([p.name for p in owner.pets])}\n")
    
    # Create Tasks for Buddy (Dog)
    task1 = CareTask(
        id="task_001",
        title="Morning Walk",
        task_type="walk",
        duration_minutes=30,
        priority=9,
        due_window="07:00-08:00",
        recurrence="daily",
        is_required=True
    )
    
    task2 = CareTask(
        id="task_002",
        title="Feed Buddy",
        task_type="feed",
        duration_minutes=10,
        priority=10,
        due_window="08:00-09:00",
        recurrence="daily",
        is_required=True
    )
    
    task3 = CareTask(
        id="task_003",
        title="Afternoon Play Session",
        task_type="play",
        duration_minutes=20,
        priority=7,
        due_window="14:00-15:00",
        recurrence="daily",
        is_required=False
    )
    
    # Intentionally add tasks out of chronological order.
    dog.add_task(task3)
    dog.add_task(task1)
    dog.add_task(task2)
    
    # Create Tasks for Whiskers (Cat)
    task4 = CareTask(
        id="task_004",
        title="Feed Whiskers",
        task_type="feed",
        duration_minutes=5,
        priority=10,
        due_window="08:30-09:00",
        recurrence="daily",
        is_required=True
    )
    
    task5 = CareTask(
        id="task_005",
        title="Clean Litter Box",
        task_type="other",
        duration_minutes=10,
        priority=8,
        due_window="09:00-10:00",
        recurrence="daily",
        is_required=True
    )
    
    task6 = CareTask(
        id="task_006",
        title="evening Feed Whiskers",
        task_type="feed",
        duration_minutes=5,
        priority=10,
        due_window="18:00-18:30",
        recurrence="daily",
        is_required=True
    )

    # Intentional same-time conflict with Buddy's "Morning Walk" (07:00-08:00).
    task7 = CareTask(
        id="task_007",
        title="Give Whiskers Medication",
        task_type="medication",
        duration_minutes=5,
        priority=9,
        due_window="07:00-08:00",
        recurrence="daily",
        is_required=True
    )
    
    # Intentionally add tasks out of chronological order.
    cat.add_task(task6)
    cat.add_task(task7)
    cat.add_task(task4)
    cat.add_task(task5)

    # Update a couple task statuses to test filtering behavior.
    task3.mark_done()
    task6.mark_skipped()
    
    print("📋 Tasks Created:")
    for pet in owner.pets:
        print(f"\n  {pet.name}:")
        for task in pet.tasks:
            priority_emoji = "🔴" if task.priority >= 9 else "🟡" if task.priority >= 7 else "🟢"
            print(f"    {priority_emoji} {task.title} - {task.duration_minutes}min [{task.due_window}]")
    
    # Display total time needed
    total_time_needed = owner.get_total_task_time_needed()
    can_fit = owner.can_fit_all_tasks()
    print(f"\n⏱️  Total time needed: {total_time_needed} minutes")
    print(f"{'✅ All tasks fit!' if can_fit else '❌ Not enough time for all tasks!'}\n")

    # Demonstrate sorting and filtering helpers in terminal output.
    print("=" * 60)
    print("🧪 SORTING + FILTERING CHECKS")

    all_tasks_out_of_order = [
        task6,  # 18:00
        task2,  # 08:00
        task5,  # 09:00
        task1,  # 07:00
        task7,  # 07:00 (intentional conflict)
        task3,  # 14:00
        task4,  # 08:30
    ]

    print("\nTasks in original (out-of-order) list:")
    for task in all_tasks_out_of_order:
        print(f"  - {task.due_window} | {task.title} ({task.status})")

    scheduler = Scheduler(owner)
    sorted_by_time = scheduler.sort_by_time(all_tasks_out_of_order)
    print("\nTasks sorted by due-window start time:")
    for task in sorted_by_time:
        print(f"  - {task.due_window} | {task.title} ({task.status})")

    print("\nFiltered tasks (status='pending'):")
    for task in owner.filter_tasks(status="pending"):
        print(f"  - {task.title} [{task.status}]")

    print("\nFiltered tasks (status='completed'):")
    for task in owner.filter_tasks(status="completed"):
        print(f"  - {task.title} [{task.status}]")

    print("\nFiltered tasks (pet_name='Buddy'):")
    for task in owner.filter_tasks(pet_name="Buddy"):
        print(f"  - {task.title} [{task.status}]")

    print("\nFiltered tasks (status='pending', pet_name='Whiskers'):")
    for task in owner.filter_tasks(status="pending", pet_name="Whiskers"):
        print(f"  - {task.title} [{task.status}]")

    # Generate Daily Schedule using Scheduler
    print("=" * 60)
    daily_plan = scheduler.generate_daily_plan()
    
    # Display the plan
    print(daily_plan.to_display_format())

    if daily_plan.conflict_warnings:
        print("\n⚠️ DETECTED CONFLICTS:")
        for warning in daily_plan.conflict_warnings:
            print(f"  - {warning}")
    else:
        print("\n✅ No time conflicts detected.")
    
    # Show explanations for each task
    print("\n💡 SCHEDULING EXPLANATIONS:")
    explanations = daily_plan.get_explanations()
    for task_id, explanation in explanations.items():
        task = next((t for p in owner.pets for t in p.tasks if t.id == task_id), None)
        if task:
            print(f"  • {task.title}: {explanation}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
