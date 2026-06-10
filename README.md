# Truck Optimization Engine 🚚

An end-to-end Resource Allocation Engine built to solve core logistics and supply chain inefficiencies. This system models a digital fleet dispatcher that optimally pairs incoming delivery requests with a mobile fleet of vehicles stationed across commercial hubs in Bangalore.

---

## 📌 Problem Statement
The engine coordinates a dynamic dispatch environment involving:
* **Resources (The Fleet):** Mobile trucks with specific GPS locations, strict payload capacity constraints, and distinct capabilities (e.g., Refrigerated vs. Standard).
* **Requests (The Demands):** Time-sensitive delivery orders specifying coordinates, cargo weight, and equipment prerequisites.
* **Objective:** Maximize fleet efficiency by minimizing total deadhead/travel distance across the grid while perfectly respecting all hard capability and capacity constraints.

---

## 🛠️ Algorithmic Approaches Compared
To evaluate optimization efficacy, this system implements and compares two distinct strategies side-by-side:

1. **Custom Look-Ahead Regret Heuristic (Baseline):** An advanced heuristic born out of iterative prototyping (moving from naive greedy to max-min bounds, and finally to regret modeling). It computes an opportunity cost penalty matrix for each request based on its top two closest asset choices, processing high-regret and highly constrained requests first to prevent asset starvation.
2. **Global Mixed-Integer Linear Programming (MILP):** Formulated mathematically using binary decision variables ($x_{ij} \in \{0, 1\}$) and executed via **PuLP (COIN-OR CBC Solver)** to uncover the absolute mathematical global optimum across a snapshot batch window.

---

## 📊 Empirical Quantitative Results
Running our master seeded dataset containing **10 Trucks** and **30 Requests** across Bangalore commercial zones yields the following live production metrics:

| Metric | Look-Ahead Regret Heuristic | Global MILP Solver (PuLP) | Strategic Impact |
| :--- | :--- | :--- | :--- |
| **Total Fleet Distance** | 139.62 km | 136.64 km | **2.13% Direct Distance Reduction** |
| **Execution Runtime** | ~20.41 ms | ~185.15 ms | Sub-second real-time capability |
| **Fulfillment Rate** | 100% (30/30) | 100% (30/30) | Zero order starvation |

*The MILP solver successfully eliminates localized routing traps by evaluating all potential network connections simultaneously, correcting cross-town assignment inefficiencies where the sequential heuristic suffered massive 20+ km deadhead spikes.*

---

## 🏗️ Repository Architecture & Key Features
The workspace is organized into modular tiers for a clean separation of concerns:
* `data/`: Reproducible, seeded synthetic data generation script simulating spatial coordinates around Bangalore commercial hubs.
* `src/backend/`: FastAPI application containing the core algorithmic layers (`solver.py`), parameter schemas, and Uvicorn server configs.
* `src/frontend/`: A React interface featuring an interactive Leaflet Map view displaying spatial distribution, route allocation vectors, and an **Interactive Truck Isolation Filter** allowing operators to click any truck node to isolate its specific routing path.
* `write_up/`: Technical brief detailing trade-offs, mathematical formulations, and production limitations.

---

## ⚙️ Quick Start & Setup

### Prerequisites
* Python 3.9+ (with `py` launcher configured)
* Node.js v16+ & `npm`

### 1. Data Layer Setup
Generate the static database asset artifact inside the root directory:
```bash
py data/generate_data.py
```

### 2. Backend Server Deployment
Install optimization dependencies and launch the FastAPI web server:
```bash
py -m pip install -r requirements.txt
py src/backend/main.py
```
### 3. Frontend Dashboard Launch
Navigate into the React module directory, install packages, and boot up the Vite rendering dev layer:
```bash
cd src/frontend
npm install
npm run dev
```
