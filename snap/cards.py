"""
This module contains data-structures for representing playing cards.
"""
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import List
import random


class CardValue(Enum):
    """
    Represents the value of a playing card.
    """

    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


class CardSuit(Enum):
    """
    Represents the suit of a playing card.
    """

    CLUB = "♧"
    HEART = "♡"
    SPADE = "♤"
    DIAMOND = "♢"


@dataclass
class Card:
    """
    Represents a single card, consisting of a suit and a value.
    """

    value: CardValue
    suit: CardSuit

    def __repr__(self):
        return f"{self.value.value}{self.suit.value}"


class CardStack:
    """
    Represents a collection of cards in some order.
    This could be a full deck of cards, just a few, or an empty set.
    """

    def __init__(self, cards: List[Card] = None):
        self._cards = cards or []

    def pop(self) -> Card:
        """Remove the top card and return it."""
        return self._cards.pop()

    def peek(self) -> Card:
        """Show the top card."""
        if not self._cards:
            return None
        return self._cards[-1]

    def push(self, card: Card):
        """Add a card to the top of the stack."""
        self._cards.append(card)

    def shuffle(self):
        """Randomly shuffle all the cards."""
        random.shuffle(self._cards)

    def __repr__(self):
        return f"<CardStack {str(self._cards)}>"

    def __add__(self, other_stack):
        """This way we can easily merge two stacks using the standard addition operator."""
        return CardStack(self._cards + other_stack._cards)

    def __iter__(self):
        return iter(self._cards)

    def __len__(self):
        return len(self._cards)

    @staticmethod
    def new_full_deck():
        """Create a CardStack containing one of each possible playing card."""
        return CardStack(
            [Card(value=value, suit=suit) for suit in CardSuit for value in CardValue]
        )


def find_pair(player_cards: dict[int, Card]) -> List[int]:
    """
    Checks whether the cards for the given players contain a pair.
    If so, returns the 2 indices of the first pair found.
    If no pair was found, returns None.
    """
    # maps card value to the indice(s) in the stack at which that card value occurs.
    value_to_indices = defaultdict(list)

    for i, card in player_cards.items():
        value_to_indices[card.value].append(i)

    for _, indices in value_to_indices.items():
        if len(indices) > 1:  # At least two cards have the same value.
            return indices[:2]  # Only return the first pair found.

    return None
