"""PawPal+ logic layer: Owner, Pet, Task and Scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import List, Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
VALID_FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care activity (walk, feeding, medication, ...)."""

    description: str
    time: str  # 24-hour "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # "high" | "medium" | "low"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # filled in automatically by Pet.add_task

    def __post_init__(self) -> None:
        """Validate the time, priority and frequency values."""
        try:
            datetime.strptime(self.time, "%H:%M")
        except ValueError:
            raise ValueError(f"time must be 'HH:MM' (24-hour), got {self.time!r}")
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(f"priority must be one of {list(PRIORITY_ORDER)}, got {self.priority!r}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(VALID_FREQUENCIES)}, got {self.frequency!r}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh copy of this task for its next due date, or None if it does not repeat."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return replace(self, due_date=self.due_date + delta, completed=False)

    def __str__(self) -> str:
        """Readable one-line summary of the task."""
        status = "done" if self.completed else "todo"
        pet = f" [{self.pet_name}]" if self.pet_name else ""
        return (
            f"{self.due_date.isoformat()} {self.time}  {self.description}{pet} "
            f"({self.duration_minutes} min, {self.priority}, {self.frequency}, {status})"
        )


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet's name on it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet (no error if it is not present)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def list_tasks(self) -> List[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive); None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every pet's tasks together in one list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain: retrieves, organizes and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Read all tasks from the owner (which gathers them from every pet)."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks (default: all pets' tasks) ordered by due date, then "HH:MM" time, then priority."""
        items = self.get_all_tasks() if tasks is None else tasks
        return sorted(items, key=lambda t: (t.due_date, t.time, PRIORITY_ORDER[t.priority]))

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return tasks matching a pet name and/or completion status; None means "don't filter on this"."""
        result = self.get_all_tasks()
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def detect_conflicts(self) -> List[str]:
        """Return a warning per date/time slot holding 2+ pending tasks (same or different pets); never raises."""
        slots = {}
        for task in self.get_all_tasks():
            if not task.completed:
                slots.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in group)
                warnings.append(f"Conflict on {day.isoformat()} at {time}: {names}")
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if it repeats daily/weekly, add the next occurrence to the same pet and return it."""
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(follow_up)
        return follow_up

    def todays_schedule(self, on: Optional[date] = None) -> List[Task]:
        """Return the not-yet-completed tasks due on a given day (default today), in time order."""
        day = on or date.today()
        due = [t for t in self.get_all_tasks() if t.due_date == day and not t.completed]
        return sorted(due, key=lambda t: (t.time, PRIORITY_ORDER[t.priority]))
