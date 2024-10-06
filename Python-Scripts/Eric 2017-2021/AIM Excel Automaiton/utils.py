import configparser
import re
from datetime import timedelta, datetime
import numpy as np
import logging
import os


class Config(object):
    """
    Read the config file: bharti_aim.cfg
    :return:
    """
    config_file = {'bharti_aim.cfg': ['DEFAULT', 'RESULT']}
    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str
    for file_path, sections in config_file.items():
        config_parser.read(file_path)
        for section in sections:
            config = dict(config_parser.items(section))


class Logger(object):
    """
    Create a log file
    """
    def __init__(self, file_path):
        self.logfilename = file_path

    def main(self):
        logging.basicConfig(filename=self.logfilename,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filemode='a')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        return logger


def clearNodes(node_name, node_list):
    """
    Clear the node names beginning with 'e_' or 'RAJ_E' and
    also check whether they exist in given node list
    :param node_list:
    :param node_name:
    :return:
    """
    if re.search(r'^e_*', node_name):
        pos = node_name.rfind('_')
        node_name = node_name[pos+1:]

    if re.search(r'^TN_SWAP*', node_name):
        pos = node_name.rfind('_')
        node_name = node_name[pos+1:]

    if re.search(r'^TN_E*', node_name):
        pos = node_name.rfind('_')
        pos2 = node_name[:pos].rfind('_')
        node_name = node_name[pos2+1:pos]

    if re.search(r'^RJ_E*', node_name):
        pos = node_name.rfind('_')
        pos2 = node_name[:pos].rfind('_')
        node_name = node_name[pos2+1:pos]

    l = len(node_name)
    # check if last character in node_name is digit or alphabet
    # if alphabet, then remove the last character
    if ord(node_name[l - 1:]) >= 65:
        node_name = node_name[0:l - 1]

    if node_name not in node_list:
        return np.NaN

    return node_name


def convert_timezone(t, time_zone_diff):
    """
    convert timezone from CET to IST i.e. add 4:30 hours to input time
    :param time_zone_diff:
    :param t:
    :return:
    """
    t += timedelta(minutes=time_zone_diff)
    return t


def remove_duplicate(x):
    """
    Remove duplicate values in 'Specific Problem' column
    :param x:
    :return:
    """
    lis = x.split(', ')
    return ",".join(set(lis))


def check_status(val):
    """
    Check 'Status' column in tt_details sheet, set to 'Open' if closure year == 1970
    :param val:
    :return:
    """
    if val.year == 1970:
        return 'Open'
    return 'Close'


def match_tt(x, incidents_dict):
    """
    Put TT_id corresponding to incidents in incidents_and_tt sheet wherever found valid
    :param x:
    :param incidents_dict:
    :return:
    """
    for key, values in incidents_dict.items():
        if x in values:
            return key
    return np.NaN


def update_result_dict(result_dict, param, test_incident, vc):
    """

    :param vc:
    :param test_incident:
    :param param:
    :param result_dict:
    :return:
    """
    result_dict[param]['AIM_false_positive'] = test_incident.shape[0]
    result_dict[param]['AIM_true_positive'] = test_incident['Ttmatch'].count()
    result_dict[param]['BHARTI_out_of_scope'] = vc['Out of Scope']
    result_dict[param]['BHARTI_true_positive'] = test_incident['Ttmatch'].nunique()
    return result_dict

