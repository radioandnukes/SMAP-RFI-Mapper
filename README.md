SMAP RFI Heatmap Generator

This script processes NASA SMAP L1B `.h5` data files to identify and visualize **extreme brightness temperature (TB)** values, which may indicate radio frequency interference (RFI) 
It generates an interactive HTML heatmap showing locations where TB exceeds a specified threshold (default: 310 K).

Requirements

pip install numpy h5py folium

Nuke's
