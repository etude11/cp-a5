# Earley Parser Assignment Report

**GitHub Repository:** [https://github.com/etude11/cp-a5](https://github.com/etude11/cp-a5)

---

## Q1. Earley Chart for "time flies like an arrow" (20 marks)

### Grammar (from Figure 1)

| Rule | Probability |
|---|---|
| S -> NP VP | 1.0 |
| NP -> N N | 0.25 |
| NP -> D N | 0.4 |
| NP -> N | 0.35 |
| VP -> V NP | 0.6 |
| VP -> V ADVP | 0.4 |
| ADVP -> ADV NP | 1.0 |
| N -> time | 0.4 |
| N -> flies | 0.2 |
| N -> arrow | 0.4 |
| D -> an | 1.0 |
| ADV -> like | 1.0 |
| V -> flies | 0.5 |
| V -> like | 0.5 |

### Earley Chart (ignoring probabilities)

**Column 0** (before input):

| # | Item | Operation |
|---|---|---|
| 1 | (0, ROOT -> . S) | Seed |
| 2 | (0, S -> . NP VP) | Predict from 1 |
| 3 | (0, NP -> . N N) | Predict from 2 |
| 4 | (0, NP -> . D N) | Predict from 2 |
| 5 | (0, NP -> . N) | Predict from 2 |
| 6 | (0, N -> . time) | Predict from 3, 5 |
| 7 | (0, N -> . flies) | Predict from 3, 5 |
| 8 | (0, N -> . arrow) | Predict from 3, 5 |
| 9 | (0, D -> . an) | Predict from 4 |

**Column 1** (after "time"):

| # | Item | Operation |
|---|---|---|
| 10 | (0, N -> time .) | Scan 6 |
| 11 | (0, NP -> N . N) | Attach 10 to 3 |
| 12 | (0, NP -> N .) | Attach 10 to 5 |
| 13 | (1, N -> . time) | Predict from 11 |
| 14 | (1, N -> . flies) | Predict from 11 |
| 15 | (1, N -> . arrow) | Predict from 11 |
| 16 | (0, S -> NP . VP) | Attach 12 to 2 |
| 17 | (1, VP -> . V NP) | Predict from 16 |
| 18 | (1, VP -> . V ADVP) | Predict from 16 |
| 19 | (1, V -> . flies) | Predict from 17, 18 |
| 20 | (1, V -> . like) | Predict from 17, 18 |

**Column 2** (after "flies"):

| # | Item | Operation |
|---|---|---|
| 21 | (1, N -> flies .) | Scan 14 |
| 22 | (1, V -> flies .) | Scan 19 |
| 23 | (0, NP -> N N .) | Attach 21 to 11 |
| 24 | (1, VP -> V . NP) | Attach 22 to 17 |
| 25 | (1, VP -> V . ADVP) | Attach 22 to 18 |
| 26 | (0, S -> NP . VP) | Attach 23 to 2 |
| 27 | (2, NP -> . N N) | Predict from 24 |
| 28 | (2, NP -> . D N) | Predict from 24 |
| 29 | (2, NP -> . N) | Predict from 24 |
| 30 | (2, ADVP -> . ADV NP) | Predict from 25 |
| 31 | (2, VP -> . V NP) | Predict from 26 |
| 32 | (2, VP -> . V ADVP) | Predict from 26 |
| 33 | (2, N -> . time) | Predict from 27, 29 |
| 34 | (2, N -> . flies) | Predict from 27, 29 |
| 35 | (2, N -> . arrow) | Predict from 27, 29 |
| 36 | (2, D -> . an) | Predict from 28 |
| 37 | (2, ADV -> . like) | Predict from 30 |
| 38 | (2, V -> . flies) | Predict from 31, 32 |
| 39 | (2, V -> . like) | Predict from 31, 32 |

**Column 3** (after "like"):

| # | Item | Operation |
|---|---|---|
| 40 | (2, ADV -> like .) | Scan 37 |
| 41 | (2, V -> like .) | Scan 39 |
| 42 | (2, ADVP -> ADV . NP) | Attach 40 to 30 |
| 43 | (2, VP -> V . NP) | Attach 41 to 31 |
| 44 | (2, VP -> V . ADVP) | Attach 41 to 32 |
| 45 | (3, NP -> . N N) | Predict from 42, 43 |
| 46 | (3, NP -> . D N) | Predict from 42, 43 |
| 47 | (3, NP -> . N) | Predict from 42, 43 |
| 48 | (3, ADVP -> . ADV NP) | Predict from 44 |
| 49 | (3, N -> . time) | Predict from 45, 47 |
| 50 | (3, N -> . flies) | Predict from 45, 47 |
| 51 | (3, N -> . arrow) | Predict from 45, 47 |
| 52 | (3, D -> . an) | Predict from 46 |
| 53 | (3, ADV -> . like) | Predict from 48 |

**Column 4** (after "an"):

| # | Item | Operation |
|---|---|---|
| 54 | (3, D -> an .) | Scan 52 |
| 55 | (3, NP -> D . N) | Attach 54 to 46 |
| 56 | (4, N -> . time) | Predict from 55 |
| 57 | (4, N -> . flies) | Predict from 55 |
| 58 | (4, N -> . arrow) | Predict from 55 |

**Column 5** (after "arrow"):

| # | Item | Operation |
|---|---|---|
| 59 | (4, N -> arrow .) | Scan 58 |
| 60 | (3, NP -> D N .) | Attach 59 to 55 |
| 61 | (2, ADVP -> ADV NP .) | Attach 60 to 42 |
| 62 | (2, VP -> V NP .) | Attach 60 to 43 |
| 63 | (1, VP -> V ADVP .) | Attach 61 to 25 |
| 64 | (0, S -> NP VP .) | Attach 62 to 26 (Parse 2) / Attach 63 to 16 (Parse 1) |
| 65 | (0, ROOT -> S .) | Attach 64 to 1 |

The chart contains **65 items** across 6 columns (0-5). Two complete S items reach column 5, corresponding to two valid parses.

---

## Q2. Probability of Each Parse Tree (10 marks)

### Parse Tree 1: "Time flies like an arrow" (adverbial reading)

```
(S (NP (N time))
   (VP (V flies)
       (ADVP (ADV like)
             (NP (D an) (N arrow)))))
```

Meaning: *Time flies in the manner of an arrow.*

**Probability calculation:**

| Rule | Probability |
|---|---|
| ROOT -> S | 1.0 |
| S -> NP VP | 1.0 |
| NP -> N | 0.35 |
| N -> time | 0.4 |
| VP -> V ADVP | 0.4 |
| V -> flies | 0.5 |
| ADVP -> ADV NP | 1.0 |
| ADV -> like | 1.0 |
| NP -> D N | 0.4 |
| D -> an | 1.0 |
| N -> arrow | 0.4 |

**P(Tree 1) = 1.0 x 1.0 x 0.35 x 0.4 x 0.4 x 0.5 x 1.0 x 1.0 x 0.4 x 1.0 x 0.4 = 0.00448**

-log2(0.00448) = 7.80 bits

### Parse Tree 2: "Time-flies like an arrow" (compound noun reading)

```
(S (NP (N time) (N flies))
   (VP (V like)
       (NP (D an) (N arrow))))
```

Meaning: *Time-flies (a type of insect) like an arrow.*

**Probability calculation:**

| Rule | Probability |
|---|---|
| ROOT -> S | 1.0 |
| S -> NP VP | 1.0 |
| NP -> N N | 0.25 |
| N -> time | 0.4 |
| N -> flies | 0.2 |
| VP -> V NP | 0.6 |
| V -> like | 0.5 |
| NP -> D N | 0.4 |
| D -> an | 1.0 |
| N -> arrow | 0.4 |

**P(Tree 2) = 1.0 x 1.0 x 0.25 x 0.4 x 0.2 x 0.6 x 0.5 x 0.4 x 1.0 x 0.4 = 0.00096**

-log2(0.00096) = 10.02 bits

### Summary

| Parse | Probability | -log2(prob) | Best? |
|---|---|---|---|
| Tree 1 (adverbial) | 0.00448 | 7.80 | Yes |
| Tree 2 (compound noun) | 0.00096 | 10.02 | No |

**Tree 1 is ~4.67x more likely** than Tree 2. The parser correctly outputs Tree 1 as the best parse.

---

## Q3. Grammar for "the man shot the soldier with a gun" (10 marks)

### Designed Grammar

```
1       ROOT    S
1.0     S       NP VP
0.6     NP      Det N
0.4     NP      NP PP
0.8     VP      V NP
0.2     VP      VP PP
1.0     PP      P NP
0.5     Det     the
0.5     Det     a
0.34    N       man
0.33    N       soldier
0.33    N       gun
1.0     V       shot
1.0     P       with
```

This grammar produces two structurally ambiguous parses:

### Parse 1: NP attachment (the soldier who has a gun)

```
(S (NP (Det the) (N man))
   (VP (V shot)
       (NP (NP (Det the) (N soldier))
           (PP (P with)
               (NP (Det a) (N gun))))))
```

Meaning: *The man shot [the soldier who had a gun].*

**P = 1.0 x 0.6 x 0.5 x 0.34 x 0.8 x 1.0 x 0.4 x 0.6 x 0.5 x 0.33 x 1.0 x 1.0 x 0.6 x 0.5 x 0.33 = 0.000320**

### Parse 2: VP attachment (using a gun to shoot)

```
(S (NP (Det the) (N man))
   (VP (VP (V shot)
           (NP (Det the) (N soldier)))
       (PP (P with)
           (NP (Det a) (N gun)))))
```

Meaning: *The man shot the soldier [using a gun].*

**P = 1.0 x 0.6 x 0.5 x 0.34 x 0.2 x 0.8 x 1.0 x 0.6 x 0.5 x 0.33 x 1.0 x 1.0 x 0.6 x 0.5 x 0.33 = 0.0000800**

### Parser Output

The parser correctly selects **Parse 1 (NP attachment)** as the best parse, since P(Parse 1) = 0.000320 > P(Parse 2) = 0.0000800.

### Earley Chart

**Column 0** (before input):

| Item |
|---|
| (0, ROOT -> . S) |
| (0, S -> . NP VP) |
| (0, NP -> . Det N) |
| (0, NP -> . NP PP) |
| (0, Det -> . the) |
| (0, Det -> . a) |

**Column 1** (after "the"):

| Item |
|---|
| (0, Det -> the .) |
| (0, NP -> Det . N) |
| (1, N -> . man) |
| (1, N -> . soldier) |
| (1, N -> . gun) |

**Column 2** (after "man"):

| Item |
|---|
| (1, N -> man .) |
| (0, NP -> Det N .) |
| (0, S -> NP . VP) |
| (0, NP -> NP . PP) |
| (2, VP -> . V NP) |
| (2, VP -> . VP PP) |
| (2, PP -> . P NP) |
| (2, V -> . shot) |
| (2, P -> . with) |

**Column 3** (after "shot"):

| Item |
|---|
| (2, V -> shot .) |
| (2, VP -> V . NP) |
| (3, NP -> . Det N) |
| (3, NP -> . NP PP) |
| (3, Det -> . the) |
| (3, Det -> . a) |

**Column 4** (after "the"):

| Item |
|---|
| (3, Det -> the .) |
| (3, NP -> Det . N) |
| (4, N -> . man) |
| (4, N -> . soldier) |
| (4, N -> . gun) |

**Column 5** (after "soldier"):

| Item |
|---|
| (4, N -> soldier .) |
| (3, NP -> Det N .) |
| (2, VP -> V NP .) |
| (3, NP -> NP . PP) |
| (0, S -> NP VP .) |
| (2, VP -> VP . PP) |
| (5, PP -> . P NP) |
| (0, ROOT -> S .) |
| (5, P -> . with) |

**Column 6** (after "with"):

| Item |
|---|
| (5, P -> with .) |
| (5, PP -> P . NP) |
| (6, NP -> . Det N) |
| (6, NP -> . NP PP) |
| (6, Det -> . the) |
| (6, Det -> . a) |

**Column 7** (after "a"):

| Item |
|---|
| (6, Det -> a .) |
| (6, NP -> Det . N) |
| (7, N -> . man) |
| (7, N -> . soldier) |
| (7, N -> . gun) |

**Column 8** (after "gun"):

| Item |
|---|
| (7, N -> gun .) |
| (6, NP -> Det N .) |
| (5, PP -> P NP .) |
| (6, NP -> NP . PP) |
| (3, NP -> NP PP .) |
| (2, VP -> VP PP .) |
| (8, PP -> . P NP) |
| (2, VP -> V NP .) |
| (3, NP -> NP . PP) |
| (0, S -> NP VP .) |
| (2, VP -> VP . PP) |
| (8, P -> . with) |
| (0, ROOT -> S .) |

---

## Q4. Implementation Details (10 marks)

### Correctness: Tracking Best Derivations

Each Earley item is uniquely identified by its **(rule, dot_position, start_position)** tuple. The `Item` class is a frozen (immutable, hashable) dataclass using these three fields for equality and hashing.

For each item, the `Agenda` maintains:

- **`_weights` dict**: Maps each item to its best (lowest) weight so far.
  Weight = -log2(probability), so lower weight = higher probability.

- **`_backpointers` dict**: Maps each item to a backpointer tuple that
  records how the best derivation was constructed.

**Weight computation:**

- **Predict**: A new item `A -> . alpha` gets weight = -log2(P(A -> alpha | A)),
  the rule's own weight.

- **Scan**: Advancing the dot over a terminal preserves the weight (terminal
  matching costs nothing beyond the rule weight already paid at prediction).

- **Attach**: When a completed item `B` (weight w\_B) attaches to a customer
  `A -> alpha . B beta` (weight w\_A), the new item gets weight = w\_A + w\_B.
  This correctly accumulates the total -log2 probability of the subtree parsed so far.

**Handling duplicate derivations:** When `push()` encounters an item already in the agenda:

- If the new weight is **lower** (better probability): update the weight and backpointer.

- If the new weight is **higher or equal**: ignore (the existing derivation is at least as good).

This ensures each item always records its **current best derivation**.

**Tree reconstruction:** Backpointers form a chain from each completed item back through its constituents:

- For **scan** steps: backpointer = (previous\_item, previous\_column, terminal\_word)

- For **attach** steps: backpointer = (customer\_item, customer\_column,
  (completed\_item, completed\_column))

The `_build_tree()` method follows this chain to reconstruct the full parse tree in parenthesized notation.

### Efficiency: O(n^2) Space, O(n^3) Time

**O(n\textsuperscript{2}) space:**

- There are n+1 columns (one per word boundary).

- Each column contains at most O(n x |G|) items, where |G| is the grammar size
  (constant w.r.t. n). For a fixed grammar, each item in column k has a
  start\_position in \{0, 1, ..., k\}, giving O(n) possible start positions.
  Combined with O(|G|) possible (rule, dot\_position) pairs, each column has O(n) items.

- Total: (n+1) x O(n) = **O(n\textsuperscript{2})** items.

**O(1) push (including duplicate check):**

- The `Agenda` uses a Python dictionary (`_index`) mapping items to their
  position. Since `Item` is a frozen dataclass, it is hashable and supports
  O(1) dict lookup.

- Each `push()` call performs one dict lookup (`item in self._index`), which is
  O(1) amortized.

- This is necessary because each item may be pushed multiple times (from
  different attachments), and without O(1) duplicate checking, the algorithm
  could degrade to higher complexity.

**O(n\textsuperscript{3}) time:**

- **Predict**: For each column, prediction adds at most O(|G|) items (each
  nonterminal predicted at most once per column). Total: O(n x |G|) = O(n).

- **Scan**: Each item is scanned at most once, O(1) per scan. Total scans
  bounded by total items: O(n\textsuperscript{2}).

- **Attach**: This is the bottleneck. When a completed item in column k with
  start\_position j is processed, it iterates over all items ever pushed to
  column j. Column j has O(n) items. There are O(n) possible completed items
  per column (O(n) start positions x O(|G|) rules), across n+1 columns.
  Thus: O(n) columns x O(n) completed items per column x O(n) customers per
  attach = **O(n\textsuperscript{3})**.

The O(1) push is critical: without it, if push took O(n) time (e.g., linear
scan for duplicates), the total time would increase to O(n\textsuperscript{4}),
violating the required bound.
