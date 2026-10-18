# Estigia - Thermodynamic Topological Attractor

This repository contains a Python simulation that demonstrates a "Thermodynamic Topological Attractor" (MAT) interacting with a legacy Lorenz attractor.

The included script generates a visualization (PNG) of the attractor state-space collapse and an efficiency decay curve.

## Files added
- `simulation.py` - main simulation and visualization script (headless-ready).
- `requirements.txt` - Python dependencies.
- `README.md` - this file.
- `.gitignore` - ignore outputs and Python caches.

## How to run

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate    # on Windows: .\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the simulation (this will generate `outputs/MAT_Simulation_v4.1.png`):

```bash
python simulation.py
```

Notes:
- The script is configured to run in headless environments (no display) by forcing the Matplotlib `Agg` backend.
- Output is saved to the `outputs/` directory. The folder will be created automatically.

If you want the images to appear on GitHub, upload the generated PNG into the repository (e.g. `images/`) and open a PR.
