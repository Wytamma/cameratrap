# Cameratrap photo submit

This repo will batch megadetector jobs for submission to PBS.

## Setup (only need to do this once)

Clone this repo.

```bash
$ git clone https://github.com/Wytamma/cameratrap && cd cameratrap
```

Run the setup script.

```bash
$ bash setup.sh
```

## Submit jobs 

```
$ python cameratrap.py /path/to/image/directory
```

Increase the amount of cores to speed up the analysis. 

```
$ python cameratrap.py --ncores 12 /path/to/image/directory
```

## Process results 

Once the analysis is finshed you can join the batched results into a single file.
```
$ python cameratrap.py --join-json /path/to/image/directory
```
