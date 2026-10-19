# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before any code I wrote down the three things a user needs to do: add a pet, schedule a task for that pet, and see today's tasks in order. That led to four classes (the draft is in `diagrams/uml_draft.mmd`):

- **Task** is one care activity: description, "HH:MM" time, duration, priority, how often it repeats (once, daily, weekly), due date, and whether it's done. It can mark itself complete.
- **Pet** has a name, a species, and its own list of tasks. It can add, remove and list them.
- **Owner** has a list of pets and a `get_all_tasks()` method that gives back every pet's tasks in one list.
- **Scheduler** is the brain. It doesn't keep its own copy of tasks. It asks the Owner for them, so it works across all the pets, and it does the sorting, filtering and conflict checking.

I used dataclasses for Task, Pet and Owner so they stay short. An Owner has many Pets, a Pet has many Tasks, and the Scheduler reads from the Owner. I went with this split because each class has one job, and the Scheduler never has to dig into a single pet.

**b. Design changes**

Yes, it changed a bit once I got into the code. Comparing `uml_draft.mmd` to `uml_final.mmd`:

- I added `Task.pet_name`, which `Pet.add_task()` sets automatically. Once the Scheduler pulls everything into one list, a task doesn't know whose it is anymore, so sorting and filtering by pet would have needed extra lookups. Putting the name on the task fixed that.
- I added `Task.next_occurrence()` and `Scheduler.mark_task_complete()` so finishing a daily or weekly task creates the next one.
- I added `Scheduler.todays_schedule()` and let `sort_by_time()` take an optional list, so the app can sort tasks that are already filtered.

The AI suggested these while building, and I kept them because each one filled a real gap instead of adding extra stuff.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler sorts by date and time first, then uses priority (high, medium, low) to break ties between tasks at the same time. Completed tasks are left out of today's schedule and out of conflict checks, and a task's frequency decides whether a follow-up gets created.

I put time first because the main thing an owner needs is "what's next today?", and the assignment's algorithm features (sorting, filtering, conflicts, recurring tasks) are all about time. Priority is only the tiebreaker.

One thing it doesn't do yet is use `duration_minutes` or an owner's available time to decide what fits in a day. Duration is saved and shown, but it doesn't change the plan.

**b. Tradeoffs**

The conflict check only flags tasks at the exact same date and time. It doesn't look at overlap, so a 30-minute walk at 08:00 and a feeding at 08:15 won't be flagged even though they collide.

I think that's fine for this project. It's simple, easy to test, and it catches the most common mistake, double-booking one slot. It also returns a warning message instead of crashing or blocking the user. The downside is that real overlaps get through, and the fix would be comparing start and end times once duration is part of scheduling.

A smaller tradeoff: a repeating task only creates its next copy when the current one is completed, instead of making a month of tasks ahead of time. That keeps the list short, but a task that never gets completed never repeats.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude as an agent in the desktop app with access to my project folder, and I let it do most of the building. It drafted the Mermaid UML, made the class skeleton, wrote the four classes and the Scheduler features, wrote the demo script and the tests, hooked up the Streamlit app, and filled in the README using real output from the demo and tests. I also used it to help write this reflection.

What worked best was giving it everything up front: the grading rubric, the full phase-by-phase instructions, and the starter repo. That worked a lot better than asking for small pieces one at a time. I stayed in one long session instead of splitting it into a new chat for each phase.

**b. Judgment and verification**

I didn't reject any of the AI's design ideas outright. I accepted the class layout and the extra methods because they matched the rubric and fixed real gaps. What I did spend effort on was checking its work instead of just trusting it:

- The first version of the time input in the app had no default value, which only works on newer Streamlit versions than the starter's `requirements.txt` allows (`streamlit>=1.30`). It was changed to a default time so it works on the minimum version.
- All 22 tests passed on the first run, and that made me suspicious. To check them, the AI broke the code on purpose in a scratch copy (the sort order, the recurrence date math, and the conflict check). Four tests failed, so I know they can actually catch bugs.
- The "Done!" message vanished right away because the app re-ran the page, so it now saves the message in `st.session_state` and shows it on the next run.
- The app was run through Streamlit's headless test tool: add pets, add two tasks at the same time, see the conflict warning, and complete a daily task to see the next day's task appear.

If I did this again, I'd push back on the conflict check and ask for overlap detection based on duration, instead of only exact times.

---

## 4. Testing and Verification

**a. What you tested**

There are 22 tests in `tests/test_pawpal.py` covering:

- Completing a task, adding tasks to a pet, and rejecting a bad time.
- The Owner collecting tasks from every pet, and the Scheduler reading from all of them.
- Sorting: in time order across pets, date before time, and an empty list.
- Filtering by pet, by status, and both together.
- Repeating tasks: daily makes one for the next day, weekly makes one seven days later, one-time tasks make nothing.
- Conflicts: same time for two pets, same time for one pet, no false alarm for different times or different days, and completed tasks ignored.
- Edge cases like a pet with no tasks.

I focused on those because sorting, repeating and conflict warnings are the "smart" parts of the app, the parts a user would trust it to get right, and the easiest to break quietly with something like an off-by-one-day mistake.

**b. Confidence**

About 4 out of 5. The main behaviors and edge cases pass, the demo output looks right, and the tests fail when the code is deliberately broken. The app itself got a headless test but not much beyond that.

If I had more time I'd test:

- Overlapping durations (the tradeoff above).
- Repeating tasks across a month or year boundary.
- Completing a task that's already complete, which would currently create a duplicate next task. The app only shows pending tasks so a user can't do this, but the method doesn't guard against it.
- Empty or bad input through the app.

---

## 5. Reflection

**a. What went well**

Building and checking the logic in `main.py` and pytest before touching Streamlit. By the time I connected the app, the logic was already proven, so the UI was a thin layer on top and needed very little debugging. I'm also happy that the Scheduler reads everything through `Owner.get_all_tasks()`, because that made multiple pets work without any special cases.

**b. What you would improve**

I'd use `duration_minutes` to build a real daily plan that fits the owner's available time and catches overlapping tasks. I'd also add editing and deleting tasks in the app, and save pets and tasks to a file, since right now everything disappears when the app restarts because it only lives in `st.session_state`.

**c. Key takeaway**

Working with AI made me the lead architect. My job was to decide what each class is responsible for and what "done" means, and then check the AI's work instead of just trusting it. The biggest lesson was that passing tests don't prove the code is right. I only trusted the tests after seeing them fail on code that was deliberately broken. And giving the AI full context at the start (rubric, instructions, starter repo) saved a lot more time than steering it piece by piece.
