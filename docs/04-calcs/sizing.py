"""FieldNode sizing calculations, FND-CAL-001 v0.2 (TRL 3, decisions of FND-DDR-002 applied).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md (tags in brackets, for example
[A3]) and writes docs/04-calcs/results.csv. The script imports PARAMS and derived() from
cad/src/model.py and builds the model once for part volumes, so the geometry here is the
geometry in the STEP files and in drawing FND-DWG-001. It also reads bom/bom.csv and
budget_usd in project.yaml. First-principles paper estimates; nothing here is measured.
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad/src"))
from model import PARAMS as P, derived, build_parts, bracket_geometry, build_shield, shield_geometry  # noqa: E402

D = derived(P)
rows = []


def out(tag, text):
    print(f"[{tag}] {text}")


def res(rid, value, target, status):
    rows.append((rid, value, target, status))


# =============================================================== assumptions
# Energy chain (as FND-PRC-001 v0.2, now stated once here)
PANEL_W = 6.0            # W at STC
PSH_WORST = 2.0          # peak sun hours on the tilted panel, worst month
PANEL_DERATE = 0.80      # heat, dust, angle
ETA_MPPT = 0.85          # 1S LiFePO4 charger
ETA_CHG = 0.95           # cell charge efficiency
ETA_RAIL = 0.90          # rail converters
CELL_V, CELL_AH = 3.2, 6.0
USABLE = 0.80            # of nameplate, as R6 states
CAP_COLD = 0.70          # discharge capacity at -20 C, typical LiFePO4 cell data
CAP_EOL = 0.80           # end of life capacity
AUTONOMY_REQ = 5.0       # days (R6)
ALLOW_REQ = 0.100        # W (R7); published sensor allowance (FND-DDR-002)
# Core: SX1262 at +14 dBm about 45 mA; receive 4.6 mA (Semtech datasheet); controller awake 8 mA
I_TX, I_RX, I_MCU = 45e-3, 4.6e-3, 8e-3
T_RX, N_RX, T_AWAKE = 0.10, 2, 0.5          # s per RX window, windows per uplink, controller awake per report
I_SLEEP = 33e-6          # whole node, sleep plus power board quiescent
V_CORE = 3.3
INTERVAL_MIN = 15.0      # default reporting interval (DDR-001, D6)
# Radio
PAYLOAD, OVERHEAD = 20, 13
BW, CR, NPRE = 125e3, 1, 8
TTN_S = 30.0             # s per node per day (TTN fair use)
EU_DC = 0.01             # EU868 sub-band duty cycle
TX_DBM, ANT_DBI_NODE, ANT_DBI_GW = 14.0, 2.0, 2.0
LOSS_NODE, LOSS_GW = 0.5, 2.0               # dB cable and connector
NF = 6.0                 # dB receiver noise figure (gateway and node alike, assumption)
SNR_LIM = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
F_MHZ, D_KM = 868.0, 2.0
HB, HB_LOW = 30.0, 15.0  # gateway antenna height, m (Hata validity starts at 30 m)
FADE = 10.0              # dB margin for fading, foliage and clutter
# Store and forward
REC_B = 32               # bytes per stored reading (20 payload, 4 time, 2 status, 2 CRC, padding)
FLASH_B = 16 * 1024 * 1024
OUTAGE_D = 30
MAXPL_EU = {7: 222, 8: 222, 9: 115, 10: 51}  # EU868 max application payload at 125 kHz
BATCH_REC = 24           # bytes per reading when batched (payload plus time offset)
# Thermal
H_COMB = 10.0            # W/m2K combined convection and radiation, still air
ALPHA = {"clean": 0.45, "dusty": 0.70}      # light grey polycarbonate
SHIELD_F = 0.25          # share of solar gain reaching a box under a ventilated white shield (assumed, as WWT-CAL-001)
ALBEDO = 0.20
SHIELD_COST = 8.0        # hot-climate option, BOM line 14 (FND-DDR-002); mass from the model below
SHIELD_FIX_KG = 0.02     # screws and standoffs for the shield
T_DESIGN_MAX = 60.0      # C, R3 interior limit
P_BASE_INT = 0.10        # W average dissipation inside the box outside charging
CP = {"enclosure": 1200.0, "cell": 1000.0, "boards": 900.0, "asa": 1300.0}   # J/kgK
T_CHG_MIN, T_CHG_MAX = 0.0, 45.0
BETA_VMP = -0.0035       # 1/K, panel Vmp temperature coefficient (typical crystalline silicon)
VMP_STC = 9.0            # V, "9 V class" panel (FND-DDR-002); 6 V class kept for comparison
VMP_STC_OLD = 6.0
NOCT_RISE = 30.0         # K, panel cell above ambient at 1000 W/m2, mounted in the open
VIN_MIN = 5.0            # V, typical minimum input of the charger class (to confirm per part at TRL 4)
# Wind and mounting
RHO, V_GUST = 1.225, 35.0
CD_PANEL, CD_BOX = 1.2, 1.3
T_BAND = 1000.0          # N preload per band clamp (assumed, to be measured)
MU = 0.20                # friction, V-block and band on a galvanized pole
E_AL, FY_AL = 69e3, 150.0                   # MPa, 6063-T5 class flat bar
# Mass (bought parts, typical catalogue masses, kg)
M_BOUGHT = {"panel": 0.55, "cell": 0.15, "holder_fuse_ntc": 0.03, "power": 0.05, "ctrl": 0.02,
            "antenna": 0.06, "ports": 0.06, "glands": 0.03, "vent": 0.01, "bands": 0.08, "hardware": 0.10}
RHO_KG = {"pc": 1.20e-6, "al": 2.70e-6, "asa": 1.07e-6}     # kg/mm3

# =============================================================== A. Core consumption and energy budget
toa_cache = {}


def toa(sf, pl=PAYLOAD + OVERHEAD, bw=BW):
    """LoRa time on air, s (Semtech AN1200.13), explicit header, CRC on, CR 4/5."""
    de = 1 if (sf >= 11 and bw == 125e3) else 0
    ts = 2 ** sf / bw
    n = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16) / (4 * (sf - 2 * de))) * (CR + 4), 0)
    return (NPRE + 4.25) * ts + n * ts


reports = round(24 * 60 / INTERVAL_MIN)
q_report = I_TX * toa(9) + I_RX * T_RX * N_RX + I_MCU * T_AWAKE          # A s
core_mah = (q_report * reports + I_SLEEP * 86400) / 3.6
core_wh = core_mah * V_CORE / 1000
out("A1", f"per report {q_report * 1000:.1f} mA s at SF9; {reports:.0f} reports {q_report * reports / 3.6:.2f} mAh; "
          f"sleep {I_SLEEP * 86400 / 3.6:.2f} mAh; core {core_mah:.2f} mAh = {core_wh * 1000:.1f} mWh/day")

harv = [PANEL_W * PSH_WORST]
harv.append(harv[-1] * PANEL_DERATE)
harv.append(harv[-1] * ETA_MPPT)
harv.append(harv[-1] * ETA_CHG)
stored = harv[-1]
out("A2", "worst month: panel x sun {:.1f}, panel out {:.2f}, charger out {:.2f}, stored {:.2f} Wh/day".format(*harv))

e_usable = CELL_V * CELL_AH * USABLE
allow_max = (e_usable / AUTONOMY_REQ * ETA_RAIL - core_wh) / 24     # W that gives exactly 5.0 days
out("A3", f"usable {e_usable:.2f} Wh; sensor allowance that gives exactly {AUTONOMY_REQ:.0f} days: {allow_max * 1000:.1f} mW")


def draw(allow_w):
    return (allow_w * 24 + core_wh) / ETA_RAIL


for tag, a in (("A4", 0.115), ("A5", ALLOW_REQ)):
    d = draw(a)
    out(tag, f"at {a * 1000:.0f} mW: delivered {a * 24 + core_wh:.2f}, drawn {d:.2f} Wh/day; stored/drawn {stored / d:.2f}; "
             f"surplus {stored - d:.2f} Wh/day; autonomy {e_usable / d:.2f} d nominal, {e_usable * CAP_COLD / d:.2f} d at -20 C, "
             f"{e_usable * CAP_EOL / d:.2f} d at end of life; refill after 5 sunless days {AUTONOMY_REQ * d / (stored - d):.1f} worst-month days")
d100 = draw(ALLOW_REQ)
# largest sensor load that stays energy neutral in the worst month
allow_neutral = (stored * ETA_RAIL - core_wh) / 24
out("A6", f"largest energy-neutral sensor load in the worst month {allow_neutral * 1000:.0f} mW")
# siblings' loads quoted in their TRL 2 notes (mW) against the allowances
SIBLINGS = {"AirStreet": 45, "NoiseMap": 21, "FloodGauge (10 s sampling)": 7, "WellSense": 0.75,
            "HeatMap Node": 1, "SlopeWatch": 1, "CurbCount": 300}
out("A7", "published allowance 100 mW (FND-DDR-002); sibling loads within it: " + ", ".join(f"{k} {v:g} mW" for k, v in SIBLINGS.items() if v <= 100)
    + "; above: " + ", ".join(f"{k} {v:g} mW" for k, v in SIBLINGS.items() if v > 100))

# =============================================================== B. Airtime (R9), link (R8), store and forward (R10)
tab = []
for sf in range(7, 13):
    t = toa(sf)
    per_day = t * reports
    min_int = math.ceil(t * 24 * 60 / TTN_S)                       # minutes, to stay within 30 s/day
    tab.append((sf, t, per_day, min_int))
    out("B1", f"SF{sf}: {t * 1000:.1f} ms per uplink, {per_day:.1f} s/day at {INTERVAL_MIN:.0f} min; "
              f"shortest interval within {TTN_S:.0f} s/day {min_int} min; EU868 1 % off-time {t / EU_DC:.0f} s")
RULE = {sf: max(INTERVAL_MIN, float(mi)) for sf, _, _, mi in tab}         # firmware airtime rule (FND-DDR-002)
worst_rule = max(t * 24 * 60 / RULE[sf] for sf, t, _, _ in tab)
out("B1b", "firmware rule on The Things Network: interval " + ", ".join(f"SF{sf} {RULE[sf]:.0f} min" for sf in RULE)
    + f"; largest airtime under the rule {worst_rule:.1f} s/day")


def hata_suburban(f, hb, hm, d):
    lf = math.log10(f)
    a = (1.1 * lf - 0.7) * hm - (1.56 * lf - 0.8)
    lu = 69.55 + 26.16 * lf - 13.82 * math.log10(hb) - a + (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
    return lu - 2 * math.log10(f / 28) ** 2 - 5.4


hm = (D["whip_tip"] + P["z0"] - 20) / 2 / 1000                          # m, middle of the whip
eirp = TX_DBM - LOSS_NODE + ANT_DBI_NODE
out("B2", f"EIRP {eirp:.1f} dBm = {eirp - 2.15:.2f} dBm ERP (EU868 limit 14 dBm ERP); node antenna height {hm:.2f} m")
for sf in (7, 9, 10, 12):
    sens = -174 + 10 * math.log10(BW) + NF + SNR_LIM[sf]
    budget = eirp + ANT_DBI_GW - LOSS_GW - sens
    pl2 = hata_suburban(F_MHZ, HB, hm, D_KM)
    # range at which path loss plus fade margin equals the budget
    lo, hi = 0.1, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if hata_suburban(F_MHZ, HB, hm, mid) + FADE < budget else (lo, mid)
    r30 = lo
    lo, hi = 0.1, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if hata_suburban(F_MHZ, HB_LOW, hm, mid) + FADE < budget else (lo, mid)
    out("B3", f"SF{sf}: sensitivity {sens:.1f} dBm, budget {budget:.1f} dB; Hata suburban at {D_KM:.0f} km, gateway {HB:.0f} m: "
              f"{pl2:.1f} dB, margin {budget - pl2:.1f} dB; range with {FADE:.0f} dB fade margin {r30:.1f} km "
              f"(gateway {HB:.0f} m), {lo:.1f} km (gateway {HB_LOW:.0f} m, outside Hata's range)")
    if sf == 9:
        link9 = (budget, pl2, budget - pl2, r30, lo)

per_day_b = reports * REC_B
out("B4", f"store: {per_day_b:,} B/day; {OUTAGE_D} days {per_day_b * OUTAGE_D / 1024:.0f} kB; "
          f"16 MB flash holds {FLASH_B / per_day_b:,.0f} days")
backlog = reports * OUTAGE_D
for sf in (7, 9):
    k = MAXPL_EU[sf] // BATCH_REC
    t_b = toa(sf, k * BATCH_REC + OVERHEAD)
    n_up = math.ceil(backlog / k)
    spare = TTN_S - reports * toa(sf)
    dc_day = 86400 * EU_DC - reports * toa(sf)                          # one sub-band, 1 %
    out("B5", f"SF{sf}: {backlog:.0f} readings after {OUTAGE_D} days, {k} per uplink, {n_up} uplinks of {t_b * 1000:.0f} ms = "
              f"{n_up * t_b:.0f} s; spare fair-use airtime {spare:.1f} s/day -> {n_up * t_b / spare:.0f} days; "
              f"under the 1 % duty cycle alone {n_up * t_b / dc_day:.2f} days")

# =============================================================== C. Enclosure temperature (R2, R3) and charging window (R4, R5)
ew, ed, eh = (v / 1000 for v in P["enc"])
FACES = {  # name: (outward normal, area m2, grid of sample points in mm)
    "front": ((0, -1, 0), ew * eh), "left": ((-1, 0, 0), ed * eh), "right": ((1, 0, 0), ed * eh),
    "top": ((0, 0, 1), ew * ed), "bottom": ((0, 0, -1), ew * ed)}
A_EXP = sum(a for _, a in FACES.values())
UA = H_COMB * A_EXP
x0, x1 = -P["enc"][0] / 2, P["enc"][0] / 2
y0, y1 = D["enc_front"], D["enc_back"]
zb, zt = D["enc_bot"], D["enc_top"]
g = np.linspace(0.02, 0.98, 21)


def face_points(name):
    u, v = np.meshgrid(g, g)
    u, v = u.ravel(), v.ravel()
    if name == "front":
        return np.c_[x0 + u * (x1 - x0), np.full_like(u, y0), zb + v * (zt - zb)]
    if name in ("left", "right"):
        return np.c_[np.full_like(u, x0 if name == "left" else x1), y0 + u * (y1 - y0), zb + v * (zt - zb)]
    return np.c_[x0 + u * (x1 - x0), y0 + v * (y1 - y0), np.full_like(u, zt if name == "top" else zb)]


PTS = {k: face_points(k) for k in FACES}
tr = math.radians(P["tilt"])
PC = np.array([0.0, D["panel_cy"], D["panel_cz"]])
PU, PV = np.array([1.0, 0, 0]), np.array([0, math.cos(tr), math.sin(tr)])
PN = np.cross(PU, PV)                                                     # (0, -sin t, cos t): faces the sky and -Y
HALF_U, HALF_V = P["panel"][0] / 2, P["panel"][1] / 2


def shaded_fraction(name, s):
    pts = PTS[name]
    sn = s @ PN
    if abs(sn) < 1e-9:
        return 0.0
    lam = ((PC - pts) @ PN) / sn
    q = pts + lam[:, None] * s
    du, dv = (q - PC) @ PU, (q - PC) @ PV
    hit = (lam > 0) & (np.abs(du) <= HALF_U) & (np.abs(dv) <= HALF_V)
    return float(hit.mean())


def meinel(h):
    if h <= math.radians(2):
        return 0.0
    am = 1 / math.sin(h)
    return 1353.0 * 0.7 ** (am ** 0.678)


def solar_gain(s, dni, alpha, shield=False):
    """Absorbed solar power on the exposed faces, W, for sun unit vector s (x east, y north, z up)."""
    h = math.asin(max(-1, min(1, s[2])))
    dhi = 0.1 * dni
    ghi = dni * max(0.0, s[2]) + dhi
    q = 0.0
    for name, (n, a) in FACES.items():
        cos_i = float(np.dot(s, n))
        direct = dni * cos_i * (1 - shaded_fraction(name, s)) if cos_i > 0 and h > 0 else 0.0
        if name == "top":
            diff = dhi * 0.5                                  # the panel hides about half the sky from the top
        elif name == "bottom":
            diff = ALBEDO * ghi
        else:
            diff = 0.5 * dhi + 0.5 * ALBEDO * ghi
        q += alpha * a * (direct + diff)
    return q * (SHIELD_F if shield else 1.0)


def sun_vec(lat, dec, omega):
    la, de = math.radians(lat), math.radians(dec)
    e = -math.cos(de) * math.sin(omega)
    n = math.cos(la) * math.sin(de) - math.sin(la) * math.cos(de) * math.cos(omega)
    u = math.sin(la) * math.sin(de) + math.cos(la) * math.cos(de) * math.cos(omega)
    return np.array([e, n, u])


# thermal mass inside and of the box, from the model
parts = build_parts()
vol = {k: v.volume for k, v in parts.items()}
m_box = (vol["body"] + vol["lid"]) * RHO_KG["pc"]
m_mplate = vol["mplate"] * RHO_KG["asa"]          # printed ASA (BOM line 11)
C_TH = (m_box * CP["enclosure"] + (M_BOUGHT["cell"] + M_BOUGHT["holder_fuse_ntc"]) * CP["cell"]
        + (M_BOUGHT["power"] + M_BOUGHT["ctrl"]) * CP["boards"] + m_mplate * CP["asa"])
out("C1", f"exposed area {A_EXP:.4f} m2 (back against the plate); UA {UA:.3f} W/K; heat capacity {C_TH:.0f} J/K; "
          f"time constant {C_TH / UA / 60:.0f} min")
out("C1b", f"panel plan overhang beyond the lid {D['overhang_front']:.1f} mm; front edge {D['clear_top']:.1f} mm above the enclosure top")

# worst sun position at 45 C ambient (steady state, envelope)
worst = {}
for case, al in ALPHA.items():
    best = (0, None)
    for hdeg in range(10, 91, 5):
        for az in range(-180, 181, 10):                     # az 0: sun due equator side (in front)
            h, a = math.radians(hdeg), math.radians(az)
            s = np.array([math.cos(h) * math.sin(a), -math.cos(h) * math.cos(a), math.sin(h)])
            q = solar_gain(s, meinel(h), al)
            if q > best[0]:
                best = (q, (hdeg, az))
    worst[case] = best
    out("C2", f"{case}: worst sun position elevation {best[1][0]} deg, azimuth {best[1][1]} deg from the front normal: "
              f"{best[0]:.1f} W absorbed, steady rise {best[0] / UA:.1f} K, {45 + (best[0] + P_BASE_INT) / UA:.1f} C inside at 45 C")
s_front = np.array([0, -math.cos(math.radians(60)), math.sin(math.radians(60))])
out("C2b", f"top face shaded by the panel with the sun 60 deg high in front: {shaded_fraction('top', s_front) * 100:.0f} %; "
           f"front face {shaded_fraction('front', s_front) * 100:.0f} %")
rise_worst = {k: (v[0] + P_BASE_INT) / UA for k, v in worst.items()}
rise_worst_sh = {k: (SHIELD_F * v[0] + P_BASE_INT) / UA for k, v in worst.items()}
t_hot_site = T_DESIGN_MAX - rise_worst["dusty"]
out("C2c", f"worst sun position with the shield at 45 C: {45 + rise_worst_sh['clean']:.1f} C clean, {45 + rise_worst_sh['dusty']:.1f} C dusty; "
           f"without it the dusty box stays at {T_DESIGN_MAX:.0f} C or less up to {t_hot_site:.1f} C ambient, so the shield "
           f"is needed where the design maximum exceeds {math.floor(t_hot_site / 5) * 5:.0f} C")
T_HOT_SITE = math.floor(t_hot_site / 5) * 5


def design_day(lat, dec, tmin, tmax, alpha, shield=False, days=3, dt=60.0):
    """Hourly-varying clear day; returns peak inside temperature, charge hours and energy stored (Wh)."""
    T = (tmin + tmax) / 2
    peak, hours_ok, e_ok, e_all, hours_sun = -99, 0.0, 0.0, 0.0, 0.0
    n = int(86400 / dt)
    for day in range(days):
        for i in range(n):
            t = i * dt / 3600                                             # solar time, h
            ta = (tmin + tmax) / 2 + (tmax - tmin) / 2 * math.cos(2 * math.pi * (t - 15) / 24)
            s = sun_vec(lat, dec, math.radians(15 * (t - 12)))
            if s[1] > 0 and lat < 0:
                pass
            h = math.asin(max(-1, min(1, s[2])))
            dni = meinel(h)
            # panel faces the equator (-Y in the northern hemisphere)
            poa = dni * max(0.0, float(s @ PN)) + 0.1 * dni * (1 + math.cos(tr)) / 2 + ALBEDO * (dni * max(0, s[2]) + 0.1 * dni) * (1 - math.cos(tr)) / 2
            p_in = PANEL_W * poa / 1000 * PANEL_DERATE
            ok = T_CHG_MIN <= T <= T_CHG_MAX and p_in > 0
            q_int = P_BASE_INT + (p_in * (1 - ETA_MPPT) + p_in * ETA_MPPT * (1 - ETA_CHG) if ok else 0.0)
            q = solar_gain(s, dni, alpha, shield) + q_int
            T += dt * (q - UA * (T - ta)) / C_TH
            if day == days - 1:
                peak = max(peak, T)
                if p_in > 0:
                    hours_sun += dt / 3600
                    e_all += p_in * ETA_MPPT * ETA_CHG * dt / 3600
                    if ok:
                        hours_ok += dt / 3600
                        e_ok += p_in * ETA_MPPT * ETA_CHG * dt / 3600
    return peak, hours_ok, e_ok, e_all, hours_sun


HOT = (28.6, 21.5, 30.0, 45.0)        # Delhi-like latitude, late May, 30 to 45 C, clear
COLD = (50.0, -20.0, -20.0, -10.0)    # 50 deg N, late January, -20 to -10 C, clear
hot = {}
for case in ("clean", "dusty"):
    for sh in (False, True):
        r = design_day(*HOT, ALPHA[case], sh)
        hot[(case, sh)] = r
        out("C3", f"hot day {HOT[2]:.0f} to {HOT[3]:.0f} C, lat {HOT[0]} N: {case}{', with shield' if sh else ', no shield'}: "
                  f"peak inside {r[0]:.1f} C; charging allowed {r[1]:.1f} of {r[4]:.1f} sun h; stored {r[2]:.1f} of {r[3]:.1f} Wh possible")
for case in ("clean", "dusty"):
    deficit = d100 - hot[(case, False)][2]
    out("C3b", f"{case}, no shield: a run of hot clear days loses {deficit:.2f} Wh/day at 100 mW; from full the cell lasts "
               f"{e_usable / deficit:.1f} days; with the shield the day ends {hot[(case, True)][2] - d100:+.1f} Wh")
for case in ("clean", "dusty"):
    r = design_day(HOT[0], HOT[1], T_HOT_SITE - 15, T_HOT_SITE, ALPHA[case], False)
    out("C3c", f"base node, no shield, clear day {T_HOT_SITE - 15:.0f} to {T_HOT_SITE:.0f} C: {case}: peak inside {r[0]:.1f} C; "
               f"charging allowed {r[1]:.1f} of {r[4]:.1f} sun h; stored {r[2]:.1f} Wh against {d100:.2f} Wh drawn")
cold = {}
for case in ("clean", "dusty"):
    r = design_day(*COLD, ALPHA[case], False)
    cold[case] = r
    out("C4", f"cold day {COLD[2]:.0f} to {COLD[3]:.0f} C, lat {COLD[0]} N: {case}: peak inside {r[0]:.1f} C; "
              f"charging allowed {r[1]:.1f} of {r[4]:.1f} sun h; stored {r[2]:.1f} of {r[3]:.1f} Wh possible")
# daytime ambient at which the sunlit box first reaches 0 C (clean, peak rise on the cold day)
rise_cold = cold["clean"][0] - COLD[3]
out("C5", f"peak rise above the day's maximum ambient on the cold day {rise_cold:.1f} K: the cell reaches 0 C only on days "
          f"whose maximum is above about {-rise_cold:.0f} C")
# panel voltage headroom on the hot day
t_panel = HOT[3] + NOCT_RISE
vmp_hot = VMP_STC * (1 + BETA_VMP * (t_panel - 25))
vmp_old = VMP_STC_OLD * (1 + BETA_VMP * (t_panel - 25))
out("C6", f"panel at {t_panel:.0f} C: 9 V class Vmp {vmp_hot:.2f} V against a {VIN_MIN:.1f} V charger minimum input ({vmp_hot - VIN_MIN:.2f} V headroom); "
          f"the 6 V class panel it replaces gave {vmp_old:.2f} V ({vmp_old - VIN_MIN:.2f} V)")

# =============================================================== F1. Mass (R14), needed for the wind case
_pr = P["pole_od"] / 2
band_vol = len(D["clamps"]) * math.pi * ((_pr + 2) ** 2 - _pr ** 2) * P["band_w"]    # massing rings, counted as bought bands
m_made = {"enclosure body and lid (PC)": m_box, "internal plate (ASA)": m_mplate,
          "bracket (Al)": vol["bracket"] * RHO_KG["al"],
          "back plate and V-blocks (Al)": (vol["mount"] - band_vol) * RHO_KG["al"]}
m_total = sum(m_made.values()) + sum(M_BOUGHT.values())
out("F1", "made parts: " + ", ".join(f"{k} {v:.2f}" for k, v in m_made.items())
    + f" kg; bought parts {sum(M_BOUGHT.values()):.2f} kg; total {m_total:.2f} kg (base node)")
SG = shield_geometry()
SHIELD_KG = build_shield().volume * RHO_KG["al"] + SHIELD_FIX_KG
out("F1b", f"sun shield option {SG['w']:.0f} x {SG['d']:.0f} x {SG['h']:.0f} mm, {P['shield_t']} mm aluminium, {SG['area_m2']:.4f} m2: "
           f"{SHIELD_KG:.2f} kg with fixings; hot-climate node {m_total + SHIELD_KG:.2f} kg")

# =============================================================== D. Wind and mounting (R13, R12)
q = 0.5 * RHO * V_GUST ** 2
F_p = q * CD_PANEL * D["panel_area_m2"]
F_e = q * CD_BOX * FACES["front"][1]
F_side = q * CD_BOX * FACES["left"][1]
out("D1", f"q {q:.0f} Pa; panel {F_p:.1f} N normal to the panel; enclosure {F_e:.1f} N front-on, {F_side:.1f} N side-on")
zl, zu = D["clamps"]
pan = np.array([0, D["panel_cy"], D["panel_cz"]])
box_c = np.array([0, D["enc_yc"], D["enc_zc"]])


def moment_lower(loads):
    """Moment about the X axis through the lower clamp, N m (positive tips the top away from the pole, to -Y)."""
    m = 0.0
    for r, f in loads:
        dy, dz = (r[1]) / 1000, (r[2] - zl) / 1000
        m += dy * f[2] - dz * f[1]
    return m


cases = {}
nrm = np.array([0, -math.sin(tr), math.cos(tr)])
for name, sgn in (("wind from the front (+Y)", -1), ("wind from behind (-Y)", 1)):
    fp = sgn * F_p * nrm
    fe = np.array([0, -sgn * F_e, 0])
    wp = np.array([0, 0, -M_BOUGHT["panel"] * 9.81])
    wr = np.array([0, 0, -(m_total - M_BOUGHT["panel"]) * 9.81])
    loads = [(pan, fp), (box_c, fe), (pan, wp), (box_c, wr)]
    M = moment_lower(loads)
    fy = fp[1] + fe[1]
    fz = fp[2]
    cases[name] = (M, fy, fz)
    out("D2", f"{name}: panel force (y {fp[1]:.1f}, z {fp[2]:.1f}) N, enclosure {fe[1]:.1f} N; overturning moment about the "
              f"lower clamp {M:.1f} N m; pull on the upper clamp {max(0.0, M) / (D['clamp_span'] / 1000):.0f} N")
M_max = max(abs(c[0]) for c in cases.values())
pull = M_max / (D["clamp_span"] / 1000)
N_clamp = 2 * T_BAND
out("D3", f"worst pull on one clamp {pull:.0f} N against a band preload that holds {2 * T_BAND:.0f} N "
          f"(factor {2 * T_BAND / pull:.1f})")
# the same check with the shield fitted: larger front area and weight on the enclosure
F_e_sh = q * CD_BOX * SG["front_m2"]
M_sh = 0.0
for sgn in (-1, 1):
    fp = sgn * F_p * nrm
    loads = [(pan, fp), (box_c, np.array([0, -sgn * F_e_sh, 0])), (pan, np.array([0, 0, -M_BOUGHT["panel"] * 9.81])),
             (box_c, np.array([0, 0, -(m_total + SHIELD_KG - M_BOUGHT["panel"]) * 9.81]))]
    M_sh = max(M_sh, abs(moment_lower(loads)))
pull_sh = M_sh / (D["clamp_span"] / 1000)
out("D3b", f"with the shield: enclosure front load {F_e_sh:.1f} N; worst pull on one clamp {pull_sh:.0f} N (factor {2 * T_BAND / pull_sh:.1f})")
# slip along and around the pole
torque = F_side * abs(D["enc_yc"]) / 1000
slip_ax = 2 * MU * N_clamp
slip_t = slip_ax * P["pole_od"] / 2 / 1000
# bracket members
bg = bracket_geometry()
dang = math.radians(abs(bg["post"]["angle"] - bg["strut"]["angle"]))
f_member = F_p / 2 / math.sin(dang)
Ib = P["bar"][0] * P["bar"][1] ** 3 / 12
Lmax = max(bg["post"]["L"], bg["strut"]["L"])
Pcr = math.pi ** 2 * E_AL * Ib / Lmax ** 2
out("D5", f"bracket: members {bg['post']['L']:.0f} and {bg['strut']['L']:.0f} mm at {bg['post']['angle']:.0f} and "
          f"{bg['strut']['angle']:.0f} deg; member force bound {f_member:.0f} N; flat bar {P['bar'][0]:.0f} x {P['bar'][1]:.0f} "
          f"buckles at {Pcr:.0f} N out of plane (factor {Pcr / f_member:.0f})")
# V-block range
for dpole in P["pole_range"]:
    r = dpole / 2
    half_w_contact = r * math.sin(math.radians(45))
    out("D6", f"pole {dpole:.0f} mm: V contact points {half_w_contact:.1f} mm either side of center (block half-width "
              f"{P['vblock'][0] / 2:.0f} mm); band length around pole and block about {math.pi * dpole / 2 + 2 * (D['vblock_depth'] + r) + P['vblock'][0]:.0f} mm")
out("D6b", f"largest pole the {P['vblock'][0]:.0f} mm V-block seats: {2 * P['vblock'][0] / 2 / math.sin(math.radians(45)):.0f} mm")

# =============================================================== E. Installation and service (R12, R15)
INSTALL = [("Fit bracket and panel to the back plate on the ground", 3), ("Carry the node up a step ladder, hold it on the pole", 2),
           ("Pass and tighten two band clamps", 4), ("Aim panel toward the equator, check tilt", 1),
           ("Plug in sensor, close lid", 2), ("Power on, confirm a join and an uplink on a phone", 3)]
t_inst = sum(t for _, t in INSTALL)
out("E1", "install: " + "; ".join(f"{n} {t} min" for n, t in INSTALL) + f"; total {t_inst} min with a helper")
SERVICE = [("Open lid (4 captive screws)", 1), ("Unplug cell lead at the holder", 1), ("Swap cell, check fuse and NTC lead", 2),
           ("Replace desiccant, check gasket", 1), ("Close lid, confirm an uplink", 2)]
t_srv = sum(t for _, t in SERVICE)
out("E2", "cell swap: " + "; ".join(f"{n} {t} min" for n, t in SERVICE) + f"; total {t_srv} min")

# =============================================================== F. Cost (R16)
w_node = m_total * 9.81
fz_down = w_node + max(0.0, -min(c[2] for c in cases.values()))
out("D4", f"slip along the pole: weight {w_node:.0f} N plus wind down-load gives {fz_down:.0f} N against {slip_ax:.0f} N "
          f"(factor {slip_ax / fz_down:.0f}); twist: side wind {torque:.2f} N m against {slip_t:.1f} N m (factor {slip_t / torque:.0f})")

bom = list(csv.DictReader((ROOT / "bom/bom.csv").open()))
total = sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in bom)
budget = None
for line in (ROOT / "project.yaml").read_text().splitlines():
    if line.startswith("budget_usd:"):
        budget = float(line.split(":")[1].split("#")[0])
unpriced = [r["item"] for r in bom if not r["unit_cost_usd"].strip()]
options = [r["item"] for r in bom if float(r["qty"]) == 0]
out("F2", f"BOM {len(bom)} lines ({len(options)} option at qty 0), all priced: {not unpriced}; base node ${total:.2f} against budget_usd ${budget:.0f}; "
          f"margin ${budget - total:.2f} ({(budget - total) / budget * 100:.0f} %)")
out("F3", f"hot-climate node with the shield (+${SHIELD_COST:.0f}, +{SHIELD_KG:.2f} kg): ${total + SHIELD_COST:.2f}, {m_total + SHIELD_KG:.2f} kg")

# =============================================================== L. Results against every requirement
cc, cs = hot[("clean", False)], hot[("clean", True)]
dd = hot[("dusty", False)]
res("R1", "IP65 enclosure, ePTFE vent; 2 glands, 2 capped M12 ports, antenna bulkhead, all IP67 class", "IP65, sealed penetrations",
    "Met by design (sealing of fitted glands not verifiable at TRL 3)")
ds = hot[("dusty", True)]
res("R2", f"Electronics -20 to +70 C; worst sun position {45 + rise_worst_sh['dusty']:.1f} C dusty with the shield at 45 C, {T_HOT_SITE + rise_worst['dusty']:.1f} C dusty without it at {T_HOT_SITE:.0f} C; no charging on clear days below about {-rise_cold:.0f} C",
    "-20 to +45 C ambient; -20 to +70 C inside", "At risk (cold charging)")
res("R3", f"With the shield at 45 C: hot-day peak {cs[0]:.1f} C clean, {ds[0]:.1f} C dusty, worst sun position {45 + rise_worst_sh['dusty']:.1f} C; without it at {T_HOT_SITE:.0f} C: worst sun position {T_HOT_SITE + rise_worst['dusty']:.1f} C dusty (at 45 C: {cc[0]:.1f} to {45 + rise_worst['dusty']:.1f} C)",
    f"60 C or less; shield fitted where the design maximum exceeds {T_HOT_SITE:.0f} C", "Met on paper (shield factor assumed)")
res("R4", "NTC on the cell gates the charger at 0 and 45 C", "Charging blocked below 0 C and above 45 C", "Met by design")
res("R5", f"Worst month: stored {stored:.2f} Wh/day against {d100:.2f} Wh/day drawn ({stored / d100:.1f} times); hot clear day with the shield {cs[2]:.1f} Wh clean, {ds[2]:.1f} Wh dusty stored; 9 V class Vmp headroom {vmp_hot - VIN_MIN:.2f} V when hot",
    "Harvest exceeds demand at 2 peak sun hours", "Met on paper")
res("R6", f"{e_usable / d100:.2f} d at the published 100 mW ({(e_usable / d100 / AUTONOMY_REQ - 1) * 100:.0f} % margin); {e_usable * CAP_COLD / d100:.2f} d at -20 C; {e_usable * CAP_EOL / d100:.2f} d at end of life",
    "5 days or more at full allowance", "At risk (cold or aged cell)")
res("R7", f"Published allowance 100 mW; {allow_max * 1000:.1f} mW would give exactly 5 days", "100 mW or more", "Met on paper")
res("R8", f"SF9 budget {link9[0]:.1f} dB; Hata suburban loss {link9[1]:.1f} dB at 2 km (30 m gateway); margin {link9[2]:.1f} dB",
    "2 km suburban at SF9 or faster", "Met on paper")
res("R9", f"{tab[2][2]:.1f} s/day at SF9 at 15 min; firmware rule lengthens the interval to {RULE[10]:.0f} min at SF10 and {RULE[12]:.0f} min at SF12; largest {worst_rule:.1f} s/day",
    "30 s/day or less on The Things Network", "Met on paper (firmware rule)")
res("R10", f"30 days = {per_day_b * OUTAGE_D / 1024:.0f} kB of 16 MB flash; backlog upload limited by fair use",
    "30 days or more kept on the node", "Met on paper")
res("R11", "Two M12 5-pin ports: V+, GND and three signal pins; one switched rail per port, 3.3, 5 or 12 V",
    "Two sealed ports, I2C, UART or RS-485, analog, switched rails", "Met on paper (pinout awaiting adopting projects)")
res("R12", f"V-block seats 40 to 60 mm poles; install estimate {t_inst} min", "40 to 60 mm poles and walls; 15 min or less",
    "Not verifiable at TRL 3 (install time); fit met by design")
res("R13", f"Clamp pull {pull:.0f} N ({pull_sh:.0f} N with the shield) against {2 * T_BAND:.0f} N; slip factor {slip_ax / fz_down:.0f}; bracket factor {Pcr / f_member:.0f}",
    "35 m/s gusts without loosening", "Met on paper (band preload assumed)")
res("R14", f"Base node {m_total:.2f} kg ({2.5 - m_total:.2f} kg margin); {m_total + SHIELD_KG:.2f} kg with the hot-climate shield, which R14 excludes", "2.5 kg or less, base node", "Met on paper")
res("R15", f"Cell swap estimate {t_srv} min, screwdriver, plug-in cell lead", "10 min or less, no soldering", "Met by design")
res("R16", f"${total:.2f} base node; ${total + SHIELD_COST:.2f} with the shield", f"${budget:.0f} or less (FieldNode core, gateway excluded)", "Met on paper")
res("R17", "CERN-OHL-S-2.0 and MIT; standard LoRaWAN", "Open files, any network server", "Met by design")
res("R18", "Core forwards only what the sensor firmware passes", "No images or audio leave the node", "Met by design")

print("\n[L] Requirement status")
for r in rows:
    print(f"  {r[0]:4} | {r[3]:40} | {r[1]}")
counts = {}
for r in rows:
    key = r[3].split(" (")[0]
    counts[key] = counts.get(key, 0) + 1
print("  counts: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
with (ROOT / "docs/04-calcs/results.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "value", "target", "status"])
    w.writerows(rows)
