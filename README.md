
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

Encoding the state of the puzzle
--------------------------------

Each piece is described by the colors on its sides: either 2 or 3 colors.
Starting at the top (bottom), read the colors off clockwise.  So 'wrg' means
'white red green'.

Starting from e.g. the front left top, follow the pieces around clockwise.
Once you've encoded all the top pieces, start from the same corner on the bottom
and encode the pieces clockwise (but counter-clockwise as viewed from underneath).

The puzzle need not be in a square shape to encode it.

Applying the Solution
---------------------

    ...
    solved it.
    [wg yog wb wbr yr ybo yb ygr ] [wrg yg wob wr yrb yo wgo wo ]
     wr | wbr	[wrg wg yog wb wbr wr wob yg ] [wgo wo ygr yb ybo yr yrb yo ]
    wgo |  wr	[wgo yo yrb yr yog wb wbr wr ] [wrg yg wob wo ygr yb ybo wg ]
     yb | wgo	[wgo yb ygr wo wob wb wbr wr ] [wrg yg yog yr yrb yo ybo wg ]
    ...


Each step in the solution is performed as follows: The two pieces described,
are on the bottom and top respectively, and you will bring the bottom piece
[on the right] to match up with the top piece [on the left], so they are next
to each other in the back.

        o x o     o x y
      o o o     o o o
    o o o     o o o
    o o o     o o o
    o o y     o o o

In the example solution above, you would place 'wr' (white red) to the right
of the flip line on the bottom front, and 'wbr' (white blue red) to the left of the
dividing line on the top back.

          --- wbr ---
       --- --- ---
    --- --- wr

Then turn the right side clockwise to bring the two
pieces together:

          --- wbr wr
       --- --- ---
    --- --- ---

