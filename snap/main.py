import argparse
import logging

from snap.simulator import SnapSimulator, SnapGameConfig

class SnapGameConfig:
    """
    Configuration for the game of Snap.
    """
    num_decks: int = 1
    num_players: int = 2
    turn_delay: float = 2.0
    fast_ai: bool = False
    use_human_player: bool = False

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--decks", type=int, default=1, help="The number of decks to play with.")
    parser.add_argument("--players", type=int, default=2, help="The number of players to simulate.")
    parser.add_argument("--turn-delay", type=float, default=0.0, help="Amount of time to wait between turns.")
    parser.add_argument("--fast-ai", action="store_true",
        help="If set, the AI will react almost instantly (useful for testing purposes).")
    parser.add_argument("--human-player", action="store_true",
        help="Enable playing vs. the AI as a human.")
    args = parser.parse_args()

    if args.players not in range(2, 5):
        raise SystemExit("Number of players must be 2, 3 or 4.")

    logging.info("Simulating snap with %d deck(s) and %d players.", args.decks, args.players)

    config = SnapGameConfig()
    config.num_decks = args.decks
    config.num_players = args.players
    config.turn_delay = args.turn_delay
    config.fast_ai = args.fast_ai
    config.use_human_player = args.human_player

    SnapSimulator().run(config)


if __name__ == "__main__":
    main()