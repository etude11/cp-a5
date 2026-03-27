#!/usr/bin/env python3
"""
Probabilistic Earley parser that reconstructs the highest-probability parse
of each given sentence under a PCFG.

Usage: ./parse.py foo.gr foo.sen
"""

from __future__ import annotations
import argparse
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
from typing import Counter as CounterType, Iterable, List, Optional, Dict, Tuple, Any

log = logging.getLogger(Path(__file__).stem)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "grammar", type=Path, help="Path to .gr file containing a PCFG"
    )
    parser.add_argument(
        "sentences", type=Path, help="Path to .sen file containing tokenized input sentences"
    )
    parser.add_argument(
        "-s", "--start_symbol", type=str, default="ROOT",
        help="Start symbol of the grammar (default: ROOT)"
    )
    parser.add_argument(
        "--progress", action="store_true", default=False,
        help="Display a progress bar"
    )
    parser.set_defaults(logging_level=logging.INFO)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", dest="logging_level",
        action="store_const", const=logging.DEBUG
    )
    verbosity.add_argument(
        "-q", "--quiet", dest="logging_level",
        action="store_const", const=logging.WARNING
    )
    parser.add_argument(
        "--chart", action="store_true", default=False,
        help="Print the Earley chart after parsing"
    )
    return parser.parse_args()


@dataclass(frozen=True)
class Rule:
    """A grammar rule with a left-hand side, right-hand side, and weight (-log2 prob)."""
    lhs: str
    rhs: Tuple[str, ...]
    weight: float = 0.0

    def __repr__(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs)}"


@dataclass(frozen=True)
class Item:
    """An Earley item: a dotted rule with a start position."""
    rule: Rule
    dot_position: int
    start_position: int

    def next_symbol(self) -> Optional[str]:
        if self.dot_position == len(self.rule.rhs):
            return None
        return self.rule.rhs[self.dot_position]

    def with_dot_advanced(self) -> Item:
        if self.next_symbol() is None:
            raise IndexError("Can't advance dot past end of rule")
        return Item(
            rule=self.rule,
            dot_position=self.dot_position + 1,
            start_position=self.start_position
        )

    def __repr__(self) -> str:
        DOT = "·"
        rhs = list(self.rule.rhs)
        rhs.insert(self.dot_position, DOT)
        return f"({self.start_position}, {self.rule.lhs} → {' '.join(rhs)})"


class Agenda:
    """An agenda of items with weights and backpointers for Viterbi parsing."""

    def __init__(self) -> None:
        self._items: List[Item] = []       # all items in push order
        self._index: Dict[Item, int] = {}  # item -> index in _items (for O(1) lookup)
        self._next: int = 0                # next item to pop
        self._weights: Dict[Item, float] = {}
        self._backpointers: Dict[Item, Any] = {}

    def __len__(self) -> int:
        return len(self._items) - self._next

    def push(self, item: Item, weight: float, backpointer: Any = None) -> None:
        """Add item, or update if a better weight is found (O(1) with dict lookup)."""
        if item in self._index:
            if weight < self._weights[item]:
                self._weights[item] = weight
                self._backpointers[item] = backpointer
        else:
            self._items.append(item)
            self._index[item] = len(self._items) - 1
            self._weights[item] = weight
            self._backpointers[item] = backpointer

    def pop(self) -> Item:
        if len(self) == 0:
            raise IndexError
        item = self._items[self._next]
        self._next += 1
        return item

    def all(self) -> Iterable[Item]:
        return self._items

    def get_weight(self, item: Item) -> float:
        return self._weights[item]

    def get_backpointer(self, item: Item) -> Any:
        return self._backpointers.get(item)

    def __repr__(self) -> str:
        n = self._next
        return f"Agenda({self._items[:n]}; {self._items[n:]})"


class Grammar:
    """A weighted context-free grammar."""

    def __init__(self, start_symbol: str, *files: Path) -> None:
        self.start_symbol = start_symbol
        self._expansions: Dict[str, List[Rule]] = {}
        for file in files:
            self.add_rules_from_file(file)

    def add_rules_from_file(self, file: Path) -> None:
        with open(file, "r") as f:
            for line in f:
                line = line.split("#")[0].rstrip()
                if line == "":
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                _prob, lhs, _rhs = parts[0], parts[1], parts[2]
                prob = float(_prob)
                rhs = tuple(_rhs.split())
                weight = -math.log2(prob) if prob > 0 else float('inf')
                rule = Rule(lhs=lhs, rhs=rhs, weight=weight)
                if lhs not in self._expansions:
                    self._expansions[lhs] = []
                self._expansions[lhs].append(rule)

    def expansions(self, lhs: str) -> Iterable[Rule]:
        return self._expansions.get(lhs, [])

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self._expansions


class EarleyChart:
    """Earley chart parser with Viterbi (best-parse) tracking."""

    def __init__(self, tokens: List[str], grammar: Grammar, progress: bool = False) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.progress = progress
        self.profile: CounterType[str] = Counter()
        self.cols: List[Agenda]
        self._run_earley()

    def accepted(self) -> bool:
        for item in self.cols[-1].all():
            if (item.rule.lhs == self.grammar.start_symbol
                    and item.next_symbol() is None
                    and item.start_position == 0):
                return True
        return False

    def get_best_parse(self) -> Optional[Tuple[float, str]]:
        """Return (weight, tree_string) for the best parse, or None."""
        best_item = None
        best_weight = float('inf')
        for item in self.cols[-1].all():
            if (item.rule.lhs == self.grammar.start_symbol
                    and item.next_symbol() is None
                    and item.start_position == 0):
                w = self.cols[-1].get_weight(item)
                if w < best_weight:
                    best_weight = w
                    best_item = item
        if best_item is None:
            return None
        tree = self._build_tree(best_item, len(self.tokens))
        return (best_weight, tree)

    def _build_tree(self, item: Item, col_idx: int) -> str:
        """Reconstruct parse tree by following backpointers from a completed item."""
        children = []
        cur_item = item
        cur_col = col_idx

        while cur_item.dot_position > 0:
            bp = self.cols[cur_col].get_backpointer(cur_item)
            if bp is None:
                break
            prev_item, prev_col, child_info = bp

            if isinstance(child_info, str):
                # SCAN: child_info is the scanned terminal word
                children.append(child_info)
            else:
                # ATTACH: child_info is (completed_item, col_of_completed_item)
                attached_item, attached_col = child_info
                children.append(self._build_tree(attached_item, attached_col))

            cur_item = prev_item
            cur_col = prev_col

        children.reverse()
        return "(" + item.rule.lhs + " " + " ".join(children) + ")"

    def _run_earley(self) -> None:
        """Run the Earley algorithm to fill the chart."""
        n = len(self.tokens)
        self.cols = [Agenda() for _ in range(n + 1)]

        # Seed with predictions for the start symbol
        self._predict(self.grammar.start_symbol, 0)

        for i in range(n + 1):
            log.debug("")
            log.debug(f"=== Processing column {i} ===")
            column = self.cols[i]
            while column:
                item = column.pop()
                next_sym = item.next_symbol()
                if next_sym is None:
                    # Completed item -> attach
                    log.debug(f"  {item} => ATTACH")
                    self._attach(item, i)
                elif self.grammar.is_nonterminal(next_sym):
                    # Next symbol is nonterminal -> predict
                    log.debug(f"  {item} => PREDICT")
                    self._predict(next_sym, i)
                else:
                    # Next symbol is terminal -> scan
                    log.debug(f"  {item} => SCAN")
                    self._scan(item, i)

    def _predict(self, nonterminal: str, position: int) -> None:
        """Predict all expansions of a nonterminal at this position."""
        for rule in self.grammar.expansions(nonterminal):
            new_item = Item(rule, dot_position=0, start_position=position)
            # Initial weight = rule weight (cost of choosing this production)
            self.cols[position].push(new_item, weight=rule.weight, backpointer=None)
            log.debug(f"    Predicted: {new_item} (w={rule.weight:.4f})")
            self.profile["PREDICT"] += 1

    def _scan(self, item: Item, position: int) -> None:
        """If the next terminal matches the input word, advance the dot."""
        if position < len(self.tokens) and self.tokens[position] == item.next_symbol():
            new_item = item.with_dot_advanced()
            weight = self.cols[position].get_weight(item)
            # Backpointer: (previous_item, previous_column, child_info)
            # For scan, child_info is the terminal word string
            bp = (item, position, self.tokens[position])
            self.cols[position + 1].push(new_item, weight=weight, backpointer=bp)
            log.debug(f"    Scanned: {new_item} in col {position+1} (w={weight:.4f})")
            self.profile["SCAN"] += 1

    def _attach(self, item: Item, position: int) -> None:
        """Attach a completed item to waiting customers in earlier columns."""
        mid = item.start_position
        completed_weight = self.cols[position].get_weight(item)

        for customer in self.cols[mid].all():
            if customer.next_symbol() == item.rule.lhs:
                new_item = customer.with_dot_advanced()
                customer_weight = self.cols[mid].get_weight(customer)
                new_weight = customer_weight + completed_weight
                # Backpointer: (customer, customer_column, (completed_item, completed_column))
                bp = (customer, mid, (item, position))
                self.cols[position].push(new_item, weight=new_weight, backpointer=bp)
                log.debug(f"    Attached: {new_item} in col {position} (w={new_weight:.4f})")
                self.profile["ATTACH"] += 1

    def print_chart(self) -> None:
        """Print the Earley chart (all columns and their items)."""
        for i, col in enumerate(self.cols):
            if i == 0:
                print(f"\n--- Column {i} (before input) ---")
            elif i <= len(self.tokens):
                print(f"\n--- Column {i} (after '{self.tokens[i-1]}') ---")
            else:
                print(f"\n--- Column {i} ---")
            for item in col.all():
                w = col.get_weight(item)
                print(f"  {item}  [w={w:.4f}]")


def main():
    args = parse_args()
    logging.basicConfig(level=args.logging_level)
    grammar = Grammar(args.start_symbol, args.grammar)

    with open(args.sentences) as f:
        for sentence in f.readlines():
            sentence = sentence.strip()
            if sentence != "":
                log.debug("=" * 70)
                log.debug(f"Parsing: {sentence}")
                chart = EarleyChart(sentence.split(), grammar, progress=args.progress)
                if args.chart:
                    chart.print_chart()
                result = chart.get_best_parse()
                if result is not None:
                    weight, tree = result
                    print(tree)
                    log.debug(f"Weight: {weight:.4f} (-log2 prob)")
                    log.debug(f"Prob:   {2**(-weight):.6f}")
                else:
                    print("NONE")
                log.debug(f"Profile: {chart.profile}")


if __name__ == "__main__":
    main()
