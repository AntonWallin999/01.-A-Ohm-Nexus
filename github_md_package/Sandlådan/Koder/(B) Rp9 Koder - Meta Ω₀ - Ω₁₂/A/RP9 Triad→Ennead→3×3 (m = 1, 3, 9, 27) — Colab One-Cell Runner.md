
# RP9 Triad→Ennead→3×3 (m = 1, 3, 9, 27) — Colab One-Cell Runner
*(Fullständig, körbar kod. Kör i en cell i Colab eller lokalt med Python ≥ 3.10.)*

---

## Syfte och nyckelmått

Kalibrerar RP9-faktorn $k=1.5$ för $m\in\{1,3,9,27\}$ mot alternativa skalor ($\varphi$ och $\sqrt{2}$) över ett frekvensfönster:

$$
f_{i,k} \;=\; \theta\cdot r^{\,k+\frac{i}{m}}\,,\qquad i=0,\dots,m-1,\quad k\in[k_{\min},k_{\max}]
$$

Jämförelsemått:

$$
U \;=\; \frac{P^*_{1.5}}{P^*_{\text{alt}}} - 1
\qquad\text{och}\qquad
D \;=\; P^*_{1.5} - P^*_{\text{alt}}\,.
$$

Rapporteras per $m$: $\bar U$, $SE$, $95\%$-CI, ensidigt $t/p$, vinstfrekvens $\hat p$ med Wilson-CI samt permutationstest $p_{\text{perm}}$.

---

## Körbar kod

```python
# === RP9 Triad→Ennead→3×3 (m = 1, 3, 9, 27) — Colab One-Cell Runner ===
# Funktion:
# - Skalar upp halva–halva-relationen r=1.5 från 1 spole → 3 → 9 → 27 (3×3).
# - För varje m beräknas kalibrerad effekt P* över θ för skalfamiljen f_{i,k}=θ·r^{k+i/m}.
# - Jämför r=1.5 mot alternativ (altA = φ och valbart altB = √2) med samma m-struktur.
# - Producerar CSV/JSON och skriver en tydlig konsol-rapport.

import sys, subprocess, os, math, json, time, glob
from pathlib import Path

def _pip_try(pkgs):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + pkgs, check=True)
        return True
    except Exception:
        return False

_pip_try(["numpy", "pandas"])

import numpy as np
import pandas as pd

def _ts(): return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
def _ensure_dir(p): Path(p).mkdir(parents=True, exist_ok=True)
def _has_csv(folder): return any(Path(folder).glob("*.csv"))

# -------- Syntetiska spektra (om ./spectra saknar CSV) --------
def generate_synthetic_spectra(spectra_dir, n_files=12, n_points=2000, fmin=0.5, fmax=500.0, seed=123):
    rng = np.random.default_rng(seed); _ensure_dir(spectra_dir)
    f = np.exp(np.linspace(np.log(fmin), np.log(fmax), n_points))
    r_main = 1.5; r_phi = (1.0 + math.sqrt(5.0)) / 2.0

    for i in range(n_files):
        theta_main = np.exp(rng.uniform(np.log(1.2), np.log(3.5)))
        theta_phi  = np.exp(rng.uniform(np.log(0.9), np.log(2.2)))
        ks = np.arange(-8, 9, dtype=int)
        peaks_main = theta_main * (r_main ** ks.astype(float))
        peaks_phi  = theta_phi  * (r_phi  ** ks.astype(float))

        s = np.zeros_like(f)
        def add(peaks, amp, width):
            nonlocal s
            for pk in peaks:
                s += amp * (width**2) / ((f - pk)**2 + width**2)

        amp1, amp2 = rng.uniform(1.5,3.5), rng.uniform(0.8,2.0)
        width1, width2 = rng.uniform(0.3,1.2), rng.uniform(0.3,1.2)
        add(peaks_main, amp1, width1); add(peaks_phi, amp2, width2)
        s += 0.2 * (f**-0.3); s += rng.normal(0.0, 0.02, size=f.shape); s = np.maximum(s, 0.0)

        pd.DataFrame({"freq": f, "value": s}).to_csv(Path(spectra_dir)/f"synthetic_window_{i+1:02d}.csv", index=False)

# -------- Kolumndetektering & inläsning --------
def detect_columns(df, fcol=None, scol=None):
    if fcol and scol and fcol in df and scol in df: return fcol, scol
    cols = list(df.columns); lower = [c.lower() for c in cols]
    cf = cs = None
    for i,c in enumerate(lower):
        if c in ("f","freq","frequency","hz"): cf = cols[i]
        if c in ("s","pow","power","amp","amplitude","psd","value","mag"): cs = cols[i]
    if cf and cs: return cf, cs
    nums = []
    for c in cols:
        try: pd.to_numeric(df[c], errors="raise"); nums.append(c)
        except Exception: pass
    if len(nums)>=2: return nums[0], nums[1]
    if len(cols)>=2: return cols[0], cols[1]
    raise ValueError("Kunde inte detektera frekvens- och spektralkolumner.")

def read_spectrum_csv(path, fcol=None, scol=None):
    df = pd.read_csv(path)
    fcol, scol = detect_columns(df, fcol, scol)
    f = pd.to_numeric(df[fcol], errors="coerce").to_numpy()
    s = pd.to_numeric(df[scol], errors="coerce").to_numpy()
    m = np.isfinite(f) & np.isfinite(s); f = f[m]; s = s[m]
    order = np.argsort(f); return f[order], s[order], fcol, scol

# -------- Triad/Ennead/3×3-kärna --------
def theta_grid_from_range_multi(fmin, fmax, r, kmin, kmax, m, n_theta_base):
    log_r = math.log(r); gmax = r**((m-1)/m) if m>1 else 1.0
    lo = math.log(max(1e-18, fmin)) - kmax*log_r - math.log(max(gmax,1.0))
    hi = math.log(max(1e-18, fmax)) - kmin*log_r
    n_theta = int(max(2, round(n_theta_base * (1 + 0.5*(m>1) + 1.0*(m>3) + 1.5*(m>9)))))
    if not math.isfinite(lo) or not math.isfinite(hi) or hi<=lo:
        lo = math.log(max(1e-18, fmin)) - 5.0*log_r; hi = math.log(max(1e-18, fmax)) + 5.0*log_r
    return np.exp(np.linspace(lo, hi, n_theta))

def captured_power_multi(theta, r, kmin, kmax, f, s, m):
    ks = np.arange(int(kmin), int(kmax)+1, dtype=int).astype(float)
    base = theta * (r ** ks)
    fmin, fmax = float(f[0]), float(f[-1])
    total = 0.0
    for i in range(m):
        gi = r ** (i/m)
        fk = base * gi
        mask = (fk>=fmin) & (fk<=fmax)
        if np.any(mask):
            total += float(np.interp(fk[mask], f, s).sum())
    return total

def calibrated_power_multi(f, s, r, kmin, kmax, n_theta_base, m):
    tg = theta_grid_from_range_multi(float(np.min(f)), float(np.max(f)), r, kmin, kmax, m, n_theta_base)
    best_val, best_theta = -1.0, None
    for theta in tg:
        val = captured_power_multi(theta, r, kmin, kmax, f, s, m)
        if val > best_val:
            best_val, best_theta = val, float(theta)
    if best_val < 0.0: best_val, best_theta = 0.0, np.nan
    return best_val, best_theta

# -------- Statistik --------
def mean_ci_normal(x):
    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]
    n = x.size
    if n==0: return (np.nan, np.nan, (np.nan, np.nan))
    m = float(np.mean(x)); sd = float(np.std(x, ddof=1)) if n>1 else 0.0
    se = sd/ math.sqrt(n) if n>1 else np.nan; z=1.959963984540054
    lo = m - z*se if se==se else np.nan; hi = m + z*se if se==se else np.nan
    return (m, se, (lo, hi))

def t_stat_p_one_sided_from_mean(x, mu0=0.0):
    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]
    n = x.size
    if n<2: return (np.nan, np.nan)
    m = float(np.mean(x)); sd = float(np.std(x, ddof=1))
    if sd==0.0:
        t = math.inf if m>mu0 else -math.inf; p = 0.0 if m>mu0 else 1.0
        return (t,p)
    se = sd/math.sqrt(n); t = (m-mu0)/se; p = 0.5*math.erfc(t/math.sqrt(2.0))
    return (t,p)

def wilson_interval(w, n):
    if n==0: return (np.nan, np.nan)
    z=1.959963984540054; phat=w/n; denom=1.0+(z*z)/n
    center=(phat+(z*z)/(2*n))/denom
    radius=(z/denom)*math.sqrt((phat*(1-phat)/n)+(z*z)/(4*n*n))
    return (max(0.0, center-radius), min(1.0, center+radius))

def permutation_pvalue_signed_mean(diffs, n_perm=2000, seed=123):
    rng = np.random.default_rng(seed)
    diffs = np.asarray(diffs, dtype=float); diffs = diffs[np.isfinite(diffs)]
    n = diffs.size
    if n==0: return np.nan
    obs = float(np.mean(diffs))
    flips = rng.choice([-1.0,1.0], size=(n_perm,n))
    perm_means = (flips*diffs).mean(axis=1)
    return float(np.mean(perm_means >= obs))

# -------- Huvudkörning --------
def run_rp9_multiplex(
    spectra_dir="./spectra",
    out_root="./",
    kmin=-8, kmax=8,
    n_theta_base=200,
    m_list=(1,3,9,27),
    altA="phi",                # 'phi', 'sqrt2' eller numeriskt ('1.6')
    altB=True,                 # True => jämför dessutom mot √2 i separat block
    permutations=5000,
    seed=123
):
    r_main = 1.5

    # altA-ratio
    r_altA = None
    if isinstance(altA, str):
        low = altA.lower()
        if low in ("phi","varphi","golden","goldenratio"):
            r_altA = (1.0 + math.sqrt(5.0)) / 2.0
        elif low in ("sqrt2","root2"):
            r_altA = math.sqrt(2.0)
        else:
            r_altA = float(low.replace(",", "."))
    elif altA is None:
        r_altA = None
    else:
        r_altA = float(altA)

    # altB-ratio
    r_altB = math.sqrt(2.0) if altB else None

    # Input
    if not Path(spectra_dir).exists(): _ensure_dir(spectra_dir)
    if not _has_csv(spectra_dir): generate_synthetic_spectra(spectra_dir)

    files = sorted(glob.glob(str(Path(spectra_dir) / "*.csv")))
    if not files: raise RuntimeError("Ingen CSV hittades i ./spectra (och generering misslyckades).")

    outdir = os.path.join(out_root, "rp9_3x3_out_" + _ts()); _ensure_dir(outdir)

    perwin_rows = []
    statsA, statsB = {}, {}

    def _run_block(r_alt, stats_dict, tag):
        for m in m_list:
            U,D,Pm,Pa,Tm,Ta,W = [],[],[],[],[],[],[]
            for pth in files:
                try:
                    f,s,fc,sc = read_spectrum_csv(pth, None, None)
                except Exception:
                    continue
                if f.size < 10: continue
                p_main, th_main = calibrated_power_multi(f,s,r_main,kmin,kmax,n_theta_base,m)
                if r_alt is not None:
                    p_alt, th_alt = calibrated_power_multi(f,s,r_alt ,kmin,kmax,n_theta_base,m)
                    u = (p_main/p_alt - 1.0) if p_alt>0 else np.nan
                    d = p_main - p_alt
                else:
                    p_alt, th_alt, u, d = np.nan, np.nan, np.nan, np.nan
                perwin_rows.append({
                    "tag": tag or "main-only",
                    "m": m, "window": Path(pth).name,
                    "fcol": fc, "scol": sc,
                    "Pstar_main": p_main, "Theta_main": th_main,
                    "Pstar_alt": p_alt,  "Theta_alt": th_alt,
                    "U": u, "D": d
                })
                Pm.append(p_main); Pa.append(p_alt); Tm.append(th_main); Ta.append(th_alt); W.append(Path(pth).name)
                if r_alt is not None: U.append(u); D.append(d)

            st = {"n_windows": int(len(Pm)), "m": int(m), "kmin": int(kmin), "kmax": int(kmax),
                  "n_theta_base": int(n_theta_base), "r_main": float(r_main)}
            if r_alt is not None and len(U)>0:
                mU,seU,ciU = mean_ci_normal(U); tU,pU = t_stat_p_one_sided_from_mean(U,0.0)
                wins = int(np.sum(np.asarray(Pm) > np.asarray(Pa))); nW = len(Pm)
                phat = wins/nW if nW>0 else np.nan; wil_lo,wil_hi = wilson_interval(wins,nW)
                p_perm = permutation_pvalue_signed_mean(D, n_perm=permutations, seed=seed)
                st.update({"r_alt": float(r_alt), "mean_U": float(mU), "se_U": float(seU),
                           "ci95_U_lo": float(ciU[0]), "ci95_U_hi": float(ciU[1]),
                           "t_U": float(tU), "p_U_one_sided": float(pU),
                           "wins": int(wins), "n": int(nW), "phat_wins": float(phat),
                           "wilson95_lo": float(wil_lo), "wilson95_hi": float(wil_hi), "p_perm": float(p_perm)})
            stats_dict[m] = st
        return stats_dict

    tagA = None
    if r_altA is not None:
        tagA = "altA=φ" if abs(r_altA - (1+math.sqrt(5))/2)<1e-12 else f"altA={r_altA:.6g}"
        statsA = _run_block(r_altA, {}, tagA)

    tagB = None
    if r_altB is not None and (r_altA is None or abs(r_altA-r_altB)>1e-12):
        tagB = "altB=√2"
        statsB = _run_block(r_altB, {}, tagB)

    df_perwin = pd.DataFrame(perwin_rows)
    res_csv = str(Path(outdir)/"rp9_3x3_results.csv"); df_perwin.to_csv(res_csv, index=False)

    summary = {
        "kmin": int(kmin), "kmax": int(kmax), "n_theta_base": int(n_theta_base),
        "r_main": float(r_main), "m_list": list(map(int, m_list)),
        "altA": None if r_altA is None else float(r_altA),
        "altB": None if r_altB is None else float(r_altB)
    }
    if statsA: summary["altA_stats"] = { str(m): statsA[m] for m in statsA }
    if statsB: summary["altB_stats"] = { str(m): statsB[m] for m in statsB }
    res_json = str(Path(outdir)/"rp9_3x3_summary.json")
    with open(res_json,"w",encoding="utf-8") as f: json.dump(summary,f,indent=2)

    def _print_block(name, stats):
        if not stats: return
        print("\n=== Resultat:", name, "===")
        for m in sorted(stats.keys(), key=int):
            st = stats[m]
            if "mean_U" not in st:
                print(f"m={m}: (ingen alt-data)")
                continue
            print(f"\n[m={m}]  n={st['n']}")
            print(f"  mean U         = {st['mean_U']:.6f}  (SE = {st['se_U']:.6f})")
            print(f"  95% CI(U)      = [{st['ci95_U_lo']:.6f}, {st['ci95_U_hi']:.6f}]")
            print(f"  t, p (ensidigt)= {st['t_U']:.6f}, {st['p_U_one_sided']:.6g}")
            print(f"  wins / n       = {st['wins']}/{st['n']}  (p_hat = {st['phat_wins']:.6f})")
            print(f"  Wilson 95% CI  = [{st['wilson95_lo']:.6f}, {st['wilson95_hi']:.6f}]")
            print(f"  p_perm         = {st['p_perm']:.6g}")

    print("\n===============================================")
    print("RP9 Triad/Ennead/3×3 — Körning klar")
    print("Spectra-dir :", str(Path(spectra_dir).resolve()))
    print("Utdata-mapp :", str(Path(outdir).resolve()))
    print("CSV         :", res_csv)
    print("JSON        :", res_json)
    print("m-läge      :", m_list)
    print("altA        :", summary["altA"], "(φ om ≈1.618...)")
    print("altB        :", summary["altB"], "(√2 om ≈1.4142)")
    print("===============================================")

    _print_block("1.5 vs altA", statsA)
    _print_block("1.5 vs altB (√2)", statsB)

    def sign_str(x):
        if not np.isfinite(x): return "NA"
        return "POS" if x>0 else ("NEG" if x<0 else "ZERO")

    print("\n--- Samlad tolkning (kompakt) ---")
    for name,stats in [("altA (t.ex. φ)", statsA), ("altB (√2)", statsB)]:
        if not stats: continue
        vals = [(int(m), stats[m]["mean_U"]) for m in stats if "mean_U" in stats[m]]
        if not vals: continue
        trend = " → ".join([f"m={m}:{sign_str(mu)}" for m,mu in sorted(vals)])
        print(f"{name}: {trend}")

    return {"results_csv": res_csv, "summary_json": res_json, "summary": summary}

# === Körning: m = 1,3,9,27; altA=φ; altB=√2 ===
if __name__ == "__main__":
    result = run_rp9_multiplex(
        spectra_dir="./spectra",   # lägg egna CSV här; annars genereras syntetiska
        kmin=-8, kmax=8,
        n_theta_base=200,
        m_list=(1,3,9,27),
        altA="phi",
        altB=True,
        permutations=5000,
        seed=123
    )
    print("\nDone.")
```


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

