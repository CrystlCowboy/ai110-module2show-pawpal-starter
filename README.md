# PawPal+ (Module 2 Project)

PawPal+ is a pet care planner for busy owners. It tracks care tasks (walks, feeding, meds, vet visits) across **multiple pets**, then uses a `Scheduler` to sort them by time, filter them, warn about conflicts, and automatically repeat daily/weekly tasks. The logic lives in `pawpal_system.py`, is demonstrated from the terminal in `main.py`, verified with pytest, and shown in a Streamlit UI (`app.py`).

## System overview

| Class | Responsibility |
|-------|----------------|
| `Task` | One activity: `description`, `time` ("HH:MM"), `duration_minutes`, `priority`, `frequency` (once/daily/weekly), `due_date`, `completed`. `mark_complete()` marks it done; `next_occurrence()` builds the next repeat. |
| `Pet` | Name, species and a list of `Task`s. `add_task()`, `remove_task()` and `list_tasks()` manage them; adding a task stamps it with the pet's name. |
| `Owner` | Name and a list of `Pet`s. `add_pet()`, `get_pet()`, and `get_all_tasks()`, which returns every pet's tasks together. |
| `Scheduler` | The "brain". Reads all tasks through `Owner.get_all_tasks()` (so it always works across multiple pets) and provides sorting, filtering, conflict detection, recurrence and a daily schedule. |

The UML is in `diagrams/uml_final.mmd` (Mermaid source; `diagrams/uml_draft.mmd` is the original draft and `diagrams/uml.mmd` mirrors the final version).

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python main.py
```

Run the Streamlit app:

```bash
streamlit run app.py
```

Run the tests:

```bash
python -m pytest
```

## Features

- **Multi-pet scheduling:** one owner, many pets; the Scheduler works across all of them.
- **Sorting by time:** chronological order by date, then "HH:MM", then priority.
- **Filtering:** by pet name and/or completion status.
- **Conflict warnings:** flags two pending tasks at the same date and time, for the same pet or different pets, and returns warning text instead of crashing.
- **Recurring tasks:** completing a daily or weekly task automatically creates the next occurrence.
- **Input validation:** bad times, priorities or frequencies raise a clear `ValueError`.

## 🖥️ Sample Output

Output of `python main.py` (tasks are added out of order on purpose, and two tasks share 08:00 to trigger a conflict):

```
PawPal+ for Jordan: 2 pets, 5 tasks

=== As added (unsorted) ===
  Date       Time   Pet       Task                  Min  Priority Repeats Status
  ------------------------------------------------------------------------------
  2026-10-19 18:00  Mochi     Evening walk           30  medium   daily   todo
  2026-10-19 08:00  Mochi     Morning walk           30  high     daily   todo
  2026-10-19 13:30  Mochi     Vet checkup            60  medium   once    todo
  2026-10-19 07:30  Whiskers  Breakfast feeding      10  high     daily   todo
  2026-10-19 08:00  Whiskers  Flea medication         5  high     weekly  todo

=== Sorted by time ===
  Date       Time   Pet       Task                  Min  Priority Repeats Status
  ------------------------------------------------------------------------------
  2026-10-19 07:30  Whiskers  Breakfast feeding      10  high     daily   todo
  2026-10-19 08:00  Mochi     Morning walk           30  high     daily   todo
  2026-10-19 08:00  Whiskers  Flea medication         5  high     weekly  todo
  2026-10-19 13:30  Mochi     Vet checkup            60  medium   once    todo
  2026-10-19 18:00  Mochi     Evening walk           30  medium   daily   todo

=== Filter: Mochi's tasks only ===
  Date       Time   Pet       Task                  Min  Priority Repeats Status
  ------------------------------------------------------------------------------
  2026-10-19 18:00  Mochi     Evening walk           30  medium   daily   todo
  2026-10-19 08:00  Mochi     Morning walk           30  high     daily   todo
  2026-10-19 13:30  Mochi     Vet checkup            60  medium   once    todo

=== Conflict check ===
  WARNING: Conflict on 2026-10-19 at 08:00: Morning walk (Mochi), Flea medication (Whiskers)

=== Completing 'Morning walk' (daily) ===
  Marked done: Morning walk on 2026-10-19
  Next occurrence created for: 2026-10-20 at 08:00

=== Filter: completed tasks ===
  Date       Time   Pet       Task                  Min  Priority Repeats Status
  ------------------------------------------------------------------------------
  2026-10-19 08:00  Mochi     Morning walk           30  high     daily   done

=== Today's Schedule (pending) ===
  Date       Time   Pet       Task                  Min  Priority Repeats Status
  ------------------------------------------------------------------------------
  2026-10-19 07:30  Whiskers  Breakfast feeding      10  high     daily   todo
  2026-10-19 08:00  Whiskers  Flea medication         5  high     weekly  todo
  2026-10-19 13:30  Mochi     Vet checkup            60  medium   once    todo
  2026-10-19 18:00  Mochi     Evening walk           30  medium   daily   todo
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

**What the 22 tests cover:** task completion; adding tasks to a pet; time validation; the Owner collecting tasks from every pet; sorting (chronological across pets, date before time, empty list); filtering (by pet, by status, both together); recurrence (daily +1 day, weekly +7 days, one-time tasks create nothing); conflict detection (same time across pets, same pet, no false positive for different times or different days, completed tasks ignored); and edge cases such as a pet with no tasks.

Sample passing output:

```
============================= test session starts ==============================
collected 22 items

tests/test_pawpal.py ......................                              [100%]

============================== 22 passed in 0.03s ==============================
```

**Confidence level: ★★★★☆ (4/5).** The core behaviors and the main edge cases pass, and I checked the tests can fail by deliberately breaking the sort, recurrence and conflict logic. Not yet tested: overlapping durations, month/year rollover on recurrence, and Streamlit UI behavior beyond a manual walkthrough.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts by `(due_date, "HH:MM", priority)`. Zero-padded 24-hour strings sort correctly as text. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter, both, or neither; pet name is case-insensitive. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by exact date and time; returns warning strings for any slot with 2+ tasks. Exact-match only; it does not look at overlapping durations. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Daily adds 1 day, weekly adds 7 days (using `timedelta`); the new task goes to the same pet. |
| Daily view | `Scheduler.todays_schedule()` | Pending tasks for one day, in time order. |

## 📸 Demo Walkthrough

1. Run `streamlit run app.py`. The app creates one `Owner` and keeps it in `st.session_state`, so your data survives button clicks.
2. In **Owner and pets**, type a pet name, pick a species and click **Add pet**. Add at least two pets.
3. In **Add a task**, choose a pet, describe the task, set a time, duration, priority, repeat frequency and date, then click **Add task**. Add a few tasks in any order.
4. In **Schedule**, tasks appear sorted by time across all pets. Use the pet and status dropdowns to filter the table.
5. Add two tasks at the same time. A yellow warning names the conflicting tasks and pets; with no clashes you see a green "No scheduling conflicts" message.
6. Pick a daily or weekly task under **Mark a task complete** and click the button. It moves to "done" and the next occurrence appears automatically.

The same behaviors can be seen without the UI by running `python main.py` (output shown above).
