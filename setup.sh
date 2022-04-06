#!/bin/bash
set -e

[ ! -d "./CameraTraps" ] && git clone https://github.com/microsoft/CameraTraps/
[ ! -d "./ai4eutils" ] && git clone https://github.com/microsoft/ai4eutils/
[ ! -f "./md_v4.1.0.pb" ] && wget -O ./md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb

conda env create --file environment-detector.yml