# Quantized Orbital Refraction in a Super-Solid Vacuum: A Multi-Decadal Forensic Audit of the 2008–2009 Phase-Slip and Persistent Crystalline Stasis.

## Forensic Pipeline Documentation

This document provides a comprehensive overview of the scripts, diagnostics, and simulations used to establish the Super-Solid Bose-Einstein Condensate (SS-BEC) vacuum model and verify the 2009 topological phase-slip. To make the most of this, follow our paper "Quantized Orbital Refraction in a Super-Solid Vacuum" to replicate the steps and results.

---

## Phase I: Track Frequency & VTI
**Objective:** Establish the "Laminar" (fluid) ground state of the vacuum before modern turbulence.

### `vortex_hunter.py` (§10.3)
* **Function:** The core diagnostic engine. It performs spectral audits of post-2000 data to track frequency migration.
* **Result:** Detected the 7.4% elevation in resonance ($486.86 \pm 1.2$ c/y), interpreted as the structural "stiffening" of the SS-BEC manifold.

---

## Phase II: High-Resolution Jitter & Turbulence Mapping
**Objective:** Capture the "shimmer" of the vacuum and quantify the onset of the Galactic Storm.

### `cod_05s_precision_hourly_mapper.py` (§9)
* **Function:** Ingests ultra-high-resolution $05$s GPS clock data. It maps magnitude variations on an hour-by-hour basis to find harmonic bands.
* **Result:** Identified discrete energy bands in vacuum density, proving the background noise is structured rather than random.

### `vortex_hunter_yearly_average.py` (§11.2, §10.4)
* **Function:** A multi-threaded version of the hunter suite. It automates the Vacuum Turbulence Index (VTI) calculation by measuring the Full Width at Half Maximum (FWHM) of spectral peaks. Aggregates daily/monthly spectral data into yearly "Forensic Snapshots."
* **Result:** Captured the 2013 "Phase-Slip Migration" where the frequency hit a transient high of $547.87$ c/y.

---

## Phase III: LLR Bifurcation & Station Verification
**Objective:** Confirm that the 7.99 cm shift is a physical reality in the Earth-Moon distance.

### `vortex_hunter_seperator.py` (§10.1)
* **Function:** Separates Lunar Laser Ranging (LLR) residuals by firing station (e.g., McDonald Observatory vs. Observatoire de la Côte d'Azur).
* **Result:** Confirmed the 2009 anomaly was consistent across global stations, eliminating local instrumentation error.

### `Residuals_Forensic_Verification.py` (§10.1)
* **Function:** Performs a statistical T-test and variance check on the "Pre-Snap" vs. "Post-Snap" LLR data.
* **Result:** Statistically verified the 7.99 cm bifurcation at a $>99\%$ confidence interval.

---

## Phase IV: Inter-Agency Divergence (IAD) & Rigidity
**Objective:** Use the breakdown in modeling consensus to measure vacuum tension.

### `ch_agency_divergence_audit.py` (§11)
* **Function:** Compares COD (rigid relativistic model) vs. IGS (physical path consensus) to calculate the "Jerk Variance."
* **Result:** Identified the 2004 fracture point (24x divergence) and the 2008 rupture (1266x divergence).

### `CH_Agency_Divergence_Audit_v2.py` (§20.2)
* **Function:** An advanced iteration that maps the "Bowstring" stress accumulation. It specifically isolates the 2044x variance magnitude shift.
* **Result:** Visualized the buildup of potential energy in the substrate leading to the 2009 release.

### `power_spectral_density_zoom.py` (§11.3)
* **Function:** Performs a high-fidelity "zoom" on the spectral floor during the rupture.
* **Result:** Documented a 98.1% dissipation of coherent orbital energy into the substrate as Reynolds Stress.

---

## Phase V: Substrate Hardening & Modern Stasis
**Objective:** Document the final transition into the Crystalline phase.

### `satellite_only_sniper_combined.py` (§12)
* **Function:** Isolates individual GPS satellite clock phase accelerations ($| \Delta^2 \phi |$), stripping away orbital drift.
* **Result:** Observed a 300-fold reduction in vacuum shimmer, confirming the "Lattice Hardening" phase.

### `erp_analyzer.py` (§12.1)
* **Function:** Analyzes Earth Rotation Parameters (ERP). It looks for Length of Day (LOD) jitter suppression.
* **Result:** Found a historical minimum in rotational jitter ($90.01$ $\mu$s) in 2015, proving macroscopic "Drag-Lock."

### `PSD_Comparison_6th_Degree_Combined.py` (§12.2)
* **Function:** Uses a 6th-degree polynomial filter to "Deep Audit" clock residuals at the $10^{-18}$ ns² floor.
* **Result:** Provided the definitive proof of Saturated Phase-Lock; different satellites converging to a single shared noise floor.

### `G25_Full_Timeline_2000_2022_Audit.csv` (§13)
* **Artifact:** Master data output of the sniper scripts. Contains every peak jitter measurement used to generate the decadal decay curves.

---

## Phase VI: Final Synthesis
**Objective:** Bridge the gap between GPS/LLR forensics and the SS-BEC theoretical model.

### `ch_lunar_resonance_v3_forensic_breakdown.py` (§15)
* **Function:** The final "Master Script." It pulls the VTI, IAD, and LLR residuals into a single calculation.
* **Result:** Successfully aligned the refractive shift to the Fine Structure Constant ($\alpha \approx 1/137$) with $99.9\%$ accuracy, accounting for the $0.29$ cm Berry Phase residual.

---

## Phase VII: MATLAB/GPELab Simulation Suite
**Objective:** Provide the mechanical "proof of concept" for a vacuum that can rupture and remember.

## 🛠️ Global Dependencies

Before running the scripts, ensure your environment meets the following requirements:

* **Primary Engine:** MATLAB (R2020b or later).
* **Required Toolbox:** [GPELab](https://www.mathworks.com/matlabcentral/fileexchange/48347-gpelab) (Gross-Pitaevskii Equation Laboratory).
* **Path Configuration:** Ensure the following GPELab core files are in your MATLAB path:
    * `Geometry2D_Var2d.m`
    * `Method_Var2d.m`
    * `Physics2D_Var2d.m`
    * `Potential_Var2d.m`
    * `GPELab2d.m`

### 1. Numerical Manifold Simulations (Self-Contained)
These scripts provide the theoretical and mechanical basis for the CH-Framework. They do not require external data files to execute.

| File Name | Primary Forensic Function | Needs Data? | Forensic Result |
| :--- | :--- | :---: | :--- |
| `CH_MultiBody_lock.m` | Simulates Earth-Moon phase-locked bridge. | **NO** | Discovered the **"W-Well" potential**, proving gravity is a topological ring rather than a simple point-source pit. |
| `CH_Wake_Visualization.m` | Simulates the 2009 "Galactic Storm" environment. | **NO** | Proved the existence of a **Stable Super-Critical Corridor** (the "Shock Wall") that maintains the new orbit. |
| `ch_2009_rupture_event.m` | Models the 2009 Shear event and the resulting "Snap." | **NO** | Generated the **Mechanical Torque ($L_z$)** necessary for the observed 7.99 cm LLR refraction. |
| `CH_Galactic_Wind_Distortion.m` | Analyzes "W-Well" distortion under steady wind. | **NO** | Measured the **Pressure Differential ($\Delta Q$)** required to trigger the 2009 topological snap. |
| `CH_Phonon_Speed_Audit.m` | Measures signal propagation speed in the lattice. | **NO** | Confirmed **Super-Celerity ($175c$)**, explaining why the Earth and Moon moved in perfect synchronicity. |
| `CH_Resonance_Alignment.m` | Tests stability limits against distance and $\alpha_{fs}$. | **NO** | Identified the **Topological Truth Peak** ($g=21,000, \xi=3.20$ nm) with **99.80% accuracy**. |
| `CH_Sweep_Distances.m` | Sweeps distances to map quantized orbital grooves. | **NO** | Identified that the vacuum undergoes **Brittle Fracture** at specific thresholds, explaining the "jump" vs. "drift." |
| `CH_Snap_Transition.m` | Simulates transition from metastable to integer states. | **NO** | Demonstrated **Integer Harmonic Capture**, where the Moon "snaps" to the nearest $n=3$ node. |
| `CH_Gravit_Test_New.m` | Audits Rigidity, Resonance, and Hysteresis. | **NO** | Confirmed **Permanent Topological Phase-Slip**; the system retains a "memory" of the 2009 rupture event. |
| `Energy_Release_Audit.m` | Calculates Joules released during the 2009 Snap. | **NO** | Matched latent energy discharge to the observed **$10^{-18}$ ns² thermal floor** of the GPS constellation. |




### `CH_Gravity_Test.m` (§16.1, §18.3, §19.2)
* **Function:** This script executes a three-act simulation to validate the mechanical properties of the SS-BEC substrate, specifically focusing on its rigidity and topological memory.

#### **Act I: Stabilization**
*Establishing the $n \approx 2.62$ State*

* **Action:** The script initializes a 2D condensate with high stiffness (`Physics2D.g = 20000`) and introduces a mass potential representing the Earth-Moon barycenter.
* **The Math:** It calculates the **Quantum Potential ($Q$)**, which defines the spatial "groove" or potential well where the planetary mass is seated.
* **Result:** Identification of the initial **harmonic node ($n$)**. This corresponds to the pre-2009 state described in the paper, where the system is pinned between the 2nd and 3rd vacuum harmonics.

#### **Act II: Rigidity Audit**
*Testing the Elastic Limit*

* **Action:** The script incrementally increases the mass stress ($M = 2.0, 4.0, 8.0$).
* **The Physics:** This simulates **Mass-Recoil**. As the mass increases, the engine measures the structural deformation of the vacuum lattice (the shift in Trough Coordinate $X$).
* **Result:**
    * **Elastic Phase:** At lower mass levels, the lattice shift is minor and linear.
    * **Rupture Phase:** At $M=8.0$, the shift becomes non-linear, representing the **Topological Rupture** where the vacuum substrate reaches its ultimate tensile strength and can no longer maintain its original geometry.

#### **Act III: Hysteresis Audit**
*The "Smoking Gun" for Vacuum Memory*

* **Action:** This is the critical forensic component. It follows a non-linear loading loop:
    1.  Initialize at Baseline ($M=2.0$).
    2.  Increase to Peak Stress ($M=8.0$).
    3.  Return to Baseline ($M=2.0$).
* **The Logic:** If the vacuum were a simple fluid or perfectly elastic, the system would return to its original coordinate ($X$).
* **Result:** The script demonstrates a **Permanent Topological Phase-Slip**. Because the vacuum is a Super-Solid with a quantized lattice structure, the system "snaps" into a higher-order groove ($n=3$) and remains there post-stress.
