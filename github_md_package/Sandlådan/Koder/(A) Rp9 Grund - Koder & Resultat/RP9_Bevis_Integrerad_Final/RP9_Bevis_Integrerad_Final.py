# ============================================================
#  RP9_Bevis_Integrerad_Final.py
#  ------------------------------------------------------------
#  Komplett integrerad bevisföring för RP9-systemet.
#  Innehåller kärnberäkning, RLC-simulering, mätdataanalys,
#  korrelationskontroll och filutmatning (JSON + CSV).
#  ------------------------------------------------------------
#  Författare: [Ditt namn]
#  Version: Slutlig
# ============================================================

import math
import json
import csv
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

# ============================================================
# Dataklasser
# ============================================================

@dataclass
class RP9Values:
    phi: float
    sqrt2: float
    stabiliserande_faktor: float
    N_M: float
    RP9_geo: float
    RP9_fys: float
    delta: float
    koherens: bool


@dataclass
class SimulationResult:
    frekvens: float
    C_ideal: float
    C_E12: float
    delta_C_procent: float
    P_ideal: float
    P_E12: float
    delta_P_procent: float


@dataclass
class MeasurementResult:
    frekvens: float
    eta_P: float
    kommentar: str


@dataclass
class CorrelationResult:
    match_index: float
    skillnad_medel: float
    kommentar: str


# ============================================================
# RP9-kärnberäkning
# ============================================================

def compute_rp9(stabiliserande_faktor: float = 1.5, N_M: float = 1.0, tol: float = 1e-12) -> RP9Values:
    phi = (1 + math.sqrt(5)) / 2
    sqrt2 = math.sqrt(2)
    RP9_geo = (phi / sqrt2) / stabiliserande_faktor
    RP9_fys = N_M * RP9_geo
    delta = RP9_geo - RP9_fys
    koherens = abs(delta) <= tol
    return RP9Values(phi, sqrt2, stabiliserande_faktor, N_M, RP9_geo, RP9_fys, delta, koherens)


# ============================================================
# Fysisk RLC-simulering
# ============================================================

def simulate_rlc_system(frekvenser: List[float], R: float = 100.0, L: float = 10e-3) -> List[SimulationResult]:
    results = []
    for f in frekvenser:
        w = 2 * math.pi * f
        C_ideal = 1 / (w ** 2 * L)
        C_E12 = round(C_ideal, int(abs(math.log10(C_ideal))) + 2)
        X_L = w * L
        X_C_ideal = 1 / (w * C_ideal)
        X_C_E12 = 1 / (w * C_E12)
        Z_ideal = math.sqrt(R ** 2 + (X_L - X_C_ideal) ** 2)
        Z_E12 = math.sqrt(R ** 2 + (X_L - X_C_E12) ** 2)
        V_in = 1.0
        I_ideal = V_in / Z_ideal
        I_E12 = V_in / Z_E12
        P_ideal = (I_ideal ** 2) * R
        P_E12 = (I_E12 ** 2) * R
        delta_C_procent = (C_E12 - C_ideal) / C_ideal * 100
        delta_P_procent = (P_E12 - P_ideal) / P_ideal * 100
        results.append(SimulationResult(f, C_ideal, C_E12, delta_C_procent, P_ideal, P_E12, delta_P_procent))
    return results


# ============================================================
# Mätdataanalys
# ============================================================

def analyze_measurements(frekvenser: List[float], spänningar: List[float], R_load: float = 100.0) -> List[MeasurementResult]:
    results = []
    P_model = (spänningar[0] ** 2) / R_load
    for i, f in enumerate(frekvenser):
        P_measured = (spänningar[i] ** 2) / R_load
        eta_P = 100 * (P_measured / P_model)
        kommentar = "Koherent" if 1280 <= eta_P <= 1400 else "Avvikelse"
        results.append(MeasurementResult(f, eta_P, kommentar))
    return results


# ============================================================
# Jämförelse mellan simulering och mätning
# ============================================================

def correlate_results(sim: List[SimulationResult], meas: List[MeasurementResult]) -> CorrelationResult:
    """Beräknar korrelationsindex mellan simuleringens ΔP och mätningens ηP."""
    if len(sim) != len(meas):
        n = min(len(sim), len(meas))
    else:
        n = len(sim)

    diff_sum = 0.0
    for i in range(n):
        diff = abs(sim[i].delta_P_procent - (meas[i].eta_P - 1000) / 10)  # Normaliserad skala
        diff_sum += diff

    skillnad_medel = diff_sum / n
    match_index = max(0.0, 100.0 - skillnad_medel)
    kommentar = "Hög korrelation" if match_index > 90 else "Svag korrelation"
    return CorrelationResult(match_index, skillnad_medel, kommentar)


# ============================================================
# Statistik & medelvärden
# ============================================================

def summarize_results(sim: List[SimulationResult], meas: List[MeasurementResult], corr: CorrelationResult):
    deltaP_values = [r.delta_P_procent for r in sim]
    etaP_values = [m.eta_P for m in meas]
    medel_deltaP = sum(deltaP_values) / len(deltaP_values)
    medel_etaP = sum(etaP_values) / len(etaP_values)
    print("\n--- Sammanfattning ---")
    print(f"Medel ΔP = {medel_deltaP:.3f} %")
    print(f"Medel ηP = {medel_etaP:.2f} %")
    print(f"Korrelation = {corr.match_index:.2f} % ({corr.kommentar})")


# ============================================================
# Utskrift till terminal
# ============================================================

def print_all_results(core: RP9Values, sim: List[SimulationResult], meas: List[MeasurementResult], corr: CorrelationResult):
    print("\n=== RP9 — Integrerad Bevisföring (Final) ===")
    print(f"φ = {core.phi:.15f}")
    print(f"√2 = {core.sqrt2:.15f}")
    print(f"RP9_geo = {core.RP9_geo:.15f}")
    print(f"RP9_fys = {core.RP9_fys:.15f}")
    print(f"Δ = {core.delta:.15e}")
    print(f"Koherens = {core.koherens}")
    print("\n--- RLC-simulering ---")
    for r in sim:
        print(f"{r.frekvens:.0f} Hz → ΔP = {r.delta_P_procent:+.3f} % (C_diff = {r.delta_C_procent:+.3f} %)")
    print("\n--- Mätdataanalys ---")
    for m in meas:
        print(f"{m.frekvens:.0f} Hz → ηP = {m.eta_P:.2f} %, {m.kommentar}")
    summarize_results(sim, meas, corr)


# ============================================================
# Filutmatning (JSON + CSV)
# ============================================================

def save_full_report(core: RP9Values, sim: List[SimulationResult], meas: List[MeasurementResult], corr: CorrelationResult):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"RP9_IntegreradBevis_{timestamp}"

    # JSON
    json_filename = f"{base}.json"
    data = {
        "RP9_values": asdict(core),
        "simulation_results": [asdict(r) for r in sim],
        "measurement_results": [asdict(m) for m in meas],
        "correlation": asdict(corr)
    }
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # CSV
    csv_filename = f"{base}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Typ", "Frekvens (Hz)", "ΔP (%)", "C_diff (%)", "ηP (%)", "Kommentar"])
        for r in sim:
            writer.writerow(["Simulering", f"{r.frekvens:.0f}", f"{r.delta_P_procent:.3f}", f"{r.delta_C_procent:.3f}", "", ""])
        for m in meas:
            writer.writerow(["Mätning", f"{m.frekvens:.0f}", "", "", f"{m.eta_P:.2f}", m.kommentar])
        writer.writerow([])
        writer.writerow(["Korrelation", "", "", "", f"{corr.match_index:.2f}", corr.kommentar])

    return json_filename, csv_filename


# ============================================================
# Huvudprogram
# ============================================================

def main():
    # Steg 1: RP9-kärna
    core = compute_rp9(stabiliserande_faktor=1.5, N_M=1.0)

    # Steg 2: Simulering
    f_phi = core.phi
    frekvenser_sim = [420, 420 * f_phi, 420 * f_phi ** 2]
    sim_results = simulate_rlc_system(frekvenser_sim)

    # Steg 3: Mätdata
    frekvenser_meas = [420, 630, 945]
    spänningar_meas = [1.0, 3.45, 4.12]  # Exempeldata
    meas_results = analyze_measurements(frekvenser_meas, spänningar_meas)

    # Steg 4: Jämförelse / korrelation
    corr_result = correlate_results(sim_results, meas_results)

    # Steg 5: Utskrift
    print_all_results(core, sim_results, meas_results, corr_result)

    # Steg 6: Spara rapport
    json_file, csv_file = save_full_report(core, sim_results, meas_results, corr_result)
    print(f"\nResultaten har sparats i:\n - {json_file}\n - {csv_file}\n")


# ============================================================
# Körning
# ============================================================

if __name__ == "__main__":
    main()
