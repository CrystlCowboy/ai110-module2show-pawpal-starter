from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 10, 19)


def make_owner():
    """An owner with two pets, tasks added out of order."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    mochi.add_task(Task("Evening walk", "18:00", due_date=DAY))
    whiskers.add_task(Task("Breakfast", "07:30", due_date=DAY))
    mochi.add_task(Task("Morning walk", "08:00", due_date=DAY))
    return owner, mochi, whiskers


# --- Task and Pet basics -------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", "07:30"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 2


def test_add_task_records_pet_name():
    pet = Pet("Mochi")
    task = Task("Walk", "08:00")
    pet.add_task(task)
    assert task.pet_name == "Mochi"


def test_invalid_time_is_rejected():
    with pytest.raises(ValueError):
        Task("Walk", "8am")


# --- Owner / Scheduler across multiple pets -------------------------------

def test_owner_get_all_tasks_combines_every_pet():
    owner, _, _ = make_owner()
    assert len(owner.get_all_tasks()) == 3


def test_scheduler_reads_tasks_from_all_pets():
    owner, _, _ = make_owner()
    pets_seen = {t.pet_name for t in Scheduler(owner).get_all_tasks()}
    assert pets_seen == {"Mochi", "Whiskers"}


# --- Sorting -------------------------------------------------------------

def test_sort_by_time_is_chronological_across_pets():
    owner, _, _ = make_owner()
    times = [t.time for t in Scheduler(owner).sort_by_time()]
    assert times == ["07:30", "08:00", "18:00"]


def test_sort_orders_by_date_before_time():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Tomorrow early", "06:00", due_date=DAY + timedelta(days=1)))
    ordered = Scheduler(owner).sort_by_time()
    assert ordered[-1].description == "Tomorrow early"


def test_sort_with_no_tasks_returns_empty_list():
    assert Scheduler(Owner("Empty")).sort_by_time() == []


# --- Filtering -----------------------------------------------------------

def test_filter_by_pet_name():
    owner, _, _ = make_owner()
    result = Scheduler(owner).filter_tasks(pet_name="mochi")
    assert len(result) == 2
    assert all(t.pet_name == "Mochi" for t in result)


def test_filter_by_completion_status():
    owner, mochi, _ = make_owner()
    mochi.tasks[0].mark_complete()
    scheduler = Scheduler(owner)
    assert len(scheduler.filter_tasks(completed=True)) == 1
    assert len(scheduler.filter_tasks(completed=False)) == 2


def test_filter_by_pet_and_status_together():
    owner, mochi, _ = make_owner()
    mochi.tasks[0].mark_complete()
    result = Scheduler(owner).filter_tasks(pet_name="Mochi", completed=False)
    assert [t.description for t in result] == ["Morning walk"]


# --- Recurring tasks -----------------------------------------------------

def test_completing_daily_task_creates_next_day_task():
    owner, mochi, _ = make_owner()
    walk = Task("Daily pill", "09:00", frequency="daily", due_date=DAY)
    mochi.add_task(walk)
    before = len(mochi.tasks)
    follow_up = Scheduler(owner).mark_task_complete(walk)
    assert walk.completed is True
    assert follow_up.due_date == DAY + timedelta(days=1)
    assert follow_up.completed is False
    assert len(mochi.tasks) == before + 1


def test_completing_weekly_task_creates_task_seven_days_later():
    owner, mochi, _ = make_owner()
    task = Task("Bath", "10:00", frequency="weekly", due_date=DAY)
    mochi.add_task(task)
    follow_up = Scheduler(owner).mark_task_complete(task)
    assert follow_up.due_date == DAY + timedelta(days=7)


def test_completing_one_time_task_creates_nothing():
    owner, mochi, _ = make_owner()
    before = len(mochi.tasks)
    assert Scheduler(owner).mark_task_complete(mochi.tasks[0]) is None
    assert len(mochi.tasks) == before


# --- Conflict detection --------------------------------------------------

def test_conflict_detected_for_same_time_across_pets():
    owner, mochi, whiskers = make_owner()
    whiskers.add_task(Task("Meds", "08:00", due_date=DAY))  # same slot as Mochi's walk
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0] and "Morning walk" in warnings[0] and "Meds" in warnings[0]


def test_conflict_detected_for_same_pet():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Brushing", "08:00", due_date=DAY))
    assert len(Scheduler(owner).detect_conflicts()) == 1


def test_no_conflict_when_times_differ():
    owner, _, _ = make_owner()
    assert Scheduler(owner).detect_conflicts() == []


def test_same_time_on_different_days_is_not_a_conflict():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Next day walk", "08:00", due_date=DAY + timedelta(days=1)))
    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_do_not_conflict():
    owner, mochi, whiskers = make_owner()
    other = Task("Meds", "08:00", due_date=DAY)
    whiskers.add_task(other)
    other.mark_complete()
    assert Scheduler(owner).detect_conflicts() == []


# --- Edge cases ----------------------------------------------------------

def test_pet_with_no_tasks_is_handled():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Lonely"))
    scheduler = Scheduler(owner)
    assert scheduler.get_all_tasks() == []
    assert scheduler.todays_schedule() == []
    assert scheduler.detect_conflicts() == []


def test_todays_schedule_excludes_completed_and_other_days():
    owner, mochi, _ = make_owner()
    mochi.tasks[0].mark_complete()
    mochi.add_task(Task("Future", "07:00", due_date=DAY + timedelta(days=3)))
    schedule = Scheduler(owner).todays_schedule(on=DAY)
    assert [t.description for t in schedule] == ["Breakfast", "Morning walk"]
