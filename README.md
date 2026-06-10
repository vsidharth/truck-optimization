# Truck Optimization Engine 🚚

An end-to-end Resource Allocation Engine built to solve core logistics and supply chain inefficiencies. This system models a digital fleet dispatcher that optimally pairs incoming delivery requests with a mobile fleet of vehicles stationed across commercial hubs in Bangalore.

---

## 📌 Problem Statement
The engine coordinates a dynamic dispatch environment involving:
* **Resources (The Fleet):** Mobile trucks with specific GPS locations, strict payload capacity constraints, and distinct capabilities (e.g., Refrigerated vs. Standard).
* **Requests (The Demands):** Time-sensitive delivery orders specifying coordinates, cargo weight, and equipment prerequisites.
* **Objective:** Maximize fleet efficiency by minimizing total travel distance across the grid while perfectly respecting all hard capability and capacity constraints.

---

## 🛠️ Algorithmic Approaches Compared
To evaluate optimization efficacy, this system implements and compares two distinct strategies side-by-side:

1. **Custom Heuristic:** An advanced heuristic that computes the "opportunity cost" for each request based on its top two closest asset choices. By prioritizing high-regret and highly constrained requests first, it intelligently mitigates classic greedy bottlenecking.
2. **Mixed-Integer Programming Solver:** Formulated mathematically using binary decision variables ($x_{ij} \in \{0,1\}$) and executed via **PuLP (CBC Solver)** to uncover the absolute mathematical global optimum across a snapshot batch window.

---

## 📊 Empirical Quantitative Results
Running the seeded dataset containing **10 Trucks** and **30 Requests** across Bangalore commercial zones yielded the following benchmark matrix comparison:

| Metric | Heuristic | MIP Solver (PuLP) | Strategic Impact |
| :--- | :--- | :--- | :--- |
| **Total Fleet Distance** | 330.53 km | 290.86 km | **12.0% Distance Reduction** |
| **Execution Runtime** | ~21.2 ms | ~1105.5 ms | Sub-second real-time capability |
| **Fulfillment Rate** | 100% (30/30) | 100% (30/30) | Zero order starvation |

*The MIP solver successfully eliminated cross-town assignment bottlenecks by evaluating all potential network connections simultaneously instead of sequentially.*

---

## 🏗️ Repository Architecture
The workspace is organized into modular tiers for a clean separation of concerns:
* `data/`: Reproducible, seeded synthetic data generation script simulating spatial coordinates around Bangalore commercial hubs.
* `src/backend/`: FastAPI application containing the core algorithmic layers (`solver.py`), parameter schemas, and solver configurations.
* `src/frontend/`: A React single-page dashboard featuring an open-source Leaflet Map view for spatial distribution and vector lines showing side-by-side route allocations.
* `write_up/`: Technical brief detailing trade-offs, shadow pricing, and production limitations.

---

## ⚙️ Quick Start & Setup

### Prerequisites
* Python 3.9+ (with `py` launcher configured)
* Node.js v16+ & `npm`

### 1. Data Layer Setup
Generate the static database asset artifact inside the root directory:
```bash
py data/generate_data.py
