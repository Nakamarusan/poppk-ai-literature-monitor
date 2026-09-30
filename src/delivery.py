"""Durable notifications: saving an article is not the same as delivering it."""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Any

from .core import JST, MonitorError, clean, save_json, succeeded_on_jst_date
from .reporting import create_issue


def should_skip_retry(state: dict[str, Any], today: dt.date) -> bool:
    """An empty or undelivered run must not suppress the scheduled retry."""
    return (succeeded_on_jst_date(state, today)
            and state.get("last_delivery_date_jst") == today.isoformat()
            and not state.get("pending_notifications"))


def queue_notification(state: dict[str, Any], *, title: str, body: str,
                       marker: str, date: str, kind: str) -> None:
    queue = state.setdefault("pending_notifications", [])
    if not any(item["marker"] == marker for item in queue):
        queue.append({"title": title, "body": body, "marker": marker,
                      "date": date, "kind": kind})


def deliver_pending(state: dict[str, Any], path: Path) -> list[str]:
    """Checkpoint after each send; a failed send remains pending for recovery."""
    queue = state.setdefault("pending_notifications", [])
    if not queue:
        return []
    token, repository, owner = (os.getenv(key, "") for key in
        ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "GITHUB_REPOSITORY_OWNER"))
    if not all((token, repository, owner)):
        raise MonitorError("Notification credentials are unavailable; queued notices are retained.")
    urls = []
    while queue:
        item = queue[0]
        url = create_issue(item["title"],
            f"{item['marker']}\n\n@{owner}\n\n{item['body']}",
            item["marker"], token, repository, owner)
        if not clean(url):
            raise MonitorError("GitHub did not confirm an Issue URL; the notification remains pending.")
        queue.pop(0)
        if item["kind"] == "papers":
            state["last_delivery_date_jst"] = max(item["date"], state.get("last_delivery_date_jst", ""))
        else:
            state["last_status_notice_date_jst"] = item["date"]
        state["last_notification_url"] = url
        save_json(path, state)
        urls.append(url)
    return urls
