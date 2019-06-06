import os

def data_fetch_decode():
    norad=input('Enter the NORAD ID of the satellite: ')
    start=input('Enter the start timestamp (YYYY-MM-DDTHH:MM:SS): ')
    end= input('Enter the end timestamp (YYYY-MM-DDTHH:MM:SS: ')
    cmd='cd ../utils/glouton/; python3 ./glouton.py -s'+start+' -e '+end+' -n '+norad+' --demoddata --demodm CSV'
    os.system(cmd)
