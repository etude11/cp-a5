# Assignment 5: Earley Parser

## Report
Found in [report.pdf](report.pdf).

## Parser usage
```sh
./parse.py foo.gr foo.sen            # output best parse tree
./parse.py -v foo.gr foo.sen         # verbose (shows weights, profile)
./parse.py --chart foo.gr foo.sen    # print the Earley chart
./parse.py -s S foo.gr foo.sen       # use S as start symbol instead of ROOT
```

## Key results
- Q1: Chart has 65 items across 6 columns, two valid parses found
- Q2: Tree 1 (adverbial: "time flies like an arrow") has P = 0.00448; Tree 2 (compound noun: "time-flies like an arrow") has P = 0.00096. Tree 1 is ~4.67x more likely
- Q3: NP-attachment parse ("soldier with a gun") has P = 0.000320 vs VP-attachment ("shot with a gun") P = 0.0000160. Parser correctly picks NP-attachment
- Q4: Correctness via weight/backpointer tracking in O(1) hash-based agenda; O(n^2) space, O(n^3) time
