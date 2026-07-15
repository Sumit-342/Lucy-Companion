from enum import Enum


class LucyState(Enum):
    HIDDEN = "hidden"
    WALKING_IN = "walking_in"
    THINKING = "thinking"
    ACTIVE_REMINDER = "active_reminder"
    CONFIRMING = "confirming"
    WALKING_OUT = "walking_out"
    DRAGGING = "dragging"
