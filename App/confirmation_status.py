from enum import Enum


class ConfirmationStatus(Enum):
    NO_MESSAGE = 0,
    EDITED = 1,
    CLEAR = 2,
    DELETE = 3,
    CONFIRM_EDIT = 4,
    CONFIRM_REMOVE = 5

