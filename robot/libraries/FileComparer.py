"""
File Comparer module
"""
import os
import re

from robot.api.deco import keyword, library


@library
class FileComparer:
    """ File Comparer predictor class
    """
    @keyword
    def compare_files(self, first_file_path, second_file_path, precision=4):
        """ Test if two files are identicals

            :param first_file_path: Path to the first file
            :type first_file_path: String
            :param second_file_path: Path to the second file
            :type second_file_path: String
            :param precision: Precision of the comparison
            :type precision: Integer
            :return: The result of the comparison
            :rtype: Boolean
        """
        first_file = open(first_file_path, 'r')
        second_file = open(second_file_path, 'r')

        matcher = re.compile(r'^(.+?)([0-9]+\.[0-9]+)(.*?)$')

        for file_1_line, file_2_line in zip(first_file, second_file):
            if file_1_line != file_2_line:
                f1_match = matcher.match(file_1_line)
                f2_match = matcher.match(file_2_line)

                if f1_match is not None and f2_match is not None:
                    f1_match_grps = f1_match.groups()
                    f2_match_grps = f2_match.groups()

                    if f1_match_grps[0].strip() == f2_match_grps[0].strip(
                    ) and (f1_match_grps[2] and f1_match_grps[2].strip()) == (
                            f2_match_grps[2] and f2_match_grps[2].strip()):
                        file_1_value = float(f1_match_grps[1])
                        file_2_value = float(f2_match_grps[1])

                        if abs(file_1_value -
                               file_2_value) < 10**-int(precision):
                            continue
                if file_1_line is None and file_2_line is None:
                    continue
                return False

        first_file.close()
        second_file.close()

        return True

    @keyword
    def compare_files_sizes(self, first_file_path, second_file_path):
        """ Test if two files sizes are identicals

            :param first_file_path: Path to the first file
            :type first_file_path: String
            :param second_file_path: Path to the second file
            :type second_file_path: String
            :return: The result of the size comparison
            :rtype: Boolean
        """
        return os.path.getsize(first_file_path) == os.path.getsize(
            second_file_path)
