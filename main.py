"""CLI demo for PawPal+: builds an owner, pets and tasks, then exercises the Scheduler."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title, tasks):
    """Print a list of tasks as a readable table."""
    print(f"\n=== {title} ===")
    if not tasks:
        print("  (nothing to show)")
        return
    print(f"  {'Date':<11}{'Time':<6} {'Pet':<9} {'Task':<20} {'Min':>4}  {'Priority':<8} {'Repeats':<7} Status")
    print("  " + "-" * 78)
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(
            f"  {t.due_date.isoformat():<11}{t.time:<6} {t.pet_name:<9} {t.description:<20} "
            f"{t.duration_minutes:>4}  {t.priority:<8} {t.frequency:<7} {status}"
        )


def main():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # Tasks are deliberately added out of chronological order.
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    whiskers.add_task(Task("Breakfast feeding", "07:30", 10, "high", "daily"))
    mochi.add_task(Task("Morning walk", "08:00", 30, "high", "daily"))
    whiskers.add_task(Task("Flea medication", "08:00", 5, "high", "weekly"))  # same time as Mochi's walk
    mochi.add_task(Task("Vet checkup", "13:30", 60, "medium"))

    scheduler = Scheduler(owner)
    print(f"PawPal+ for {owner.name}: {len(owner.pets)} pets, {len(scheduler.get_all_tasks())} tasks")

    print_tasks("As added (unsorted)", scheduler.get_all_tasks())
    print_tasks("Sorted by time", scheduler.sort_by_time())
    print_tasks("Filter: Mochi's tasks only", scheduler.filter_tasks(pet_name="Mochi"))

    print("\n=== Conflict check ===")
    warnings = scheduler.detect_conflicts()
    for w in warnings:
        print(f"  WARNING: {w}")
    if not warnings:
        print("  No conflicts found.")

    print("\n=== Completing 'Morning walk' (daily) ===")
    walk = next(t for t in mochi.tasks if t.description == "Morning walk")
    follow_up = scheduler.mark_task_complete(walk)
    print(f"  Marked done: {walk.description} on {walk.due_date.isoformat()}")
    print(f"  Next occurrence created for: {follow_up.due_date.isoformat()} at {follow_up.time}")

    print_tasks("Filter: completed tasks", scheduler.filter_tasks(completed=True))
    print_tasks("Today's Schedule (pending)", scheduler.todays_schedule())


if __name__ == "__main__":
    main()
