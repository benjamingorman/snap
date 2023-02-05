"""
Tests for snap.player
"""
import unittest
from queue import SimpleQueue

from snap.player import (
    PlayerMessage,
    PlayerMessageType,
    ServerMessage,
    ServerMessageType,
)
from snap.cards import CardStack
from tests.utils import ConsistentSnapPlayer, ConsistentNoSnapPlayer


class TestPlayer(unittest.TestCase):
    """
    Tests for snap.player.Player
    """

    def test_snap_called(self):
        """
        The player should call SNAP if should_call_snap returns True.
        """
        snap_queue = SimpleQueue()
        player = ConsistentSnapPlayer(1, snap_queue)
        player.turn_queue.put(
            ServerMessage(message_type=ServerMessageType.TURN, cards=CardStack())
        )
        player.turn_queue.put(ServerMessage(message_type=ServerMessageType.END_GAME))
        player.run()
        response = snap_queue.get_nowait()
        self.assertEqual(
            response, PlayerMessage(player_id=1, message_type=PlayerMessageType.SNAP)
        )

    def test_no_snap_called(self):
        """
        The player should call NO_SNAP if should_call_snap returns False.
        """
        snap_queue = SimpleQueue()
        player = ConsistentNoSnapPlayer(1, snap_queue)
        player.turn_queue.put(
            ServerMessage(message_type=ServerMessageType.TURN, cards=CardStack())
        )
        player.turn_queue.put(ServerMessage(message_type=ServerMessageType.END_GAME))
        player.run()
        response = snap_queue.get_nowait()
        self.assertEqual(
            response, PlayerMessage(player_id=1, message_type=PlayerMessageType.NO_SNAP)
        )


if __name__ == "__main__":
    unittest.main()
