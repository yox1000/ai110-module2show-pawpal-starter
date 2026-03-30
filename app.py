import streamlit as st
from pawpal_system import Owner, Pet, CareTask as Task, Scheduler


def find_pet_name(owner: Owner, task: Task) -> str:
    """Return the pet name that owns a given task."""
    for pet in owner.pets:
        if task in pet.tasks:
            return pet.name
    return "Unknown"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=120)
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None
if "plan_explanations" not in st.session_state:
    st.session_state.plan_explanations = {}

owner: Owner = st.session_state.owner

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pet Setup")
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available minutes per day",
    min_value=15,
    max_value=1440,
    value=owner.available_minutes_per_day,
    step=15,
)

owner.update_profile(name=owner_name.strip() or owner.name)
owner.set_availability(int(available_minutes))

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Pet age (years)", min_value=0.0, max_value=40.0, value=3.0, step=0.5)
    pet_weight = st.number_input(
        "Pet weight (lbs)", min_value=0.1, max_value=300.0, value=25.0, step=0.5
    )
    add_pet_clicked = st.form_submit_button("Add / Update Pet")

if add_pet_clicked:
    clean_name = pet_name.strip()
    if not clean_name:
        st.error("Pet name is required.")
    else:
        existing_pet = next((p for p in owner.pets if p.name.lower() == clean_name.lower()), None)
        if existing_pet:
            existing_pet.update_pet_info(species=species, age=float(pet_age), weight=float(pet_weight))
            st.success(f"Updated pet '{existing_pet.name}'.")
        else:
            owner.add_pet(
                Pet(
                    name=clean_name,
                    species=species,
                    age=float(pet_age),
                    weight=float(pet_weight),
                )
            )
            st.success(f"Added pet '{clean_name}'.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "weight": pet.weight,
                "pending_tasks": len(pet.get_pending_tasks()),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are now stored as real CareTask objects on each Pet.")

if owner.pets:
    with st.form("task_form"):
        pet_choice = st.selectbox("Select pet", [pet.name for pet in owner.pets])

        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        col4, col5, col6 = st.columns(3)
        with col4:
            task_type = st.selectbox(
                "Task type",
                ["walk", "feed", "medication", "play", "grooming", "training", "veterinary", "other"],
            )
        with col5:
            due_window = st.text_input("Due window", value="08:00-12:00")
        with col6:
            recurrence = st.selectbox("Recurrence", ["daily", "weekly", "once"], index=0)

        is_required = st.checkbox("Required task", value=True)
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        clean_title = task_title.strip()
        if not clean_title:
            st.error("Task title is required.")
        else:
            priority_map = {"low": 1, "medium": 2, "high": 3}
            selected_pet = next((pet for pet in owner.pets if pet.name == pet_choice), None)
            if selected_pet is None:
                st.error("Could not find the selected pet.")
            else:
                task = Task(
                    id=f"task-{st.session_state.task_counter}",
                    title=clean_title,
                    task_type=task_type,
                    duration_minutes=int(duration),
                    priority=priority_map[priority],
                    due_window=due_window,
                    recurrence=recurrence,
                    is_required=is_required,
                )
                selected_pet.add_task(task)
                st.session_state.task_counter += 1
                st.success(f"Added task '{clean_title}' for {selected_pet.name}.")

all_tasks = []
for pet in owner.pets:
    for task in pet.tasks:
        all_tasks.append(
            {
                "pet": pet.name,
                "title": task.title,
                "type": task.task_type,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "due_window": task.due_window,
                "status": task.status,
            }
        )

if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a plan from your Owner -> Pet -> CareTask objects.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()
    st.session_state.last_plan = plan
    st.session_state.plan_explanations = {
        task.id: scheduler.explain_selection(task)
        for task in (plan.scheduled_items + plan.unscheduled_items)
    }

if st.session_state.last_plan is not None:
    plan = st.session_state.last_plan
    st.success("Schedule generated.")

    if plan.scheduled_items:
        st.write("Scheduled tasks:")
        st.table(
            [
                {
                    "pet": find_pet_name(owner, task),
                    "title": task.title,
                    "window": task.due_window,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "reason": st.session_state.plan_explanations.get(task.id, ""),
                }
                for task in plan.scheduled_items
            ]
        )
    else:
        st.info("No tasks were scheduled.")

    if plan.unscheduled_items:
        st.write("Unscheduled tasks:")
        st.table(
            [
                {
                    "pet": find_pet_name(owner, task),
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "reason": st.session_state.plan_explanations.get(task.id, ""),
                }
                for task in plan.unscheduled_items
            ]
        )

    st.caption(plan.reasoning_summary)
