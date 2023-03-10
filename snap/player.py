"""
Code for players of Snap, as well as the messages that can be sent between players
and the game server.

Each player runs in a different thread. These threads communicate with the main thread
by reading/writing messages on thread-safe queues.

Players send PlayerMessage instances to the server via the snap_queue. This queue
is shared between all players and helps to determine who called snap first.

The server sends ServerMessage instances to each player via that player's turn_queue.
A TURN message tells the player about the current face-up cards for example.
A GAME_OVER message tells the player that the game is over and allows the thread to finish.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from queue import SimpleQueue, Queue, Empty, Full
import threading
import time
import random
import logging

from snap.cards import CardStack, find_pair


class PlayerMessageType(Enum):
    """
    Represents the possible types of messages sent from players to the game server.
    """

    SNAP = "SNAP"
    NO_SNAP = "NO_SNAP"


class ServerMessageType(Enum):
    """
    Represents the possible types of messages sent from the game server to players.
    """

    TURN = "TURN"
    PLAYER_OUT = "PLAYER_OUT"
    END_GAME = "END_GAME"


@dataclass
class PlayerMessage:
    """
    A message sent from players to the game server.
    """

    player_id: int
    message_type: PlayerMessageType


@dataclass
class ServerMessage:
    """
    A message sent from the game server to players.
    """

    message_type: ServerMessageType
    cards: CardStack = None


class Player(ABC):
    """
    Represents an abstract player of Snap.

    Each player runs in a different thread and communicates with the main thread that runs
    the game by reading/writing messages on a queue.
    """

    def __init__(self, player_id: int, snap_queue: SimpleQueue):
        # The player ID
        self.player_id = player_id

        # A queue that the main thread will use to inform this player about new cards on each turn.
        self.turn_queue = SimpleQueue()

        # A queue that this player will use to alert the dealer if she wants to say "snap".
        # This queue is shared by all players, providing the order of who called "snap" first.
        self.snap_queue = snap_queue

        # Changed to false when the player is out of the game.
        self.still_in_game = True

        # The thread that will run the game loop for this player.
        self.thread = None

    def run(self):
        """
        The game loop for this player, which will be the target of a threading.Thread instance.
        """
        logging.debug("Running")
        while True:
            # logging.debug("Waiting for turn")
            server_message = self.turn_queue.get(block=True)
            if server_message.message_type == ServerMessageType.END_GAME:
                self.still_in_game = False
                break

            if server_message.message_type == ServerMessageType.PLAYER_OUT:
                # The game is still ongoing but this player is out
                self.still_in_game = False
                break

            if server_message.message_type != ServerMessageType.TURN:
                logging.error("Unexpected message: %s", server_message)
                break

            cards = server_message.cards
            if self.should_call_snap(cards):
                # logging.debug("Calling snap")
                self.snap_queue.put_nowait(
                    PlayerMessage(
                        player_id=self.player_id, message_type=PlayerMessageType.SNAP
                    )
                )
            else:
                # logging.debug("Not calling snap")
                self.snap_queue.put_nowait(
                    PlayerMessage(
                        player_id=self.player_id, message_type=PlayerMessageType.NO_SNAP
                    )
                )

    @abstractmethod
    def should_call_snap(self, cards) -> bool:
        """Return whether or not to say SNAP."""


class ComputerPlayer(Player):
    """
    A computer controlled player.
    This player will mostly only call SNAP when it sees an actual snap, but will make some mistakes.
    It has a random reaction time.
    """

    def __init__(self, player_id: int, snap_queue: SimpleQueue):
        super().__init__(player_id, snap_queue)
        self.mistake_chance = random.uniform(
            0.01, 0.04
        )  # the chance the AI will incorrectly call snap
        self.miss_chance = random.uniform(
            0.05, 0.2
        )  # the chance the AI will miss a snap
        self.reaction_time_min = random.uniform(
            0.4, 0.6
        )  # the minimum reaction time of this AI
        self.reaction_time_max = random.uniform(
            1.0, 2.5
        )  # the maximum reaction time of this AI

    def should_call_snap(self, cards: CardStack) -> bool:
        """Return whether or not to say SNAP."""
        reaction_time = random.uniform(self.reaction_time_min, self.reaction_time_max)
        time.sleep(reaction_time)

        if find_pair(dict(enumerate(cards))):
            if random.random() < self.miss_chance:
                # We missed it
                return False
            return True

        return random.random() < self.mistake_chance  # incorrectly call snap


class HumanPlayer(Player):
    """
    A human player controlled by you.
    Press Enter to indicate when you want to say SNAP.
    """

    def __init__(self, player_id: int, snap_queue: SimpleQueue):
        super().__init__(player_id, snap_queue)

        print(
            "You've chosen to play as a human!. You'll be player 0. Hit Enter when you see a snap."
        )
        print("Press Enter to continue...")
        input()

        self.should_snap_queue = Queue(maxsize=1)
        keyboard_input_thread = threading.Thread(
            target=self.keyboard_watcher, daemon=True
        )
        keyboard_input_thread.start()

    def keyboard_watcher(self):
        """
        Wait for the player to hit Enter. When they do, post to the queue.
        """
        while self.still_in_game:
            try:
                input()
            except EOFError:
                # Can happen on Ctrl-C
                pass

            try:
                self.should_snap_queue.put_nowait(True)
            except Full:
                # Prevent stacking up a lot of snaps if the user hits enter a lot.
                pass

    def should_call_snap(self, cards) -> bool:
        """Return whether or not to say SNAP."""
        try:
            return self.should_snap_queue.get(timeout=3)
        except Empty:
            return False
