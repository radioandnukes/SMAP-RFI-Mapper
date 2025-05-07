import os
import argparse
import numpy as np
import h5py
import folium
from folium.plugins import HeatMap
import json

def extract_extreme_tb(h5_file, threshold=310):
    points = []
    features = []
    try:
        with h5py.File(h5_file, 'r') as f:
            bt = f['Brightness_Temperature']
            tb_h = bt['tb_h'][:]
            tb_v = bt['tb_v'][:]
            lat = bt['tb_lat'][:]
            lon = bt['tb_lon'][:]
            avg_tb = (tb_h + tb_v) / 2
            mask = (avg_tb > threshold) & np.isfinite(avg_tb) & np.isfinite(lat) & np.isfinite(lon)

            lat_flat = lat[mask].flatten()
            lon_flat = lon[mask].flatten()
            tb_flat = avg_tb[mask].flatten()

            for la, lo, tb in zip(lat_flat, lon_flat, tb_flat):
                pt = [float(la), float(lo), float(tb)]
                points.append(pt)
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [float(lo), float(la)]},
                    "properties": {"brightness_temp": float(tb)}
                })

    except Exception as e:
        print(f"Error processing {h5_file}: {e}")
    return points, features

def process_files(paths, threshold=310):
    all_points, all_features = [], []
    for path in paths:
        if path.lower().endswith(".h5"):
            pts, feats = extract_extreme_tb(path, threshold)
            all_points.extend(pts)
            all_features.extend(feats)
    return all_points, all_features

def generate_heatmap(data, output_path):
    if not data:
        print("No extreme TB data found.")
        return
    lat_vals = [p[0] for p in data]
    lon_vals = [p[1] for p in data]
    heat_data = [[p[0], p[1], p[2]] for p in data]

    m = folium.Map(location=[np.mean(lat_vals), np.mean(lon_vals)],
                   zoom_start=2, tiles='CartoDB dark_matter')
    HeatMap(heat_data, radius=7, blur=10, max_zoom=4).add_to(m)
    m.save(output_path)
    print(f"✅ Heatmap saved: {output_path}")

def save_geojson(features, geojson_path):
    geojson = {"type": "FeatureCollection", "features": features}
    with open(geojson_path, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"✅ GeoJSON saved: {geojson_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate heatmaps and GeoJSON of extreme SMAP brightness temperatures.")
    parser.add_argument("input", help="Path to a single HDF5 file or directory of files.")
    parser.add_argument("--threshold", type=float, default=310, help="TB threshold in Kelvin (default: 310)")
    parser.add_argument("--output", type=str, default="smap_extreme_tb_heatmap.html", help="HTML heatmap output filename")
    parser.add_argument("--geojson", type=str, help="Optional output GeoJSON filename")

    args = parser.parse_args()

    # Resolve file list
    if os.path.isfile(args.input):
        files = [args.input]
    elif os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(".h5")]
    else:
        print("❌ Invalid input path.")
        return

    points, features = process_files(files, args.threshold)

    if points:
        generate_heatmap(points, args.output)
        if args.geojson:
            save_geojson(features, args.geojson)
    else:
        print("⚠️ No data above the threshold was found.")

if __name__ == "__main__":
    main()
