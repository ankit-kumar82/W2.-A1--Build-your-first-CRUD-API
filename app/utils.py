"""
Utility functions for filtering, searching, and analytics.
"""
from typing import List, Dict, Any, Optional, Union
from app.models import Task


def filter_and_search_tasks(
    tasks: List[Union[Task, Dict[str, Any]]],
    done: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[Union[Task, Dict[str, Any]]]:
    """
    Filter tasks by completion status and/or search term matching the title.
    """
    results = tasks

    if done is not None:
        results = [
            t for t in results
            if (t.done if isinstance(t, Task) else t["done"]) == done
        ]

    if search is not None and search.strip():
        query = search.strip().lower()
        results = [
            t for t in results
            if query in (t.title if isinstance(t, Task) else t["title"]).lower()
        ]

    return results


def calculate_task_stats(tasks: List[Union[Task, Dict[str, Any]]]) -> Dict[str, int]:
    """
    Calculate totals for total, done, and open tasks.
    """
    total = len(tasks)
    done_count = sum(
        1 for t in tasks
        if (t.done if isinstance(t, Task) else t["done"])
    )
    open_count = total - done_count

    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }
