 ````python
 === RP9 Calibrated Report — Colab One-Cell Runner (self-contained) ===
# - No arguments needed. No paths to edit.
# - Auto-generates synthetic spectra if ./spectra is empty, so it ALWAYS runs.
# - Produces HTML report and shows it inline in Colab.
# - Math in comments uses inline LaTeX: $r=1.5$, $\varphi=\frac{1+\sqrt{5}}{2}$, $\sqrt{2}$, $P^*$, $U$, $D$.
# - Design note: $r=1.5$ är ett exakt, avsiktligt konstantvärde i denna modell (inte approximation).

import sys, subprocess, os, math, json, time, webbrowser, glob
from pathlib import Path

def _pip_install(pkgs):
    try:
        import importlib
        for p in pkgs:
            try:
                importlib.import_module(p if p != "plotly" else "plotly.graph_objects")
            except Exception:
                raise
        return
    except Exception:
        pass
    cmd = [sys.executable, "-m", "pip", "install"] + pkgs
    subprocess.run(cmd, check=True)

_pip_install(["numpy", "pandas", "plotly"])

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import IFrame, display, HTML

# ---------- Utility: timestamps, I/O ----------
def _ts():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

def _ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def _has_csv(folder):
    return any(Path(folder).glob("*.csv"))

# ---------- Synthetic spectra generator (only if needed) ----------
def generate_synthetic_spectra(spectra_dir, n_files=12, n_points=2000, fmin=0.5, fmax=500.0, seed=123):
    # Builds PSD-like curves with geometric peaks per ratio; adds noise; saves CSVs.
    # Peaks families follow $f_k=\theta \cdot r^k$ with $r\in\{1.5,\varphi\}$ and diverse $\theta$ across files.
    rng = np.random.default_rng(seed)
    _ensure_dir(spectra_dir)
    f = np.exp(np.linspace(np.log(fmin), np.log(fmax), n_points))
    for i in range(n_files):
        r_main = 1.5
        r_alt = (1.0 + math.sqrt(5.0)) / 2.0
        theta_main = np.exp(rng.uniform(np.log(1.2), np.log(3.5)))
        theta_alt = np.exp(rng.uniform(np.log(0.9), np.log(2.2)))
        ks = np.arange(-8, 9, dtype=int)
        peaks_main = theta_main * (r_main ** ks.astype(float))
        peaks_alt = theta_alt * (r_alt ** ks.astype(float))
        s = np.zeros_like(f)
        def add_peaks(peaks, amp, width):
            nonlocal s
            for pk in peaks:
                # Lorentzian-like bump centered at pk
                s += amp * (width**2) / ((f - pk)**2 + width**2)
        # Mix two families with random amplitudes
        amp1 = rng.uniform(1.5, 3.5)
        amp2 = rng.uniform(0.8, 2.0)
        width1 = rng.uniform(0.3, 1.2)
        width2 = rng.uniform(0.3, 1.2)
        add_peaks(peaks_main, amp1, width1)
        add_peaks(peaks_alt, amp2, width2)
        # Add background slope and noise
        s += 0.2 * (f**-0.3)
        s += rng.normal(0.0, 0.02, size=f.shape)
        s = np.maximum(s, 0.0)
        df = pd.DataFrame({"freq": f, "value": s})
        out = Path(spectra_dir) / ("synthetic_window_%02d.csv" % (i+1))
        df.to_csv(out, index=False)

# ---------- Column detection and reading ----------
def detect_columns(df, fcol=None, scol=None):
    if fcol and scol and fcol in df and scol in df:
        return fcol, scol
    cols = list(df.columns)
    lower = [c.lower() for c in cols]
    cf = None
    cs = None
    for i, c in enumerate(lower):
        if c in ("f", "freq", "frequency", "hz"):
            cf = cols[i]
        if c in ("s", "pow", "power", "amp", "amplitude", "psd", "value", "mag"):
            cs = cols[i]
    if cf and cs:
        return cf, cs
    # Fallback: first two numeric columns
    nums = []
    for c in cols:
        try:
            pd.to_numeric(df[c], errors="raise")
            nums.append(c)
        except Exception:
            pass
    if len(nums) &gt;= 2:
        return nums[0], nums[1]
    if len(cols) &gt;= 2:
        return cols[0], cols[1]
    raise ValueError("Could not detect frequency and spectrum columns.")

def read_spectrum_csv(path, fcol=None, scol=None):
    df = pd.read_csv(path)
    fcol, scol = detect_columns(df, fcol, scol)
    f = pd.to_numeric(df[fcol], errors="coerce").to_numpy()
    s = pd.to_numeric(df[scol], errors="coerce").to_numpy()
    m = np.isfinite(f) & np.isfinite(s)
    f = f[m]
    s = s[m]
    order = np.argsort(f)
    return f[order], s[order], fcol, scol

# ---------- Calibration core ----------
def theta_grid_from_range(fmin, fmax, r, kmin, kmax, n_theta):
    log_r = math.log(r)
    lo = math.log(max(1e-18, fmin)) - kmax * log_r
    hi = math.log(max(1e-18, fmax)) - kmin * log_r
    if not math.isfinite(lo) or not math.isfinite(hi) or hi &lt;= lo:
        lo = math.log(max(1e-18, fmin)) - 5.0 * log_r
        hi = math.log(max(1e-18, fmax)) + 5.0 * log_r
    return np.exp(np.linspace(lo, hi, int(max(2, n_theta))))

def captured_power(theta, r, kmin, kmax, f, s):
    ks = np.arange(int(kmin), int(kmax) + 1, dtype=int)
    fk = theta * (r ** ks.astype(float))
    fmin = float(f[0])
    fmax = float(f[-1])
    mask = (fk &gt;= fmin) & (fk &lt;= fmax)
    if not np.any(mask):
        return 0.0
    fk_valid = fk[mask]
    s_interp = np.interp(fk_valid, f, s)
    return float(np.sum(s_interp))

def calibrated_power(f, s, r, kmin, kmax, n_theta):
    tg = theta_grid_from_range(float(np.min(f)), float(np.max(f)), r, kmin, kmax, n_theta)
    best_val = -1.0
    best_theta = None
    for theta in tg:
        val = captured_power(theta, r, kmin, kmax, f, s)
        if val &gt; best_val:
            best_val = val
            best_theta = float(theta)
    if best_val &lt; 0.0:
        best_val = 0.0
        best_theta = np.nan
    return best_val, best_theta

# ---------- Simple stats ----------
def mean_ci_normal(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n == 0:
        return (np.nan, np.nan, (np.nan, np.nan))
    m = float(np.mean(x))
    sd = float(np.std(x, ddof=1)) if n &gt; 1 else 0.0
    se = sd / math.sqrt(n) if n &gt; 1 else np.nan
    z = 1.959963984540054
    lo = m - z * se if se == se else np.nan
    hi = m + z * se if se == se else np.nan
    return (m, se, (lo, hi))

def t_stat_p_one_sided_from_mean(x, mu0=0.0):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n &lt; 2:
        return (np.nan, np.nan)
    m = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    if sd == 0.0:
        t = math.inf if m &gt; mu0 else -math.inf
        p = 0.0 if m &gt; mu0 else 1.0
        return (t, p)
    se = sd / math.sqrt(n)
    t = (m - mu0) / se
    p = 0.5 * math.erfc(t / math.sqrt(2.0))
    return (t, p)

def wilson_interval(w, n):
    if n == 0:
        return (np.nan, np.nan)
    z = 1.959963984540054
    phat = w / n
    denom = 1.0 + (z*z)/n
    center = (phat + (z*z)/(2*n)) / denom
    radius = (z/denom) * math.sqrt((phat*(1-phat)/n) + (z*z)/(4*n*n))
    return (max(0.0, center - radius), min(1.0, center + radius))

def permutation_pvalue_signed_mean(diffs, n_perm=2000, seed=123):
    rng = np.random.default_rng(seed)
    diffs = np.asarray(diffs, dtype=float)
    diffs = diffs[np.isfinite(diffs)]
    n = diffs.size
    if n == 0:
        return np.nan
    obs = float(np.mean(diffs))
    flips = rng.choice([-1.0, 1.0], size=(n_perm, n))
    perm_means = (flips * diffs).mean(axis=1)
    return float(np.mean(perm_means &gt;= obs))

# ---------- Report builder ----------
def write_html_report(out_dir, title, meta, tables, figs):
    parts = []
    parts.append("")
    parts.append("")
    parts.append(title)
    parts.append("")
    parts.append("")
    parts.append("")
    parts.append("body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;margin:24px}")
    parts.append("h1{margin-bottom:0}.sub{color:#666;margin-top:4px}")
    parts.append("table{border-collapse:collapse;margin:16px 0;width:100%}")
    parts.append("th,td{border:1px solid #ddd;padding:8px;text-align:left}")
    parts.append("th{background:#f7f7f7}")
    parts.append(".note{color:#444;font-size:0.95em}")
    parts.append("")
    parts.append("
# "+title+"
")
    parts.append("Generated: "+time.strftime("%Y-%m-%d %H:%M:%S")+"")
    if meta:
        parts.append("
## Meta
")
        for k, v in meta.items():
            parts.append("")
        parts.append("
| "+str(v)+" |
")
    for tab in tables:
        parts.append("
## "+tab["title"]+"
")
        parts.append("")
        for h in tab["headers"]:
            parts.append("")
        parts.append("")
        for row in tab["rows"]:
            parts.append("")
            for cell in row:
                parts.append("")
            parts.append("")
        parts.append("
| "+h+" |
| ---- |
| "+str(cell)+" |
")
    for fig in figs:
        parts.append("
## "+fig["title"]+"
")
        parts.append("")
    parts.append("
All math uses inline LaTeX $...$; $r=1.5$ är ett exakt designvärde i denna modell.
")
    parts.append("")
    html = "\n".join(parts)
    out_html = os.path.join(out_dir, "rp9_calibrated_report.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return out_html

# ---------- Core runner ----------
def run_rp9_colab(
    spectra_dir="./spectra",
    out_root="./",
    kmin=-8,
    kmax=8,
    n_theta=200,
    alt_ratio="phi",
    compare_sqrt2=True,
    permutations=5000,
    seed=123
):
    r_main = 1.5
    if str(alt_ratio).lower() in ("phi", "varphi", "golden", "goldenratio"):
        r_alt = (1.0 + math.sqrt(5.0)) / 2.0
    elif str(alt_ratio).lower() in ("sqrt2", "root2"):
        r_alt = math.sqrt(2.0)
    else:
        r_alt = float(str(alt_ratio).replace(",", "."))

    if not Path(spectra_dir).exists():
        _ensure_dir(spectra_dir)
    if not _has_csv(spectra_dir):
        generate_synthetic_spectra(spectra_dir)

    files = sorted(glob.glob(str(Path(spectra_dir) / "*.csv")))
    if not files:
        raise RuntimeError("No CSV files after generation. Aborting.")

    outdir = os.path.join(out_root, "rp9_calib_out_" + _ts())
    _ensure_dir(outdir)

    rows = []
    U = []
    D = []
    P1 = []
    P2 = []
    T1 = []
    T2 = []
    names = []

    for path in files:
        try:
            f, s, fcol_used, scol_used = read_spectrum_csv(path, None, None)
        except Exception as ex:
            continue
        if f.size &lt; 10:
            continue
        p_main, th_main = calibrated_power(f, s, r_main, kmin, kmax, n_theta)
        p_alt, th_alt = calibrated_power(f, s, r_alt, kmin, kmax, n_theta)
        u = (p_main / p_alt - 1.0) if p_alt &gt; 0.0 else np.nan
        d = p_main - p_alt
        rows.append({
            "window": Path(path).name,
            "fcol": fcol_used,
            "scol": scol_used,
            "Pstar_1p5": p_main,
            "Theta_1p5": th_main,
            "Pstar_alt": p_alt,
            "Theta_alt": th_alt,
            "U": u,
            "D": d
        })
        U.append(u)
        D.append(d)
        P1.append(p_main)
        P2.append(p_alt)
        T1.append(th_main)
        T2.append(th_alt)
        names.append(Path(path).name)

    if len(rows) == 0:
        raise RuntimeError("No valid windows processed.")

    df_res = pd.DataFrame(rows)
    res_csv = str(Path(outdir) / "rp9_calibrated_results.csv")
    df_res.to_csv(res_csv, index=False)

    mU, seU, ciU = mean_ci_normal(U)
    tU, pU = t_stat_p_one_sided_from_mean(U, mu0=0.0)
    wins = int(np.sum(np.asarray(P1) &gt; np.asarray(P2)))
    n = int(len(U))
    phat = wins / n if n &gt; 0 else np.nan
    wil_lo, wil_hi = wilson_interval(wins, n)
    p_perm = permutation_pvalue_signed_mean(D, n_perm=permutations, seed=seed)

    extra = None
    if compare_sqrt2 and abs(r_alt - math.sqrt(2.0)) &gt; 1e-12:
        P_s2 = []
        U_s2 = []
        D_s2 = []
        r2 = math.sqrt(2.0)
        for path in files:
            f, s, _, _ = read_spectrum_csv(path)
            p_s2, _th = calibrated_power(f, s, r2, kmin, kmax, n_theta)
            P_s2.append(p_s2)
            # align by index
        for i in range(len(P1)):
            p15 = P1[i]
            ps2 = P_s2[i]
            U_s2.append((p15 / ps2 - 1.0) if ps2 &gt; 0.0 else np.nan)
            D_s2.append(p15 - ps2)
        mU2, seU2, ciU2 = mean_ci_normal(U_s2)
        tU2, pU2 = t_stat_p_one_sided_from_mean(U_s2, mu0=0.0)
        wins2 = int(np.sum(np.asarray(P1) &gt; np.asarray(P_s2)))
        n2 = int(len(U_s2))
        phat2 = wins2 / n2 if n2 &gt; 0 else np.nan
        wil_lo2, wil_hi2 = wilson_interval(wins2, n2)
        p_perm2 = permutation_pvalue_signed_mean(D_s2, n_perm=permutations, seed=seed)
        extra = {
            "mU2": float(mU2), "seU2": float(seU2), "ciU2": [float(ciU2[0]), float(ciU2[1])],
            "tU2": float(tU2), "pU2": float(pU2), "wins2": int(wins2), "n2": int(n2),
            "phat2": float(phat2), "wil_lo2": float(wil_lo2), "wil_hi2": float(wil_hi2),
            "p_perm2": float(p_perm2)
        }

    summary = {
        "n_windows": int(len(names)),
        "kmin": int(kmin),
        "kmax": int(kmax),
        "n_theta": int(n_theta),
        "r_main": float(1.5),
        "r_alt": float(r_alt),
        "mean_U": float(mU),
        "se_U": float(seU),
        "ci95_U_lo": float(ciU[0]),
        "ci95_U_hi": float(ciU[1]),
        "t_U": float(tU),
        "p_U_one_sided": float(pU),
        "wins": int(wins),
        "n": int(n),
        "phat_wins": float(phat),
        "wilson95_lo": float(wil_lo),
        "wilson95_hi": float(wil_hi),
        "p_perm": float(p_perm)
    }
    if extra is not None:
        summary["sqrt2_comparison"] = extra

    res_json = str(Path(outdir) / "rp9_calibrated_summary.json")
    with open(res_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    figs = []

    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(x=np.asarray(U), name="U = P*1.5/P*alt - 1", nbinsx=60, opacity=0.75))
    fig1.update_layout(title="Distribution of U across windows", xaxis_title="U", yaxis_title="Count")
    p1 = str(Path(outdir) / "fig_U_hist.html")
    fig1.write_html(p1, include_plotlyjs="cdn")
    fig1.show()
    figs.append({"title":"Distribution of $U$", "file":os.path.basename(p1)})

    y_means = [mU]
    y_err_lo = [mU - (summary["ci95_U_lo"] if summary["ci95_U_lo"] == summary["ci95_U_lo"] else mU)]
    y_err_hi = [(summary["ci95_U_hi"] if summary["ci95_U_hi"] == summary["ci95_U_hi"] else mU) - mU]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=["U (1.5 vs alt)"], y=y_means, error_y=dict(type="data", array=y_err_hi, arrayminus=y_err_lo, visible=True)))
    fig2.update_layout(title="Mean U with 95% CI", xaxis_title="Metric", yaxis_title="Mean(U)")
    p2 = str(Path(outdir) / "fig_U_mean.html")
    fig2.write_html(p2, include_plotlyjs="cdn")
    fig2.show()
    figs.append({"title":"Mean $U$ with $95\\%$ CI", "file":os.path.basename(p2)})

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=np.asarray(P2), y=np.asarray(P1), mode="markers", name="Windows"))
    if len(P2) &gt; 0:
        mmax = float(max(np.max(P2), np.max(P1)))
        fig3.add_shape(type="line", x0=0, y0=0, x1=mmax, y1=mmax)
    fig3.update_layout(title="P* (alt) vs P* (1.5) per window", xaxis_title="P* (alt)", yaxis_title="P* (1.5)")
    p3 = str(Path(outdir) / "fig_scatter_pstar.html")
    fig3.write_html(p3, include_plotlyjs="cdn")
    fig3.show()
    figs.append({"title":"$P^*$ comparison per window", "file":os.path.basename(p3)})

    fig4 = go.Figure()
    if len(T1) &gt; 0:
        fig4.add_trace(go.Histogram(x=np.log10(np.asarray(T1) + 1e-18), name="log10(theta*) 1.5", nbinsx=60, opacity=0.75))
    if len(T2) &gt; 0:
        fig4.add_trace(go.Histogram(x=np.log10(np.asarray(T2) + 1e-18), name="log10(theta*) alt", nbinsx=60, opacity=0.75))
    fig4.update_layout(title="Calibrated theta* distributions (log10)", barmode="overlay", xaxis_title="log10(theta*)", yaxis_title="Count")
    p4 = str(Path(outdir) / "fig_theta_hist.html")
    fig4.write_html(p4, include_plotlyjs="cdn")
    fig4.show()
    figs.append({"title":"Calibrated $\\theta^*$ distributions (log10)", "file":os.path.basename(p4)})

    title = "RP9 Calibrated Dominance Report " + _ts()
    meta = {
        "spectra_dir": str(Path(spectra_dir).resolve()),
        "outdir": str(Path(outdir).resolve()),
        "k_range": "["+str(kmin)+","+str(kmax)+"]",
        "n_theta": int(n_theta),
        "r_main": 1.5,
        "r_alt": float(r_alt),
        "windows": int(len(names))
    }
    out_html = write_html_report(outdir, title, meta, [{
        "title": "Primary metrics ($U$ mean, $95\\%$ CI, $t/p$; win-rate and permutation)",
        "headers": ["Metric", "$\\bar{U}$", "$SE$", "$95\\%$ CI (lo, hi)", "$t$ (vs $0$)", "$p$ (one-sided)", "wins", "n", "$\\hat{p}$", "$95\\%$ CI (lo, hi)", "$p_{perm}$"],
        "rows": [[
            "1.5 vs alt",
            "{:.6g}".format(mU),
            "{:.6g}".format(seU),
            "["+"{:.6g}".format(summary["ci95_U_lo"])+", "+"{:.6g}".format(summary["ci95_U_hi"])+"]",
            "{:.6g}".format(tU),
            "{:.6g}".format(pU),
            str(wins),
            str(n),
            "{:.6g}".format(phat),
            "["+"{:.6g}".format(wil_lo)+" , "+"{:.6g}".format(wil_hi)+"]",
            "{:.6g}".format(p_perm)
        ]]
    }] , figs)

    print("OK: Results saved.")
    print("CSV:", res_csv)
    print("JSON:", res_json)
    print("HTML report:", out_html)

    try:
        display(HTML("
### RP9 Calibrated Dominance Report
"))
        display(IFrame(src=out_html, width="100%", height=600))
    except Exception:
        try:
            webbrowser.open("file://" + os.path.abspath(out_html))
        except Exception:
            pass

    return {
        "results_csv": res_csv,
        "summary_json": res_json,
        "report_html": out_html,
        "summary": summary
    }

# === Execute now with safe defaults ===
result = run_rp9_colab()
result
````

---

````python
import shutil
import time
from google.colab import files

# Skapar en zip av alla mappar som börjar med "rp9_calib_out"
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
zip_name = f"rp9_outputs_{timestamp}.zip"

# Packar ihop alla mappar som matchar mönstret
shutil.make_archive("rp9_outputs_tmp", 'zip', '.', base_dir='.')
shutil.move("rp9_outputs_tmp.zip", zip_name)

print(f"Skapad zip: {zip_name}")

# Ladda hem
files.download(zip_name)
