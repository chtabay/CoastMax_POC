#!/usr/bin/env python3
"""
Géolocalisation des segments CoastMax - identifier villages et cols proches.
"""

import argparse
import geopandas as gpd
import osmnx as ox
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import requests
from typing import List, Dict, Tuple, Optional


def get_node_coordinates(node_ids: List[int], place: str = "Ariège, France") -> Dict[int, Tuple[float, float]]:
    """Récupère les coordonnées lat/lon des nœuds OSM."""
    print(f"Récupération des coordonnées des nœuds...")
    
    # Charger le graphe pour avoir accès aux nœuds
    G = ox.graph_from_place(place, network_type="bike", simplify=True)
    
    coords = {}
    for node_id in node_ids:
        if node_id in G.nodes:
            node_data = G.nodes[node_id]
            lat = node_data.get('y')
            lon = node_data.get('x') 
            if lat is not None and lon is not None:
                coords[node_id] = (lat, lon)
                print(f"  Nœud {node_id}: {lat:.6f}, {lon:.6f}")
            else:
                print(f"  Nœud {node_id}: coordonnées manquantes")
        else:
            print(f"  Nœud {node_id}: introuvable dans le graphe")
    
    return coords


def reverse_geocode_nominatim(lat: float, lon: float) -> Optional[str]:
    """Géocodage inverse avec Nominatim."""
    try:
        geolocator = Nominatim(user_agent="coastmax_poc", timeout=10)
        location = geolocator.reverse(f"{lat}, {lon}", language='fr')
        if location:
            return location.address
        return None
    except Exception as e:
        print(f"    Erreur géocodage {lat:.6f}, {lon:.6f}: {e}")
        return None


def find_nearby_places_overpass(lat: float, lon: float, radius_km: float = 5.0) -> List[Dict]:
    """Trouve les lieux proches via Overpass API."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Requête Overpass pour trouver villages, cols, sommets
    query = f"""
    [out:json][timeout:25];
    (
      node["place"~"^(village|town|city|hamlet)$"](around:{radius_km*1000},{lat},{lon});
      node["natural"="peak"](around:{radius_km*1000},{lat},{lon});
      node["mountain_pass"="yes"](around:{radius_km*1000},{lat},{lon});
      node["natural"="saddle"](around:{radius_km*1000},{lat},{lon});
    );
    out geom;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            places = []
            
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                place_lat = element.get('lat')
                place_lon = element.get('lon')
                
                if place_lat and place_lon:
                    # Calculer la distance
                    distance = geodesic((lat, lon), (place_lat, place_lon)).kilometers
                    
                    # Déterminer le type et le nom
                    place_type = "Lieu"
                    name = tags.get('name', 'Sans nom')
                    
                    if tags.get('place'):
                        place_type = f"Village/Ville ({tags['place']})"
                    elif tags.get('natural') == 'peak':
                        place_type = "Sommet"
                        if 'ele' in tags:
                            place_type += f" ({tags['ele']}m)"
                    elif tags.get('mountain_pass') == 'yes' or tags.get('natural') == 'saddle':
                        place_type = "Col"
                        if 'ele' in tags:
                            place_type += f" ({tags['ele']}m)"
                    
                    places.append({
                        'name': name,
                        'type': place_type,
                        'distance_km': distance,
                        'lat': place_lat,
                        'lon': place_lon
                    })
            
            # Trier par distance
            places.sort(key=lambda x: x['distance_km'])
            return places[:5]  # Top 5 plus proches
            
        else:
            print(f"    Erreur Overpass API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"    Erreur Overpass: {e}")
        return []


def analyze_segment_locations(geojson_path: str, place: str = "Ariège, France", top_n: int = 10):
    """Analyse les localisations des meilleurs segments."""
    print(f"=== GÉOLOCALISATION SEGMENTS COASTMAX ===")
    
    # Charger les résultats
    df = gpd.read_file(geojson_path)
    
    # Prendre les top segments par distance
    top_segments = df.nlargest(top_n, 'coast_distance_m')
    
    # Récupérer tous les nœuds uniques
    all_nodes = set()
    for _, row in top_segments.iterrows():
        all_nodes.add(int(row['u']))
        all_nodes.add(int(row['v']))
    
    print(f"Analyse de {len(top_segments)} segments avec {len(all_nodes)} nœuds uniques...")
    
    # Obtenir les coordonnées
    node_coords = get_node_coordinates(list(all_nodes), place)
    
    # Analyser chaque segment
    for i, (_, row) in enumerate(top_segments.iterrows(), 1):
        print(f"\n🏔️  SEGMENT #{i} - {row['coast_distance_m']:.0f}m")
        print(f"    Vitesse max: {row['v_max_mps']*3.6:.1f} km/h")
        print(f"    Temps: {row['coast_time_s']/60:.1f} min")
        
        start_node = int(row['u'])
        end_node = int(row['v'])
        
        # Point de départ
        if start_node in node_coords:
            lat, lon = node_coords[start_node]
            print(f"\n  📍 DÉPART (nœud {start_node}): {lat:.6f}, {lon:.6f}")
            
            # Géocodage simple
            address = reverse_geocode_nominatim(lat, lon)
            if address:
                print(f"      Adresse: {address}")
            
            # Lieux proches
            nearby = find_nearby_places_overpass(lat, lon, radius_km=8.0)
            if nearby:
                print(f"      Lieux proches:")
                for place_info in nearby:
                    print(f"        • {place_info['name']} ({place_info['type']}) - {place_info['distance_km']:.1f} km")
            
            time.sleep(1)  # Éviter de surcharger les APIs
        
        # Point d'arrivée
        if end_node in node_coords:
            lat, lon = node_coords[end_node]
            print(f"\n  🏁 ARRIVÉE (nœud {end_node}): {lat:.6f}, {lon:.6f}")
            
            # Géocodage simple
            address = reverse_geocode_nominatim(lat, lon)
            if address:
                print(f"      Adresse: {address}")
            
            # Lieux proches
            nearby = find_nearby_places_overpass(lat, lon, radius_km=8.0)
            if nearby:
                print(f"      Lieux proches:")
                for place_info in nearby:
                    print(f"        • {place_info['name']} ({place_info['type']}) - {place_info['distance_km']:.1f} km")
            
            time.sleep(1)
        
        print("    " + "="*60)


def main():
    parser = argparse.ArgumentParser(description="Géolocalise les segments CoastMax")
    parser.add_argument("--results", type=str, default="output/edges_coast_50.geojson",
                       help="Fichier GeoJSON des résultats")
    parser.add_argument("--place", type=str, default="Ariège, France",
                       help="Zone d'étude")
    parser.add_argument("--top", type=int, default=5,
                       help="Nombre de segments à analyser")
    
    args = parser.parse_args()
    
    analyze_segment_locations(args.results, args.place, args.top)


if __name__ == "__main__":
    main()


