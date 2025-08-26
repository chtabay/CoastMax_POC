#!/usr/bin/env python3
"""
Intégration des données Ariège dans l'architecture France.
"""

import json
import os
from pathlib import Path


def integrate_ariege_into_france():
    """Intègre les données de l'Ariège dans la structure France."""
    print("🔄 Intégration des données Ariège dans l'architecture France...")
    
    # Charger les données Ariège existantes
    ariege_data_path = Path("docs/top_segments.json")
    if not ariege_data_path.exists():
        print("❌ Fichier docs/top_segments.json introuvable")
        print("Exécutez d'abord: python src/prepare_web_data.py")
        return
    
    with open(ariege_data_path, 'r', encoding='utf-8') as f:
        ariege_data = json.load(f)
    
    # Charger la structure France
    france_structure_path = Path("docs/france/france_structure.json")
    if not france_structure_path.exists():
        print("❌ Fichier docs/france/france_structure.json introuvable")
        print("Exécutez d'abord: python src/france_architecture.py")
        return
    
    with open(france_structure_path, 'r', encoding='utf-8') as f:
        france_data = json.load(f)
    
    # Calculer les statistiques Ariège
    ariege_stats = calculate_ariege_stats(ariege_data)
    
    # Mettre à jour la région Pyrénées avec les données Ariège
    france_data["regions"]["pyrenees"]["stats"] = ariege_stats
    france_data["regions"]["pyrenees"]["segments"] = ariege_data["top_distance"][:20]  # Top 20
    
    # Mettre à jour les records nationaux si nécessaire
    if ariege_stats["max_distance"] > france_data["national_records"]["max_distance"]["value"]:
        france_data["national_records"]["max_distance"] = {
            "value": ariege_stats["max_distance"],
            "region": "pyrenees",
            "segment_id": f"{ariege_data['top_distance'][0]['start_node']}-{ariege_data['top_distance'][0]['end_node']}"
        }
    
    if ariege_stats["max_speed"] > france_data["national_records"]["max_speed"]["value"]:
        france_data["national_records"]["max_speed"] = {
            "value": ariege_stats["max_speed"],
            "region": "pyrenees", 
            "segment_id": f"{ariege_data['top_speed'][0]['start_node']}-{ariege_data['top_speed'][0]['end_node']}"
        }
    
    # Sauvegarder la structure mise à jour
    with open(france_structure_path, 'w', encoding='utf-8') as f:
        json.dump(france_data, f, ensure_ascii=False, indent=2)
    
    # Créer les fichiers spécifiques Pyrénées
    create_pyrenees_files(ariege_data, ariege_stats)
    
    print("✅ Données Ariège intégrées dans l'architecture France")
    print(f"   📊 {ariege_stats['total_segments']} segments intégrés")
    print(f"   🏆 Record distance: {ariege_stats['max_distance']}m")
    print(f"   ⚡ Record vitesse: {ariege_stats['max_speed']} km/h")


def calculate_ariege_stats(ariege_data):
    """Calcule les statistiques pour l'Ariège."""
    all_segments = ariege_data["top_distance"] + ariege_data["top_speed"]
    
    # Éviter les doublons
    unique_segments = {}
    for segment in all_segments:
        segment_id = segment["id"]
        if segment_id not in unique_segments:
            unique_segments[segment_id] = segment
    
    segments = list(unique_segments.values())
    
    distances = [s["coast_distance_m"] for s in segments]
    speeds = [s["v_max_kmh"] for s in segments]
    
    return {
        "total_segments": len(segments),
        "max_distance": max(distances) if distances else 0,
        "max_speed": max(speeds) if speeds else 0,
        "avg_distance": sum(distances) / len(distances) if distances else 0,
        "last_updated": "2024-12"
    }


def create_pyrenees_files(ariege_data, ariege_stats):
    """Crée les fichiers spécifiques pour les Pyrénées."""
    france_dir = Path("docs/france")
    
    # Fichier de statistiques Pyrénées
    pyrenees_stats = {
        "region": "pyrenees",
        "display_name": "Pyrénées",
        "stats": ariege_stats,
        "description": "Chaîne pyrénéenne - cols mythiques et vallées sauvages",
        "sub_regions": {
            "ariege": {
                "name": "Ariège",
                "segments": len(ariege_data["top_distance"]),
                "max_distance": max([s["coast_distance_m"] for s in ariege_data["top_distance"]]),
                "max_speed": max([s["v_max_kmh"] for s in ariege_data["top_speed"]])
            }
        }
    }
    
    with open(france_dir / "pyrenees_stats.json", 'w', encoding='utf-8') as f:
        json.dump(pyrenees_stats, f, ensure_ascii=False, indent=2)
    
    # Fichier des top segments Pyrénées
    pyrenees_top = {
        "region": "pyrenees",
        "top_distance": ariege_data["top_distance"][:10],
        "top_speed": ariege_data["top_speed"][:10],
        "total_segments": len(ariege_data["top_distance"])
    }
    
    with open(france_dir / "pyrenees_top.json", 'w', encoding='utf-8') as f:
        json.dump(pyrenees_top, f, ensure_ascii=False, indent=2)


def main():
    """Point d'entrée principal."""
    integrate_ariege_into_france()
    
    print("\n🎯 Prochaines étapes:")
    print("   1. Tester la carte France interactive")
    print("   2. Ajouter d'autres régions (Alpes, Massif Central)")
    print("   3. Implémenter la navigation niveau 2 (régional)")


if __name__ == "__main__":
    main()
