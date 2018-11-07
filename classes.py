import enum
import dataclasses

@dataclasses.dataclass
class Robot:
    damage_count: int
    life_count: int
    robot_direction: <Direction>
    is_active: bool
    field: <Position>
    flags_count: int
    robot_type: <Robot_type>
    initial_pozition: <Position>
    program: <Program>
    
    
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
                

def perform_card_effect(self, game_state, card_effect):
    if ...:
        be_moved(self, game_state, move_direction, distance)
        return game_state  
    elif ...:
        be turned(self, game_state, turn_direction):
        return game_state  
    
def perform_field_effect(self, game_state, field_effect):
    if ...:
        be_moved(self, game_state, move_direction, distance)
        return game_state   
    elif ...:
        be_turned(self, game_state, turn_direction):
        return game_state  
    elif...:
        be_killed(self, game_state)     
        return game_state  
    elif ...:
        be_damaged(self, game_state)     
        return game_state      
    
