import os
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Import our mathematical engines
from solver import solve_regret_heuristic, solve_milp

app = FastAPI(
    title="Truck Resource Allocation Engine",
    description="FastAPI Optimization Server comparing Regret Heuristics vs MILP matrix calculations."
)

# Enable CORS so your React frontend can communicate seamlessly with this backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths to read our static data file
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "bangalore_fleet_data.json")

def load_fleet_data() -> Dict[str, Any]:
    """Helper utility to extract coordinates and metrics from the database file."""
    if not os.path.exists(DATA_PATH):
        raise HTTPException(
            status_code=500, 
            detail="Fleet dataset missing. Please run 'generate_data.py' first."
        )
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@app.get("/api/data")
def get_raw_data():
    """Exposes the raw fleet dataset containing baseline truck locations and order metrics."""
    return load_fleet_data()


@app.get("/api/optimize")
def run_optimization_pipeline():
    """
    Executes both strategies side-by-side over the baseline batch snapshot,
    capturing exact runtime profiles and aggregate optimization gaps.
    """
    data = load_fleet_data()
    trucks = data["trucks"]
    requests = data["requests"]

    # 1. Profile and execute the Custom Regret Heuristic
    start_heuristic = time.perf_counter()
    heuristic_assignments, heuristic_dist = solve_regret_heuristic(trucks, requests)
    end_heuristic = time.perf_counter()
    heuristic_runtime_ms = (end_heuristic - start_heuristic) * 1000

    # 2. Profile and execute the Global MILP Solver
    start_milp = time.perf_counter()
    milp_assignments, milp_dist = solve_milp(trucks, requests)
    end_milp = time.perf_counter()
    milp_runtime_ms = (end_milp - start_milp) * 1000

    # 3. Calculate metrics and performance gap differences
    unassigned_count_heuristic = len(requests) - len(heuristic_assignments)
    unassigned_count_milp = len(requests) - len(milp_assignments)
    
    # Distance efficiency improvement percentage
    efficiency_gain_pct = 0.0
    if heuristic_dist > 0:
        efficiency_gain_pct = round(((heuristic_dist - milp_dist) / heuristic_dist) * 100, 2)

    return {
        "metadata": {
            "total_trucks": len(trucks),
            "total_requests": len(requests)
        },
        "results": {
            "regret_heuristic": {
                "assignments": heuristic_assignments,
                "total_distance_km": heuristic_dist,
                "runtime_ms": round(heuristic_runtime_ms, 3),
                "unassigned_orders": unassigned_count_heuristic,
                "constraint_satisfaction_rate": round(((len(requests) - unassigned_count_heuristic) / len(requests)) * 100, 2)
            },
            "milp_solver": {
                "assignments": milp_assignments,
                "total_distance_km": milp_dist,
                "runtime_ms": round(milp_runtime_ms, 3),
                "unassigned_orders": unassigned_count_milp,
                "constraint_satisfaction_rate": round(((len(requests) - unassigned_count_milp) / len(requests)) * 100, 2)
            }
        },
        "analysis": {
            "distance_reduction_by_milp_pct": efficiency_gain_pct,
            "explanation": (
                f"The PuLP MILP solver achieved a {efficiency_gain_pct}% reduction in total deadhead distance "
                f"compared to the Regret Heuristic by resolving all cross-town assignment matrix conflict links simultaneously."
            )
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)