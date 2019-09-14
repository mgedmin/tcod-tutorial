What's this?
============

I'm amusing myself by following the [TCOD Roguelike
Tutorial](http://rogueliketutorials.com/tutorials/tcod/).

This is not my code: I'm reimplementing what I see on the tutorial pages, with
some changes due to personal preferences:

- I've added a setup.py and a Makefile so I can `make run` and not worry about
  installing tcod
- I'm not using subpackages for organizing files because that would make my
  setup.py a little bit more annoying
- (maybe I'll move all the code into one package someday)
- math.hypot() is nice but nobody knows about it!
- why int(x/2) if you can x // 2?
- operator.attrgetter() instead of a lambda
- some other minor changes where I though I had a better idea
