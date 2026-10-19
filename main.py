"""CLI demo for PawPal+: builds an owner, pets and tasks, then prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(title, tasks):
    """Print a list of tasks as a readable table."""
    print(f"\n=== {title} ===")
    if not tasks:
        print("  (nothing scheduled)")
        return
    print(f"  {'Time':<6} {'Pet':<9} {'Task':<22} {'Min':>4}  {'Priority':<8} Status")
    print("  " + "-" * 62)
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(f"  {t.time:<6} {t.pet_name:<9} {t.description:<22} {t.duration_minutes:>4}  {t.priority:<8} {status}")


def main():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    mochi.add_task(Task("Morning walk", "08:00", 30, "high"))
    whiskers.add_task(Task("Breakfast feeding", "07:30", 10, "high"))
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium"))

    scheduler = Scheduler(owner)
    print(f"PawPal+ for {owner.name} ({len(owner.pets)} pets)")
    print_schedule("Today's Schedule", scheduler.todays_schedule())


if __name__ == "__main__":
    main()
