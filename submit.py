# to run
# python mega_model.py [PATH]
# to join output
# python mega_model.py [PATH] --join-json
# to run folder as a single job
# python mega_model.py [PATH] --single-job

from glob import glob
import os
import argparse
import sys
import json


def make_batch_json(folder, batch_size=200):
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

def submit_job(directory, mem="12gb", ncores="1"):
    make_batch_json()


def submit_batch_job(directory, mem="12gb", ncores="1"):
    json_files = [f for f in glob(directory + "/*.json")]

    for json_file in json_files:
        basename = os.path.basename(json_file)
        cmd = f"""set -e;
        module load anaconda3/2019.10; 
        source ~/.bashrc;
        conda activate cameratraps-detector; 
        PYTHONPATH=/home/jc449852/CameraTraps:/home/jc449852/ai4eutils python /home/jc449852/CameraTraps/detection/run_tf_detector_batch.py /home/jc449852/CameraTraps/megadetector_v4_1_0.pb "{json_file}" "{directory}/results_{basename}" """
        job_name = basename.replace(" ", "_")
        print(f"Submitting Job {job_name}")
        os.system(f'echo "{cmd}" | qsub -N {job_name} -l walltime=1:00:00 -l mem={mem} -l ncpus={ncores}')

def get_folders_from_path(folder):
    dirs = [f for f in glob(folder + "/*") if not os.path.isfile(f)]
    print(f"Found {len(dirs)} subfolders")
    return dirs


def combine_data(folder):
    dirs = get_folders_from_path(folder)
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
    basename = os.path.basename(folder)
    with open(f"{folder}/{basename}.json", "w") as f:
        json.dump(data, f)
    print(
        f"Saved combined data ({len(data['images'])}) as '{basename}.json' in '{folder}'"
    )


def main(folder, ncores="1"):
    dirs = get_folders_from_path(folder)
    if (
        input(
            "Are you sure you want run the megadetector model on these folders? (y/n) "
        ).lower()
        != "y"
    ):
        print("Aborted!")
        return None
    for image_dir in dirs:
        submit_job(image_dir, ncores=ncores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder by default run all folders inside run as a separate job",
    )
    parser.add_argument(
        "--join-json",
        default=False,
        action="store_true",
        help="Look for json files in the subfolders and join them.",
    )
    parser.add_argument(
        "--single-job",
        default=False,
        action="store_true",
        help="Run the specified folder as a single job.",
    )
    parser.add_argument(
        "--batch-job",
        default=False,
        action="store_true",
        help="Run as JSON batch job",
    )
    parser.add_argument(
        "--ncores",
        default="1",
        type=str,
        help="Number of cores to use.",
    )
    args = parser.parse_args()

    if args.single_job:
        submit_job(args.folder, ncores=args.ncores)
    elif args.join_json:
        combine_data(args.folder)
    elif args.batch_job:
        submit_batch_job(args.folder, ncores=args.ncores)
    else:
        main(args.folder, ncores=args.ncores)
