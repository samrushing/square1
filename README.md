
Square-1 Puzzle Solver
======================

First I wrote the python version, but it was unable to fix a
nearly-solved cube with two corners
swapped. [turns out this is a Known Problem with this puzzle - a "Parity" issue].

Quickly wrote the C++ one to see if I could fix it with less than 20G of memory.
It eventually solved it around 3M states ~4G of RAM.

I've since noticed that if it gets stuck in this mode, just scramble
the thing and it will usually solve it in a few seconds.

Methods
-------

The Python code has a few different searchers, depth-first, GBFS, and finally an A*.

The C++ implements the A* searcher, but I never bothered with path replacement.


Building & Running
------------------

Both programs accept a configuration on the command line:

```
$ clang++ -std=c++11 s1.cpp -O3 -o s1
$ ./s1 "wrg wg wgo yo wob wb ygr yb wo yrb wr wbr yg yog yr ybo"
```

```
$ python square1.py "wrg wg wgo yo wob wb ygr yb wo yrb wr wbr yg yog yr ybo"
```
