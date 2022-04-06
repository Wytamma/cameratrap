# to run
# python mega_model.py [PATH]
# to join output
# python mega_model.py [PATH] --join-json
# to run directory as a single job
# python mega_model.py [PATH] --single-job

from glob import glob
import os
import argparse
import sys
import json
from pathlib import Path


def make_batch_json(directory, batch_size):
    print(directory)
    images = [f for f in glob(directory + "/*") if os.path.isfile(f)]
    print(len(images))
    batches = [images[i:i + batch_size] for i in range(0, len(images), batch_size)]
    print([len(x) for x in batches])
    out_dir = directory.replace("/", "_")
    if out_dir[-1] == "_":
        out_dir = out_dir[:-1]
    for i, batch in enumerate(batches):
        with open(f"{out_dir}/batch_{i}.json", 'w') as f:
            json.dump(batch, f)


def submit_batch_job(directory, mem="12gb", ncores="1"):
    PATH = Path(__file__).parent.absolute()
    json_files = [f for f in glob(directory + "/*.json")]
    for json_file in json_files:
        basename = os.path.basename(json_file)
        cmd = f"""set -e;
        module load anaconda3/2019.10; 
        source ~/.bashrc;
        conda activate cameratrap; 
        PYTHONPATH={PATH}/CameraTraps:{PATH}/ai4eutils python {PATH}/CameraTraps/detection/run_tf_detector_batch.py {PATH}/md_v4.1.0.pb "{json_file}" "{directory}/results_{basename}" """
        job_name = basename.replace(" ", "_")
        print(f"Submitting Job {job_name}")
        os.system(f'echo "{cmd}" | qsub -N {job_name} -l walltime=1:00:00 -l mem={mem} -l ncpus={ncores}')

def get_directories_from_path(directory):
    dirs = [f for f in glob(directory + "/*") if not os.path.isfile(f)]
    print(f"Found {len(dirs)} subdirectories")
    return dirs


def combine_data(directory):
    dirs = get_directories_from_path(directory)
    combined_data = []
    for image_dir in dirs:
        basename = os.path.basename(image_dir)
        try:
            with open(f"{image_dir}/{basename}.json") as f:
                data = json.load(f)
            print(f"{basename}.json - {len(data['images'])}")
        except:
            print(f"{basename}.json not found!")
            continue
        combined_data += data["images"]
    # use 'info' and 'detection_categories' from last image_dir
    data["images"] = combined_data
    basename = os.path.basename(directory)
    with open(f"{directory}/{basename}.json", "w") as f:
        json.dump(data, f)
    print(
        f"Saved combined data ({len(data['images'])}) as '{basename}.json' in '{directory}'"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "directory",
        type=str,
        help="Path to directory of images",
    )
    parser.add_argument(
        "--join-json",
        default=False,
        action="store_true",
        help="Look for json files in the subdirectories and join them.",
    )
    parser.add_argument(
        "--recursive",
        default=False,
        action="store_true",
        help="Run the specified directory as a single job.",
    )
    parser.add_argument(
        "--ncores",
        default="1",
        type=str,
        help="Number of cores to use.",
    )
    parser.add_argument(
        "--mem",
        default="12gb",
        type=str,
        help="Amount of memory to use.",
    )
    parser.add_argument(
        "--walltime",
        default="1:00:00",
        type=str,
        help="Amount of memory to use.",
    )
    args = parser.parse_args()

    if args.join_json:
        combine_data(args.directory)
    elif args.recursive:
        dirs = get_directories_from_path(args.directory)
        if (
            input(
                "Are you sure you want run the megadetector model on these directories? (y/n) "
            ).lower()
            == "y"
        ):
            for image_dir in dirs:
                make_batch_json(directory=image_dir)
                submit_batch_job(directory=image_dir, mem=args.mem, ncores=args.ncores)
        else:
            print("Aborted!")
    else:
        make_batch_json(directory=args.directory)
        submit_batch_job(args.directory, ncores=args.ncores)
        
