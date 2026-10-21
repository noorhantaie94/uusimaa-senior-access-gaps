"""
Mapper module for Uusimaa Senior Access Gaps project.
Provides publication-quality static visualization with coverage buffers, 
cartographic inset map, and interactive web visualization (folium).
"""

import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from shapely.geometry import box
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def plot_service_distribution(boundary_gdf, services_gdf, output_path="data/uusimaa_services_map.png"):
    """
    Generates an advanced publication-quality static map displaying:
    1. Essential service POIs and exact counts.
    2. 2 km Healthcare Coverage Buffers & Service Access Gaps.
    3. Cartographic Inset Map neatly anchored inside top-left.
    4. North Arrow indicator.
    """
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)

    # 1. Base Regional Boundary
    boundary_gdf.plot(
        ax=ax, 
        color='#F8F9FA', 
        edgecolor='#2B2D42', 
        linewidth=1.8, 
        linestyle='--',
        label='Uusimaa Regional Boundary'
    )

    # 2. Healthcare Coverage Buffers (2 km Spatial Service Coverage)
    health_services = services_gdf[services_gdf['service_type'].isin(["Pharmacy", "Health Center"])]
    if not health_services.empty:
        buffered_geoms = health_services.geometry.buffer(2000)
        buffers_union = buffered_geoms.unary_union
        
        gpd.GeoSeries([buffers_union], crs=services_gdf.crs).plot(
            ax=ax,
            color='#2A9D8F',
            alpha=0.20,
            edgecolor='#2A9D8F',
            linewidth=1.0,
            linestyle='-'
        )

    # 3. Plot POIs by Category with Exact Counts
    style_config = {
        "Pharmacy": {"color": "#E63946", "marker": "o", "size": 45},
        "Health Center": {"color": "#1D3557", "marker": "^", "size": 55},
        "Supermarket": {"color": "#E76F51", "marker": "s", "size": 40}
    }

    counts = services_gdf['service_type'].value_counts()

    for stype, cfg in style_config.items():
        subset = services_gdf[services_gdf['service_type'] == stype]
        if not subset.empty:
            count_val = counts.get(stype, len(subset))
            ax.scatter(
                subset.geometry.x, 
                subset.geometry.y, 
                c=cfg["color"], 
                marker=cfg["marker"], 
                s=cfg["size"], 
                alpha=0.90,
                edgecolors='white',
                linewidths=0.5,
                zorder=5,
                label=f"{stype} ({count_val})"
            )

    # 4. Municipality Callouts and Labels
    city_centers = {
        "Helsinki": (385000, 6672000),
        "Espoo": (373000, 6675000),
        "Vantaa": (388000, 6685000),
        "Porvoo": (428000, 6695000),
        "Lohja": (336000, 6683000)
    }

    for city, (x, y) in city_centers.items():
        ax.annotate(
            city, 
            xy=(x, y), 
            xytext=(x, y + 5500),
            fontsize=10, 
            fontweight='bold', 
            color='#1D3557',
            ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#1D3557', alpha=0.95, lw=1.2),
            arrowprops=dict(arrowstyle='->', color='#1D3557', lw=1.2),
            zorder=10
        )

    # 5. Cartographic Inset Map strictly anchored inside top-left
    ax_inset = inset_axes(ax, width="16%", height="20%", loc='upper left', borderpad=3)
    finland_box = box(100000, 6600000, 750000, 7800000)
    finland_gdf = gpd.GeoDataFrame(geometry=[finland_box], crs=3067)
    
    finland_gdf.plot(ax=ax_inset, color='#E9ECEF', edgecolor='#ADB5BD', lw=0.8)
    boundary_gdf.plot(ax=ax_inset, color='#E63946', edgecolor='#990000', lw=1.2)
    
    ax_inset.set_title("Uusimaa in Finland", fontsize=8, fontweight='bold', color='#1D3557', pad=3)
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])

    # 6. North Arrow Indicator
    ax.text(0.97, 0.08, 'N\n▲', transform=ax.transAxes, fontsize=12, fontweight='bold',
            ha='center', va='center', color='#1D3557',
            bbox=dict(boxstyle='circle,pad=0.3', facecolor='white', edgecolor='#1D3557', lw=1.1))

    # Title & Metadata Labels
    total_services = len(services_gdf)
    ax.set_title(
        f"Uusimaa Senior Access Gaps: Healthcare Coverage & Service Access Analysis\n"
        f"MAPPED FACILITIES: {total_services} | Green Shade = 2km Healthcare Access Coverage Zone", 
        fontsize=13, 
        fontweight='bold', 
        pad=15,
        color='#1D3557'
    )

    ax.set_xlabel("Easting / Coordinate X (m, EPSG:3067)", fontsize=10, labelpad=8)
    ax.set_ylabel("Northing / Coordinate Y (m, EPSG:3067)", fontsize=10, labelpad=8)

    ax.legend(
        title="Legend & Service Counts", 
        title_fontsize='10', 
        fontsize='9', 
        loc='upper right', 
        frameon=True, 
        facecolor='white', 
        edgecolor='#CCCCCC'
    )
    ax.grid(True, linestyle=':', alpha=0.3, color='#888888')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Advanced static map saved successfully to: {output_path}")


def create_interactive_map(services_gdf, output_path="data/uusimaa_interactive_map.html"):
    """
    Creates an interactive Folium web map featuring clustered markers
    and detailed popups using direct reliable CartoDB tiles.
    """
    services_wgs84 = services_gdf.to_crs(epsg=4326)

    center_lat = services_wgs84.geometry.y.mean()
    center_lon = services_wgs84.geometry.x.mean()

    carto_tile_url = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
    carto_attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'

    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=10, 
        tiles=carto_tile_url,
        attr=carto_attr
    )

    color_dict = {
        "Pharmacy": "red",
        "Health Center": "blue",
        "Supermarket": "green"
    }

    marker_cluster = MarkerCluster(name="Clustered Facilities").add_to(m)

    for _, row in services_wgs84.iterrows():
        stype = row["service_type"]
        lat = row.geometry.y
        lon = row.geometry.x
        
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; width: 160px;">
            <b>Service Type:</b> {stype}<br>
            <b>Latitude:</b> {lat:.4f}<br>
            <b>Longitude:</b> {lon:.4f}
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{stype}",
            icon=folium.Icon(color=color_dict.get(stype, "gray"), icon="info-sign")
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)
    m.save(output_path)
    print(f"Interactive map saved successfully to: {output_path}")