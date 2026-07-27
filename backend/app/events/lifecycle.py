_TEMPLATES: dict[str, str] = {  # maps the last segment of an event_type slug to a human-readable message template
    "init":       "{name} initialized successfully.",
    "warn":       "A warning occurred in {name}.",
    "success":    "{name} completed successfully.",
    "error":      "An error occurred in {name}.",
    # info uses the message arg directly — callers pass it as the message kwarg
    "info":       "",
}


def lifecycle_message(event_type: str, name: str) -> str:
    """Return the human-readable message for a lifecycle event type and entity name."""
    key = event_type.split(".")[-1]  # extract the action segment (e.g. "init" from "call.init")
    return _TEMPLATES.get(key, "").format(name=name)  # substitute entity name; returns empty string for unrecognised event keys
