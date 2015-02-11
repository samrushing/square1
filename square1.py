# -*- Mode: Python -*-

# fresh look at square-1 since I bought another one.

# the shape of the puzzle can be changed radically.
# but it consists of basically two 'rings' of pieces,
# separated by a middle piece that has two trival states.
#
# In the rings are two sizes of pieces.  Think of them
#   as being either one unit or two units.
# A possible configuration can have a total of 12 units,
#   and it appears all configs can be found (for example,
#   I have put all the small ones on top plus two large,
#   with 6 large on the bottom).

# note: all moves are possible when in the cube shape.

# with this info, can we easily detect the list of possible
#  moves and begin searching?

# There's only one kind of move, the flip.
# the two rings must match up in a particular way...
# there must be 6 units on the left, and 6 units on the right.
# this must be true of the top and the bottom, they line up,
# and a flip is made.

# heh, maybe the middle is not as trivial as I thought.
# it seems to be flippable.

# given that there are N possible moves on the top, coupled
#  with M possible moves on the bottom, we get MxN possible
#  moves, ignoring symmetry.

# let's number the pieces 0-15, 0-F in hex.
# so the solved configuration is simply:
solved = [0,1,2,3,4,5,6,7], [8,9,10,11,12,13,14,15]

# piece 0 is on top (white), the white green red corner.
# following clockwise from there,

names = [
  'wrg',  # 0
  'wg',	  # 1
  'wgo',  # 2
  'wo',	  # 3 
  'wob',  # 4 
  'wb',	  # 5 
  'wbr',  # 6 
  'wr',	  # 7 
  'ygr',  # 8 
  'yg',	  # 9 
  'yog',  # a 
  'yo',	  # b 
  'ybo',  # c 
  'yb',   # d 
  'yrb',  # e 
  'yr',   # F
]

next = [1,2,3,4,5,6,7,0,9,10,11,12,13,14,15,8]

# the widths of each of the pieces. i.e., wrg == 0 and is 2 wide.
wmap = [2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,]

rmap = {names[i]:i for i in range (16)}

import sys
W = sys.stderr.write

def weights (t, b):
    wt = sum (wmap[i] for i in t)
    wb = sum (wmap[i] for i in b)
    return wt, wb

def valid_state_check (t, b):
    assert (len(t) + len(b)) == 16
    x = [False] * 16
    for p in t:
        x[p] = True
    for p in b:
        x[p] = True
    if all(x):
        wt, wb = weights (t, b)
        assert wt==12 and wb==12
    else:
        assert False

def name_to_num (s):
    return [rmap[x] for x in s]

def num_to_name (s):
    return repr(' '.join ([names[i] for i in s]))

def valid_moves_1 (ring):
    # find all valid turns on this ring
    moves = []
    lr = len(ring)
    for i in range (lr):
        # from the right side of the piece, we have a line
        #  only if we get '6' as the sum of the next few pieces.
        #  we can stop once we hit 7 or higher.
        wsum = 0
        j = i + 1
        n = 0
        while wsum < 6:
            p = ring[j%lr]
            wsum += wmap[p]
            n += 1
            j += 1
        if wsum == 6:
            moves.append ((i, n))
    return moves

def valid_moves (t, b):
    mt = valid_moves_1 (t)
    mb = valid_moves_1 (b)
    for i,ip in mt:
        for j,jp in mb:
            yield ((i,ip),(j,jp))

def rotary_slice (s, start, n):
    r = []
    for i in range (n):
        r.append (s[start % len(s)])
        start += 1
    return r

def reverse_rotary_slice (s, start, n):
    r = []
    for i in range (n):
        r.insert (0, s[start % len(s)])
        start += 1
    return r

def rotary_replace (s, start, items):
    ls = len(s)
    for i in range (len(items)):
        s[(start + i) % ls] = items[i]

def rotate (s, n):
    if n == 0:
        return s
    else:
        s0 = [None]*len(s)
        ls = len(s)
        for i in range (ls):
            s0[i] = s[(i+n)%ls]
        return s0

N = num_to_name

def perform_move (st, sb, (mt, mb)):
    # perform a turn from state <s>
    #  with the top line at position i
    #  and the bottom line at position j
    i, ni = mt
    ip = reverse_rotary_slice (st, i+1, ni)
    j, nj = mb
    jp = reverse_rotary_slice (sb, j+1, nj)
    st0 = rotate (st, i+1)
    sb0 = rotate (sb, j+1)
    st0 = jp + st0[ni:]
    sb0 = ip + sb0[nj:]
    return canon(st0), canon(sb0)

def canon (ring):
    mp = min(ring)
    mi = ring.index(mp)
    return tuple (rotate (ring, mi))

def score_consecutive_1 (ring):
    # let's try measuring how 'consecutive' it is?
    s = 0
    lr = len(ring)
    for i in range (lr):
        s += ring[(i+1)%lr] == next[ring[i]]
    return s

# consecutive pieces score - counts the longest sequence of correctly ordered pieces.
# maximum value: 16 minimum value: 0
def score_consecutive (st, sb):
    return score_consecutive_1 (st) + score_consecutive_1 (sb)

def score_position_1 (s, target):
    ls =len(s)
    score = 0
    for i in range(min(ls,len(target))):
        score += s[i] == target[i]
    return score

# exact position score - how many pieces are in place (with rotations).
# maximum value: 16 minimum value: 0
def score_position (st, sb):
    ts = 0
    for i in range(len(st)):
        ts = max (ts, score_position_1 (rotate (st, i), solved[0]))
    tb = 0
    for i in range(len(st)):
        tb = max (tb, score_position_1 (rotate (sb, i), solved[1]))
    return ts + tb

def score_pairs_1 (ring):
    s = 0
    lr = len(ring)
    for i in range (lr):
        p = ring[i]
        if wmap[p] == 2 and ring[(i+1)%lr] == next[p]:
            s += 1
    return s

def score_pairs_2 (ring):
    s = 0
    lr = len(ring)
    for i in range (lr):
        p = ring[i]
        if wmap[p] == 1 and next[ring[(i-1)%lr]] == p:
            s += 1
    return s

def score_pairs (st, sb):
    return score_pairs_1 (st) + score_pairs_2 (sb)

class Searcher:

    def __init__ (self, limit):
        self.best = 0
        self.best_len = 0
        self.seen = set()
        self.moves = []
        self.limit = limit

    def score (self, st, sb):
        #return score_consecutive (st, sb) + score_position (st, sb)
        return score_position (st, sb)

    def check (self, score, st, sb, history):
        if score > self.best or (score == self.best and len(history) < self.best_len):
            self.best = score
            self.best_len = len(history)
            print
            print score, N(st), N(sb)
            for mt, mb, move in history:
                print N(mt), N(mb), move


    def search (self, st, sb, history):
        moves = []
        for move in valid_moves (st, sb):
            st0, sb0 = perform_move (st, sb, move)
            score = self.score (st0, sb0)
            moves.append ((score, move, st0, sb0))
        moves.sort()
        moves.reverse()
        #for move in moves:
        #    print move
        if len(history) < self.limit:
            for score, move, st0, sb0 in moves:
                #key = canon(st0), canon(sb0)
                key = st0, sb0
                if key not in self.seen:
                    self.seen.add (key)
                    #print 'about to try', score, N(st0), N(sb0)
                    #raw_input()
                    self.search (st0, sb0, history + [(st0, sb0, move)])
                    self.check (score, st0, sb0, history)

import heapq

class GBFS:

    def __init__ (self):
        self.closed = set()
        self.open_q = []
        self.open_m = {}
        self.history = []
        
    def put (self, key, item):
        heapq.heappush (self.open_q, item)
        self.open_m[key] = item
        
    def get (self):
        item = heapq.heappop (self.open_q)
        (score, move, st, sb) = item
        key = st, sb
        del self.open_m[key]
        return item

    def length (self, moves):
        n = 0
        while moves is not None:
            n += 1
            _, moves = moves
        return n

    def print_moves (self, moves):
        ml = []
        while moves is not None:
            x, moves = moves
            ml.append (x)
        ml.reverse()
        for st, sb in ml:
            print N(st), N(sb)
        return len(ml)

    def score (self, st, sb):
        return max(score_consecutive (st, sb),score_position (st, sb))

    def search (self, st, sb):
        #item = (-self.score(st, sb), None, st, sb)
        item = (0, None, st, sb)
        key = st, sb
        self.put (key, item)
        best = 0
        best_path = 10000
        i = 0
        while self.open_q:
            i += 1
            score, move0, st, sb = self.get()
            #if i % 1000 == 0:
            #    print score, best, self.length (move0)
            #W ('%d ' % (score,))
            if score <= best:
                flag = False
                if score == best:
                    plen = self.length (move0)
                    if plen < best_path:
                        print 'best_path', best_path, 'plen', plen
                        best_path = plen
                        flag = True
                else:
                    best = score
                    best_path = self.length (move0)
                    flag = True
                if flag:
                    print
                    print self.score(st,sb), N(st), N(sb)
                    self.print_moves (move0)
            if key == solved:
                return
            else:
                self.closed.add (key)
                for move1 in valid_moves (st, sb):
                    st0, sb0 = perform_move (st, sb, move1)
                    key = st0, sb0
                    if key not in self.closed:
                        probe = self.open_m.get (key, None)
                        path = ((st0,sb0), move0)
                        if probe is None:
                            lp = self.length(path)
                            score = self.score (st0, sb0) - lp
                            #score = score_consecutive (st0, sb0)
                            #score = score_position (st0, sb0)
                            #import pdb; pdb.set_trace()
                            item = [-score, path, st0, sb0]
                            self.put (key, item)
                        else:
                            olen = self.length (probe[1])
                            if self.length (path) < olen:
                                probe[1] = path
                                if probe[0] == best:
                                    print 'better path for best', probe[0]
                                    self.print_moves (path)

# A*
# f(x) := g(x) + h(x)
# g := length of solution so far
# h := distance from x to the goal (related to inverse of score)
#
# h is just an estimate - do be accurate we would need to know the average
#   number of moves to increase the score by one unit.  [we could measure that?]

import heapq

class AStar:

    def __init__ (self):
        self.open_q = []
        self.open_m = {}
        self.closed = {}
        self.history = []
        
    def put (self, key, item):
        heapq.heappush (self.open_q, item)
        self.open_m[key] = item
        
    def get (self):
        while 1:
            item = heapq.heappop (self.open_q)
            (score, move, st, sb) = item
            key = st, sb
            try:
                del self.open_m[key]
                return item
            except KeyError:
                # this node was replaced, pretend it doesn't exist.
                pass

    def length (self, moves):
        n = 0
        while moves is not None:
            n += 1
            _, moves = moves
        return n

    def print_moves (self, moves):
        ml = []
        while moves is not None:
            x, moves = moves
            ml.append (x)
        ml.reverse()
        for st, sb in ml:
            print N(st), N(sb)
        return len(ml)

    def score (self, st, sb):
        s0 = 16 - score_position (st, sb)
        #s1 = 16 - score_consecutive (st, sb)
        s1 = 8 - score_pairs (st, sb)
        return s0 + s1

    def sample_h_factor (self, moves):
        ml = []
        while moves is not None:
            x, moves = moves
            ml.append (x)
        ml.reverse()
        scores = []
        # ignore starting state, often 
        for st, sb in ml[1:]:
            s = self.score (st, sb)
            scores.append (s)
        min_s = min(scores)
        max_s = max(scores)
        print scores

    def search (self, st, sb):
        st, sb = canon(st), canon(sb)
        print 0, self.score(st,sb), N(st), N(sb)
        key = st, sb
        item = (self.score (st, sb), ((st, sb), None), st, sb)
        self.put (key, item)
        best = 10000
        best_path = 10000
        i = 0
        while self.open_q:
            score, move0, st, sb = item = self.get()
            key = st, sb
            if i % 1000 == 0:
                print '-', score, self.score(st,sb), self.length(move0), N(st), N(sb)
                if i > 0:
                    self.sample_h_factor(move0)
            i += 1
            #print score, N(st), N(sb)
            #raw_input()
            if key == solved:
                return
            else:
                self.closed[key] = item
                for move1 in valid_moves (st, sb):
                    st0, sb0 = perform_move (st, sb, move1)
                    key0 = st0, sb0
                    path = ((st0, sb0), move0)
                    # f(x) := g(x) + h(x)
                    # g(x) is the length of the path to here
                    g = self.length(path)
                    # let's say we need at least 5 moves per unit of score?
                    h0 = self.score (st0, sb0)
                    if h0 < best:
                        best = h0
                        best_path = g
                        print
                        print h0, N(st0), N(sb0)
                        self.print_moves (path)
                        print
                    h = h0 * 4
                    f = g + h
                    probe0 = self.open_m.get (key0, None)
                    if probe0 is not None and probe0[0] < f:
                        # no better, skip
                        pass
                    else:
                        probe1 = self.closed.get (key0, None)
                        if probe1 is not None and probe1[0] < f:
                            # no better, skip
                            pass
                        else:
                            item = [f, path, st0, sb0]
                            self.put (key0, item)

def t1(st, sb):
    global best
    print N(st), N(sb)
    print 'score', score_position (st, sb)
    print 'hit enter:',
    raw_input()
    valid_state_check (st, sb)
    s = Searcher (70)
    s.search (st, sb, [])

def t2 (st, sb):
    global best
    print N(st), N(sb)
    print 'score', score_position (st, sb)
    print 'hit enter:',
    raw_input()
    valid_state_check (st, sb)
    s = GBFS()
    s.search (st, sb)

def t3 (st, sb):
    global best
    print N(st), N(sb)
    print 'score', score_position (st, sb)
    print 'hit enter:',
    raw_input()
    valid_state_check (st, sb)
    s = AStar()
    s.search (st, sb)

def parse_config (s):
    parts = s.split()
    st = []
    sb = []
    wsum = 0
    for part in parts:
        part = rmap[part]
        wsum += wmap[part]
        if wsum > 12:
            sb.append (part)
        else:
            st.append (part)
    return st, sb

if __name__ == '__main__':
    if len(sys.argv) < 2:
        s = "wb wob wbr wr wrg wg wgo wo yog yo ybo yb yrb yr ygr yg"
    else:
        s = sys.argv[1]
    t3 (*parse_config (s))
