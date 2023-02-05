# Snap

This is my implementation of the game Snap in Python.

Python 3.8+ is required.
No third party libraries are required.

To run the game, execute the main module in a terminal:
```
$ python3 -m snap.main
```

To change the number of decks or players, use the `--decks` or `--players` CLI arg.
```
$ python3 -m snap.main --decks 2 --players 4
```

To play as a human against the AI use the `--human-player` CLI arg.
```
$ python3 -m snap.main --decks 2 --players 4 --human-player
```

To make the AI play instantly use the `--fast-ai` CLI arg.
```
$ python3 -m snap.main --decks 2 --players 4 --human-player
```

To run the unit-tests:
```
$ python3 -m unittest discover
```

## Notes:

On each turn the game will print lines like this:

```
Turn 3: (Player 0) 3♤ 7♢  |  Up: 1, 1  |  Down: 25, 25
```

This indicates that it is turn 3 and it is player 0's turn to play. There is 1 card in the 'up' pile for
each player respectively. There are 25 cards in the 'pile' for each player respectively.

* The game ends with a win if only 1 player has cards in his down pile at the end of a turn.
* The game ends in a draw if no players have cards in their down piles at the end of a turn.
* I've chosen not to include jokers in the playing cards.
* I've chosen not to implement a central 'snap pot'. If a player mistakenly calls snap then
  their top card will be given to a random other player who is still in the game.
* A player is marked as being out of the game if their down pile is empty at the end of their turn.