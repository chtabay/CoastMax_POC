#!/usr/bin/env python3
"""
Architecture CoastMax France - Gestion multi-régions et navigation progressive.
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RegionConfig:
    """Configuration d'une région."""
    name: str
    display_name: str
    bounds: tuple  # (west, south, east, north)
    center: tuple  # (lat, lon)
    zoom: int
    color: str
    description: str


class FranceCoastMax:
    """Gestionnaire principal pour CoastMax France."""
    
    def __init__(self):
        self.regions = self._init_regions()
        self.output_dir = Path("docs/france")
        self.output_dir.mkdir(exist_ok=True)
    
    def _init_regions(self) -> Dict[str, RegionConfig]:
        """Initialise les configurations des régions."""
        return {
            "alpes": RegionConfig(
                name="alpes",
                display_name="Alpes",
                bounds=(5.0, 44.0, 7.5, 46.5),
                center=(45.2, 6.2),
                zoom=8,
                color="#ff6b6b",
                description="Massif alpin - cols légendaires et descentes épiques"
            ),
            "pyrenees": RegionConfig(
                name="pyrenees", 
                display_name="Pyrénées",
                bounds=(-1.5, 42.0, 3.0, 43.5),
                center=(42.8, 1.0),
                zoom=8,
                color="#4ecdc4",
                description="Chaîne pyrénéenne - cols mythiques et vallées sauvages"
            ),
            "massif_central": RegionConfig(
                name="massif_central",
                display_name="Massif Central", 
                bounds=(1.5, 44.5, 4.5, 46.0),
                center=(45.2, 3.0),
                zoom=8,
                color="#45b7d1",
                description="Massif central - volcans éteints et plateaux"
            ),
            "jura": RegionConfig(
                name="jura",
                display_name="Jura",
                bounds=(5.0, 46.0, 7.0, 47.5),
                center=(46.7, 6.0),
                zoom=9,
                color="#96ceb4",
                description="Massif du Jura - reliefs doux et lacs"
            ),
            "vosges": RegionConfig(
                name="vosges",
                display_name="Vosges",
                bounds=(6.0, 47.5, 8.0, 49.0),
                center=(48.2, 7.0),
                zoom=9,
                color="#feca57",
                description="Massif des Vosges - forêts et sommets arrondis"
            ),
            "corse": RegionConfig(
                name="corse",
                display_name="Corse",
                bounds=(8.5, 41.5, 9.5, 43.0),
                center=(42.2, 9.0),
                zoom=9,
                color="#ff9ff3",
                description="Île de Beauté - montagnes dans la mer"
            )
        }
    
    def create_france_structure(self) -> Dict[str, Any]:
        """Crée la structure de données pour la France entière."""
        return {
            "metadata": {
                "version": "1.0",
                "generated": "2024-12",
                "description": "CoastMax France - Meilleurs parcours de roue libre",
                "total_regions": len(self.regions)
            },
            "france_overview": {
                "bounds": (2.0, 41.0, 8.5, 51.0),  # France métropolitaine
                "center": (46.0, 2.0),
                "zoom": 6
            },
            "regions": {
                name: {
                    "config": {
                        "display_name": region.display_name,
                        "bounds": region.bounds,
                        "center": region.center,
                        "zoom": region.zoom,
                        "color": region.color,
                        "description": region.description
                    },
                    "stats": {
                        "total_segments": 0,
                        "max_distance": 0,
                        "max_speed": 0,
                        "avg_distance": 0,
                        "last_updated": None
                    },
                    "segments": []
                }
                for name, region in self.regions.items()
            },
            "national_records": {
                "max_distance": {"value": 0, "region": None, "segment_id": None},
                "max_speed": {"value": 0, "region": None, "segment_id": None},
                "longest_route": {"value": 0, "region": None, "route_id": None}
            }
        }
    
    def generate_france_data(self) -> None:
        """Génère tous les fichiers de données pour la France."""
        print("🏗️  Génération de l'architecture CoastMax France...")
        
        # Structure principale
        france_data = self.create_france_structure()
        
        # Sauvegarder la structure
        with open(self.output_dir / "france_structure.json", "w", encoding="utf-8") as f:
            json.dump(france_data, f, ensure_ascii=False, indent=2)
        
        # Générer les fichiers de configuration
        self._generate_region_configs()
        self._generate_navigation_config()
        
        print(f"✅ Architecture France générée dans {self.output_dir}")
        print(f"   📁 {len(self.regions)} régions configurées")
        print(f"   📄 Structure: france_structure.json")
    
    def _generate_region_configs(self) -> None:
        """Génère les configurations individuelles par région."""
        for name, region in self.regions.items():
            config = {
                "name": name,
                "display_name": region.display_name,
                "bounds": region.bounds,
                "center": region.center,
                "zoom": region.zoom,
                "color": region.color,
                "description": region.description,
                "data_files": {
                    "segments": f"{name}_segments.geojson",
                    "stats": f"{name}_stats.json",
                    "top_segments": f"{name}_top.json"
                }
            }
            
            with open(self.output_dir / f"{name}_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _generate_navigation_config(self) -> None:
        """Génère la configuration de navigation progressive."""
        navigation = {
            "levels": {
                "france": {
                    "name": "Vue France",
                    "description": "Vue d'ensemble nationale avec heatmap des régions",
                    "features": [
                        "Carte France avec régions colorées",
                        "Top 20 national",
                        "Statistiques comparatives",
                        "Recherche par région"
                    ]
                },
                "region": {
                    "name": "Vue Régionale", 
                    "description": "Zoom sur une région avec segments détaillés",
                    "features": [
                        "Carte régionale détaillée",
                        "Liste des segments avec filtres",
                        "Comparaison inter-régions",
                        "Statistiques régionales"
                    ]
                },
                "segment": {
                    "name": "Vue Segment",
                    "description": "Détail d'un segment avec profil et simulation",
                    "features": [
                        "Profil d'altitude interactif",
                        "Simulation physique temps réel",
                        "Export GPX/TCX",
                        "Comparaison avec segments similaires"
                    ]
                }
            },
            "navigation": {
                "france_to_region": "Clic sur région → zoom automatique",
                "region_to_segment": "Clic sur segment → détail complet",
                "breadcrumb": "France > Région > Segment"
            }
        }
        
        with open(self.output_dir / "navigation_config.json", "w", encoding="utf-8") as f:
            json.dump(navigation, f, ensure_ascii=False, indent=2)


def main():
    """Point d'entrée principal."""
    france = FranceCoastMax()
    france.generate_france_data()
    
    print("\n🎯 Prochaines étapes:")
    print("   1. Générer les données par région")
    print("   2. Créer la carte France interactive")
    print("   3. Implémenter la navigation progressive")


if __name__ == "__main__":
    main()
