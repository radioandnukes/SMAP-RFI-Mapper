import os
import argparse
import numpy as np
import h5py
import folium
from folium.plugins import HeatMap

def extract_extreme_tb_heat_data(h5_file, threshold=310):
    try:
        with h5py.File(h5_file, 'r') as f:
            bt = f['Brightness_Temperature']
            tb_h = bt['tb_h'][:]
            tb_v = bt['tb_v'][:]
            lat = bt['tb_lat'][:]
            lon = bt['tb_lon'][:]
            avg_tb = (tb_h + tb_v) / 2
            mask = (avg_tb > threshold) & np.isfinite(avg_tb) & np.isfinite(lat) & np.isfinite(lon)
            return np.vstack([
                lat[mask].flatten(),
                lon[mask].flatten(),
                avg_tb[mask].flatten()
            ]).T.tolist()
    except Exception as e:
        print(f"Failed to process {h5_file}: {e}")
        return []

def process_files(paths, threshold=310):
    all_data = []
    for path in paths:
        if path.lower().endswith(".h5"):
            all_data += extract_extreme_tb_heat_data(path, threshold)
    return all_data

def generate_heatmap(data, output_path):
    if not data:
        print("No extreme TB data found.")
        return
    lat_vals = [row[0] for row in data]
    lon_vals = [row[1] for row in data]
    m = folium.Map(location=[np.mean(lat_vals), np.mean(lon_vals)],
                   zoom_start=2, tiles='CartoDB dark_matter')
    HeatMap(data, radius=7, blur=10, max_zoom=4).add_to(m)
    m.save(output_path)
    print(f"Heatmap saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a SMAP extreme TB heatmap from HDF5 files.")
    parser.add_argument("input", help="Path to a .h5 file or a directory containing them.")
    parser.add_argument("--threshold", type=float, default=310, help="TB threshold (default: 310K)")
    parser.add_argument("--output", type=str, default="smap_extreme_tb_heatmap.html", help="Output HTML file")

    args = parser.parse_args()

    if os.path.isfile(args.input):
        files = [args.input]
    elif os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(".h5")]
    else:
        print("Invalid input path.")
        return

    all_data = process_files(files, args.threshold)
    generate_heatmap(all_data, args.output)

if __name__ == "__main__":
    main()
