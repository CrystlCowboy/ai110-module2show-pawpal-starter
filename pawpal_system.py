"""PawPal+ logic layer: Owner, Pet, Task and Scheduler (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass

    def list_tasks(self) -> List[Task]:
        """Return this pet's tasks."""
        pass


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return every pet's tasks together."""
        pass


class Scheduler:
    """The brain: organizes and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Read all tasks from the owner."""
        pass

    def sort_by_time(self) -> List[Task]:
        """Return all tasks in chronological order."""
        pass

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        pass

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks scheduled at the same time."""
        pass
