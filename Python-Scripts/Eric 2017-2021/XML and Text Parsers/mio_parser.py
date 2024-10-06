import xmltodict
import json

xml_file='mio_config.xmlpd'

with open(xml_file) as xmlf:
    data_dict = xmltodict.parse(xmlf.read())
json_string=json.dumps(data_dict)
print(json_string)

# ========================================for shared ip name and status========================================#

# def parse():
#     try:
#         shared_ip_dict = {}
#         shared_ips = []
#         for mi in data_dict['mdc']['md']:
#             for mi

#                 # mt={}
#                 # mt_parsed_value=mi['mt']
#                 # mt[mt_parsed_value]=mt_parsed_value




#     except Exception as e:
#         print('exception: {}'.format(e))

# parse()




#list1= ['mdc']['md']['mi']
#list2= ['mdc']['md']['mi']['mv']['r']