# to run
# python mega_model.py [PATH]
# to join output
# python mega_model.py [PATH] --join-json
# to run directory as a single job
# python mega_model.py [PATH] --single-job

from glob import glob
import os
import argparse
import json
from pathlib import Path


def make_batch_json(directory, batch_size=100):
    images = [os.path.join(os.getcwd(), f) for f in glob(directory + "/*") if os.path.isfile(f) and not f.endswith(".json")]
    batches = [images[i:i + batch_size] for i in range(0, len(images), batch_size)]
    print(f"Creating {len(batches)} batches ({[len(x) for x in batches]})")
    if not os.path.exists(f"{directory}/batches"):
        os.mkdir(f"{directory}/batches")
    for i, batch in enumerate(batches):
        with open(f"{directory}/batches/batch_{i}.json", 'w') as f:
            json.dump(batch, f)


def submit_batch_jobs(directory, mem="12gb", ncores="1", walltime="1:00:00", model="5a"):
    if not os.path.exists(f"{directory}/results"):
        os.mkdir(f"{directory}/results")
    batch_files = [os.path.join(os.getcwd(), f) for f in glob(directory + "/batches/batch_*.json")]
    for json_file in batch_files:
        submit_batch_job(json_file, mem=mem, ncores=ncores, walltime=walltime, model=model)
        
def submit_batch_job(json_file, mem="12gb", ncores="1", walltime="1:00:00", model="5a", no_q=False):
    models = {
        '5a':"md_v5a.0.0.pt",
        '5b':"md_v5b.0.0.pt",
        '4':"md_v4.1.0.pb"
    }
    PATH = Path(__file__).parent.absolute()
    directory = str(Path(json_file).parent.parent)
    basename = os.path.basename(json_file)
    if directory.endswith('/'):
        directory = directory[:-1]
    jobname = f'{directory.split("/")[-1]}_{basename}'
    THREADS = int(ncores)
    cmd = f"""set -e;
    source ~/.bashrc;
    conda activate cameratraps-detector;
    echo Processing batch {json_file};
    export OMP_NUM_THREADS={THREADS};
    export TF_NUM_INTEROP_THREADS={THREADS};
    export TF_NUM_INTRAOP_THREADS={THREADS};
    PYTHONPATH=$PYTHONPATH:{PATH}/CameraTraps:{PATH}/ai4eutils:{PATH}/yolov5 python {PATH}/CameraTraps/detection/run_detector_batch.py {PATH}/{models[model]} {json_file} {os.path.join(os.getcwd(), directory)}/results/{basename}"""
    print(f"Submitting Job {basename} ({directory})")
    if no_q:
        os.system(cmd)
    else:
        os.system(f'echo "{cmd}" | qsub -j oe -N {jobname} -l walltime={walltime} -l mem={mem} -l ncpus={ncores}')


def get_directories_from_path(directory):
    dirs = [f for f in glob(directory + "/*") if not os.path.isfile(f)]
    print(f"Found {len(dirs)} subdirectories")
    return dirs


def combine_data(directory):
    json_files = [f for f in glob(directory + "/*/PHOTO/results/*.json")]
    if not len(json_files):
        raise ValueError('No results files found')
    combined_data = []
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
        print(f"{json_file} - {len(data['images'])}")
        combined_data += data["images"]
    # use 'info' and 'detection_categories' from last image_dir

    for image in combined_data:
        image['file'] = '/'.join(image['file'].split('/')[-3:])

    data['images'] = combined_data
    # "file": "/home/jc807286/camera_trapping/Duval/Trip1/Duval_April2021_wetA_camera15/PHOTO/IM_00018.JPG"
    if directory.endswith('/'):
        directory = directory[:-1]
    filename = f"{directory.replace('/', '_')}_results_combined.json"
    with open(filename, "w") as f:
        json.dump(data, f)
    print(
        f"Saved combined data ({len(data['images'])}) as '{filename}'"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "directory",
        type=str,
        help="Path to directory of images or batch file to run",
    )
    parser.add_argument(
        "--join-json",
        default=False,
        action="store_true",
        help="Combine the batch results into a single file.",
    )
    parser.add_argument(
        "--dry",
        default=False,
        action="store_true",
        help="Create batches don't run.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Size of batches",
    )
    parser.add_argument(
        "--recursive",
        default=False,
        action="store_true",
        help="Run recursively on a directory of directories.",
    )
    parser.add_argument(
        "--ncores",
        default="1",
        type=str,
        help="Number of cores to allocate.",
    )
    parser.add_argument(
        "--mem",
        default="8gb",
        type=str,
        help="Amount of memory to allocate.",
    )
    parser.add_argument(
        "--walltime",
        default="2:00:00",
        type=str,
        help="Amount of time to allocate.",
    )
    parser.add_argument(
        "--model",
        default="5a",
        type=str,
        help="The model to use. 5a, 5b, or 4",
    )
    args = parser.parse_args()
    if args.join_json:
        combine_data(args.directory)
    elif args.directory.endswith(".json"):
        submit_batch_job(json_file=args.directory, mem=args.mem, ncores=args.ncores, walltime=args.walltime, model=args.model)
    elif args.recursive:
        dirs = get_directories_from_path(args.directory)
        if (
            input(
                "Are you sure you want run the megadetector model on these directories? (y/n) "
            ).lower()
            == "y"
        ):
            for image_dir in dirs:
                make_batch_json(directory=image_dir, batch_size=args.batch_size)
                if not args.dry:
                    submit_batch_jobs(directory=image_dir, mem=args.mem, ncores=args.ncores, walltime=args.walltime, model=args.model)
        else:
            print("Aborted!")
    else:
        make_batch_json(directory=args.directory, batch_size=args.batch_size)
        if not args.dry:
            submit_batch_jobs(directory=args.directory,  mem=args.mem, ncores=args.ncores,  walltime=args.walltime, model=args.model)
        
