import os
import argparse
class Fetch(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data_fetch_decode()
def data_fetch_decode():
    fetch_cmd='cd ../utils/glouton-satnogs-data-downloader/; python3 ./glouton.py -s 2019-05-01T00:00:00 -e 2019-06-01T00:00:00 -n 43617 --demoddata --demodm CSV'
    os.system(fetch_cmd)
    all_directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    latest_directory = max(all_directories, key = os.path.getatime)
    print('Saving the dataframes in directory: '+latest_directory)
    merge_cmd='cd ../utils/glouton-satnogs-data-downloader/'+latest_directory+'; sed 1d *.csv > ../merged_frames.csv'
    os.system(merge_cmd)
    decode_cmd='cd ../utils/satnogs-decoders/; python decode-multiple.py -d Elfin -p -x ../glouton-satnogs-data-downloader/merged_frames.csv > ../../decoded_frames.json'
    os.system(decode_cmd)