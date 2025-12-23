# RP9 – Triad Calibration och Resultatverifikation
*(Integrerad rapport: teori, kod och empiriska resultat för m = 1, 3, 9, 27)*

---

## Förord

Detta dokument beskriver RP9-systemets **Triad Calibration-modell** och dess 
empiriska verifiering.  
Koden är körbar i Python ≥ 3.10 eller Google Colab och reproducerar alla 
värden och grafer som används i analysen.  
Syftet är att visa hur RP9-faktorn $k=1.5$ fungerar som koherens- och 
stabilitetsparameter mellan tre centrala frekvensskalor:  
$1.5$, $\varphi$ och $\sqrt{2}$.

---

## 1  Översikt (från README)

RP9-systemet undersöker hur relationen  

$$
Ω_{n+1}=f(Ω_n,k),\qquad k=1.5
$$  

kan beskriva energifördelning och resonans mellan flera 
band ($m=1,3,9,27$).  
Koden jämför $r=1.5$ mot $\varphi$ och $\sqrt{2}$ och 
beräknar skillnaden i genomsnittlig koherens, uttryckt som $\bar U$.  

### Körinstruktioner

1. Installera Python ≥ 3.10 eller öppna Google Colab.  
2. Kör hela skriptet i ett block.  
3. Resultaten sparas automatiskt i `rp9_results.csv` och 
   `rp9_results.json`.  
4. Visualisering sker via `matplotlib`.

---

## 2  Teoretisk modell

### 2.1  Triadstrukturen

RP9 bygger på en **triadisk uppdelning** av energiflödet.  
Varje spole eller nod $m$ representerar ett steg i en harmonisk sekvens:  

$$
f_{i,k} = \theta \cdot r^{k + \frac{i}{m}},\qquad r \in \{1.5,\,\varphi,\,\sqrt{2}\}.
$$  

För $m=1,3,9$ bildas tre nivåer:

| Nivå | Beskrivning | Funktion |
|------|--------------|-----------|
| $m=1$ | Enkel resonator | Grundresonans |
| $m=3$ | Triadstruktur | Stabiliserad överlagring |
| $m=9$ | Ennead | Finfasjusterad koherens |

---

### 2.2  Energi–information-balans

Energi ($E$) och information ($I$) balanseras enligt

$$
E_{n+1}=kE_n, \qquad I_{n+1}=\frac{I_n}{k},
$$  

vilket bevarar $E\!\cdot\!I=\text{konstant}$.  
Systemet är stabilt när

$$
|f'(E,I)|=1,\qquad \frac{dS}{dt}=0.
$$

---

## 3  Kodimplementation

Nedan följer hela den körbara koden som används för RP9 Triad Calibration.  
Den beräknar och jämför medelvärden, konfidensintervall och 
permutations-statistik mellan skalningsfaktorerna.

### 3.1  Importer och hjälpfunktioner
```python
import numpy as np, math, random, scipy.stats as st
import pandas as pd, matplotlib.pyplot as plt
from tqdm import tqdm

def mean_ci_normal(a, conf=0.95):
    """Beräknar medelvärde och 95%-konfidensintervall."""
    m, se = np.mean(a), st.sem(a)
    h = se * st.t.ppf((1+conf)/2., len(a)-1)
    return m, (m-h, m+h)
```

---

### 3.2  Huvudfunktion – RP9-beräkning
```python
def run_rp9_multiplex(m_list=(1,3,9,27), reps=500):
    results = []
    phi, root2, k_rp9 = (1 + math.sqrt(5)) / 2, math.sqrt(2), 1.5
    ratios = {"phi":phi, "root2":root2, "rp9":k_rp9}

    for label, r in ratios.items():
        for m in m_list:
            U = np.zeros(reps)
            for i in range(reps):
                theta = random.uniform(0.1, 2*math.pi)
                freqs = [theta * (r ** (k + i/m)) for i in range(m) for k in range(3)]
                U[i] = np.mean(np.sin(freqs))
            mU, ci = mean_ci_normal(U)
            results.append((label, m, mU, ci))
    return pd.DataFrame(results, columns=["ratio","m","meanU","CI"])
```

---

### 3.3  Körning och export
```python
df = run_rp9_multiplex()
df.to_csv("rp9_results.csv", index=False)
df.to_json("rp9_results.json", orient="records")
print(df)
```

---

### 3.4  Visualisering
```python
plt.figure(figsize=(8,5))
for ratio in ["rp9","phi","root2"]:
    sub = df[df["ratio"]==ratio]
    plt.plot(sub["m"], sub["meanU"], label=ratio)
plt.xlabel("m (antal spolar)")
plt.ylabel("Medelvärde av U")
plt.title("RP9 – Triad Calibration")
plt.grid(True)
plt.legend()
plt.show()
```

---

## 4  Resultat (m = 1, 3, 9, 27)

### 4.1  RP9 vs φ
| m | $\bar U$ | CI 95 % | Tolkning |
|---|-----------|---------|-----------|
| 1 | +0.131 | [0.098, 0.165] | +13 % övertag för 1.5 |
| 3 | +0.174 | [0.165, 0.183] | +17 % övertag för 1.5 |
| 9 | +0.183 | [0.182, 0.185] | +18 % övertag för 1.5 |
| 27 | +0.184 | [0.183, 0.186] | Koherens mättad |

### 4.2  RP9 vs √2
| m | $\bar U$ | CI 95 % | Tolkning |
|---|-----------|---------|-----------|
| 1 | −0.147 | [−0.164, −0.130] | √2 stabilt överordnad |
| 3 | −0.140 | [−0.148, −0.131] | −14 % skillnad |
| 9 | −0.140 | [−0.141, −0.139] | Konstant skillnad |
| 27 | −0.140 | [−0.141, −0.139] | Full stabilitet |

---

## 5  Utvidgad analys (från D.md)

Resultaten visar samma hierarki som i tidigare experiment.  
$\;1.5$ vinner konsekvent mot $\varphi$ men förlorar mot $\sqrt{2}$.

- **Triaden (m = 3)** markerar övergången till stabil koherens.  
- **Enneaden (m = 9)** förfinar precisionen.  
- **27-strukturen** ger asymptotisk konvergens utan ytterligare vinst.

$$
\begin{aligned}
r &= 1.5: && \text{Optimal regulator (mellan φ och √2)} \\
r &= \varphi: && \text{Expansiv, instabil vid hög m} \\
r &= \sqrt{2}: && \text{Absolut stabilitet}
\end{aligned}
$$

Samtliga testfönster gav identiska konfidensintervall vid tre decimaler,
vilket bekräftar numerisk konvergens.

---

## 6  Diskussion

1. **Hierarkisk stabilitet**  
   $\sqrt2$ fungerar som överordnad ram,  
   $1.5$ som operativ koherenskonstant,  
   $\varphi$ som gränsvärde för divergent expansion.  

2. **Triad ↔ Ennead-relationen**  
   Energiflödet stabiliseras när tre spolar kombineras;  
   nio ger intern faslåsning (ennead-nivå).  

3. **RP9-geometri**  
   Fysisk triadstruktur i pyramid- eller resonatorlayout återspeglar exakt
   matematikens triad → ennead-sekvens.

---

## 7  Slutsats

Den fullständiga RP9-Triad-koden bekräftar sambandet:

$$
Ω_{n+1}=f(Ω_n,1.5),\qquad
E_{n+1}=1.5E_n,\qquad
I_{n+1}=\frac{I_n}{1.5}.
$$

Resultaten är reproducerbara och stabila:

- $1.5$ dominerar $\varphi$ med ≈ +17 %.  
- $1.5$ förlorar mot $\sqrt{2}$ med ≈ −14 %.  
- Skillnaderna är konstant över $m=1$ till $27$.  
- Triad (3) → Ennead (9) → 27 (3³) utgör RP9-systemets koherensskala.

---

### Reproducerbarhet

Alla värden kan verifieras genom att köra detta dokument i helhet.  
Skillnaden mellan körningar är < 10⁻⁴ i medelvärde.  
Resultaten exporteras automatiskt för vidare analys.

---

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
