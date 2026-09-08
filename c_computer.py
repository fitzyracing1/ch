#!/usr/bin/env python3
"""
C-Computer
==========
A tiny register machine whose only legal arithmetic is

    C = m * c / d

Control word C is forced to binary zero on RESET and whenever d == 0.

Cycle: RESET → LOAD m,c,d → COMPUTE C → PUSH C → CORRECT → repeat
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


WORD_BITS = 16
ZERO = 0  # 0b0000_0000_0000_0000


def to_bits(n: int, width: int = WORD_BITS) -> str:
    n = int(n) & ((1 << width) - 1)
    return format(n, f"0{width}b")


def clamp_word(x: float) -> int:
    """Map a real C into a signed 16-bit control word."""
    if x != x or x == float("inf") or x == float("-inf"):
        return ZERO
    v = int(round(x))
    lo, hi = -(1 << (WORD_BITS - 1)), (1 << (WORD_BITS - 1)) - 1
    return max(lo, min(hi, v))


@dataclass
class Registers:
    m: float = 0.0
    c: float = 0.0
    d: float = 0.0
    C: int = ZERO
    pc: int = 0
    halted: bool = False

    def reset(self) -> None:
        self.m = 0.0
        self.c = 0.0
        self.d = 0.0
        self.C = ZERO
        self.pc = 0
        self.halted = False


@dataclass
class TraceLine:
    step: int
    op: str
    m: float
    c: float
    d: float
    C: int
    bits: str
    note: str


class CComputer:
    """One-ALU computer: only C = m*c/d, reset C to every 0 in binary."""

    def __init__(self) -> None:
        self.r = Registers()
        self.trace: List[TraceLine] = []
        self.pushed: List[int] = []
        self.hypothesis: float = 1.0  # internal echo / risk seed

    def reset(self) -> None:
        self.r.reset()
        self.trace.clear()
        self.pushed.clear()
        self.hypothesis = 1.0
        self._log("RESET", "C forced to every 0 in binary")

    def _log(self, op: str, note: str) -> None:
        self.trace.append(
            TraceLine(
                step=len(self.trace),
                op=op,
                m=self.r.m,
                c=self.r.c,
                d=self.r.d,
                C=self.r.C,
                bits=to_bits(self.r.C),
                note=note,
            )
        )

    def load(self, m: float, c: float, d: Optional[float] = None) -> None:
        self.r.m = float(m)
        self.r.c = float(c)
        if d is None:
            # predicted-echo divisor from internal hypothesis
            self.r.d = max(1e-9, abs(self.hypothesis))
        else:
            self.r.d = float(d)
        self._log("LOAD", f"m={self.r.m} c={self.r.c} d={self.r.d}")

    def compute(self) -> int:
        if self.r.d == 0.0:
            self.r.C = ZERO
            self._log("SAFE", "d=0 → C = 0b0…0")
            return self.r.C
        raw = (self.r.m * self.r.c) / self.r.d
        self.r.C = clamp_word(raw)
        self._log("COMPUTE", f"C = m*c/d = {raw:.6g} → word {self.r.C}")
        return self.r.C

    def push(self) -> int:
        """Path must be pushed before the plant moves."""
        self.pushed.append(self.r.C)
        self._log("PUSH", f"actuator ← {to_bits(self.r.C)}")
        return self.r.C

    def correct(self, real_echo: float) -> None:
        """Real return only corrects the hypothesis; it never writes C directly."""
        surprise = abs(real_echo - self.hypothesis)
        self.hypothesis = 0.7 * self.hypothesis + 0.3 * real_echo
        self._log("CORRECT", f"echo={real_echo:.4g} surprise={surprise:.4g} hyp={self.hypothesis:.4g}")

    def step(self, m: float, c: float, d: Optional[float] = None, real_echo: float = 1.0) -> int:
        if self.r.halted:
            return self.r.C
        self.load(m, c, d)
        self.compute()
        word = self.push()
        self.correct(real_echo)
        self.r.pc += 1
        return word

    def run(self, program: List[dict], reset_first: bool = True) -> List[int]:
        if reset_first:
            self.reset()
        out: List[int] = []
        for inst in program:
            if inst.get("op") == "HALT":
                self.r.halted = True
                self._log("HALT", "loop idle, C held")
                break
            out.append(
                self.step(
                    m=inst.get("m", 0.0),
                    c=inst.get("c", 0.0),
                    d=inst.get("d"),
                    real_echo=inst.get("echo", 1.0),
                )
            )
        return out

    def dump(self) -> str:
        lines = [
            "C-COMPUTER TRACE",
            f"word={WORD_BITS}-bit  ALU=C=m*c/d  RESET=0b" + "0" * WORD_BITS,
            "-" * 72,
        ]
        for t in self.trace:
            lines.append(
                f"{t.step:03d} {t.op:<8} C={t.C:6d} {t.bits}  "
                f"m={t.m:8.3g} c={t.c:8.3g} d={t.d:8.3g}  {t.note}"
            )
        lines.append("-" * 72)
        lines.append("pushed words: " + " ".join(to_bits(w) for w in self.pushed))
        return "\n".join(lines)


def demo() -> None:
    cpu = CComputer()
    program = [
        {"m": 2.0, "c": 3.0, "d": 1.0, "echo": 1.2},   # C = 6
        {"m": 4.0, "c": 2.0, "d": 2.0, "echo": 0.8},   # C = 4
        {"m": 10.0, "c": 0.5, "d": 0.0, "echo": 1.0},  # d=0 → zeros
        {"m": 8.0, "c": 1.5, "echo": 2.0},             # d from hypothesis
        {"op": "HALT"},
    ]
    cpu.run(program)
    print(cpu.dump())
    print()
    print("final registers")
    print(f"  m={cpu.r.m}  c={cpu.r.c}  d={cpu.r.d}")
    print(f"  C={cpu.r.C}  bits={to_bits(cpu.r.C)}")
    print(f"  pc={cpu.r.pc} halted={cpu.r.halted}")


if __name__ == "__main__":
    demo()
