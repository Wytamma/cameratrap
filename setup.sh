#!/bin/bash
set -e

[ ! -d "./CameraTraps" ] && git clone https://github.com/microsoft/CameraTraps/
[ ! -d "./ai4eutils" ] && git clone https://github.com/microsoft/ai4eutils/
[ ! -d "./yolov5" ] && git clone https://github.com/ultralytics/yolov5/
cd yolov5 
git checkout c23a441c9df7ca9b1f275e8c8719c949269160d1
cd ..
[ ! -f "./md_v4.1.0.pb" ] && wget -O ./md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb
[ ! -f "./md_v5a.0.0.pt" ] && wget -O ./md_v5a.0.0.pt https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt
[ ! -f "./md_v5b.0.0.pt" ] && wget -O ./md_v5b.0.0.pt https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5b.0.0.pt

# if you have mamba use that because conda takes ages
conda env create --file CameraTraps/environment-detector.yml

# if you want to use the v4 model 
# conda activate cameratraps-detector && pip install tensorflow
