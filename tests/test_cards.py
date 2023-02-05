import unittest
import copy
from snap.cards import CardValue, CardSuit, Card, CardStack, find_pair


class TestCardStack(unittest.TestCase):
    """
    Tests for snap.cards.CardStack
    """

    def test_push_pop(self):
        """
        Push should add a card and pop should remove one.
        """
        cards = CardStack()
        cards.push(Card(value=CardValue.ACE, suit=CardSuit.SPADE))
        self.assertEqual(len(cards), 1)

        card = cards.pop()
        self.assertEqual(len(cards), 0)
        self.assertEqual(card, Card(value=CardValue.ACE, suit=CardSuit.SPADE))

    def test_new_full_deck(self):
        """
        Test that new_full_deck includes all possible cards.
        """
        cards = CardStack.new_full_deck()
        self.assertEqual(len(cards), 52)
        self.assertEqual(len(set(map(str, cards))), 52)  # all should be unique

    def test_shuffle(self):
        """
        Shuffle should change the order of the deck.
        """
        cards = CardStack.new_full_deck()
        order1 = copy.deepcopy(cards._cards)
        cards.shuffle()
        order2 = cards._cards
        self.assertNotEqual(order1, order2)


class TestCardsHelpers(unittest.TestCase):
    """
    Tests for helper functions in snap.cards
    """

    def test_find_pair(self):
        """
        Test that find pair can find a matching pair.
        """
        cards = {
            0: Card(value=CardValue.TWO, suit=CardSuit.CLUB),
            1: Card(value=CardValue.TWO, suit=CardSuit.SPADE),
        }
        self.assertEqual(find_pair(cards), [0, 1])

    def test_find_pair_no_match(self):
        """
        Test that find pair returns None if there is no pair to be found.
        """
        cards = {
            0: Card(value=CardValue.TWO, suit=CardSuit.CLUB),
            1: Card(value=CardValue.THREE, suit=CardSuit.SPADE),
        }
        self.assertEqual(find_pair(cards), None)




if __name__ == "__main__":
    unittest.main()