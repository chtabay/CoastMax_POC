#!/usr/bin/env python3
"""
Prépare les données CoastMax pour visualisation web.
Convertit en WGS84 et crée les fichiers pour GitHub Pages.
"""

import geopandas as gpd
import json
import os
from typing import Dict, Any


def convert_to_web_format(geojson_path: str, output_dir: str = "docs") -> None:
    """Convertit les données pour visualisation web."""
    print("=== PRÉPARATION DONNÉES WEB ===")
    
    # Charger les données
    df = gpd.read_file(geojson_path)
    print(f"Segments chargés: {len(df)}")
    
    # Convertir en WGS84 pour la web
    if df.crs != 'EPSG:4326':
        df_wgs84 = df.to_crs('EPSG:4326')
        print("Conversion en WGS84 effectuée")
    else:
        df_wgs84 = df.copy()
    
    # Créer le dossier docs pour GitHub Pages
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder en WGS84
    output_geojson = os.path.join(output_dir, "coastmax_ariege.geojson")
    df_wgs84.to_file(output_geojson, driver="GeoJSON")
    print(f"GeoJSON WGS84 sauvegardé: {output_geojson}")
    
    # Vérifier que le fichier a été créé
    if os.path.exists(output_geojson):
        print(f"✓ Fichier GeoJSON créé avec succès: {os.path.getsize(output_geojson)} octets")
    else:
        print("✗ Erreur: fichier GeoJSON non créé")
    
    # Créer un résumé JSON pour l'interface
    summary_data = create_summary(df_wgs84)
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print(f"Résumé sauvegardé: {summary_path}")
    
    # Créer les top segments pour affichage rapide
    top_segments = create_top_segments(df_wgs84)
    top_path = os.path.join(output_dir, "top_segments.json")
    with open(top_path, 'w', encoding='utf-8') as f:
        json.dump(top_segments, f, ensure_ascii=False, indent=2)
    print(f"Top segments sauvegardés: {top_path}")


def create_summary(df: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Crée un résumé des données."""
    return {
        "metadata": {
            "zone": "Ariège, France",
            "total_segments": len(df),
            "date_generated": "2024-12",
            "description": "Meilleurs segments de roue libre en Ariège"
        },
        "records": {
            "max_distance": {
                "value": float(df['coast_distance_m'].max()),
                "unit": "mètres",
                "segment_id": f"{df.loc[df['coast_distance_m'].idxmax(), 'u']}-{df.loc[df['coast_distance_m'].idxmax(), 'v']}"
            },
            "max_speed": {
                "value": float(df['v_max_mps'].max() * 3.6),
                "unit": "km/h",
                "segment_id": f"{df.loc[df['v_max_mps'].idxmax(), 'u']}-{df.loc[df['v_max_mps'].idxmax(), 'v']}"
            }
        },
        "statistics": {
            "distance_moyenne": float(df['coast_distance_m'].mean()),
            "distance_mediane": float(df['coast_distance_m'].median()),
            "vitesse_max_moyenne": float(df['v_max_mps'].mean() * 3.6),
            "distance_min": float(df['coast_distance_m'].min()),
            "distance_max": float(df['coast_distance_m'].max())
        }
    }


def create_top_segments(df: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Crée la liste des top segments avec coordonnées simplifiées."""
    
    # Top 10 par distance
    top_distance = df.nlargest(10, 'coast_distance_m')
    
    # Top 10 par vitesse
    top_speed = df.nlargest(10, 'v_max_mps')
    
    def segment_to_dict(row):
        # Extraire les coordonnées de début et fin
        coords = list(row.geometry.coords)
        start_coord = coords[0][:2]  # lon, lat
        end_coord = coords[-1][:2]
        
        return {
            "id": f"{row['u']}-{row['v']}",
            "start_node": int(row['u']),
            "end_node": int(row['v']),
            "start_coords": [float(start_coord[0]), float(start_coord[1])],  # [lon, lat]
            "end_coords": [float(end_coord[0]), float(end_coord[1])],
            "coast_distance_m": float(row['coast_distance_m']),
            "v_max_kmh": float(row['v_max_mps'] * 3.6),
            "v_out_kmh": float(row['v_out_mps'] * 3.6),
            "time_min": float(row['coast_time_s'] / 60),
            "length_m": float(row['length_m'])
        }
    
    return {
        "top_distance": [segment_to_dict(row) for _, row in top_distance.iterrows()],
        "top_speed": [segment_to_dict(row) for _, row in top_speed.iterrows()]
    }


def main():
    prepare_web_data = convert_to_web_format
    prepare_web_data("output/edges_coast_50.geojson")
    print("\n✅ Données prêtes pour GitHub Pages dans le dossier 'docs/'")


if __name__ == "__main__":
    main()
