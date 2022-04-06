for json in $( ls Chapter_4_trapping/FelixerTrialMonitoring/*/Chapter_*/combined.json )
do
    mv $json $(dirname $(dirname $json))/$(basename $(dirname $(dirname $json))).json
done
