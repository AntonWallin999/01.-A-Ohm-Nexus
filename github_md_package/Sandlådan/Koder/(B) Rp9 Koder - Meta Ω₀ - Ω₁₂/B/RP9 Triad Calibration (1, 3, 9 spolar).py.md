````python
  
# === RP9 Triad Calibration (1, 3, 9 spolar) — Colab One-Cell Runner (self-contained) ===

# - Kör allt i en cell. Ingen manuell konfiguration krävs.

# - Skalar upp halva–halva-relationen $r=1.5$ från 1 spole → 3 spolar → 9 spolar.

# - För varje m ∈ {1,3,9} beräknas kalibrerad effekt $P^*$ för form $H_{r,m}$ med bandcentra

#   $f_{i,k}=\theta\cdot r^{k + \frac{i}{m}}$, $i=0,\dots,m-1$, $k\in[k_{\min},k_{\max}]$.

# - (Valfritt) jämförelse mot alternativ $r_{alt}$ (t.ex. $\varphi$) med samma triad/ennead-offsetstruktur.

# - Genererar syntetiska spektra om ./spectra är tomt (så körningen ALLTID fungerar).

# - Skriver ut CSV, JSON, HTML-rapport och figurer i tidsstämplad mapp: ./rp9_tri_calib_out_YYYY-mm-dd_HH-MM-SS

# - All matematik i kommentarer använder korrekt formaterad inline-LaTeX: $r=1.5$, $\varphi=\frac{1+\sqrt{5}}{2}$, $\sqrt{2}$, $P^*$, $U$, $D$, $\theta^*$.

  

import sys, subprocess, os, math, json, time, glob, zipfile

from pathlib import Path

  

def _pip_install(pkgs):

    cmd = [sys.executable, "-m", "pip", "install"] + pkgs

    subprocess.run(cmd, check=True)

  

# Installera beroenden (Colab/ren miljö)

_pip_install(["numpy", "pandas", "plotly", "reportlab", "kaleido"])

  

import numpy as np

import pandas as pd

import plotly.graph_objects as go

import plotly.io as pio

from IPython.display import IFrame, display, HTML

from reportlab.lib.pagesizes import A4

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib import colors

  

# ---------- Hjälpfunktioner ----------

def _ts():

    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

  

def _ensure_dir(p):

    Path(p).mkdir(parents=True, exist_ok=True)

  

def _has_csv(folder):

    return any(Path(folder).glob("*.csv"))

  

# ---------- Syntetiska spektra (endast om ./spectra saknar CSV) ----------

def generate_synthetic_spectra(spectra_dir, n_files=12, n_points=2000, fmin=0.5, fmax=500.0, seed=123):

    # Skapar PSD-liknande kurvor med blandade peak-familjer (inkl. $r=1.5$ och $\varphi$), bakgrund och brus.

    rng = np.random.default_rng(seed)

    _ensure_dir(spectra_dir)

    f = np.exp(np.linspace(np.log(fmin), np.log(fmax), n_points))

    for i in range(n_files):

        r_main = 1.5

        r_phi = (1.0 + math.sqrt(5.0)) / 2.0

        theta_main = np.exp(rng.uniform(np.log(1.2), np.log(3.5)))

        theta_phi = np.exp(rng.uniform(np.log(0.9), np.log(2.2)))

        ks = np.arange(-8, 9, dtype=int)

        peaks_main = theta_main * (r_main ** ks.astype(float))

        peaks_phi = theta_phi * (r_phi ** ks.astype(float))

        s = np.zeros_like(f)

        def add_peaks(peaks, amp, width):

            nonlocal s

            for pk in peaks:

                s += amp * (width**2) / ((f - pk)**2 + width**2)

        amp1 = rng.uniform(1.5, 3.5)

        amp2 = rng.uniform(0.8, 2.0)

        width1 = rng.uniform(0.3, 1.2)

        width2 = rng.uniform(0.3, 1.2)

        add_peaks(peaks_main, amp1, width1)

        add_peaks(peaks_phi, amp2, width2)

        s += 0.2 * (f**-0.3)

        s += rng.normal(0.0, 0.02, size=f.shape)

        s = np.maximum(s, 0.0)

        df = pd.DataFrame({"freq": f, "value": s})

        out = Path(spectra_dir) / ("synthetic_window_%02d.csv" % (i+1))

        df.to_csv(out, index=False)

  

# ---------- Kolumn-detektering ----------

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

    nums = []

    for c in cols:

        try:

            pd.to_numeric(df[c], errors="raise")

            nums.append(c)

        except Exception:

            pass

    if len(nums) >= 2:

        return nums[0], nums[1]

    if len(cols) >= 2:

        return cols[0], cols[1]

    raise ValueError("Kunde inte detektera frekvens- och spektralkolumner.")

  

def read_spectrum_csv(path, fcol=None, scol=None):

    df = pd.read_csv(path)

    fcol, scol = detect_columns(df, fcol, scol)

    f = pd.to_numeric(df[fcol], errors="coerce").to_numpy()

    s = pd.to_numeric(df[scol], errors="coerce").to_numpy()

    m = np.isfinite(f) & np.isfinite(s)

    f = f[m]; s = s[m]

    order = np.argsort(f)

    return f[order], s[order], fcol, scol

  

# ---------- Triad/Ennead-kärna ----------

def theta_grid_from_range_multi(fmin, fmax, r, kmin, kmax, m, n_theta):

    # För m serier med fraktionella skift $\frac{i}{m}$ gäller att frekvenserna multipliceras med $g_i=r^{i/m}$.

    # Det mest extrema skiftet är $g_{\max}=r^{(m-1)/m}$. Säkra $\theta$-området så att alla $f_{i,k}$ kan landa inom [fmin,fmax].

    g_min = r**0.0

    g_max = r**((m-1)/m) if m > 1 else 1.0

    log_r = math.log(r)

    lo = math.log(max(1e-18, fmin)) - kmax * log_r - math.log(max(g_max, 1.0))

    hi = math.log(max(1e-18, fmax)) - kmin * log_r - math.log(min(g_min, 1.0))

    if not math.isfinite(lo) or not math.isfinite(hi) or hi <= lo:

        lo = math.log(max(1e-18, fmin)) - 5.0 * log_r

        hi = math.log(max(1e-18, fmax)) + 5.0 * log_r

    return np.exp(np.linspace(lo, hi, int(max(2, n_theta))))

  

def captured_power_multi(theta, r, kmin, kmax, f, s, m):

    # $P(\theta;H_{r,m},S)=\sum_{i=0}^{m-1}\sum_{k=k_{\min}}^{k_{\max}} S\!\left(\theta\cdot r^{k+i/m}\right)$.

    ks = np.arange(int(kmin), int(kmax) + 1, dtype=int).astype(float)

    base = theta * (r ** ks)  # storlek: |ks|

    fmin = float(f[0]); fmax = float(f[-1])

    total = 0.0

    for i in range(m):

        gi = r ** (i / m)

        fk = base * gi

        mask = (fk >= fmin) & (fk <= fmax)

        if np.any(mask):

            s_interp = np.interp(fk[mask], f, s)

            total += float(np.sum(s_interp))

    return total

  

def calibrated_power_multi(f, s, r, kmin, kmax, n_theta, m):

    tg = theta_grid_from_range_multi(float(np.min(f)), float(np.max(f)), r, kmin, kmax, m, n_theta)

    best_val = -1.0; best_theta = None

    for theta in tg:

        val = captured_power_multi(theta, r, kmin, kmax, f, s, m)

        if val > best_val:

            best_val = val; best_theta = float(theta)

    if best_val < 0.0:

        best_val = 0.0; best_theta = np.nan

    return best_val, best_theta

  

# ---------- Statistik ----------

def mean_ci_normal(x):

    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]

    n = x.size

    if n == 0: return (np.nan, np.nan, (np.nan, np.nan))

    m = float(np.mean(x))

    sd = float(np.std(x, ddof=1)) if n > 1 else 0.0

    se = sd / math.sqrt(n) if n > 1 else np.nan

    z = 1.959963984540054

    lo = m - z * se if se == se else np.nan

    hi = m + z * se if se == se else np.nan

    return (m, se, (lo, hi))

  

def t_stat_p_one_sided_from_mean(x, mu0=0.0):

    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]

    n = x.size

    if n < 2: return (np.nan, np.nan)

    m = float(np.mean(x)); sd = float(np.std(x, ddof=1))

    if sd == 0.0:

        t = math.inf if m > mu0 else -math.inf

        p = 0.0 if m > mu0 else 1.0

        return (t, p)

    se = sd / math.sqrt(n); t = (m - mu0) / se

    p = 0.5 * math.erfc(t / math.sqrt(2.0))

    return (t, p)

  

def wilson_interval(w, n):

    if n == 0: return (np.nan, np.nan)

    z = 1.959963984540054

    phat = w / n

    denom = 1.0 + (z*z)/n

    center = (phat + (z*z)/(2*n)) / denom

    radius = (z/denom) * math.sqrt((phat*(1-phat)/n) + (z*z)/(4*n*n))

    return (max(0.0, center - radius), min(1.0, center + radius))

  

def permutation_pvalue_signed_mean(diffs, n_perm=2000, seed=123):

    rng = np.random.default_rng(seed)

    diffs = np.asarray(diffs, dtype=float); diffs = diffs[np.isfinite(diffs)]

    n = diffs.size

    if n == 0: return np.nan

    obs = float(np.mean(diffs))

    flips = rng.choice([-1.0, 1.0], size=(n_perm, n))

    perm_means = (flips * diffs).mean(axis=1)

    return float(np.mean(perm_means >= obs))

  

# ---------- Rapportbyggare ----------

def write_html_report(out_dir, title, meta, tables, figs_by_m):

    parts = []

    parts.append("<!doctype html><html><head><meta charset='utf-8'><title>"+title+"</title>")

    parts.append("<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>")

    parts.append("<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;margin:24px}h1{margin-bottom:0}.sub{color:#666;margin-top:4px}table{border-collapse:collapse;margin:16px 0;width:100%}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#f7f7f7}.note{color:#444;font-size:0.95em}h2{margin-top:28px}</style>")

    parts.append("</head><body>")

    parts.append("<h1>"+title+"</h1><div class='sub'>Generated: "+time.strftime("%Y-%m-%d %H:%M:%S")+"</div>")

    # Meta

    if meta:

        parts.append("<h2>Meta</h2><table><tbody>")

        for k,v in meta.items():

            parts.append("<tr><th>"+str(k)+"</th><td>"+str(v)+"</td></tr>")

        parts.append("</tbody></table>")

    # Tables

    for tab in tables:

        parts.append("<h2>"+tab["title"]+"</h2><table><thead><tr>")

        for h in tab["headers"]:

            parts.append("<th>"+h+"</th>")

        parts.append("</tr></thead><tbody>")

        for row in tab["rows"]:

            parts.append("<tr>"+ "".join("<td>"+str(c)+"</td>" for c in row) + "</tr>")

        parts.append("</tbody></table>")

    # Figures

    for m, figs in figs_by_m.items():

        parts.append(f"<h2>Figurer för m = {m}</h2>")

        for fig in figs:

            parts.append("<h3>"+fig["title"]+f" (m={m})</h3>")

            parts.append("<iframe src='"+fig["file"]+"' style='width:100%;height:520px;border:1px solid #ddd;border-radius:8px'></iframe>")

    parts.append("<p class='note'>All math uses inline LaTeX $...$; skalförhållandet är alltid $r=1.5$ (halva–halva). Alternativ används endast för kontrastmått $U$ och $D$.</p>")

    parts.append("</body></html>")

    out_html = os.path.join(out_dir, "rp9_tri_calibrated_report.html")

    with open(out_html, "w", encoding="utf-8") as f:

        f.write("\n".join(parts))

    return out_html

  

# ---------- Huvudkörning ----------

def run_rp9_triad(

    spectra_dir="./spectra",

    out_root="./",

    kmin=-8,

    kmax=8,

    n_theta=200,

    m_list=(1,3,9),

    alt_ratio="phi",           # 'phi', 'sqrt2', eller numeriskt som '1.6'; alt jämförs med samma m-offsetstruktur

    compare_sqrt2=False,

    permutations=5000,

    seed=123

):

    r_main = 1.5

    # Alternativt r

    if alt_ratio is None:

        r_alt = None

    else:

        low = str(alt_ratio).lower()

        if low in ("phi","varphi","golden","goldenratio"):

            r_alt = (1.0 + math.sqrt(5.0)) / 2.0

        elif low in ("sqrt2","root2"):

            r_alt = math.sqrt(2.0)

        else:

            r_alt = float(str(alt_ratio).replace(",", "."))

  

    # Säkerställ input

    if not Path(spectra_dir).exists():

        _ensure_dir(spectra_dir)

    if not _has_csv(spectra_dir):

        generate_synthetic_spectra(spectra_dir)

  

    files = sorted(glob.glob(str(Path(spectra_dir) / "*.csv")))

    if not files:

        raise RuntimeError("Ingen CSV hittades i ./spectra (och generering misslyckades).")

  

    outdir = os.path.join(out_root, "rp9_tri_calib_out_" + _ts())

    _ensure_dir(outdir)

  

    # Resultatstrukturer

    per_window_rows = []

    per_m_stats = {}

  

    for m in m_list:

        U_list = []; D_list = []; Pm_list = []; Pa_list = []; Tm_list = []; Ta_list = []; W_names = []

        for path in files:

            try:

                f, s, fcol_used, scol_used = read_spectrum_csv(path, None, None)

            except Exception:

                continue

            if f.size < 10:

                continue

            # Huvud: r=1.5, m

            p_main, th_main = calibrated_power_multi(f, s, r_main, kmin, kmax, n_theta, m)

            # Alt (om satt)

            if r_alt is not None:

                p_alt, th_alt = calibrated_power_multi(f, s, r_alt, kmin, kmax, n_theta, m)

                u = (p_main / p_alt - 1.0) if p_alt > 0.0 else np.nan

                d = p_main - p_alt

            else:

                p_alt, th_alt, u, d = np.nan, np.nan, np.nan, np.nan

  

            per_window_rows.append({

                "m": m,

                "window": Path(path).name,

                "fcol": fcol_used,

                "scol": scol_used,

                "Pstar_main": p_main,

                "Theta_main": th_main,

                "Pstar_alt": p_alt,

                "Theta_alt": th_alt,

                "U": u,

                "D": d

            })

            Pm_list.append(p_main); Pa_list.append(p_alt); Tm_list.append(th_main); Ta_list.append(th_alt); W_names.append(Path(path).name)

            if r_alt is not None:

                U_list.append(u); D_list.append(d)

  

        # Sammanfatta per m

        stats = {"n_windows": int(len(Pm_list)), "m": int(m), "kmin": int(kmin), "kmax": int(kmax), "n_theta": int(n_theta), "r_main": float(r_main)}

        if r_alt is not None:

            mU, seU, ciU = mean_ci_normal(U_list)

            tU, pU = t_stat_p_one_sided_from_mean(U_list, mu0=0.0)

            wins = int(np.sum(np.asarray(Pm_list) > np.asarray(Pa_list)))

            nW = len(Pm_list)

            phat = wins / nW if nW>0 else np.nan

            wil_lo, wil_hi = wilson_interval(wins, nW)

            p_perm = permutation_pvalue_signed_mean(D_list, n_perm=permutations, seed=seed)

            stats.update({

                "r_alt": float(r_alt),

                "mean_U": float(mU),

                "se_U": float(seU),

                "ci95_U_lo": float(ciU[0]),

                "ci95_U_hi": float(ciU[1]),

                "t_U": float(tU),

                "p_U_one_sided": float(pU),

                "wins": int(wins),

                "n": int(nW),

                "phat_wins": float(phat),

                "wilson95_lo": float(wil_lo),

                "wilson95_hi": float(wil_hi),

                "p_perm": float(p_perm)

            })

        per_m_stats[m] = stats

  

        # Figurer per m (om alt finns)

        figs = []

        if r_alt is not None and len(U_list) > 0:

            # Histogram av U

            fig1 = go.Figure()

            fig1.add_trace(go.Histogram(x=np.asarray(U_list), nbinsx=60, opacity=0.8))

            fig1.update_layout(title=f"Distribution of U (m={m})", xaxis_title="U", yaxis_title="Count")

            p1 = str(Path(outdir) / f"m{m}_fig_U_hist.html")

            fig1.write_html(p1, include_plotlyjs="cdn"); fig1.show()

            figs.append({"title": "Histogram av $U$", "file": os.path.basename(p1)})

            # Mean U + 95% CI

            y_means = [per_m_stats[m]["mean_U"]]

            y_err_lo = [per_m_stats[m]["mean_U"] - per_m_stats[m]["ci95_U_lo"]]

            y_err_hi = [per_m_stats[m]["ci95_U_hi"] - per_m_stats[m]["mean_U"]]

            fig2 = go.Figure()

            fig2.add_trace(go.Bar(x=[f"U (m={m})"], y=y_means, error_y=dict(type="data", array=y_err_hi, arrayminus=y_err_lo, visible=True)))

            fig2.update_layout(title=f"Mean U with 95% CI (m={m})", xaxis_title="Metric", yaxis_title="Mean(U)")

            p2 = str(Path(outdir) / f"m{m}_fig_U_mean.html")

            fig2.write_html(p2, include_plotlyjs="cdn"); fig2.show()

            figs.append({"title": "Medel $U$ med $95\\%$ CI", "file": os.path.basename(p2)})

            # Scatter P* alt vs P* main

            Pa_arr = np.asarray(Pa_list); Pm_arr = np.asarray(Pm_list)

            fig3 = go.Figure()

            fig3.add_trace(go.Scatter(x=Pa_arr, y=Pm_arr, mode="markers", name="Windows"))

            if len(Pa_arr)>0:

                mmax = float(max(np.max(Pa_arr), np.max(Pm_arr)))

                fig3.add_shape(type="line", x0=0, y0=0, x1=mmax, y1=mmax)

            fig3.update_layout(title=f"P* (alt) vs P* (1.5) (m={m})", xaxis_title="P* (alt)", yaxis_title="P* (1.5)")

            p3 = str(Path(outdir) / f"m{m}_fig_scatter_pstar.html")

            fig3.write_html(p3, include_plotlyjs="cdn"); fig3.show()

            figs.append({"title": "$P^*$: alt vs $1.5$", "file": os.path.basename(p3)})

            # Theta* (log10) för main och alt

            fig4 = go.Figure()

            Tm_arr = np.asarray(Tm_list); Ta_arr = np.asarray(Ta_list)

            if np.isfinite(Tm_arr).any():

                fig4.add_trace(go.Histogram(x=np.log10(Tm_arr + 1e-18), name="1.5", opacity=0.6))

            if np.isfinite(Ta_arr).any():

                fig4.add_trace(go.Histogram(x=np.log10(Ta_arr + 1e-18), name="alt", opacity=0.6))

            fig4.update_layout(title=f"Theta* distributions (log10) (m={m})", barmode="overlay", xaxis_title="log10(theta*)", yaxis_title="Count")

            p4 = str(Path(outdir) / f"m{m}_fig_theta_hist.html")

            fig4.write_html(p4, include_plotlyjs="cdn"); fig4.show()

            figs.append({"title": "Kalibrerade $\\theta^*$-fördelningar (log10)", "file": os.path.basename(p4)})

        per_m_stats[m]["_figs"] = figs

  

    # Skriv per-fönster CSV

    df_perwin = pd.DataFrame(per_window_rows)

    res_csv = str(Path(outdir) / "rp9_tri_calibrated_results.csv")

    df_perwin.to_csv(res_csv, index=False)

  

    # Skriv per-m JSON-sammanfattning

    summary = {

        "kmin": int(kmin), "kmax": int(kmax), "n_theta": int(n_theta),

        "r_main": float(r_main), "m_list": list(map(int, m_list)),

        "alt_ratio": (None if r_alt is None else float(r_alt))

    }

    for m in m_list:

        summary[f"m{m}"] = per_m_stats[m]

    res_json = str(Path(outdir) / "rp9_tri_calibrated_summary.json")

    with open(res_json, "w", encoding="utf-8") as f:

        json.dump(summary, f, indent=2)

  

    # Tabeller för rapport

    tables = []

    if r_alt is not None:

        headers = ["m", "$\\bar{U}$", "$SE$", "$95\\%$ CI (lo, hi)", "$t$", "$p$ (ensidigt)", "wins", "n", "$\\hat{p}$", "$95\\%$ CI (lo, hi)", "$p_{perm}$"]

        rows = []

        for m in m_list:

            st = per_m_stats[m]

            if "mean_U" in st:

                rows.append([

                    str(m),

                    "{:.6g}".format(st["mean_U"]),

                    "{:.6g}".format(st["se_U"]),

                    f"[{st['ci95_U_lo']:.6g}, {st['ci95_U_hi']:.6g}]",

                    "{:.6g}".format(st["t_U"]),

                    "{:.6g}".format(st["p_U_one_sided"]),

                    str(st.get("wins","")),

                    str(st.get("n","")),

                    "{:.6g}".format(st.get("phat_wins", float("nan"))),

                    f"[{st.get('wilson95_lo', float('nan')):.3f}, {st.get('wilson95_hi', float('nan')):.3f}]",

                    "{:.6g}".format(st.get("p_perm", float("nan")))

                ])

        tables.append({"title": "Kontrastmått mot alternativ form (samma m-offsetstruktur)", "headers": headers, "rows": rows})

  

    # Meta

    meta = {

        "spectra_dir": str(Path(spectra_dir).resolve()),

        "outdir": str(Path(outdir).resolve()),

        "k_range": f"[{kmin},{kmax}]",

        "n_theta": int(n_theta),

        "r_main": 1.5,

        "alt_ratio": (None if r_alt is None else float(r_alt)),

        "modes": ",".join(map(str, m_list))

    }

    figs_by_m = { m: per_m_stats[m]["_figs"] for m in m_list }

    title = "RP9 Triad/Ennead Calibrated Dominance Report " + _ts()

    out_html = write_html_report(outdir, title, meta, tables, figs_by_m)

  

    # PDF-samlingsblad (kort)

    styles = getSampleStyleSheet()

    styleH = styles["Heading1"]; styleH2 = styles["Heading2"]; styleN = styles["BodyText"]

    pdf_path = str(Path(outdir) / "RP9_Triad_Report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)

    elements = []

    elements.append(Paragraph("RP9 Triad/Ennead – Samlingsblad", styleH)); elements.append(Spacer(1, 12))

    elements.append(Paragraph("Grunddata", styleH2))

    elements.append(Paragraph(

        f"spectra_dir: {meta['spectra_dir']}<br/>"

        f"k ∈ [{kmin},{kmax}], n_theta = {n_theta}<br/>"

        f"r_main = 1.5; alt_ratio = {meta['alt_ratio']}", styleN))

    if r_alt is not None:

        tdata = [["m", "mean U", "95% CI", "t", "p (ens)", "wins/n", "p_hat", "Wilson 95%", "p_perm"]]

        for m in m_list:

            st = per_m_stats[m]

            tdata.append([

                str(m),

                f"{st['mean_U']:.4f}",

                f"[{st['ci95_U_lo']:.4f}, {st['ci95_U_hi']:.4f}]",

                f"{st['t_U']:.2f}",

                f"{st['p_U_one_sided']:.2e}",

                f"{st['wins']}/{st['n']}",

                f"{st['phat_wins']:.3f}",

                f"[{st['wilson95_lo']:.2f}, {st['wilson95_hi']:.2f}]",

                f"{st['p_perm']:.4f}"

            ])

        tab = Table(tdata, hAlign="LEFT")

        tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("GRID",(0,0),(-1,-1),0.5,colors.grey)]))

        elements.append(Paragraph("Kontrasttabell (1.5 vs alt) per m", styleH2))

        elements.append(tab)

    doc.build(elements)

  

    # Visa sammanfattning

    print("OK: Triad/Ennead-resultat sparade.")

    print("CSV:", res_csv)

    print("JSON:", res_json)

    print("HTML:", out_html)

    print("PDF:", pdf_path)

  

    try:

        display(HTML("<h3>RP9 Triad/Ennead – Rapport</h3>"))

        display(IFrame(src=out_html, width="100%", height=600))

    except Exception:

        pass

  

    return {

        "results_csv": res_csv,

        "summary_json": res_json,

        "report_html": out_html,

        "report_pdf": pdf_path,

        "summary": summary

    }

  

# === Kör nu med säkra standarder ===

result = run_rp9_triad(

    spectra_dir="./spectra",      # lägg dina CSV här om du har egna, annars genereras syntetiska

    m_list=(1,3,9),               # 1 spole, 3 spolar (triad), 9 spolar (ennead)

    alt_ratio="phi",              # jämför mot samma m-struktur men med r_alt = φ

    compare_sqrt2=False,          # kan utökas vid behov

    permutations=5000,

    seed=123

)

result
````


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
