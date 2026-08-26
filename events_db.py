import streamlit as st
from supabase_auth import get_supabase_client

TABLE = "events"

DEFAULT_EVENTS = ["Hackathon 2026", "Science Fair", "Sports Meet", "Other"]


def get_events():
    """Returns the current list of event names, seeding defaults on first run."""
    client = get_supabase_client()

    try:
        result = client.table(TABLE).select("name").order("name").execute()
        events = [row["name"] for row in result.data] if result.data else []
    except Exception:
        events = []

    if not events:
        _seed_default_events(client)
        events = DEFAULT_EVENTS.copy()

    # Keep "Other" as the last option for a cleaner dropdown.
    if "Other" in events:
        events = [e for e in events if e != "Other"] + ["Other"]

    return events


def _seed_default_events(client):
    for name in DEFAULT_EVENTS:
        try:
            client.table(TABLE).insert({"name": name}).execute()
        except Exception:
            pass  # already exists — ignore


def add_event(name):
    """Admin-only: call this from a UI path already gated on is_admin."""
    name = (name or "").strip()

    if not name:
        return False, "Event name cannot be empty."

    client = get_supabase_client()

    existing = client.table(TABLE).select("name").eq("name", name).execute()
    if existing.data:
        return False, "This event already exists."

    try:
        client.table(TABLE).insert({"name": name}).execute()
    except Exception as e:
        return False, f"Could not add event: {e}"

    return True, f"Event '{name}' added."
