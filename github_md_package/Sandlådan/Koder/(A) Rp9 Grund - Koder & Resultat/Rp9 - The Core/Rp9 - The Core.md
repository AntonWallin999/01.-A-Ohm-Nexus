- [Vad koden gör steg för steg](#vad-koden-gör-steg-för-steg)
  - [1. Syfte](#1-syfte)
  - [2. Kärnformeln](#2-kärnformeln)
  - [3. Funktionerna i filen](#3-funktionerna-i-filen)
---
# rp9_core.py
`````python
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
`````
---

```´Markdown
Resultat: rp9_core.py
=== RP9 — Core ===
φ = 1.618033988749895
√2 = 1.4142135623730951
stabiliserande_faktor = 1.5
N(M) = 1.0
RP9_geo = 0.7627485370902457
RP9_fys = 0.7627485370902457
Δ = 0.0
Full koherens (|Δ| ≤ 1e-12): True

C:\Users\Namn\Desktop\Kod\Rp9 - The Core>
```
---
## **Vad koden gör steg för steg**

### 1. Syfte

Den beräknar och kontrollerar **RP9-konstanterna**:

- den gyllene snittet $\varphi = \frac{1+\sqrt{5}}{2}$  
- roten ur två $\sqrt{2}$  
- den **stabiliserande faktorn** (oftast $1.5$ eller $1.618$)  
- den **fysiska projektionen** $N(M)$ (en skalningsfaktor, normalt $1.0$)  
- samt de två centrala resultaten:  
  - **RP9_geo** – den geometriska formen av RP9  
  - **RP9_fys** – den fysiska versionen ($RP9_{\text{geo}}$ multiplicerat med $N(M)$)  
  - **Δ (Delta)** – skillnaden mellan dessa två  

Det är alltså motorn som beräknar själva **RP9-relationen**.

---

### 2. Kärnformeln

Formeln för RP9-relationen är:

$$
RP9_{\text{geo}} = \frac{\varphi / \sqrt{2}}{\text{stabiliserande\_faktor}}
$$

och

$$
RP9_{\text{fys}} = N(M) \cdot RP9_{\text{geo}}
$$

Skillnaden  
$$
\Delta = RP9_{\text{geo}} - RP9_{\text{fys}}
$$  
visar hur nära **full koherens** systemet är.

Om $|\Delta| \leq 10^{-12}$ anses systemet vara **fullt koherent**, dvs. geometriskt och fysiskt perfekt balanserat.

---

### 3. Funktionerna i filen

| Funktion | Vad den gör | Returnerar |
|-----------|--------------|-------------|
| `compute_rp9(stabiliserande_faktor, N_M)` | Räknar ut alla RP9-värden och Δ | Ett objekt (`RP9Values`) med alla värden |
| `is_full_coherence(values, tol)` | Kollar om Δ ligger inom toleransgränsen | `True` eller `False` |
| `main()` | Gör det möjligt att köra skriptet direkt i terminalen | Skriver ut resultaten |

---

|Egenskap|Beskrivning|
|---|---|
|Typ|Grundmodul / kärna|
|Funktion|Beräknar RP9-konstanter och koherens|
|Ingång|Stabiliserande faktor och N(M)|
|Utgång|φ, √2, RP9_geo, RP9_fys, Δ och koherensstatus|
|Används av|Alla övriga RP9-skript|
|Praktisk betydelse|Definierar den exakta relationen mellan RP9:s geometri och dess fysiska uttryck|


> [!QUESTION]
> $$- - - =(\ Rp9 \ )= - - -$$
> >## ⚖️ *Licens & Ägarskap*  
> >>### **Creative Commons — CC BY-SA 4.0**
> >> >---
> >>>*Detta verk är fritt att delas, remixas och byggas vidare på,  
> >>>så länge korrekt erkännande ges och samma licens bibehålls.*
> >>>
> >>> **Du har rätt att:**  
> >>>- **Dela** — kopiera och vidaredistribuera materialet i vilket format eller medium som helst  
> >>>- **Bearbeta** — remixa, transformera och bygga vidare på materialet  
> >>>
> >>>**Under följande villkor:**  
> >>>- **Erkännande:** Du måste ge korrekt erkännande till _Anton Wallin_  
> >>>- **DelaLika:** Om du transformerar eller bygger vidare på detta verk  
> >>>  ska du sprida det under samma licens.  
> >>>
> >> >---
> >> >
> >>>
> >>> ### _Co-Creator_  
 >>>
> >>**Konceptuellt ägarskap & axiomatisk kalibrering**  
 >>>**Författare:** _Anton Wallin_  
 >>
>>
>>© 2025 – Alla rättigheter förbehållna.
>
># $$---=(0)=---$$
>---
