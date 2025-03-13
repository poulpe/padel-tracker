from padel_tracker.models.base import Logs
from datetime import datetime


def test_create_log_entry():
    log_entry = Logs(
        timestamp=datetime.now(),
        name="Test Log",
        level="INFO",
        message="This is a test log entry.",
    )
    assert log_entry.name == "Test Log"
    assert log_entry.level == "INFO"
    assert log_entry.message == "This is a test log entry."
