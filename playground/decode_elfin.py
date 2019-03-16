import sys, getopt
import pandas as pd
from tqdm import tqdm
import binascii
from datetime import datetime

from kaitai_parsers.ax25frames import Ax25frames
from kaitai_parsers.elfin import Elfin


def get_date(pkt):
    def _dec(date):
        date_str = str(hex(date))
        return int(date_str[2:])

    year = _dec(pkt.elfin_hskp_pwr1_rtcc_year) + 2000
    month = _dec(pkt.elfin_hskp_pwr1_rtcc_month)
    day = _dec(pkt.elfin_hskp_pwr1_rtcc_day)
    hour = _dec(pkt.elfin_hskp_pwr1_rtcc_hour)
    minute = _dec(pkt.elfin_hskp_pwr1_rtcc_minute)
    second = _dec(pkt.elfin_hskp_pwr1_rtcc_second)
    return datetime(year, month, day, hour, minute, second)

def get_bat_temp_celsius(reg):
    return (reg / 32.0) * 0.125

def get_bat_volt(reg):
    return (reg / 32.0) * 4.88 / 1000

def get_bat_curr_ma(reg):
    return reg * 0.065104167

def get_adc_volt(reg):
    return reg * 4.5 / (2**10 - 1)

def get_adc_bus_curr(reg):
    return get_adc_volt(reg) * 1000

def get_temps_cels(reg):
    return reg / 256

def decode(binary):
    # Catch exceptions decoding wrong telemetry data
    try:
        raw = binascii.unhexlify(binary)
        pkt = Elfin.from_bytes(raw)
        return pkt.ax25_info
    except Exception as e:
        pass

def decode_file(file_path):
    """ Decode a SatNOGs file

        :param file_path: input file path of a csv extracted from SatNOGS
        for instance './data/43617-482-20181022T023205Z-month.csv'
        :return: decoded pandas dataframe
    """
    df_data = pd.read_csv(file_path, index_col=0, names=['date', 'binary'], sep='|')

    # Decode and print progress bar
    tqdm.pandas()
    df_data['pkt'] = df_data['binary'].progress_apply(decode)

    # Filter out non-telemetry data
    df_data['pkt_type'] = df_data['pkt'].apply(lambda pkt: type(pkt))
    df_data = df_data[df_data['pkt_type'] == Elfin.ElfinTlmData]

    # Telemetry timestamp
    df_data['tlm_time'] = df_data['pkt'].apply(get_date)

    # Battery temperature
    df_data['tlm_pwr1_bat1_temp'] = df_data['pkt'].apply(lambda pkt: get_bat_temp_celsius(pkt.elfin_hskp_pwr1_bat_mon_1_temperature_register))
    df_data['tlm_pwr2_bat1_temp'] = df_data['pkt'].apply(lambda pkt: get_bat_temp_celsius(pkt.elfin_hskp_pwr1_bat_mon_2_temperature_register))

    # Battery voltage
    df_data['tlm_bat_mon_1_vol'] = df_data['pkt'].apply(lambda pkt: get_bat_volt(pkt.elfin_hskp_pwr1_bat_mon_1_volt_reg))
    df_data['tlm_bat_mon_2_vol'] = df_data['pkt'].apply(lambda pkt: get_bat_volt(pkt.elfin_hskp_pwr1_bat_mon_2_volt_reg))

    # Instant current
    df_data['tlm_bat_mon_1_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_1_cur_reg))
    df_data['tlm_bat_mon_2_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_1_cur_reg))

    # Average current
    df_data['tlm_bat_mon_1_avg_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_1_avg_cur_reg))
    df_data['tlm_bat_mon_2_avg_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_2_avg_cur_reg))

    # Accumulated current
    df_data['tlm_bat_mon_1_acc_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_1_acc_curr_reg))
    df_data['tlm_bat_mon_2_acc_curr'] = df_data['pkt'].apply(lambda pkt: get_bat_curr_ma(pkt.elfin_hskp_pwr1_bat_mon_2_acc_curr_reg))

    # Bus voltage
    # TODO

    # Battery voltage (from ADC)
    df_data['tlm_adc_bat_1_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_bat_1_volt))
    df_data['tlm_adc_bat_2_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_bat_2_volt))

    # Solar array voltages
    df_data['tlm_adc_sa_12_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_adc_sa_volt_12))
    df_data['tlm_adc_sa_34_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_adc_sa_volt_34))
    df_data['tlm_adc_sa_56_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_adc_sa_volt_56))

    df_data['tlm_adc_reg_sa_1_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_reg_sa_volt_1))
    df_data['tlm_adc_reg_sa_2_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_reg_sa_volt_2))
    df_data['tlm_adc_reg_sa_3_vol'] = df_data['pkt'].apply(lambda pkt: get_adc_volt(pkt.elfin_hskp_pwr1_adc_data_reg_sa_volt_3))

    # Power bus current
    df_data['tlm_adc_pb_1_curr'] = df_data['pkt'].apply(lambda pkt: get_adc_bus_curr(pkt.elfin_hskp_pwr1_adc_data_power_bus_current_1))
    df_data['tlm_adc_pb_2_curr'] = df_data['pkt'].apply(lambda pkt: get_adc_bus_curr(pkt.elfin_hskp_pwr1_adc_data_power_bus_current_2))

    # Temperatures
    df_data['tlm_tmps_1'] = df_data['pkt'].apply(lambda pkt: get_temps_cels(pkt.elfin_hskp_pwr1_tmps_tmp1))
    df_data['tlm_tmps_2'] = df_data['pkt'].apply(lambda pkt: get_temps_cels(pkt.elfin_hskp_pwr1_tmps_tmp2))
    df_data['tlm_tmps_3'] = df_data['pkt'].apply(lambda pkt: get_temps_cels(pkt.elfin_hskp_pwr1_tmps_tmp3))
    df_data['tlm_tmps_4'] = df_data['pkt'].apply(lambda pkt: get_temps_cels(pkt.elfin_hskp_pwr1_tmps_tmp4))

    # Battery capacity
    df_data['tlm_acc_curr_bat1_rarc'] = df_data['pkt'].apply(lambda pkt: pkt.elfin_hskp_pwr1_accumulated_curr_bat1_rarc)
    df_data['tlm_acc_curr_bat2_rarc'] = df_data['pkt'].apply(lambda pkt: pkt.elfin_hskp_pwr1_accumulated_curr_bat2_rarc)

    df_data['tlm_acc_curr_bat1_rsrc'] = df_data['pkt'].apply(lambda pkt: pkt.elfin_hskp_pwr1_accumulated_curr_bat1_rsrc)
    df_data['tlm_acc_curr_bat2_rsrc'] = df_data['pkt'].apply(lambda pkt: pkt.elfin_hskp_pwr1_accumulated_curr_bat2_rsrc)

    df_data = df_data.drop(['binary', 'pkt', 'pkt_type'], axis=1)

    return df_data


def main(argv):
    usage_str = "usage: python -m decode_elfin.py <inputfile>"
    # file path to be decoded
    input_file_path = ""

    try:
        opts, args = getopt.getopt(argv,"h")
    except getopt.GetoptError:
        print(usage_str)
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(usage_str)
            sys.exit()
        else:
            pass

    # rest of the options
    if len(args) > 0:
        input_file_path = args[0]

    # using default file if not set
    if len(input_file_path) == 0:
        input_file_path = "./data/43617-482-20181022T023205Z-month.csv"
        print("Using default input file: {}".format(input_file_path))
    else:
        print("Using input file: {}".format(input_file_path))

    # Running the decoder
    df = decode_file(input_file_path)
    print(" --- head(3) of the decoded data which has {} features/columns and {} data points/rows".format(len(df.columns), df.shape[0]))
    print(df.head(3))

if __name__ == "__main__":

    main(sys.argv[1:])
