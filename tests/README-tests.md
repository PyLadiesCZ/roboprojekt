Commands file structure (read by _test_effects.py_)

```
actions:
   -
     - card type: move, rotate
       priority: integer
       value: for move types: -1, 1, 2, 3;
              for rotate types: -90, 90, 180

prerequizites:
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
```
