"""
Utility functions for tests.
"""
from snap.player import Player


class ConsistentSnapPlayer(Player):
    """
    A player that always calls SNAP at every opportunity.
    """

    def should_call_snap(self, cards) -> bool:
        return True


class ConsistentNoSnapPlayer(Player):
    """
    A player that never calls SNAP.
    """

    def should_call_snap(self, cards) -> bool:
        return False
