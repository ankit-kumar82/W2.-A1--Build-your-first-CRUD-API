"""
Utility functions for filtering, searching, and analytics.
"""
from typing import List, Dict, Any, Optional


def filter_and_search_tasks(
    tasks: List[Dict[str, Any]],
    done: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter tasks by completion status and/or search term matching the title.
    """
    results = tasks

    if done is not None:
        results = [t for t in results if t["done"] == done]

    if search is not None:
        query = search.strip().lower()
        results = [t for t in results if query in t["title"].lower()]

    return results


def calculate_task_stats(tasks: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate totals for total, done, and open tasks.
    """
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    open_count = total - done_count

    return {
        "total": total,
        "done": done_count,
        "open": open_count,
    }
