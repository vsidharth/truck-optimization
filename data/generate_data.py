import json
import random
import os

# Set a fixed seed for absolute, 100% reproducibility across runs
random.seed(42)

# Coordinate bounding boxes for prominent commercial hubs in Bangalore
# Format: (Min Lat, Max Lat, Min Lng, Max Lng)
HUBS = {
    "Peenya (Industrial Zone)": (13.0100, 13.0400, 77.5000, 77.5400),
    "Whitefield (IT/Logistics Hub)": (12.9500, 12.9900, 77.7000, 77.7600),
    "Electronic City (Manufacturing Center)": (12.8300, 12.8700, 77.6500, 77.6900),
    "Yelahanka (Warehousing Area)": (13.0800, 13.1200, 77.5700, 77.6100)
}

def generate_random_coordinate(hub_name):
    lat_min, lat_max, lng_min, lng_max = HUBS[hub_name]
    lat = round(random.uniform(lat_min, lat_max), 5)
    lng = round(random.uniform(lng_min, lng_max), 5)
    return lat, lng

def generate_dataset(num_trucks=10, num_requests=30):
    hub_keys = list(HUBS.keys())
    
    # 1. Generate Trucks (Resources)
    trucks = []
    for i in range(1, num_trucks + 1):
        assigned_hub = random.choice(hub_keys)
        lat, lng = generate_random_coordinate(assigned_hub)
        
        trucks.append({
            "id": f"TRK-{i:02d}",
            "initial_hub": assigned_hub,
            "lat": lat,
            "lng": lng,
            "max_capacity": random.choice([3000, 5000, 10000]),  # Weight capacity limit in kg
            "is_refrigerated": random.choice([True, False, False]) # Cold chain capability is scarce (~33%)
        })
        
    # 2. Generate Delivery Orders (Requests)
    requests = []
    for j in range(1, num_requests + 1):
        assigned_hub = random.choice(hub_keys)
        lat, lng = generate_random_coordinate(assigned_hub)
        
        requests.append({
            "id": f"REQ-{j:02d}",
            "destination_hub": assigned_hub,
            "lat": lat,
            "lng": lng,
            "weight": random.randint(500, 2500), # Payload size requirement in kg
            "requires_refrigeration": random.choice([True, False, False, False, False]) # ~20% need cold chain
        })
        
    return {"trucks": trucks, "requests": requests}

if __name__ == "__main__":
    data = generate_dataset()
    
    # Ensure the directory path exists and save out the static JSON database artifact
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "bangalore_fleet_data.json")
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"🎉 Success! Generated {len(data['trucks'])} trucks and {len(data['requests'])} requests.")
    print(f"💾 Static data asset saved securely at: {output_path}")