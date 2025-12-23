# -*- coding: utf-8 -*-
"""
rp9_core.py — Reusable core for RP9 computations and coherence checks.

Usage:
    python rp9_core.py --nm 1.0 --stabiliserande 1.5

Exposes:
    - compute_rp9(stabiliserande_faktor: float = 1.5, N_M: float = 1.0) -> dict
    - is_full_coherence(values: dict, tol: float = 1e-12) -> bool
"""

import math
import argparse
from dataclasses import dataclass

@dataclass
class RP9Values:
    phi: float
    sqrt2: float
    stabiliserande_faktor: float
    N_M: float
    RP9_geo: float
    RP9_fys: float
    Delta: float

def compute_rp9(stabiliserande_faktor: float = 1.5, N_M: float = 1.0) -> RP9Values:
    phi = (1 + math.sqrt(5)) / 2
    sqrt2 = math.sqrt(2)
    RP9_geo = (phi / sqrt2) / stabiliserande_faktor
    RP9_fys = N_M * RP9_geo
    Delta = RP9_geo - RP9_fys
    return RP9Values(phi, sqrt2, stabiliserande_faktor, N_M, RP9_geo, RP9_fys, Delta)

def is_full_coherence(values: RP9Values, tol: float = 1e-12) -> bool:
    return abs(values.Delta) <= tol

def main():
    parser = argparse.ArgumentParser(description="Compute RP9 values and check coherence.")
    parser.add_argument("--nm", type=float, default=1.0, help="N(M) — fysisk projektion koherensfaktor")
    parser.add_argument("--stabiliserande", type=float, default=1.5, help="Självstabiliserande konstant")
    parser.add_argument("--tol", type=float, default=1e-12, help="Tolerans för full koherens")
    args = parser.parse_args()

    vals = compute_rp9(stabiliserande_faktor=args.stabiliserande, N_M=args.nm)
    print("=== RP9 — Core ===")
    print(f"φ = {vals.phi}")
    print(f"√2 = {vals.sqrt2}")
    print(f"stabiliserande_faktor = {vals.stabiliserande_faktor}")
    print(f"N(M) = {vals.N_M}")
    print(f"RP9_geo = {vals.RP9_geo}")
    print(f"RP9_fys = {vals.RP9_fys}")
    print(f"Δ = {vals.Delta}")
    print(f"Full koherens (|Δ| ≤ {args.tol}): {is_full_coherence(vals, tol=args.tol)}")

if __name__ == "__main__":
    main()