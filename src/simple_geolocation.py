#!/usr/bin/env python3
"""
Géolocalisation simplifiée des segments CoastMax.
Identifie les lieux proches des points de départ/arrivée.
"""

import json
import math
from typing import List, Dict, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en km entre deux points géographiques."""
    R = 6371  # Rayon de la Terre en km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_ariege_landmarks() -> List[Dict]:
    """Retourne une liste des principaux lieux de l'Ariège."""
    return [
        # Principales villes
        {"name": "Foix", "lat": 42.9651, "lon": 1.6071, "type": "Préfecture"},
        {"name": "Pamiers", "lat": 43.1147, "lon": 1.6109, "type": "Ville"},
        {"name": "Saint-Girons", "lat": 42.9831, "lon": 1.1394, "type": "Ville"},
        {"name": "Ax-les-Thermes", "lat": 42.7175, "lon": 1.8372, "type": "Station thermale"},
        {"name": "Tarascon-sur-Ariège", "lat": 42.8459, "lon": 1.6069, "type": "Ville"},
        
        # Cols et sommets célèbres
        {"name": "Col du Puymorens", "lat": 42.5461, "lon": 1.8419, "type": "Col (1915m)"},
        {"name": "Col de Port", "lat": 42.8031, "lon": 1.4164, "type": "Col (1249m)"},
        {"name": "Col de la Core", "lat": 42.8889, "lon": 1.3794, "type": "Col (1395m)"},
        {"name": "Pic du Midi de Bigorre", "lat": 42.9367, "lon": 0.1425, "type": "Sommet (2877m)"},
        {"name": "Pic de Montcalm", "lat": 42.6533, "lon": 1.4167, "type": "Sommet (3077m)"},
        
        # Vallées et villages
        {"name": "Vicdessos", "lat": 42.7664, "lon": 1.4919, "type": "Village"},
        {"name": "Massat", "lat": 42.9361, "lon": 1.3406, "type": "Village"},
        {"name": "Aulus-les-Bains", "lat": 42.7739, "lon": 1.3564, "type": "Station thermale"},
        {"name": "Seix", "lat": 42.8494, "lon": 1.2233, "type": "Village"},
        {"name": "Castillon-en-Couserans", "lat": 42.9439, "lon": 1.1964, "type": "Village"},
        {"name": "Mirepoix", "lat": 43.0869, "lon": 1.8739, "type": "Ville bastide"},
        {"name": "Lavelanet", "lat": 42.9353, "lon": 1.8572, "type": "Ville"},
        
        # Sites remarquables
        {"name": "Château de Foix", "lat": 42.9658, "lon": 1.6058, "type": "Monument"},
        {"name": "Grotte du Mas-d'Azil", "lat": 43.0756, "lon": 1.3656, "type": "Site naturel"},
        {"name": "Montségur", "lat": 42.8744, "lon": 1.8311, "type": "Site historique"},
        {"name": "Melles", "lat": 42.9458, "lon": 1.0494, "type": "Village"},
        {"name": "Ustou", "lat": 42.8103, "lon": 1.2364, "type": "Village"},
    ]


def find_nearest_landmarks(lat: float, lon: float, max_distance: float = 15.0) -> List[Dict]:
    """Trouve les lieux proches d'un point donné."""
    landmarks = get_ariege_landmarks()
    nearby = []
    
    for landmark in landmarks:
        distance = haversine_distance(lat, lon, landmark["lat"], landmark["lon"])
        if distance <= max_distance:
            nearby.append({
                **landmark,
                "distance_km": round(distance, 1)
            })
    
    return sorted(nearby, key=lambda x: x["distance_km"])


def analyze_top_segments():
    """Analyse les top segments et identifie les lieux proches."""
    print("=== GÉOLOCALISATION SEGMENTS COASTMAX ARIÈGE ===\n")
    
    # Charger les données des top segments
    try:
        with open("docs/top_segments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Fichier docs/top_segments.json introuvable")
        print("Exécutez d'abord: python src/prepare_web_data.py")
        return
    
    # Analyser les top 5 par distance
    print("🏆 TOP 5 SEGMENTS PAR DISTANCE\n")
    
    for i, segment in enumerate(data["top_distance"][:5], 1):
        print(f"🏔️  SEGMENT #{i} - {segment['coast_distance_m']:.0f}m")
        print(f"    Vitesse max: {segment['v_max_kmh']:.1f} km/h")
        print(f"    Temps: {segment['time_min']:.1f} min")
        print(f"    Nœuds OSM: {segment['start_node']} → {segment['end_node']}")
        
        # Point de départ
        start_lat, start_lon = segment["start_coords"][1], segment["start_coords"][0]
        print(f"\n  📍 DÉPART: {start_lat:.5f}, {start_lon:.5f}")
        
        nearby_start = find_nearest_landmarks(start_lat, start_lon)
        if nearby_start:
            print("      Lieux proches:")
            for place in nearby_start[:3]:
                print(f"        • {place['name']} ({place['type']}) - {place['distance_km']} km")
        else:
            print("      Aucun lieu remarquable à proximité")
        
        # Point d'arrivée
        end_lat, end_lon = segment["end_coords"][1], segment["end_coords"][0]
        print(f"\n  🏁 ARRIVÉE: {end_lat:.5f}, {end_lon:.5f}")
        
        nearby_end = find_nearest_landmarks(end_lat, end_lon)
        if nearby_end:
            print("      Lieux proches:")
            for place in nearby_end[:3]:
                print(f"        • {place['name']} ({place['type']}) - {place['distance_km']} km")
        else:
            print("      Aucun lieu remarquable à proximité")
        
        print("    " + "="*60 + "\n")
    
    # Analyser le segment vitesse record
    print("🚀 SEGMENT VITESSE RECORD\n")
    speed_record = data["top_speed"][0]
    
    print(f"⚡ VITESSE RECORD: {speed_record['v_max_kmh']:.1f} km/h")
    print(f"    Distance: {speed_record['coast_distance_m']:.0f}m")
    print(f"    Temps: {speed_record['time_min']:.1f} min")
    print(f"    Nœuds OSM: {speed_record['start_node']} → {speed_record['end_node']}")
    
    # Analyser les lieux pour le record vitesse
    start_lat, start_lon = speed_record["start_coords"][1], speed_record["start_coords"][0]
    end_lat, end_lon = speed_record["end_coords"][1], speed_record["end_coords"][0]
    
    print(f"\n  📍 Zone du record: {start_lat:.5f}, {start_lon:.5f}")
    nearby = find_nearest_landmarks(start_lat, start_lon)
    if nearby:
        print("      Lieux proches:")
        for place in nearby[:5]:
            print(f"        • {place['name']} ({place['type']}) - {place['distance_km']} km")


if __name__ == "__main__":
    analyze_top_segments()
