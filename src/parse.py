from __future__ import annotations

import argparse
import logging
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Counter as CounterType, Dict, Iterable, List, Optional, Tuple

log = logging.getLogger(Path(__file__).stem)

Rule = Tuple[str, Tuple[str, ...], float]
State = Tuple[int, int, int]
Trace = Tuple[Any, ...]
Column = Dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probabilistic Earley parser that reconstructs the highest-probability parse of each sentence under a PCFG."
    )
    parser.add_argument("grammar", type=Path, help="Path to .gr file containing a PCFG")
    parser.add_argument(
        "sentences", type=Path, help="Path to .sen file containing tokenized input sentences"
    )
    parser.add_argument(
        "-s",
        "--start_symbol",
        type=str,
        default="ROOT",
        help="Start symbol of the grammar (default: ROOT)",
    )
    parser.add_argument(
        "--progress", action="store_true", default=False, help="Display a progress bar"
    )

    parser.set_defaults(logging_level=logging.INFO)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", dest="logging_level", action="store_const", const=logging.DEBUG
    )
    verbosity.add_argument(
        "-q", "--quiet", dest="logging_level", action="store_const", const=logging.WARNING
    )

    parser.add_argument(
        "--chart", action="store_true", default=False, help="Print the Earley chart after parsing"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Print plain tree and span tree instead of tree and weight",
    )
    return parser.parse_args()


class Grammar:
    def __init__(self, start_symbol: str, *files: Path) -> None:
        self.start_symbol = start_symbol
        self.rules: List[Rule] = []
        self._by_lhs: Dict[str, List[int]] = defaultdict(list)
        for file in files:
            self.add_rules_from_file(file)

    def add_rules_from_file(self, file: Path) -> None:
        with open(file, "r") as handle:
            for raw in handle:
                line = raw.split("#", 1)[0].strip()
                if line == "":
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                prob_s, lhs, rhs_s = parts[0], parts[1], parts[2]
                prob = float(prob_s)
                weight = -math.log2(prob) if prob > 0 else float("inf")
                rid = len(self.rules)
                self.rules.append((lhs, tuple(rhs_s.split()), weight))
                self._by_lhs[lhs].append(rid)

    def expansions(self, lhs: str) -> Iterable[int]:
        return self._by_lhs.get(lhs, [])

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self._by_lhs


def _new_column() -> Column:
    return {
        "timeline": [],
        "queue": deque(),
        "queued": set(),
        "best": {},
        "trace": {},
    }


def _col_push(col: Column, state: State, weight: float, trace: Optional[Trace]) -> None:
    old = col["best"].get(state)
    if old is None:
        col["best"][state] = weight
        col["trace"][state] = trace
        col["timeline"].append(state)
        col["queue"].append(len(col["timeline"]) - 1)
        col["queued"].add(state)
        return

    if weight >= old:
        return

    col["best"][state] = weight
    col["trace"][state] = trace
    if state not in col["queued"]:
        col["timeline"].append(state)
        col["queue"].append(len(col["timeline"]) - 1)
        col["queued"].add(state)


def _col_pop(col: Column) -> State:
    idx = col["queue"].popleft()
    state = col["timeline"][idx]
    col["queued"].discard(state)
    return state


def _state_next(state: State, grammar: Grammar) -> Optional[str]:
    rid, dot, _ = state
    rhs = grammar.rules[rid][1]
    if dot >= len(rhs):
        return None
    return rhs[dot]


def _state_advance(state: State) -> State:
    rid, dot, origin = state
    return rid, dot + 1, origin


def _state_complete(state: State, grammar: Grammar) -> bool:
    rid, dot, _ = state
    return dot == len(grammar.rules[rid][1])


def _format_state(state: State, grammar: Grammar) -> str:
    rid, dot, origin = state
    lhs, rhs, _ = grammar.rules[rid]
    pieces = list(rhs)
    pieces.insert(dot, "·")
    return f"({origin}, {lhs} → {' '.join(pieces)})"


class EarleyChart:
    def __init__(self, tokens: List[str], grammar: Grammar, progress: bool = False) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.progress = progress
        self.profile: CounterType[str] = Counter()
        self.cols: List[Column] = []
        self._run()

    def _run(self) -> None:
        n = len(self.tokens)
        self.cols = [_new_column() for _ in range(n + 1)]
        self._predict(self.grammar.start_symbol, 0)

        for i in range(n + 1):
            log.debug("")
            log.debug(f"Column {i}")
            col = self.cols[i]
            while col["queue"]:
                state = _col_pop(col)
                next_sym = _state_next(state, self.grammar)
                if next_sym is None:
                    log.debug(f"  {_format_state(state, self.grammar)} -> ATTACH")
                    self._attach(state, i)
                elif self.grammar.is_nonterminal(next_sym):
                    log.debug(f"  {_format_state(state, self.grammar)} -> PREDICT")
                    self._predict(next_sym, i)
                else:
                    log.debug(f"  {_format_state(state, self.grammar)} -> SCAN")
                    self._scan(state, i)

    def _predict(self, nonterminal: str, position: int) -> None:
        col = self.cols[position]
        for rid in self.grammar.expansions(nonterminal):
            _, _, weight = self.grammar.rules[rid]
            _col_push(col, (rid, 0, position), weight, None)
            log.debug(f"    predicted {nonterminal} at {position} (w={weight:.4f})")
            self.profile["PREDICT"] += 1

    def _scan(self, state: State, position: int) -> None:
        if position >= len(self.tokens):
            return
        token = self.tokens[position]
        if token != _state_next(state, self.grammar):
            return
        next_state = _state_advance(state)
        weight = self.cols[position]["best"][state]
        trace: Trace = ("scan", state, position, token)
        _col_push(self.cols[position + 1], next_state, weight, trace)
        log.debug(
            f"    scanned {_format_state(next_state, self.grammar)} in col {position + 1} (w={weight:.4f})"
        )
        self.profile["SCAN"] += 1

    def _attach(self, completed: State, position: int) -> None:
        _, _, origin = completed
        lhs = self.grammar.rules[completed[0]][0]
        completed_weight = self.cols[position]["best"][completed]
        source = self.cols[origin]
        target = self.cols[position]

        for customer in source["timeline"]:
            if _state_next(customer, self.grammar) != lhs:
                continue
            advanced = _state_advance(customer)
            new_weight = source["best"][customer] + completed_weight
            trace: Trace = ("attach", customer, origin, completed, position)
            _col_push(target, advanced, new_weight, trace)
            log.debug(
                f"    attached {_format_state(advanced, self.grammar)} in col {position} (w={new_weight:.4f})"
            )
            self.profile["ATTACH"] += 1

    def _is_goal(self, state: State) -> bool:
        rid, _, origin = state
        lhs = self.grammar.rules[rid][0]
        return lhs == self.grammar.start_symbol and origin == 0 and _state_complete(state, self.grammar)

    def _best_goal(self) -> Optional[State]:
        best_state = None
        best_weight = float("inf")
        final = self.cols[-1]
        for state in final["timeline"]:
            if not self._is_goal(state):
                continue
            w = final["best"][state]
            if w < best_weight:
                best_weight = w
                best_state = state
        return best_state

    def accepted(self) -> bool:
        return self._best_goal() is not None

    def get_best_parse(self) -> Optional[Tuple[float, str, str]]:
        goal = self._best_goal()
        if goal is None:
            return None
        end_col = len(self.tokens)
        weight = self.cols[end_col]["best"][goal]
        plain = self._build_tree(goal, end_col, with_spans=False)
        spanned = self._build_tree(goal, end_col, with_spans=True)
        return weight, plain, spanned

    def _build_tree(self, state: State, col_idx: int, with_spans: bool) -> str:
        children: List[str] = []
        cur_state = state
        cur_col = col_idx

        while cur_state[1] > 0:
            trace = self.cols[cur_col]["trace"].get(cur_state)
            if trace is None:
                break
            if trace[0] == "scan":
                children.append(trace[3])
            else:
                children.append(self._build_tree(trace[3], trace[4], with_spans))
            cur_state = trace[1]
            cur_col = trace[2]

        children.reverse()
        lhs = self.grammar.rules[state[0]][0]
        if with_spans:
            lhs = f"{lhs} [{state[2]},{col_idx}]"
        if children:
            return f"({lhs} {' '.join(children)})"
        return f"({lhs})"

    def print_chart(self) -> None:
        for i, col in enumerate(self.cols):
            if i == 0:
                print(f"\n--- Column {i} (before input) ---")
            elif i <= len(self.tokens):
                print(f"\n--- Column {i} (after '{self.tokens[i - 1]}') ---")
            else:
                print(f"\n--- Column {i} ---")
            for state in col["timeline"]:
                w = col["best"][state]
                print(f"  {_format_state(state, self.grammar)}  [w={w:.4f}]")


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=args.logging_level)
    grammar = Grammar(args.start_symbol, args.grammar)

    with open(args.sentences) as handle:
        for raw in handle.readlines():
            sentence = raw.strip()
            if sentence == "":
                continue

            log.debug("=" * 70)
            log.debug(f"Parsing: {sentence}")
            chart = EarleyChart(sentence.split(), grammar, progress=args.progress)

            if args.chart:
                chart.print_chart()

            result = chart.get_best_parse()
            if result is None:
                print("NONE")
                log.debug(f"Profile: {chart.profile}")
                continue

            weight, tree, tree_with_spans = result
            print(tree)
            if args.debug:
                print(tree_with_spans)
            else:
                print(weight)
            log.debug(f"Prob:   {2 ** (-weight):.6f}")
            log.debug(f"Profile: {chart.profile}")


if __name__ == "__main__":
    main()
