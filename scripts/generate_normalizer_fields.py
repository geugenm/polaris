import argparse
from argparse import Namespace
from typing import Dict, Union, Any


def replace_and_save(input_file, output_file, replacements):
    """
    Opens a file, replaces specified strings with provided values, and saves it as another file.

    Args:
        input_file (str): Path to the file to be read from.
        output_file (str): Path to the file where the replaced content will be saved.
        replacements (dict): Dictionary containing key-value pairs for replacements.
            Keys are the strings to be replaced, and values are the replacements.
    """
    with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
        for line in in_file:
            for key, value in replacements.items():
                line = line.replace(key, value)
            out_file.write(line)


def generate_normalizer_content(fields: Dict[str, Union[str, int]]) -> str:
    """Generates the content for the normalizer class fields.

    Args:
        fields: Dictionary containing field names and values.

    Returns:
        A string representing the formatted field lines for the normalizer class.
    """

    line_template = 'Field(\'{}\', lambda x: x, None, \'{}\'),\n'
    result = ""
    for field_name, _ in fields.items():  # Iterate only over field names for efficiency
        line = line_template.format(field_name,
                                    field_name.replace('_', ' ').title())
        if result == "":
            result = line
        else:
            result += ' ' * 12 + line
    return result.rstrip()  # Remove trailing newline for cleaner output


def main():
    parser = argparse.ArgumentParser(
        description='Generate a script with normalizers.')
    parser.add_argument('satellite_name', type=str,
                        help='The name of the satellite')
    args: Namespace = parser.parse_args()

    fields: Dict[str, Union[str, int]] = {
        "dest_callsign": "EU1XX ",
        "src_callsign": "EU10S ",
        "src_ssid": 0,
        "dest_ssid": 0,
        "ctl": 3,
        "pid": 240,
        "hdr_rf_id": 1,
        "hdr_opr_time": 95,
        "hdr_reboot_cnt": 244,
        "hdr_mcusr": 5,
        "hdr_pamp_temp": 294,
        "hdr_pamp_voltage": 64,
        "hdr_tx_attenuator": 3,
        "hdr_battery_voltage": 3638,
        "hdr_system_voltage": 510,
        "hdr_seq_number": 1,
        "hdr_pwr_save_state": 0,
        "hdr_modem_on_period": 65535,
        "hdr_obc_can_status": 3,
        "hdr_eps_can_status": 0,
        "hdr_info_size": 64,
        "hdr_data_type": 254,
        "current_to_gamma": 19,
        "current_to_irsensor": 19,
        "current_to_extflash": 7,
        "current_to_solarsens": 27,
        "current_to_magnetcoils": 4,
        "current_to_coil_x": 18,
        "current_to_coil_y": 2,
        "current_to_coil_pz": 117,
        "current_to_coil_nz": 31,
        "battery1_temp": 480,
        "battery2_temp": 476,
        "numb_oc_obc": 2,
        "numb_oc_out_gamma": 0,
        "numb_oc_out_rf1": 0,
        "numb_oc_out_rf2": 0,
        "numb_oc_out_flash": 0,
        "numb_oc_out_irsens": 0,
        "numb_oc_coil_x": 0,
        "numb_oc_coil_y": 0,
        "numb_oc_coil_pz": 0,
        "numb_oc_coil_nz": 0,
        "numb_oc_magnetcoils": 0,
        "numb_oc_solarsens": 0,
        "reset_num": 9,
        "reset_reason": 4,
        "pwr_sat": 1,
        "pwr_rf1": 0,
        "pwr_rf2": 1,
        "pwr_sunsensor": 0,
        "pwr_gamma": 0,
        "pwr_irsensor": 0,
        "pwr_flash": 0,
        "pwr_magnet_x": 0,
        "pwr_magnet_y": 0,
        "pwr_magnet_z": 0,
        "sys_time": 16513,
        "adc_correctness": 0,
        "t_adc1": 195,
        "t_adc2": 199,
        "stepup_current": 20,
        "stepup_voltage": 3823,
        "afterbq_current": 786,
        "battery_voltage": 3623,
        "sys_voltage_50": 3314,
        "sys_voltage_33": 2714,
        "eps_uc_current": 565,
        "obc_uc_current": 357,
        "rf1_uc_current": 0,
        "rf2_uc_current": 556,
        "solar_voltage": 3869,
        "side_x_current": 121,
        "side_py_current": 11,
        "side_ny_current": 1,
        "side_pz_current": 11,
        "side_nz_current": 7
    }

    satellite_class_name: str = args.satellite_name.translate(
        str.maketrans('', '', '-'))
    satellite_file_name: str = satellite_class_name.lower()

    normalizer_template_path: str = "./scripts/normalizer.template"
    result_file_path: str = f"./contrib/normalizers/{satellite_file_name}.py"

    normalizer_content = generate_normalizer_content(fields)

    replacements: Dict[str, Union[str, Any]] = {
        "<satellite_name>": satellite_class_name,
        "<fields>": normalizer_content}

    # Assuming replace_and_save function exists elsewhere (not shown here)
    replace_and_save(normalizer_template_path, result_file_path, replacements)


if __name__ == '__main__':
    main()
