"""
Simulator for the game of Snap.
"""
from typing import List
import logging
import time
import threading
import random
from queue import SimpleQueue
from dataclasses import dataclass

from snap.cards import Card, CardStack, find_pair
from snap.player import (
    Player,
    PlayerMessage,
    PlayerMessageType,
    HumanPlayer,
    ComputerPlayer,
    ServerMessageType,
    ServerMessage,
)


@dataclass
class SnapGameConfig:
    """
    Configuration for the game of Snap.
    """

    num_decks: int = 1
    num_players: int = 2
    turn_delay: float = 2.0
    fast_ai: bool = False
    use_human_player: bool = False


class SnapSimulator:
    """
    Simulator for the game of Snap.
    The entrypoint is the 'run' method, which blocks until the game completes.
    """

    def __init__(self):
        self.turn_count = 0
        self.config = SnapGameConfig()
        self.players: Player = []
        self.threads = []
        self.snap_queue = SimpleQueue()
        self.player_card_up_piles: List[CardStack] = []
        self.player_card_down_piles: List[CardStack] = []

    def run(self, config: SnapGameConfig):
        """
        Run the main game loop until the game completes.
        """
        self.config = config
        self.start_game()

        try:
            while not self.is_game_over():
                self.play_turn()
            self.print_game_over_message()
        except KeyboardInterrupt:
            logging.info("Game interrupted.")
        finally:
            self.cleanup_workers()

    def is_game_over(self) -> bool:
        """
        Check whether or not the game is over.
        The game ends in a win if only one player has cards left in his down pile.
        The game ends in a draw if no players have cards left in their down piles.
        """
        non_empty_down_piles = [
            stack for stack in self.player_card_down_piles if len(stack)
        ]
        return len(non_empty_down_piles) <= 1

    def get_winning_player_index(self) -> int:
        """
        Return the index of the player who has won the game.
        Returns None if it's a draw.
        Returns None if the game is not yet over.
        """
        if not self.is_game_over():
            return None

        for i, stack in enumerate(self.player_card_down_piles):
            if len(stack):
                return i

        return None

    def print_game_over_message(self):
        """
        Print a message to indicate the winner of the game.
        """
        winner_index = self.get_winning_player_index()
        if winner_index is None:
            print("GAME OVER. It was a draw.")
        else:
            print(f"GAME OVER. Player {winner_index} won.")

    def play_turn(self):
        """
        Play a single turn in the game.
        One card will be removed from every player's face down pile.
        The players will then be given the opportunity to say SNAP.
        If someone correctly called snap then cards will be updated.
        """
        # Remove a card from each player's face down pile
        cards = self.turn_over_new_card()
        responses = self.gather_responses(cards)
        self.process_responses(cards, responses)
        self.mark_players_out()
        self.turn_count += 1
        print()
        time.sleep(self.config.turn_delay)

    def turn_over_new_card(self) -> dict[int, Card]:
        """
        Turn over a new card from one player's down pile.
        Returns a dict mapping player ID to the top card for that player.
        Excludes the players who are out of the game.
        Prints a message informing the user about all top cards from each player.
        """
        players_still_in = [player for player in self.players if player.still_in_game]
        player_whose_turn_it_is = players_still_in[
            self.turn_count % len(players_still_in)
        ]

        cards = {}
        cards_message = []
        for i, pile in enumerate(self.player_card_up_piles):
            if i == player_whose_turn_it_is.player_id:
                card = self.player_card_down_piles[i].pop()
                pile.push(card)

            if len(pile):
                cards[i] = pile.peek()
                cards_message.append(str(cards[i]))
            else:
                cards_message.append("_")

        print(
            "Turn {}: (Player {}) {}  |  Up: {}  |  Down: {}".format(  # pylint: disable=consider-using-f-string
                self.turn_count + 1,
                player_whose_turn_it_is.player_id,
                " ".join(cards_message),
                ", ".join([str(len(stack)) for stack in self.player_card_up_piles]),
                ", ".join([str(len(stack)) for stack in self.player_card_down_piles]),
            )
        )
        return cards

    def gather_responses(self, cards: dict[int, Card]) -> List[PlayerMessage]:
        """
        Given some new cards, gather responses from each player about whether
        they want to say snap or not.
        """
        # Communicate the newly drawn cards to each player.
        responses = []
        for player in self.players:
            player.turn_queue.put_nowait(
                ServerMessage(message_type=ServerMessageType.TURN, cards=cards.values())
            )

        # Wait for a response from all players still in the game (SNAP or NO_SNAP)
        while len(responses) < len(
            [player for player in self.players if player.still_in_game]
        ):
            response = self.snap_queue.get(block=True)
            if response.message_type == PlayerMessageType.SNAP:
                print(f"Player {response.player_id}: SNAP!")
            responses.append(response)

        return responses

    def process_responses(self, cards: CardStack, responses: List[PlayerMessage]):
        """
        Process the responses from each player about whether they want to say snap or not.
        Here we decide whether anyone won the turn.
        """
        for message in responses:
            if message.message_type == PlayerMessageType.SNAP:
                self.resolve_snap_decision(cards, message.player_id)
                break  # Only the first player to call snap matters

    def resolve_snap_decision(self, cards: dict[int, Card], player_id: int):
        """
        Resolve the outcome of a player saying snap.
        Either they were correct and they win some cards, or they were incorrect and they lose one.
        """
        if snap_indices := find_pair(cards):
            self.resolve_snap_decision_correct(snap_indices, player_id)
        else:
            self.resolve_snap_decision_incorrect(player_id)

    def resolve_snap_decision_correct(self, snap_indices: List[int], player_id: int):
        """
        Resolve a correct snap decision.
        """
        victory_cards = (
            self.player_card_up_piles[snap_indices[0]]
            + self.player_card_up_piles[snap_indices[1]]
        )
        print(
            f"Player {player_id} called snap correctly and won {len(victory_cards)} cards."
        )

        # Clear the card up piles for the players with snapped cards.
        self.player_card_up_piles[snap_indices[0]] = CardStack()
        self.player_card_up_piles[snap_indices[1]] = CardStack()

        # Give the victory cards to the player who called snap.
        self.player_card_down_piles[player_id] += victory_cards

    def resolve_snap_decision_incorrect(self, player_id: int):
        """
        Resolve an incorrect snap decision.
        Remove one card from the mistaken player's down pile (if any) and give it to a random
        other player.
        """
        if not self.player_card_down_piles[player_id]:
            # Their down pile is empty
            return
        card = self.player_card_down_piles[player_id].pop()
        other_players_still_in = set(
            player.player_id for player in self.players if player.still_in_game
        ) - set([player_id])
        player_to_receive_card = random.choice(list(other_players_still_in))
        self.player_card_down_piles[player_to_receive_card].push(card)
        print(
            f"Player {player_id} called snap incorrectly and "
            f"sacrificed a card to player {player_to_receive_card}."
        )

    def mark_players_out(self):
        """
        Mark players as out if they have run out of cards in their down pile.
        """
        for down_pile, player in zip(self.player_card_down_piles, self.players):
            if player.still_in_game and not down_pile:
                print(f"Player {player.player_id} is out!")
                player.turn_queue.put_nowait(
                    ServerMessage(message_type=ServerMessageType.PLAYER_OUT)
                )

    def start_game(self):
        """
        Set up the initial state of the game.
        This includes creating and shuffling the deck(s) used as well as creating
        threads for each player worker.
        """
        self.turn_count = 1
        self.players = []
        self.threads = []
        self.snap_queue = SimpleQueue()
        self.player_card_up_piles = []
        self.player_card_down_piles = []

        logging.info("Creating player workers...")
        for i in range(self.config.num_players):
            if i == 0 and self.config.use_human_player:
                player = HumanPlayer(i, self.snap_queue)
            else:
                player = ComputerPlayer(i, self.snap_queue)
                if self.config.fast_ai:
                    player.reaction_time_min = 0.0
                    player.reaction_time_max = 0.001
            thread = threading.Thread(daemon=True, target=player.run)
            thread.start()
            self.players.append(player)
            self.threads.append(thread)

        logging.info("Shuffling the deck...")
        dealer_cards = sum(
            (CardStack.new_full_deck() for _ in range(self.config.num_decks)),
            start=CardStack(),
        )
        dealer_cards.shuffle()
        logging.debug("%s", dealer_cards)

        logging.info("Dealing the cards...")
        self.player_card_up_piles = [
            CardStack() for _ in range(self.config.num_players)
        ]
        self.player_card_down_piles = [
            CardStack() for _ in range(self.config.num_players)
        ]

        # Now deal the cards
        for i, card in enumerate(dealer_cards):
            self.player_card_down_piles[i % self.config.num_players].push(card)

        for i, stack in enumerate(self.player_card_down_piles):
            logging.debug("Player %d cards: %s", i, stack)

    def cleanup_workers(self):
        """
        Ensure all player worker threads have finished properly.
        """
        for player in self.players:
            player.turn_queue.put(
                ServerMessage(message_type=ServerMessageType.END_GAME)
            )

        for thread in self.threads:
            thread.join()
