# C-Computer (repo: ch)

C-Computer is a 16-bit register machine whose only legal arithmetic is `C = m * c / d`. Reset and the illegal-divisor path force the control word to `0000000000000000`.

Cycle: `RESET → LOAD m,c,d → COMPUTE C → PUSH C → CORRECT hypothesis → next`. If `d` is omitted it comes from the internal echo hypothesis. The plant does not move until PUSH, and the real echo only corrects the hypothesis.

## Getting started

```bash
python3 c_computer.py
```

To use the web panel, open `index.html` (Pages-ready, with `.nojekyll`).

Files: `c_computer.py`, `index.html`. The repo has no tests, no CI and no LICENSE file.

Copyright (c) 2026 Joshua Almeida
