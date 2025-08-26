import argparse
import os
from typing import List, Dict, Any

import osmnx as ox
import geopandas as gpd
from shapely.geometry import LineString

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geo import build_profile_and_radii, cut_linestring_at_length
from src.physics import simulate_segment
from src.params import PhysicalParams


def ensure_edge_geometries(G) -> None:
    """Ensure every edge has a LineString geometry in projected CRS."""
    for u, v, k, data in G.edges(keys=True, data=True):
        if data.get("geometry") is None:
            xu = G.nodes[u].get("x")
            yu = G.nodes[u].get("y")
            xv = G.nodes[v].get("x")
            yv = G.nodes[v].get("y")
            if xu is None or yu is None or xv is None or yv is None:
                continue
            data["geometry"] = LineString([(float(xu), float(yu)), (float(xv), float(yv))])


def process_edges(G, dem_path: str, step_m: float, v0: float, p: PhysicalParams) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    graph_crs = G.graph.get("crs")
    for u, v, k, data in G.edges(keys=True, data=True):
        geom = data.get("geometry")
        if geom is None:
            continue
        length_m = float(geom.length)
        if not (length_m > 1.0):
            continue
        try:
            profile, radii = build_profile_and_radii(geom, graph_crs=graph_crs, dem_path=dem_path, step_m=step_m)
        except Exception as e:
            # Skip edges that fail DEM sampling
            continue
        if len(profile) == 0:
            continue
        dist, t, vout, vmax = simulate_segment(profile, v0=v0, p=p, radii=radii)
        traveled = min(float(dist), length_m)
        try:
            geom_trunc = cut_linestring_at_length(geom, traveled)
        except Exception:
            geom_trunc = geom
        results.append({
            "u": u,
            "v": v,
            "key": k,
            "length_m": length_m,
            "coast_distance_m": float(traveled),
            "coast_time_s": float(t),
            "v_out_mps": float(vout),
            "v_max_mps": float(vmax),
            "geometry": geom_trunc,
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="CoastMax POC — simulation par arête sur une zone")
    parser.add_argument("--place", type=str, required=False, default="Ariège, France",
                        help="Zone OSM (ex: 'Ariège, France' ou 'Cantal, France')")
    parser.add_argument("--dem", type=str, required=True, help="Chemin du DEM GeoTIFF (Copernicus/SRTM)")
    parser.add_argument("--step_m", type=float, default=20.0, help="Pas de densification en mètres")
    parser.add_argument("--v0", type=float, default=1.0, help="Vitesse initiale en m/s")
    parser.add_argument("--topN", type=int, default=200, help="Nombre de meilleurs segments à exporter")
    parser.add_argument("--network_type", type=str, default="bike", help="Type de réseau OSMnx (bike, walk, drive)")
    args = parser.parse_args()

    if not os.path.exists(args.dem):
        raise FileNotFoundError(f"DEM introuvable: {args.dem}")

    print(f"Chargement réseau OSM pour: {args.place}")
    G = ox.graph_from_place(args.place, network_type=args.network_type, simplify=True)
    print("Projection du graphe en métrique...")
    Gp = ox.project_graph(G)
    ensure_edge_geometries(Gp)

    print("Simulation par arête (roue libre)...")
    p = PhysicalParams()
    results = process_edges(Gp, args.dem, args.step_m, args.v0, p)
    if len(results) == 0:
        print("Aucun résultat. Vérifier la zone et le DEM.")
        return
    gdf = gpd.GeoDataFrame(results, geometry="geometry", crs=Gp.graph.get("crs"))
    gdf = gdf.sort_values("coast_distance_m", ascending=False).head(args.topN)

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"edges_coast_{args.topN}.geojson")
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"Exporté: {out_path}")


if __name__ == "__main__":
    main()


