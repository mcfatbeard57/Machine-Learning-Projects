import json
from configparser import ConfigParser
import numpy as np


# ========================================read configuration========================================#
def read_config():
    config_object = ConfigParser()
    config_object.read('conf/dld_parser.config')
    parser_config = config_object['DLD_PARSER_CONFIG']
    return parser_config


# ========================================read file content========================================#
def read_file_content(input_file):
    try:
        file_content = []
        with open(input_file) as f:
            for line in f:
                file_content.append(line)
        return file_content
    except Exception as e:
        print('read_file_content: {}'.format(e))


# ========================================method to dump parsed data in json========================================#
def dump_json(dict_data, file_identifier):
    out_file = open('planout_{}.json'.format(file_identifier), 'w')
    json.dump(dict_data, out_file)


# ========================================read file content========================================#
def read_file_content_2(input_file, block_identifier):
    content_groups = []
    try:
        with open(input_file) as f:
            for i, group in enumerate(get_groups(f, block_identifier)):
                content_groups.append(group)
            return content_groups
    except Exception as e:
        print('read_file_content: {}'.format(e))


# ====================================extract block of text with certain character====================================#
def get_groups(seq, group_by):
    data = []
    for line in seq:
        if line.startswith(group_by):
            if data:
                yield data
                data = []
        data.append(line.strip())

    if data:
        yield data


def find_max_list_len(m_list):
    list_len = [len(i) for i in m_list]
    return max(list_len)


def similarize_list(values, fill_value):
    symmetry_list = []
    max_len = find_max_list_len(values)
    for m_list in values:
        if len(m_list) < max_len:
            diff = max_len - len(m_list)
            # print(diff)
            for i in range(diff):
                m_list.append(fill_value)
            symmetry_list.append(m_list)
        else:
            symmetry_list.append(m_list)
    return symmetry_list


def transpose_matrix(list_2d, fill_value):
    list_2d = similarize_list(list_2d, fill_value)
    transpose_list = np.array(list_2d).T.tolist()
    return transpose_list
