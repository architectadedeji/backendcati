"""Enums for the application."""
from enum import Enum


class ContactStatus(str, Enum):
    """Contact interview round status."""

    ROUND_1 = "round_1"
    ROUND_2 = "round_2"
    ROUND_3 = "round_3"
    ROUND_4 = "round_4"
    ALL_ROUNDS_COMPLETED = "all_rounds_completed"

    @classmethod
    def get_display_name(cls, status: str) -> str:
        """Get human-readable name for status."""
        display_names = {
            cls.ROUND_1: "Round 1",
            cls.ROUND_2: "Round 2",
            cls.ROUND_3: "Round 3",
            cls.ROUND_4: "Round 4",
            cls.ALL_ROUNDS_COMPLETED: "All Rounds Completed",
        }
        return display_names.get(status, status)

    @classmethod
    def get_next_status(cls, current_status: str) -> str:
        """Get the next status in the sequence."""
        next_statuses = {
            cls.ROUND_1: cls.ROUND_2,
            cls.ROUND_2: cls.ROUND_3,
            cls.ROUND_3: cls.ROUND_4,
            cls.ROUND_4: cls.ALL_ROUNDS_COMPLETED,
            cls.ALL_ROUNDS_COMPLETED: cls.ALL_ROUNDS_COMPLETED,
        }
        return next_statuses.get(current_status, current_status)
