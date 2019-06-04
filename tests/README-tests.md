`commands.yaml` file structure (read by _test_effects.py_)

```
actions:
   -
     - card type: move, rotate
       priority: integer
       value: for move types: -1, 1, 2, 3;
              for rotate types: -90, 90, 180

prerequisites:
  -
     attribute: value
     attribute: value
     attribute: value
  -
     attribute: value

results:
   -
     attribute: value
     attribute: value
     attribute: value
   -
     attribute: value
```

Possible _attributes_:

 - damages: 0-9
 - flags: 0-8
 - lives: 0-3
 - power_down: boolean
 - start: [0, 0] (use only for _results_)



## How to add new tests

1) Create new folder in `tests/`, name starting with `test_`.
  The rest of the name should indicate what is tested.
2) Prepare map in Tiled (at least 1.2) with tiles from `maps/development_tileset.json`. Save it to the folder as `map.json`
  - map must contain start fields (yellow ones) and stop fields (red ones) in order to create the robots correctly. They can be in the same place if the robots don't move. Use more map layers to ensure visibility of all pieces.
3) Add `commands.yaml` to the folder. Make sure it contains all the actions, prerequisites and results you want to check.
  - if you add `actions` to file, make sure there are actions for every robot on the board (5 robots = 5 x actions).
  - each robot must have the same number of actions _on hand_.
  - if you don't test eg. the change of damages, there is no need to add damages to `prerequisites` or `results` part of file.
  - Note: if you only want to check the coordinates and direction of the robots at the end of the play, there is no need to create `commands.yaml`. Those attributes are compared to properties of the stop tiles.
