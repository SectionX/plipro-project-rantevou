"""
Δήλωση τύπων για εσωτερική χρήση από τα models.
Δεν προορίζονται για instantiation.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class SubscriberInterface(Protocol):
    """
    Ορισμός του subscriber interface για τα models
    """

    def subscriber_update(self): ...
