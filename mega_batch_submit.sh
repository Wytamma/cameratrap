for dir in Chapter_4_trapping_* 
do
    python mega_model.py --ncores 12 --batch-job $dir
done
