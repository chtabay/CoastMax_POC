#!/usr/bin/env python3
"""
Analyse des résultats de simulation CoastMax.
"""

import pandas as pd
import geopandas as gpd
import argparse
import matplotlib.pyplot as plt
import os


def analyze_results(geojson_path: str) -> None:
    """Analyse les résultats de simulation."""
    print(f"Analyse des résultats: {geojson_path}")
    
    # Charger les données
    df = gpd.read_file(geojson_path)
    print(f"\n📊 Statistiques générales:")
    print(f"   • Segments analysés: {len(df)}")
    print(f"   • Distance max: {df['coast_distance_m'].max():.1f}m")
    print(f"   • Vitesse max: {df['v_max_mps'].max():.1f} m/s ({df['v_max_mps'].max()*3.6:.1f} km/h)")
    print(f"   • Temps max: {df['coast_time_s'].max():.1f}s ({df['coast_time_s'].max()/60:.1f} min)")
    
    # Top segments par distance
    print(f"\n🏆 Top 10 segments par distance:")
    top_distance = df.nlargest(10, 'coast_distance_m')
    for i, row in top_distance.iterrows():
        print(f"   {i+1:2d}. {row['coast_distance_m']:6.0f}m | "
              f"{row['v_max_mps']*3.6:4.1f} km/h | "
              f"{row['coast_time_s']/60:4.1f} min | "
              f"[{row['u']} → {row['v']}]")
    
    # Top segments par vitesse
    print(f"\n🚀 Top 10 segments par vitesse max:")
    top_speed = df.nlargest(10, 'v_max_mps')
    for i, row in top_speed.iterrows():
        print(f"   {i+1:2d}. {row['v_max_mps']*3.6:5.1f} km/h | "
              f"{row['coast_distance_m']:6.0f}m | "
              f"{row['coast_time_s']/60:4.1f} min | "
              f"[{row['u']} → {row['v']}]")
    
    # Segments avec vitesse finale élevée (bon potentiel d'enchaînement)
    high_vout = df[df['v_out_mps'] > 5.0].sort_values('coast_distance_m', ascending=False)
    print(f"\n🔗 Segments avec vitesse finale > 18 km/h (potentiel d'enchaînement):")
    for i, row in high_vout.head(5).iterrows():
        print(f"   {i+1:2d}. {row['coast_distance_m']:6.0f}m | "
              f"v_out: {row['v_out_mps']*3.6:4.1f} km/h | "
              f"v_max: {row['v_max_mps']*3.6:4.1f} km/h | "
              f"[{row['u']} → {row['v']}]")
    
    # Statistiques par quartile
    print(f"\n📈 Distribution des distances (quartiles):")
    quartiles = df['coast_distance_m'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    for q, val in quartiles.items():
        print(f"   Q{q*100:2.0f}: {val:6.0f}m")
    
    # Créer des graphiques si matplotlib disponible
    try:
        create_plots(df, geojson_path)
    except Exception as e:
        print(f"\nAvertissement: impossible de créer les graphiques: {e}")


def create_plots(df: pd.DataFrame, geojson_path: str) -> None:
    """Crée des graphiques d'analyse."""
    base_name = os.path.splitext(os.path.basename(geojson_path))[0]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Analyse CoastMax - {base_name}', fontsize=14)
    
    # Distribution des distances
    axes[0,0].hist(df['coast_distance_m'], bins=20, alpha=0.7, color='blue')
    axes[0,0].set_xlabel('Distance de roue libre (m)')
    axes[0,0].set_ylabel('Nombre de segments')
    axes[0,0].set_title('Distribution des distances')
    axes[0,0].grid(True, alpha=0.3)
    
    # Distribution des vitesses max
    axes[0,1].hist(df['v_max_mps']*3.6, bins=20, alpha=0.7, color='red')
    axes[0,1].set_xlabel('Vitesse max (km/h)')
    axes[0,1].set_ylabel('Nombre de segments')
    axes[0,1].set_title('Distribution des vitesses max')
    axes[0,1].grid(True, alpha=0.3)
    
    # Relation distance vs vitesse max
    axes[1,0].scatter(df['coast_distance_m'], df['v_max_mps']*3.6, alpha=0.6)
    axes[1,0].set_xlabel('Distance de roue libre (m)')
    axes[1,0].set_ylabel('Vitesse max (km/h)')
    axes[1,0].set_title('Distance vs Vitesse max')
    axes[1,0].grid(True, alpha=0.3)
    
    # Relation distance vs temps
    axes[1,1].scatter(df['coast_distance_m'], df['coast_time_s']/60, alpha=0.6, color='green')
    axes[1,1].set_xlabel('Distance de roue libre (m)')
    axes[1,1].set_ylabel('Temps (minutes)')
    axes[1,1].set_title('Distance vs Temps')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sauvegarder
    plot_path = f"output/{base_name}_analysis.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 Graphiques sauvegardés: {plot_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyse des résultats CoastMax")
    parser.add_argument("--results", type=str, required=False, 
                       default="output/edges_coast_50.geojson",
                       help="Chemin du fichier GeoJSON des résultats")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.results):
        print(f"Erreur: fichier introuvable {args.results}")
        return
    
    analyze_results(args.results)


if __name__ == "__main__":
    main()


