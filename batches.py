import itertools
from glob import glob
import argparse
import os
import json

def make_batch_json(folder, batch_size):
    print(folder)
    images = [f for f in glob(folder + "/*") if os.path.isfile(f)]
    print(len(images))
    batches = [images[i:i + batch_size] for i in range(0, len(images), batch_size)]
    print([len(x) for x in batches])
    out_dir = folder.replace("/", "_")
    if out_dir[-1] == "_":
        out_dir = out_dir[:-1]
    for i, batch in enumerate(batches):
        with open(f"{out_dir}/batch_{i}.json", 'w') as f:
            json.dump(batch, f)

def combine_data(folder):
    json_files = [f for f in glob(folder + "/*") if os.path.basename(f).startswith('results_')]
    combined_data = []
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
        print(f"{json_file} - {len(data['images'])}")
        combined_data += data["images"]
    # use 'info' and 'detection_categories' from last image_dir
    data["images"] = combined_data
    basename = os.path.basename(folder)
    with open(f"{folder}/combined.json", "w") as f:
        json.dump(data, f)
    print(
        f"Saved combined data ({len(data['images'])}) as 'combined.json' in '{folder}'"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create batch files for prcessing")
    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder of imaages",
    )
    parser.add_argument(
        "batch_size",
        type=int,
        nargs='?', 
        const=200,
        help="Size of batches",
    )
    parser.add_argument(
        "--join-json",
        default=False,
        action="store_true",
        help="join the resutls",
    )
    args = parser.parse_args()
    if args.join_json:
        combine_data(args.folder)
    else:
        make_batch_json(args.folder, args.batch_size)
