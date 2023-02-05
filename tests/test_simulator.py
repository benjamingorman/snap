import unittest

from snap.simulator import SnapSimulator, find_pair
from snap.cards import CardStack, Card, CardSuit, CardValue
from snap.player import PlayerMessage, PlayerMessageType, ServerMessage, ServerMessageType
from tests.utils import ConsistentSnapPlayer, ConsistentNoSnapPlayer


class TestSnapSimulator(unittest.TestCase):
    """
    Tests for snap.simulator.SnapSimulator
    """

    def test_is_game_over_true(self):
        """
        Test that is_game_over returns True if the game is over.
        """
        sim = SnapSimulator()
        pile0 = CardStack()
        pile1 = CardStack([Card(value=CardValue.ACE, suit=CardSuit.SPADE)])
        sim.player_card_down_piles = [pile0, pile1]
        self.assertEqual(sim.is_game_over(), True)

    def test_is_game_over_false(self):
        """
        Test that is_game_over returns False if the game is not over.
        """
        sim = SnapSimulator()
        pile0 = CardStack([Card(value=CardValue.ACE, suit=CardSuit.HEART)])
        pile1 = CardStack([Card(value=CardValue.ACE, suit=CardSuit.SPADE)])
        sim.player_card_down_piles = [pile0, pile1]
        self.assertEqual(sim.is_game_over(), False)

    def test_get_winning_player_index(self):
        """
        Test that get_winning_player_index returns the correct index.
        """
        sim = SnapSimulator()
        pile0 = CardStack([])
        pile1 = CardStack([])
        pile2 = CardStack([Card(value=CardValue.ACE, suit=CardSuit.SPADE)])
        sim.player_card_down_piles = [pile0, pile1, pile2]
        self.assertEqual(sim.get_winning_player_index(), 2)

    def test_turn_over_new_cards(self):
        """
        Test that turn_over_new_cards takes a card from each down pile and returns
        the correct cards.
        """
        sim = SnapSimulator()
        down_pile0 = CardStack([
            Card(value=CardValue.ACE, suit=CardSuit.HEART),
            Card(value=CardValue.ACE, suit=CardSuit.DIAMOND),
        ])
        down_pile1 = CardStack([
            Card(value=CardValue.ACE, suit=CardSuit.SPADE),
            Card(value=CardValue.ACE, suit=CardSuit.CLUB),
        ])

        up_pile0 = CardStack()
        up_pile1 = CardStack([
            Card(value=CardValue.TWO, suit=CardSuit.SPADE),
        ])
        sim.player_card_down_piles = [down_pile0, down_pile1]
        sim.player_card_up_piles = [up_pile0, up_pile1]
        sim.players = [ConsistentSnapPlayer(0, None), ConsistentSnapPlayer(0, None)]
        cards = sim.turn_over_new_card()

        # It should be player 0's go, so the top card from his down pile should be popped.
        self.assertEqual(len(down_pile0), 1)

        # The right cards should be returned
        self.assertEqual(cards[0], Card(value=CardValue.ACE, suit=CardSuit.DIAMOND))
        self.assertEqual(cards[1], Card(value=CardValue.TWO, suit=CardSuit.SPADE))

    def test_resolve_snap_decision_when_snap_exists(self):
        """
        Test that resolve_snap_decision adds cards to a player's pile if a snap exists.
        """
        sim = SnapSimulator()
        cards = {
            0: Card(value=CardValue.TWO, suit=CardSuit.HEART),
            1: Card(value=CardValue.TWO, suit=CardSuit.CLUB),
            2: Card(value=CardValue.THREE, suit=CardSuit.CLUB),
        }
        sim.player_card_up_piles = [
            CardStack([Card(value=CardValue.TWO, suit=CardSuit.HEART)]),
            CardStack([Card(value=CardValue.TWO, suit=CardSuit.CLUB)]),
            CardStack([Card(value=CardValue.THREE, suit=CardSuit.CLUB)]),
        ]
        sim.player_card_down_piles = [CardStack(), CardStack(), CardStack()]
        sim.resolve_snap_decision(cards, 2)

        # It should clear the relevant card up piles
        self.assertEqual(len(sim.player_card_up_piles[0]), 0)
        self.assertEqual(len(sim.player_card_up_piles[1]), 0)
        self.assertEqual(len(sim.player_card_up_piles[2]), 1)

        # It should add the cards to player 2's card down pile
        self.assertEqual(len(sim.player_card_down_piles[0]), 0)
        self.assertEqual(len(sim.player_card_down_piles[1]), 0)
        self.assertEqual(len(sim.player_card_down_piles[2]), 2)

    def test_resolve_snap_decision_when_no_snap_exists(self):
        """
        Test that resolve_snap_decision punishes the calling player if no snap exists.
        """
        sim = SnapSimulator()
        sim.players = [ConsistentSnapPlayer(0, None), ConsistentSnapPlayer(1, None), ConsistentSnapPlayer(2, None)]
        cards = {
            0: Card(value=CardValue.TWO, suit=CardSuit.HEART),
            1: Card(value=CardValue.THREE, suit=CardSuit.CLUB),
            2: Card(value=CardValue.FOUR, suit=CardSuit.CLUB),
        }
        sim.player_card_up_piles = [
            CardStack([Card(value=CardValue.TWO, suit=CardSuit.HEART)]),
            CardStack([Card(value=CardValue.THREE, suit=CardSuit.CLUB)]),
            CardStack([Card(value=CardValue.FOUR, suit=CardSuit.CLUB)]),
        ]
        sim.player_card_down_piles = [
            CardStack(),
            CardStack(),
            CardStack([Card(value=CardValue.ACE, suit=CardSuit.SPADE)])
        ]
        sim.resolve_snap_decision(cards, 2)

        # It should not clear the relevant card up piles
        self.assertEqual(len(sim.player_card_up_piles[0]), 1)
        self.assertEqual(len(sim.player_card_up_piles[1]), 1)
        self.assertEqual(len(sim.player_card_up_piles[2]), 1)

        # It should remove 1 card from player 2's down pile and give to another player.
        self.assertEqual(len(sim.player_card_down_piles[2]), 0)
        self.assertEqual(len(sim.player_card_down_piles[0]) + len(sim.player_card_down_piles[1]), 1)


if __name__ == "__main__":
    unittest.main()