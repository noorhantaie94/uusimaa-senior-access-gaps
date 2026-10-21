"""
Network and spatial analysis module for Uusimaa Senior Access Gaps.
Computes distances from residential grids to nearest essential services
using spatial indexing (cKDTree).
"""

import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree


def calculate_distance_to_service(grid_gdf, services_gdf, service_type):
    """
    Calculate Euclidean distance in meters from each grid cell centroid 
    to the nearest service location of a specific type.
    """
    grid = grid_gdf.copy()
    
    # Filter services by selected type
    filtered_services = services_gdf[services_gdf["service_type"] == service_type].copy()
    
    if filtered_services.empty:
        raise ValueError(f"No services found for category: {service_type}")

    # Extract coordinates in EPSG:3067 (meters)
    grid_coords = np.array([(geom.centroid.x, geom.centroid.y) for geom in grid.geometry])
    service_coords = np.array([(geom.x, geom.y) for geom in filtered_services.geometry])

    # Nearest neighbor lookup via KDTree
    tree = cKDTree(service_coords)
    distances, _ = tree.query(grid_coords)

    # Append distance column in meters
    col_name = f"dist_{service_type.lower().replace(' ', '_')}_m"
    grid[col_name] = np.round(distances, 1)
    
    return grid


def compute_senior_access_index(grid_gdf):
    """
    Identify priority access gap zones based on senior population (65+)
    and walking distance thresholds (> 800m).
    """
    gdf = grid_gdf.copy()
    
    # Critical threshold: distance > 800m (winter walk limitation)
    gdf["desert_pharmacy"] = gdf["dist_pharmacy_m"] > 800
    
    # Vulnerability Score = Senior pop count * distance to pharmacy in km
    gdf["access_gap_score"] = gdf["pop_65plus"] * (gdf["dist_pharmacy_m"] / 1000.0)
    
    return gdf