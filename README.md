# C-Computer

16-bit register machine. The only legal arithmetic is

```
C = m * c / d
```

Reset and the illegal-divisor path force the control word to every `0` in binary:

```
0000000000000000
```

## Cycle

```
RESET → LOAD m,c,d → COMPUTE C → PUSH C → CORRECT hypothesis → next
```

- `d` may be omitted. Then `d` is taken from the internal echo hypothesis.
- The plant does not move until `PUSH`.
- The real echo never writes `C`. It only corrects the hypothesis.

## Run locally

Python:

```bash
python3 c_computer.py
```

Web panel (GitHub Pages or any static host):

open `index.html`

## Pages

This folder is Pages-ready.

- `index.html` — live control panel
- `c_computer.py` — same machine in Python
- `.nojekyll` — serve as-is

Push the folder contents to `main` (or `docs/`) and enable GitHub Pages.

## License

Use as you like. Control law stays `C = m c / d`.

## Documentation

- In-repo docs: [docs/](docs/index.md)
- Wiki: [https://github.com/fitzyracing1/ch/wiki](https://github.com/fitzyracing1/ch/wiki)
