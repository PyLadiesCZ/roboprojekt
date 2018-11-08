#WIP

import enum
import dataclasses

@dataclasses.dataclass
class Robot:
    damage_count: int
    life_count: int
    robot_direction: Direction
    is_active: bool
    field: Position
    flags_count: int
    robot_type: RobotType
    initial_pozition: Position
    program: Program


    def shoot(self, game_state):
        ...
        return game_state

    def move_forward(self, game_state, distance):
        ...
        return game_state

    def be_moved(self, game_state, move_direction, distance):
        ...
        return game_state

    def be_turned(self, game_state, turn_direction):
        ...
        return game_state

    def be_killed(self, game_state):
        ...
        return game_state

    def be_damaged(self, game_state):
        ...
        return game_state

    def get_flag(self, game_state):
        ...
        return game_state

    def repair(self, game_state):
        ...
        return game_state

    def turn_off(self, game_state):
        ...
        return game_state


    def perform_CardEffect(self, game_state, CardEffect):
        if ...:
            be_moved(self, game_state, move_direction, distance)
            return game_state
        elif ...:
            be_turned(self, game_state, turn_direction)
            return game_state

    def perform_FieldEffect(self, game_state, FieldEffect):
        if ...:
            be_moved(self, game_state, move_direction, distance)
            return game_state
        elif ...:
            be_turned(self, game_state, turn_direction)
            return game_state
        elif...:
            be_killed(self, game_state)
            return game_state
        elif ...:
            be_damaged(self, game_state)
            return game_state

@dataclasses.dataclass
class Directions:
    '''future square (where robot looks to)'''
    x: int
    y: int
    def turn_direction(self, TurnDirection):
        ...
        return x,y

class TurnDirection(enum.Enum):
    FORWARD = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3

@dataclasses.dataclass
class Program:
    cards: list #Card

@dataclasses.dataclass
class Card:
    priority: int
    effect: CardEffect
    face_up: bool = True

@dataclasses.dataclass
class CardEffect:
    card_type: CardType
    direction: Directions
    move: int

@dataclasses.dataclass
class CardType:
    move: bool
    turn: bool

@dataclasses.dataclass
class Field:
    effect: list #FieldEffect

@dataclasses.dataclass
class FieldEffect:
    field_type_effect: FieldTypeEffect
    power: int


@dataclasses.dataclass
class FieldTypeEffect:
    movement: int
    turn: TurnDirection
    damage: bool
    killing: bool
    flag: Flag
    starting_position_change: object
    wall: Wall

@dataclasses.dataclass
class Flag:
    ranking: int
    position: Position

@dataclasses.dataclass
class Position:
    x: int
    y: int

@dataclasses.dataclass
class Wall:
    ...
#need to be solved, issue created
