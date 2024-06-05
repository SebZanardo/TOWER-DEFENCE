from dataclasses import dataclass


STARTING_HEALTH = 100
STARTING_MONEY = 999


@dataclass
class Player:
    health: int
    money: int
