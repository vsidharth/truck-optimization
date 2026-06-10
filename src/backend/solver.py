import math
import pulp

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(R * c, 2)


def solve_regret_heuristic(trucks, requests):
    assignments = []
    total_distance = 0.0
    
    available_trucks = [dict(t) for t in trucks]
    for t in available_trucks:
        t['current_capacity'] = t['max_capacity']
        
    remaining_requests = [dict(r) for r in requests]
    
    while remaining_requests and available_trucks:
        request_regrets = []
        
        for req in remaining_requests:
            # Hard Constraints: Filter for valid capability and weight capacity
            valid_trucks = [
                t for t in available_trucks 
                if (not req['requires_refrigeration'] or t['is_refrigerated']) 
                and t['current_capacity'] >= req['weight']
            ]
            
            if not valid_trucks:
                continue
            
            # Calculate distance to all valid trucks and sort ascending
            truck_distances = []
            for t in valid_trucks:
                d = calculate_haversine(t['lat'], t['lng'], req['lat'], req['lng'])
                truck_distances.append((d, t))
            
            truck_distances.sort(key=lambda x: x[0])
            
            # Compute regret penalty matrix value
            if len(truck_distances) >= 2:
                regret = truck_distances[1][0] - truck_distances[0][0]
            else:
                regret = truck_distances[0][0] * 2  # Regret assigned a large value to increase priority of the request
                
            request_regrets.append({
                "regret": regret,
                "request": req,
                "best_truck": truck_distances[0][1],
                "distance": truck_distances[0][0]
            })
            
        if not request_regrets:
            break
            
        # Prioritize highest regret penalty first
        request_regrets.sort(key=lambda x: x['regret'], reverse=True)
        top_decision = request_regrets[0]
        
        req = top_decision['request']
        truck = top_decision['best_truck']
        dist = top_decision['distance']
        
        # Commit the assignment state change
        assignments.append({
            "truck_id": truck['id'],
            "request_id": req['id'],
            "distance": dist
        })
        total_distance += dist
        
        truck['current_capacity'] -= req['weight']
        if truck['current_capacity'] <= 0:
            available_trucks.remove(truck)
            
        remaining_requests.remove(req)
        
    return assignments, round(total_distance, 2)


def solve_milp(trucks, requests):
    # Initialize minimization problem
    prob = pulp.LpProblem("Fleet_Optimization", pulp.LpMinimize)
    
    # Decision Variables: Binary mapping of truck i to request j
    x = pulp.LpVariable.dicts(
        "assign", 
        ((t['id'], r['id']) for t in trucks for r in requests), 
        cat='Binary'
    )
    
    # Distance Matrix Coefficient Map
    distance_map = {
        (t['id'], r['id']): calculate_haversine(t['lat'], t['lng'], r['lat'], r['lng'])
        for t in trucks for r in requests
    }
    
    # Objective Function: Minimize overall fleet distance sum 
    prob += pulp.lpSum(x[t['id'], r['id']] * distance_map[t['id'], r['id']] for t in trucks for r in requests)
    
    # HARD CONSTRAINTS 
    
    # 1. Single Assignment Constraint: Each request processed at most once
    for r in requests:
        prob += pulp.lpSum(x[t['id'], r['id']] for t in trucks) == 1
        
    # 2. Capacity Constraint: Fleet assets cannot violate weight limitations
    for t in trucks:
        prob += pulp.lpSum(x[t['id'], r['id']] * r['weight'] for r in requests) <= t['max_capacity']
        
    # 3. Capability Compatibility Constraint: Avoid Infeasible match (Refrigerated and Non-refrigerated)
    for r in requests:
        for t in trucks:
            if r['requires_refrigeration'] and not t['is_refrigerated']:
                prob += x[t['id'], r['id']] == 0
                
    # Solve the MIP formulation
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Collect results if solution is valid
    assignments = []
    total_distance = 0.0
    
    if pulp.LpStatus[prob.status] == "Optimal":
        for t in trucks:
            for r in requests:
                if pulp.value(x[t['id'], r['id']]) == 1:
                    dist = distance_map[t['id'], r['id']]
                    assignments.append({
                        "truck_id": t['id'],
                        "request_id": r['id'],
                        "distance": dist
                    })
                    total_distance += dist
                    
    return assignments, round(total_distance, 2)