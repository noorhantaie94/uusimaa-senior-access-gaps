"""
Data loader module for Uusimaa Senior Access Gaps project.
Generates essential service POIs and boundary geometries for Uusimaa region
in EPSG:3067 CRS.
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box


def get_uusimaa_boundary():
    """Returns Uusimaa regional boundary polygon in EPSG:3067."""
    uusimaa_box = box(280000, 6630000, 460000, 6720000)
    return gpd.GeoDataFrame({"name": ["Uusimaa"]}, geometry=[uusimaa_box], crs=3067)


def fetch_essential_services(region_name="Espoo, Finland"):
    """
    Returns essential services (Pharmacies, Health Centers, Supermarkets)
    for specified Uusimaa municipalities in EPSG:3067.
    """
    city_coords = {
        "Helsinki": (385000, 6672000, 45, 25, 90),
        "Espoo": (373000, 6675000, 20, 15, 50),
        "Vantaa": (388000, 6685000, 18, 12, 45),
        "Porvoo": (428000, 6695000, 10, 8, 25),
        "Lohja": (336000, 6683000, 10, 6, 20)
    }
    
    clean_name = region_name.split(",")[0].strip()
    cx, cy, num_pharm, num_health, num_super = city_coords.get(
        clean_name, (380000, 6680000, 15, 10, 30)
    )
    
    np.random.seed(abs(hash(clean_name)) % 10000)
    records = []
    
    services = [
        ("Pharmacy", num_pharm),
        ("Health Center", num_health),
        ("Supermarket", num_super)
    ]
    
    for stype, count in services:
        xs = cx + np.random.normal(0, 3200, count)
        ys = cy + np.random.normal(0, 3200, count)
        for x, y in zip(xs, ys):
            records.append({"service_type": stype, "geometry": Point(x, y)})
            
    return gpd.GeoDataFrame(records, crs=3067)