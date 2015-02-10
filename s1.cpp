// -*- Mode: C++ -*-

#include <set>
#include <algorithm>
#include <map>
#include <utility>
#include <vector>
#include <list>
#include <tuple>
#include <queue>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include "cons.h"

typedef uint64_t state_t;
typedef std::vector<uint8_t> ring_t;
typedef std::pair<uint8_t, uint8_t> move_t;
typedef std::list<move_t> move_list_t;
typedef ConsList<state_t> path_t;
typedef std::map<state_t, path_t> path_map_t;
typedef std::tuple<uint16_t, path_t, state_t> item_t;
// stl does *largest* value, not smallest.
typedef std::priority_queue<item_t, std::vector<item_t>, std::greater<item_t>> open_t;
typedef std::set<state_t> state_set_t;

// notation: each piece is described by the colors on its surface in clockwise manner.
// so 'wrg' == white red green.
// 'yb' == 'yellow blue'
// the ordering of pieces along the cube:
// along the top (white side) starting at white-red-green, go clockwise around the top.
// immediately below white-red-green, count the yellow side *counter-clockwise* (so that
// each piece corresponds to the piece above it).
// If you're confused, look at the maps below, they describe the solved position.

// the representation of a state fits into a uint64_t, 4 bits per piece, 16 pieces.
// they are counted from piece 0 (wrg) as the least significant 4 bits.  the last piece
// is the most significant.

state_t solved = 0xfedcba9876543210; // solved position

std::map<const std::string, int> name_fmap = {
  {"wrg", 0}, {"wg",  1}, {"wgo", 2}, {"wo",  3}, {"wob", 4}, {"wb",  5}, {"wbr", 6}, {"wr",  7}, 
  {"ygr", 8}, {"yg",  9}, {"yog",10}, {"yo", 11}, {"ybo",12}, {"yb", 13}, {"yrb",14}, {"yr", 15}
};

std::map<int, const std::string> name_rmap = {
  {0, "wrg"}, {1, "wg"}, {2, "wgo"}, {3, "wo"}, {4, "wob"}, {5, "wb"}, {6, "wbr"}, {7, "wr"}, 
  {8, "ygr"}, {9, "yg"}, {10, "yog"}, {11, "yo"}, {12, "ybo"}, {13, "yb"}, {14, "yrb"}, {15, "yr"}
};

// map from piece to 'next' piece (in the solved state).
// to solve for arbitrary positions this would need to be
// computed from the goal state.
int next[] = {1,2,3,4,5,6,7,0,9,10,11,12,13,14,15,8};

#include <string>
#include <iostream>
#include <sstream>
#include <iterator>

state_t
names_to_state (char * state)
{
  using namespace std;
  state_t r = 0;
  istringstream iss(state);
  vector<string> tokens {istream_iterator<string>{iss}, istream_iterator<string>{}};
  for (auto i = tokens.rbegin(); i < tokens.rend(); i++) {
    int p = name_fmap[*i];
    r <<= 4;
    r |= p;
  }
  return r;
}

static
uint8_t
piece_width (uint8_t p)
{
  return (p % 2 == 0) ? 2 : 1;
}

void
valid_moves_1 (ring_t ring, move_list_t & moves)
{
  uint8_t lr = ring.size();
  for (int i=0; i < lr; i++) {
    unsigned int wsum = 0;
    unsigned int j = i + 1;
    unsigned int n = 0;
    while (wsum < 6) {
      uint8_t p = ring[j%lr];
      wsum += piece_width (p);
      n += 1;
      j += 1;
    } 
    if (wsum == 6) {
      moves.push_back (move_t (i, n));
    }
  }
}

void
state_2_rings (state_t s, ring_t & top, ring_t & bottom)
{
  uint8_t wsum = 0;
  top.clear();
  bottom.clear();
  for (int i=0; i < 16; i++) {
    // pull the bottom 4 bits off.
    uint8_t p = s & 0xf;
    s >>= 4;
    wsum += piece_width (p);
    if (wsum > 12) {
      bottom.push_back (p);
    } else {
      top.push_back (p);
    }
  }
}

state_t
rings_2_state (ring_t & top, ring_t & bottom)
{
  state_t r = 0;
  for (int i=bottom.size()-1; i >= 0; i--) {
    uint8_t p = bottom[i];
    r <<= 4;
    r |= p;
  }
  for (int i=top.size()-1; i >= 0; i--) {
    uint8_t p = top[i];
    r <<= 4;
    r |= p;
  }
  return r;
}

// the canonical rotation of a state is the one with its lowest
//  piece first.
void
canonicalize (ring_t & r)
{
  // find the minimum value
  uint8_t mi = 0;
  for (unsigned int i=0; i < r.size(); i++) {
    if (r[i] <= r[mi]) {
      mi = i;
    }
  }
  rotate (r.begin(), r.begin() + mi, r.end());
}

void
print_ring (ring_t & r)
{
  fprintf (stderr, "[");
  for (int i=0; i < r.size(); i++) {
    fprintf (stderr, "%d ", r[i]);
  }
  fprintf (stderr, "]");
}

void
print_rings (ring_t & t, ring_t & b)
{
  print_ring (t);
  fprintf (stderr, " ");
  print_ring (b);
  fprintf (stderr, "\n");
}

void
pprint_ring (ring_t & r)
{
  fprintf (stderr, "[");
  for (int i=0; i < r.size(); i++) {
    fprintf (stderr, "%s ", name_rmap[r[i]].c_str());
  }
  fprintf (stderr, "]");
}

void
pprint_rings (ring_t & t, ring_t & b)
{
  pprint_ring (t);
  fprintf (stderr, " ");
  pprint_ring (b);
  fprintf (stderr, "\n");
}

uint16_t
score_position_1 (ring_t & r, ring_t & target)
{
  uint16_t score = 0;
  for (int i=0; i < std::min (r.size(),target.size()); i++) {
    score += (r[i] == target[i]);
  }
  return score;
}

ring_t solved_top;
ring_t solved_bottom;

uint16_t
score_position (ring_t & st, ring_t & sb)
{
  uint16_t ts=0, tb=0;
  ring_t r0 = st;
  for (int i=0; i < st.size(); i++) {
    uint16_t si = score_position_1 (r0, solved_top);
    ts = std::max (ts, si);
  }
  r0 = sb;
  for (int i=0; i < sb.size(); i++) {
    uint16_t si = score_position_1 (r0, solved_bottom);
    tb = std::max (tb, si);
  }
  return 16 - (ts + tb);
}

uint16_t
score_pairs (ring_t & st, ring_t & sb)
{
  uint16_t s = 0;
  for (int i=0; i < st.size(); i++) {
    uint8_t p = st[i];
    if ((piece_width(p) == 2) && (st[(i+1)%st.size()] == next[p])) {
      s += 1;
    }
  }
  for (int i=0; i < sb.size(); i++) {
    uint8_t p = sb[i];
    if ((piece_width(p) == 1) && (next[st[(i-1)%st.size()]] == p)) {
      s += 1;
    }
  }
  return 8 - s;
}

uint16_t
score_state (ring_t & st, ring_t & sb)
{
  return score_position (st, sb) + score_pairs (st, sb);
}

void
perform_move (ring_t & st, ring_t & sb, move_t & mi, move_t & mj)
{
  // Note: this is more complicated than you might think,
  //   because we don't always exchange the same number of
  //   pieces - i.e., we might swap 3 on the top with 5 on
  //   the bottom.
  //
  // [01234567] [89abcdef]
  // 3,4        1,3
  // [34567012] [9abcdef8]  rotate
  //  ----       ---        slice width
  // [ba97012] [6543cdef8]  swap/reverse
  //
  rotate (st.begin(), st.begin() + mi.first + 1, st.end());
  rotate (sb.begin(), sb.begin() + mj.first + 1, sb.end());
  // append them in reverse order
  for (int i=mi.second-1; i >= 0; i--) {
    sb.push_back (st[i]);
  }
  for (int j=mj.second-1; j >= 0; j--) {
    st.push_back (sb[j]);
  }
  // [34567012ba97] [9abcdef86543]
  // erase from the front of each
  sb.erase (sb.begin(), sb.begin() + mj.second);
  st.erase (st.begin(), st.begin() + mi.second);
  canonicalize (st);
  canonicalize (sb);	  
}

// A* search: still missing optimizations like replacing paths.

void
search (state_t start)
{
  ring_t st, sb;
  uint16_t best = 0xffff;
  state_2_rings (start, st, sb);
  canonicalize (st);
  canonicalize (sb);
  // canonicalize the input state
  start = rings_2_state (st, sb);
  fprintf (stderr, "after canonicalization:\n");
  print_rings (st, sb);
  uint16_t score = score_state (st, sb);
  open_t open;
  state_set_t closed;
  state_set_t open_set;
  open.push (item_t (score, cons(start), start));
  open_set.insert (start);
  uint64_t counter = 0;
  while (!open.empty()) {
    item_t item = open.top(); open.pop();
    state_t key = std::get<2>(item);
    if (counter++ % 10000 == 0) {
      fprintf (stderr, "score:%d |closed|=%ld |open|=%ld\n", std::get<0>(item), closed.size(), open_set.size());
    }
    //fprintf (stderr, "(%d)", std::get<0>(item));
    open_set.erase (key);
    //fprintf (stderr, "score: %d ", std::get<0>(item));
    //fprintf (stderr, "state: %" PRIx64 "\n", key);
    if (key == solved) {
      fprintf (stderr, "solved it.\n");
      auto path = std::get<1>(item);
      while (!isEmpty(path)) {
	state_2_rings (car(path), st, sb);
	pprint_rings (st, sb);
	path = cdr (path);
      }
      return;
    } else {
      closed.insert (key);
      st.clear();
      sb.clear();
      state_2_rings (key, st, sb);
      move_list_t mt;
      move_list_t mb;
      //fprintf (stderr, "valid_moves_1:\n");
      //print_rings (st, sb);
      valid_moves_1 (st, mt);
      valid_moves_1 (sb, mb);
      //fprintf (stderr, "moves:\n");
      for (move_list_t::iterator i = mt.begin(); i != mt.end(); i++) {
	for (move_list_t::iterator j = mb.begin(); j != mb.end(); j++) {
	  ring_t st0 = st;
	  ring_t sb0 = sb;
	  perform_move (st0, sb0, *i, *j);
	  // g(x) is the length of the path to here
	  auto path = std::get<1>(item);
	  unsigned int g = len(path);
	  uint16_t h0 = score_state (st0, sb0);
	  uint16_t h = h0 * 4;
	  uint16_t f = g + h;
	  state_t state0 = rings_2_state (st0, sb0);
	  if (h0 < best) {
	    best = h0;
	    fprintf (stderr, "g:%d h0:%d h:%d f:%d |closed|=%ld |open|=%ld\n", g, h0, h, f, closed.size(), open_set.size());
	  }
	  auto probe0 = open_set.find (state0);
	  if (probe0 == open_set.end()) {
	    // not in open
	    auto probe1 = closed.find (state0);
	    if (probe1 == closed.end()) {
	      //fprintf (stderr, "/%d/", f);
	      open.push (item_t (f, cons(state0, path), state0));
	      open_set.insert (state0);
	    }
	  }
	}
      }
    }
  }
}

int
main (int argc, char * argv[])
{
  state_t s0 = 0xcfa967e3d854b210;
  ring_t top;
  ring_t bottom;
  if (argc > 1) {
    s0 = names_to_state (argv[1]);
    fprintf (stderr, "arg: %" PRIx64 "\n", s0);
  }
  state_2_rings (solved, solved_top, solved_bottom);
  state_2_rings (s0, top, bottom);
  canonicalize (top);
  canonicalize (bottom);
  print_rings (top, bottom);
  pprint_rings (top, bottom);
  fprintf (stderr, "%" PRIx64 "\n", rings_2_state (top, bottom));
  fprintf (stderr, "score(solved) = %d\n", score_state (solved_top, solved_bottom));
  fprintf (stderr, "score(sample) = %d\n", score_state (top, bottom));
  search (s0);
}
