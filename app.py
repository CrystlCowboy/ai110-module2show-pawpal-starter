from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planner: add pets, schedule tasks, and let the Scheduler keep things organized.")

# Streamlit reruns this script on every click, so the Owner must live in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ---------------------------------------------------------------- Owner & pets
st.subheader("Owner and pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not new_pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(new_pet_name.strip()):
            st.error(f"You already have a pet named {new_pet_name.strip()}.")
        else:
            owner.add_pet(Pet(new_pet_name.strip(), new_pet_species))
            st.success(f"Added {new_pet_name.strip()} the {new_pet_species}.")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# ----------------------------------------------------------------------- Tasks
st.divider()
st.subheader("Add a task")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=False):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        due = st.date_input("Date")
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Please describe the task.")
            else:
                owner.get_pet(pet_choice).add_task(
                    Task(
                        description.strip(),
                        task_time.strftime("%H:%M"),
                        int(duration),
                        priority,
                        frequency,
                        due,
                    )
                )
                st.success(f"Added '{description.strip()}' for {pet_choice}.")
else:
    st.info("Add a pet first, then you can schedule tasks.")

# -------------------------------------------------------------------- Schedule
st.divider()
st.subheader("Schedule")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

conflicts = scheduler.detect_conflicts()
if conflicts:
    for message in conflicts:
        st.warning(message + ". Consider moving one of these tasks.")
elif scheduler.get_all_tasks():
    st.success("No scheduling conflicts.")

col1, col2 = st.columns(2)
with col1:
    pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
with col2:
    status_filter = st.selectbox("Show status", ["All", "To do", "Completed"])

shown = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed={"All": None, "To do": False, "Completed": True}[status_filter],
)
shown = scheduler.sort_by_time(shown)

if shown:
    st.table(
        [
            {
                "Date": t.due_date.isoformat(),
                "Time": t.time,
                "Pet": t.pet_name,
                "Task": t.description,
                "Min": t.duration_minutes,
                "Priority": t.priority,
                "Repeats": t.frequency,
                "Status": "done" if t.completed else "to do",
            }
            for t in shown
        ]
    )
else:
    st.info("No tasks to show yet.")

pending = [t for t in shown if not t.completed]
if pending:
    st.markdown("**Mark a task complete**")
    labels = {f"{t.due_date.isoformat()} {t.time} - {t.description} ({t.pet_name})": t for t in pending}
    choice = st.selectbox("Task", list(labels))
    if st.button("Mark complete"):
        follow_up = scheduler.mark_task_complete(labels[choice])
        if follow_up:
            st.session_state.flash = (
                f"Done! Next {follow_up.frequency} occurrence scheduled for {follow_up.due_date.isoformat()}."
            )
        else:
            st.session_state.flash = "Done!"
        st.rerun()
