import re

from common.constants import *
from common.utils import *


class DldParser:
    def __init__(self, file_content):
        self.file_content = file_content
        self.blank_value = ' '

    def get_regex_value(self, pattern):
        regex_pattern = re.compile(r'{0}'.format(pattern))
        return regex_pattern

    def parse_context_one(self):
        type_one_context = ['s1mme', 'Gn']
        pattern_context = '^\\s{2}(context)\\s(.*)'
        pattern_context_ip_dns_lookup = '^\\s{4}(ip domain-lookup)'
        pattern_context_ip_name_servers = '^\\s{4}(ip name-servers)(.*)'
        pattern_context_dns_client = '^\\s{4}(dns-client.*)'
        pattern_context_bind_address = '^\\s{6}(bind address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        pattern_context_round_robin = '^\\s{6}(round-robin-answers)'

        regex_context = self.get_regex_value(pattern_context)
        regex_context_ip_dns_lookup = self.get_regex_value(pattern_context_ip_dns_lookup)
        regex_context_ip_name_server = self.get_regex_value(pattern_context_ip_name_servers)
        regex_context_dns_client = self.get_regex_value(pattern_context_dns_client)
        regex_context_bind_address = self.get_regex_value(pattern_context_bind_address)
        regex_context_round_robin = self.get_regex_value(pattern_context_round_robin)

        arr_context = []
        for line in self.file_content:
            result_context = regex_context.search(line)
            if result_context:
                line_index = self.file_content.index(line)
                if result_context.group(2) in type_one_context:
                    dict_context = {}
                    context_headers = []
                    context_value = []

                    for i in self.file_content[line_index:]:
                        result_context_ip_dns_lookup = regex_context_ip_dns_lookup.search(i)
                        result_context_ip_name_server = regex_context_ip_name_server.search(i)
                        result_context_dns_client = regex_context_dns_client.search(i)
                        result_context_bind_address = regex_context_bind_address.search(i)
                        result_context_round_robin = regex_context_round_robin.search(i)
                        if result_context_ip_dns_lookup:
                            context_headers.append(result_context_ip_dns_lookup.group(0).strip())
                            context_value.append(' ')
                        if result_context_ip_name_server:
                            context_headers.append(result_context_ip_name_server.group(1).strip())
                            context_value.append(result_context_ip_name_server.group(2).strip())
                        if result_context_dns_client:
                            context_headers.append(result_context_dns_client.group(0).strip())
                        if result_context_bind_address:
                            context_value.append(result_context_bind_address.group(0).strip())
                        if result_context_round_robin:
                            context_headers.append('Comments')
                            context_value.append(result_context_round_robin.group(0).strip())
                            break

                    dict_context['sheet'] = '{} {}'.format(result_context.group(2).upper(), result_context.group(1))
                    dict_context['label'] = [
                        '{} {}'.format(result_context.group(1).capitalize(), result_context.group(2))]
                    dict_context['table_name'] = ['Domain Name Configuration']
                    dict_context['headers'] = context_headers
                    dict_context['values'] = context_value
                    arr_context.append(dict_context)
        return arr_context

    def parse_network_overload_protection(self):
        pattern_nop = '^\\s{2}(network-overload-protection)\\s(.*)'
        pattern_header_value = '([a-zA-Z]+-new-connections-per-second)\\s+([0-9]+)\\s+(action)\\s([a-zA-Z\-\\s]+)(queue-size)\\s([0-9]+)\\s+(wait-time)\\s([0-9]+)'
        regex_nop = self.get_regex_value(pattern_nop)
        regex_headers = self.get_regex_value(pattern_header_value)
        arr_nops = []
        dict_nops = {}
        for line in self.file_content:
            result_nop = regex_nop.search(line)
            if result_nop:
                dict_nop = {}
                nop_headers = []
                nop_values = []
                result_nop_headers = regex_headers.search(result_nop.group(2))
                if result_nop_headers:
                    for item in result_nop_headers.groups():
                        if result_nop_headers.groups().index(item) % 2 == 0:
                            nop_headers.append(item)
                        else:
                            nop_values.append(item)

                nop_headers.append('Comment')
                dict_nop['table_name'] = ['{}'.format(result_nop.group(1))]
                dict_nop['headers'] = nop_headers
                dict_nop['values'] = nop_values
                arr_nops.append(dict_nop)
        dict_nops['sheet'] = 'Network-overload-Protection'
        dict_nops['label'] = ['Global Configuration']
        dict_nops['nop_tables'] = arr_nops
        return dict_nops

    def add_unique_header(self, header_value, arr_header):
        header_value = header_value.capitalize()
        if header_value not in arr_header:
            arr_header.append(header_value)
        return arr_header

    def reorder_list(self, list_order, unordered_list):
        unordered_list = [unordered_list[i] for i in list_order]
        return unordered_list

    def parse_context_sigtran(self):
        pattern_end_context = '^\\s{2}(context)\\s(.*)'
        pattern_sigtran_context = '^\\s{2}(context)\\s(sigtran)'
        pattern_router_ospf = '^\\s{4}(router ospf)'
        pattern_router_networks = '^\\s{6}(network)\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+/[0-9]+)\s+(area)\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        pattern_router_redistribute = '^\\s{6}(redistribute)\\s([a-zA-Z]+)'
        pattern_interface = '^\\s{4}(interface)\\s(.*)'
        pattern_ip_address = '^\\s{6}(ip address)\\s+(.*)'
        pattern_description = '^\\s{6}(description)\\s+(.*)'
        pattern_ip_ospf_network = '^\\s{6}(ip ospf network)\\s+(.*)'
        pattern_map_service = '^\\s{4}(map-service)\\s+(.*)'
        pattern_map_accesss_protocol = '^\\s{6}(access-protocol)\\s+(.*)'
        pattern_map_eir_isdn = '^\\s{6}(equipment-identity-register isdn)\\s+([0-9]+)'
        pattern_map_auth_vector = '^\\s{6}(auth-vectors)\\s+(.*)'
        pattern_map_app_context_name = '^\\s{6}(application-context-name)\\s+(.*)'
        pattern_map_policy_tcap = '^\\s{6}(policy tcap)\\s+(.*)'
        pattern_imsi_start_end = '^\\s{8}(imsi starts-with)\\s+([0-9]+)\\s+(mobile-global-title)\\s+([0-9]+)'

        regex_end_context = self.get_regex_value(pattern_end_context)
        regex_sigtran_context = self.get_regex_value(pattern_sigtran_context)
        regex_router_ospf = self.get_regex_value(pattern_router_ospf)
        regex_router_networks = self.get_regex_value(pattern_router_networks)
        regex_router_redistribute = self.get_regex_value(pattern_router_redistribute)
        regex_interface = self.get_regex_value(pattern_interface)
        regex_ip_address = self.get_regex_value(pattern_ip_address)
        regex_description = self.get_regex_value(pattern_description)
        regex_ip_ospf_network = self.get_regex_value(pattern_ip_ospf_network)
        regex_map_service = self.get_regex_value(pattern_map_service)
        regex_map_accesss_protocol = self.get_regex_value(pattern_map_accesss_protocol)
        regex_map_eir_isdn = self.get_regex_value(pattern_map_eir_isdn)
        regex_map_auth_vector = self.get_regex_value(pattern_map_auth_vector)
        regex_map_app_context_name = self.get_regex_value(pattern_map_app_context_name)
        regex_map_app_policy_tcap = self.get_regex_value(pattern_map_policy_tcap)
        regex_imsi_start_end = self.get_regex_value(pattern_imsi_start_end)

        dict_sigtran = {}
        sigtran_tables = []
        for line in self.file_content:
            result_context_sigtran = regex_sigtran_context.search(line)
            if result_context_sigtran:
                context_headers = []
                context_values = []
                router_headers = []
                service_map_headers = []
                service_map_values = []
                networks = []
                dict_context = {}
                dict_context['table_name'] = None
                dict_context['headers'] = context_headers
                dict_context['values'] = context_values
                sigtran_tables.append(dict_context)
                dict_router = {}
                dict_router['table_name'] = None
                dict_router['headers'] = router_headers
                dict_router['values'] = networks
                sigtran_tables.append(dict_router)
                dict_service_map = {}
                dict_service_map['table_name'] = None
                dict_service_map['headers'] = service_map_headers
                dict_service_map['values'] = service_map_values
                sigtran_tables.append(dict_service_map)
                index_start_context = self.file_content.index(line)
                index_end_context = None
                for i in self.file_content[index_start_context + 1:]:
                    result_end_context = regex_end_context.search(i)
                    if result_end_context:
                        index_end_context = self.file_content.index(i)
                        break
                if index_end_context:
                    service_map_merge_cell_values = []
                    for i in self.file_content[index_start_context + 1:index_end_context]:
                        self.add_unique_header('Context Name', context_headers)
                        result_interface = regex_interface.search(i)
                        result_router_ospf = regex_router_ospf.search(i)

                        # table context start
                        if result_interface:
                            interface_value = []
                            self.add_unique_header(result_interface.group(1), context_headers)
                            interface_value.append(result_interface.group(2))
                            # dict_context['table_name'] = [' ']
                            interface_index = self.file_content.index(i)
                            for j in self.file_content[interface_index + 1:index_end_context + 1]:
                                result_description = regex_description.search(j)
                                result_ip_address = regex_ip_address.search(j)
                                result_ip_ospf_network = regex_ip_ospf_network.search(j)

                                if result_description:
                                    interface_value.append(result_description.group(2))
                                if result_ip_address:
                                    self.add_unique_header(result_ip_address.group(1), context_headers)
                                    self.add_unique_header('Subnet mask', context_headers)
                                    self.add_unique_header('Description', context_headers)
                                    self.add_unique_header('ip ospf network', context_headers)

                                    interface_ips = result_ip_address.group(2).split(' ')
                                    for ip in interface_ips:
                                        interface_value.append(ip)
                                    break

                                interface_value.append(result_context_sigtran.group(2).capitalize())

                            interface_value = self.reorder_list([2, 0, 3, 4, 1], interface_value)
                            context_values.append(interface_value)

                        # table router-ospf starts
                        result_networks = regex_router_networks.search(i)
                        result_redistribute = regex_router_redistribute.search(i)

                        if result_router_ospf:
                            dict_router['table_name'] = [result_router_ospf.group(1)]
                        if result_networks:

                            network_value = []
                            for item in result_networks.groups():
                                if result_networks.groups().index(item) % 2 == 0:
                                    if item.capitalize() not in router_headers:
                                        router_headers.append(item.capitalize())
                                else:
                                    network_value.append(item)
                            networks.append(network_value)
                        if result_redistribute:
                            router_headers.append(result_redistribute.group(1).capitalize())
                            for x in networks:
                                x.append(result_redistribute.group(2))
                        # table router-ospf ends

                        # table map service starts
                        result_map = regex_map_service.search(i)
                        result_ap = regex_map_accesss_protocol.search(i)
                        result_av = regex_map_auth_vector.search(i)
                        result_acn = regex_map_app_context_name.search(i)
                        result_tcap = regex_map_app_policy_tcap.search(i)
                        result_eir_isdn = regex_map_eir_isdn.search(i)
                        result_imsi_start_end = regex_imsi_start_end.search(i)

                        if result_map:
                            dict_service_map['table_name'] = [result_map.group(1)]
                            self.add_unique_header('Service name', service_map_headers)
                            service_map_merge_cell_values.append(result_map.group(2))
                        if result_ap:
                            self.add_unique_header(result_ap.group(1), service_map_headers)
                            self.add_unique_header('EIR ISDN', service_map_headers)
                            service_map_merge_cell_values.append(result_ap.group(2))
                        if result_av:
                            self.add_unique_header(result_av.group(1), service_map_headers)
                            service_map_merge_cell_values.append(result_av.group(2))
                        if result_acn:
                            self.add_unique_header(result_acn.group(1), service_map_headers)
                            service_map_merge_cell_values.append(result_acn.group(2))
                        if result_tcap:
                            self.add_unique_header(result_tcap.group(1), service_map_headers)
                            service_map_merge_cell_values.append(result_tcap.group(2))
                        if result_eir_isdn:
                            service_map_merge_cell_values.append(result_eir_isdn.group(2))

                        if result_imsi_start_end:
                            imsi_value = []

                            for item in result_imsi_start_end.groups():
                                if result_imsi_start_end.groups().index(item) % 2 == 0:
                                    self.add_unique_header(item, service_map_headers)
                                else:
                                    imsi_value.append(item)
                            tmp_arr = service_map_merge_cell_values + imsi_value
                            tmp_arr = self.reorder_list([0, 1, 5, 2, 3, 4, 6, 7], tmp_arr)
                            service_map_values.append(tmp_arr)
                        # table map service ends

                dict_sigtran['sheet'] = '{} {}'.format(result_context_sigtran.group(2),
                                                       result_context_sigtran.group(1))
                dict_sigtran['label'] = [
                    '{} {}'.format(result_context_sigtran.group(1), result_context_sigtran.group(2).capitalize())]
                dict_sigtran['sheet_tables'] = sigtran_tables
        return dict_sigtran

    def parse_lte_policy(self, file_content_2):
        lte_headers = []
        lte_values = []
        dict_lte_policy = {}
        dict_tai_mgmt = {}
        dict_tai_mgmt['table_name'] = None
        dict_tai_mgmt['headers'] = lte_headers
        dict_tai_mgmt['values'] = lte_values
        lte_tables = []
        lte_tables.append(dict_tai_mgmt)
        pattern_tai_mgmt_db = '^(tai-mgmt-db)\\s(.*)'
        pattern_tai_mgmt_obj = '^(tai-mgmt-obj)\\s(.*)'
        pattern_zone_code = '^(tai)\\s(mcc)\\s([0-9]+)\\s(mnc)\\s([0-9]+)\\s(tac)\\s([0-9]+)'
        pattern_sgw_address = '^(sgw-address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)\\s(s5-s8-protocol)\\s(gtp)\\s(weight)\\s([0-9]+)'

        regex_tai_mgmt_db = self.get_regex_value(pattern_tai_mgmt_db)
        regex_tai_mgmt_obj = self.get_regex_value(pattern_tai_mgmt_obj)
        regex_zone_code = self.get_regex_value(pattern_zone_code)
        regex_sgw_address = self.get_regex_value(pattern_sgw_address)

        for group in file_content_2:
            if block_context in group[0]:
                # extract db block from the groups
                for i, db_block in enumerate(get_groups(group, block_tai_mgmt_db)):
                    if block_tai_mgmt_db in db_block[0]:

                        mgmt_dbs = []
                        mgmt_objs = []
                        mgmt_zen_codes = []
                        for line in db_block:
                            result_tai_mgmt_db = regex_tai_mgmt_db.search(line)
                            result_tai_mgmt_obj = regex_tai_mgmt_obj.search(line)
                            result_zone_code = regex_zone_code.search(line)
                            result_sgw_address = regex_sgw_address.search(line)

                            if result_tai_mgmt_db:
                                dict_tai_mgmt['table_name'] = [result_tai_mgmt_db.group(1)]
                                self.add_unique_header('DB Name', lte_headers)
                                mgmt_dbs.append(result_tai_mgmt_db.group(2))

                            if result_tai_mgmt_obj:
                                self.add_unique_header(result_tai_mgmt_obj.group(1), lte_headers)
                                mgmt_objs = mgmt_dbs + [result_tai_mgmt_obj.group(2)]

                            if result_zone_code:
                                tmp_zone_codes = []
                                self.add_unique_header('zone code', lte_headers)
                                for item in result_zone_code.groups():
                                    if result_zone_code.groups().index(item) % 2 == 0:
                                        tmp_zone_codes.append(item)
                                    else:
                                        self.add_unique_header(item, lte_headers)
                                mgmt_zen_codes = mgmt_objs + tmp_zone_codes

                            if result_sgw_address:
                                tmp_sgw_addresses = []
                                for item in result_sgw_address.groups():
                                    if result_sgw_address.groups().index(item) % 2 == 0:
                                        self.add_unique_header(item, lte_headers)
                                    else:
                                        tmp_sgw_addresses.append(item)
                                mgmt_sgw_addresses = mgmt_zen_codes + tmp_sgw_addresses
                                lte_values.append(mgmt_sgw_addresses)

            dict_lte_policy['sheet'] = 'LTE-POLICY'
            dict_lte_policy['label'] = ['Context Local']
            dict_lte_policy['sheet_tables'] = lte_tables

        return dict_lte_policy

    def parse_call_control_profile(self, file_content_2):
        dict_call_control_profile = {}
        dict_call_control = {}
        call_control_headers = []
        call_control_values = []
        call_control_tables = []
        call_control_tables.append(dict_call_control)
        dict_call_control['table_name'] = None
        dict_call_control['headers'] = call_control_headers
        dict_call_control_profile['sheet'] = 'Call Control Profile'
        dict_call_control_profile['label'] = ['Call Control Profiles']
        dict_call_control_profile['sheet_tables'] = call_control_tables
        for group in file_content_2:
            if block_call_control_profile in group[0]:
                for i, call_profile_block in enumerate(get_groups(group, block_call_control_profile)):
                    if block_call_control_profile in call_profile_block[0]:
                        self.add_unique_header(call_profile_block[0].replace('call-control-profile ', ''),
                                               call_control_headers)

                        operator_block = []
                        for line in call_profile_block[1:]:
                            if 'exit' not in line:
                                operator_block.append(line)
                            if 'exit' in line:
                                # break for single block of operator
                                break
                        call_control_values.append(operator_block)

        dict_call_control['values'] = transpose_matrix(call_control_values, self.blank_value)
        return dict_call_control_profile

    def parse_apn_profile(self, file_content_2):
        dict_apn_profile = {}
        dict_apn = {}
        apn_profile_headers = []
        apn_profile_values = []
        apn_profile_tables = []
        apn_profile_tables.append(dict_apn)

        dict_apn['table_name'] = None
        dict_apn['headers'] = apn_profile_headers
        dict_apn['values'] = apn_profile_values
        dict_apn_profile['sheet'] = 'APN Profile'
        dict_apn_profile['label'] = ['APN Profiles']
        dict_apn_profile['sheet_tables'] = apn_profile_tables
        for group in file_content_2:
            if block_apn_profile in group[0]:
                for i, apn_profile_block in enumerate(get_groups(group, block_apn_profile)):
                    if block_apn_profile in apn_profile_block[0]:
                        self.add_unique_header(apn_profile_block[0].replace('apn-profile ', ''),
                                               apn_profile_headers)

                        a = []
                        for line in apn_profile_block[1:]:
                            if 'exit' not in line:
                                a.append(line)
                            if 'exit' in line:
                                # break for single block of operator
                                break
                        apn_profile_values.append(a)

        dict_apn['values'] = transpose_matrix(apn_profile_values, self.blank_value)
        return dict_apn_profile

    def parse_sgsn_global(self, file_content_2):
        pattern_sgsn_msin_first_last = '^imsi-range\\s(mcc)\\s([0-9]+)\\s(mnc)\\s([0-9]+)\\s(msin first)\\s([0-9]+)\\s(last)\\s([0-9]+)\\s(operator-policy)\\s(.*)'
        pattern_imei_profile = '^(imei-profile)\\s(.*)'
        pattern_imei_associate = '^(associate apn-remap-table)\\s(.*)'
        pattern_apn_remap_table = '^(apn-remap-table)\\s(.*)'
        pattern_apn_selection_a = '^(apn-selection-default)\\s(.+)'
        pattern_apn_selection_b = '^(apn-selection-default network-identifier)\\s(.*)\\s(require-subscription-apn network-identifier)\\s(.*)'
        pattern_apn_remap = '^(apn-remap)\\s(.*)'

        regex_sgsn_msin_first_last = self.get_regex_value(pattern_sgsn_msin_first_last)
        regex_imei_profile = self.get_regex_value(pattern_imei_profile)
        regex_imei_associate = self.get_regex_value(pattern_imei_associate)
        regex_apn_remap_table = self.get_regex_value(pattern_apn_remap_table)
        regex_apn_selection_a = self.get_regex_value(pattern_apn_selection_a)
        regex_apn_selection_b = self.get_regex_value(pattern_apn_selection_b)
        regex_apn_remap = self.get_regex_value(pattern_apn_remap)

        dict_sgsn_global = {}
        dict_sgsn = {}
        sgsn_headers = []
        sgsn_values = []
        sgsn_global_tables = []

        dict_sgsn['table_name'] = None
        dict_sgsn['headers'] = sgsn_headers
        dict_sgsn['values'] = sgsn_values
        sgsn_global_tables.append(dict_sgsn)

        dict_imei_profile = {}
        imei_profile_headers = []
        imei_profile_values = []
        dict_imei_profile['table_name'] = None
        dict_imei_profile['headers'] = imei_profile_headers
        dict_imei_profile['values'] = imei_profile_values
        sgsn_global_tables.append(dict_imei_profile)

        dict_apn_remap_table = {}
        apn_remap_headers = []
        apn_remap_values = []
        dict_apn_remap_table['table_name'] = ['apn-remap-table-configuration']
        dict_apn_remap_table['headers'] = apn_remap_headers
        dict_apn_remap_table['values'] = apn_remap_values
        sgsn_global_tables.append(dict_apn_remap_table)

        dict_sgsn_global['sheet'] = 'Operator Policies'
        dict_sgsn_global['label'] = ['Context Local']
        dict_sgsn_global['sheet_tables'] = sgsn_global_tables
        for group in file_content_2:
            if block_sgsn_global in group[0]:
                for i, sgsn_block in enumerate(get_groups(group, block_sgsn_global)):
                    if block_sgsn_global in sgsn_block[0]:
                        dict_sgsn['table_name'] = [sgsn_block[0]]

                        for line in sgsn_block[1:]:
                            result_sgsn_msin_first_last = regex_sgsn_msin_first_last.search(line)
                            if result_sgsn_msin_first_last:
                                msin_value = []

                                for item in result_sgsn_msin_first_last.groups():
                                    if result_sgsn_msin_first_last.groups().index(item) % 2 == 0:
                                        self.add_unique_header(item, sgsn_headers)
                                    else:
                                        msin_value.append(item)
                                sgsn_values.append(msin_value)

            for i, imei_block in enumerate(get_groups(group, block_imei_profile)):
                if block_imei_profile in imei_block[0]:
                    dict_imei_profile['table_name'] = [block_imei_profile]
                    imei_block_value = []
                    for line in imei_block:
                        result_imei_profile = regex_imei_profile.search(line)
                        result_imei_associate = regex_imei_associate.search(line)

                        if result_imei_profile:
                            self.add_unique_header(result_imei_profile.group(1), imei_profile_headers)
                            imei_block_value.append(result_imei_profile.group(2))
                        if result_imei_associate:
                            self.add_unique_header(result_imei_associate.group(1), imei_profile_headers)
                            self.add_unique_header('APN network-identifier', imei_profile_headers)
                            imei_block_value.append(result_imei_associate.group(2))
                            imei_block_value.append('-')
                    imei_profile_values.append(imei_block_value)

            for i, apn_remap_block in enumerate(get_groups(group, block_apn_remap)):

                if block_apn_remap in apn_remap_block[0]:
                    apn_remap_tables = []
                    apn_selections = []
                    apn_remaps = []
                    for line in apn_remap_block:
                        result_apn_remap_table = regex_apn_remap_table.search(line)
                        result_apn_selection_a = regex_apn_selection_a.search(line)
                        result_apn_remap = regex_apn_remap.search(line)

                        if result_apn_remap_table:
                            self.add_unique_header(result_apn_remap_table.group(1), apn_remap_headers)
                            apn_remap_tables.append(result_apn_remap_table.group(2))

                        if result_apn_selection_a:
                            tmp_apn_selections = []
                            result_apn_selection_b = regex_apn_selection_b.search(line)
                            if result_apn_selection_b:
                                for item in result_apn_selection_b.groups():
                                    if result_apn_selection_b.groups().index(item) % 2 == 0:
                                        self.add_unique_header(item, apn_remap_headers)
                                    else:
                                        tmp_apn_selections.append(item)
                                # todo: place above imei_block in the apn_remap_profile wherever available
                                # todo: display the apn-remap values in a merged cell infron of the operator
                                tmp_apn_selections.append('PENDING')
                                tmp_apn_selections.append('PENDING')
                            else:
                                tmp_apn_selections.append(result_apn_selection_a.group(2))
                            apn_selections = apn_remap_tables + tmp_apn_selections
                            apn_remap_values.append(apn_selections)

                        if result_apn_remap:
                            self.add_unique_header('imei-profile', apn_remap_headers)
                            self.add_unique_header(result_apn_remap.group(1), apn_remap_headers)

        dict_apn_remap_table['values'] = similarize_list(apn_remap_values, '-')
        return dict_sgsn_global

    def parse_ss7_routing_domain(self, file_content_2):
        pattern_routing_domain = '^(ss7-routing-domain)\\s([0-9]+)\\s(variant)\\s([a-zA-Z]+)'
        pattern_description = '^(description)\\s(\"[.*]\")'
        pattern_ssf = '^(ssf)\\s([a-zA-Z]+)'
        pattern_routing_context = '^(routing-context)\\s([0-9]+)'

        pattern_asp_instance = '^(asp instance)\\s([0-9]+)'
        pattern_end_point_addr = '^(end-point address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)\\s(context)\\s(.*)'
        pattern_end_point_port = '^(end-point port)\\s([0-9]+)'
        pattern_end_point_bind = '^(end-point bind)'

        pattern_peer_server_id = '^(peer-server id)\\s([0-9]+)'
        pattern_peer_name = '^(name)\\s(.*)'
        pattern_peer_mode = '^(mode)\\s(.*)'
        pattern_peer_routing_context = '^(routing-context)\\s([0-9]+)'
        pattern_peer_self_point_code = '^(self-point-code)\\s([0-9]+)'
        pattern_peer_psp_instance = '^(psp instance)\\s([0-9]+)'

        pattern_psp_mode = '^(psp-mode)\\s(.*)'
        pattern_psp_endpoint_port = '^(end-point port)\\s([0-9]+)'
        pattern_psp_endpoint_address = '^(end-point address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        pattern_associate_asp_instance = '^(associate asp instance)\\s([0-9]+)'

        regex_routing_domain = self.get_regex_value(pattern_routing_domain)
        regex_description = self.get_regex_value(pattern_description)
        regex_ssf = self.get_regex_value(pattern_ssf)
        regex_routing_context = self.get_regex_value(pattern_routing_context)
        regex_asp_instance = self.get_regex_value(pattern_asp_instance)
        regex_end_point_addr = self.get_regex_value(pattern_end_point_addr)
        regex_end_point_port = self.get_regex_value(pattern_end_point_port)
        regex_end_point_bind = self.get_regex_value(pattern_end_point_bind)

        regex_peer_server_id = self.get_regex_value(pattern_peer_server_id)
        regex_peer_name = self.get_regex_value(pattern_peer_name)
        regex_peer_mode = self.get_regex_value(pattern_peer_mode)
        regex_peer_routing_context = self.get_regex_value(pattern_peer_routing_context)
        regex_peer_self_point_code = self.get_regex_value(pattern_peer_self_point_code)
        regex_peer_psp_instance = self.get_regex_value(pattern_peer_psp_instance)

        regex_psp_mode = self.get_regex_value(pattern_psp_mode)
        regex_psp_endpoint_port = self.get_regex_value(pattern_psp_endpoint_port)
        regex_psp_endpoint_address = self.get_regex_value(pattern_psp_endpoint_address)
        regex_associate_asp_instance = self.get_regex_value(pattern_associate_asp_instance)

        dict_ss7_routing_domain = {}
        ss7_routing_tables = []

        dict_ss7_info = {}
        ss7_headers = []
        ss7_values = []
        dict_ss7_info['table_name'] = [
            'SS7 Routing Domain to Support IP Signaling for SIGTRAN for IUPS -C  interface , this configuration will be done in the global configuration mode']
        dict_ss7_info['headers'] = ss7_headers
        dict_ss7_info['values'] = ss7_values
        ss7_routing_tables.append(dict_ss7_info)

        dict_asp_instance = {}
        asp_headers = []
        asp_values = []
        dict_asp_instance['table_name'] = ['Asp Instance']
        dict_asp_instance['headers'] = asp_headers
        dict_asp_instance['values'] = asp_values
        ss7_routing_tables.append(dict_asp_instance)

        dict_peer_server = {}
        peer_server_headers = []
        peer_server_values = []
        dict_peer_server['table_name'] = ['Peer Server Id']
        dict_peer_server['headers'] = peer_server_headers
        dict_peer_server['values'] = peer_server_values
        ss7_routing_tables.append(dict_peer_server)

        dict_psp_instance = {}
        psp_instance_headers = []
        psp_instance_values = []
        dict_psp_instance['table_name'] = ['PSP Parameters Server Id']
        dict_psp_instance['headers'] = psp_instance_headers
        dict_psp_instance['values'] = psp_instance_values
        ss7_routing_tables.append(dict_psp_instance)

        dict_ss7_routing_domain['sheet'] = 'SS7 Routing Domain'
        dict_ss7_routing_domain['label'] = ['Context Local']
        dict_ss7_routing_domain['sheet_tables'] = ss7_routing_tables

        for group in file_content_2:
            if block_ss7_routing in group[0]:
                for i, ss7_routing_block in enumerate(get_groups(group, block_ss7_routing)):
                    if block_ss7_routing in ss7_routing_block[0]:
                        for line in ss7_routing_block:

                            # parse asp instance
                            result_asp_instance = regex_asp_instance.search(line)
                            result_peer_server_id = regex_peer_server_id.search(line)
                            asp_instance_info = []

                            if result_asp_instance:
                                a = []
                                b = []
                                self.add_unique_header(result_asp_instance.group(1), asp_headers)
                                a.append(result_asp_instance.group(2))
                                asp_block_start_index = ss7_routing_block.index(line)

                                for i in ss7_routing_block[asp_block_start_index:]:
                                    if 'exit' in i:
                                        break
                                    result_end_point_port = regex_end_point_port.search(i)
                                    result_end_point_addr = regex_end_point_addr.search(i)
                                    result_end_point_bind = regex_end_point_bind.search(i)

                                    if result_end_point_port:
                                        self.add_unique_header(result_end_point_port.group(1), asp_headers)
                                        b = a + [result_end_point_port.group(2)]

                                    if result_end_point_addr:
                                        tmp_arr = []

                                        for item in result_end_point_addr.groups():
                                            if result_end_point_addr.groups().index(item) % 2 == 0:
                                                self.add_unique_header(item, asp_headers)
                                            else:
                                                tmp_arr.append(item)
                                                if not b:
                                                    b = a + ['-']
                                        asp_instance_info.append(b + tmp_arr)

                                    if result_end_point_bind:
                                        self.add_unique_header(result_end_point_bind.group(1), asp_headers)
                                        for list_item in asp_instance_info:
                                            c = list_item + [result_end_point_bind.group(1).split(' ')[1]]
                                            c = self.reorder_list([0, 2, 3, 4, 1], c)
                                            asp_values.append(c)

                            # parsing peer server
                            if result_peer_server_id:
                                peer_server_info = []

                                self.add_unique_header(result_peer_server_id.group(1), peer_server_headers)

                                peer_server_info.append(result_peer_server_id.group(2))

                                peer_server_block_start_index = ss7_routing_block.index(line)

                                for i in ss7_routing_block[peer_server_block_start_index + 1:]:
                                    if block_peer_server in i:
                                        # print(i)
                                        break
                                    result_peer_name = regex_peer_name.search(i)
                                    result_peer_mode = regex_peer_mode.search(i)
                                    result_peer_routing_context = regex_peer_routing_context.search(i)
                                    result_peer_self_point_code = regex_peer_self_point_code.search(i)
                                    result_peer_psp_instance = regex_peer_psp_instance.search(i)

                                    if result_peer_name:
                                        self.add_unique_header(result_peer_name.group(1), peer_server_headers)
                                        peer_server_info.append(result_peer_name.group(2))

                                    if result_peer_mode:
                                        self.add_unique_header(result_peer_mode.group(1), peer_server_headers)
                                        peer_server_info.append(result_peer_mode.group(2))

                                    if result_peer_routing_context:
                                        self.add_unique_header(result_peer_routing_context.group(1),
                                                               peer_server_headers)
                                        peer_server_info.append(result_peer_routing_context.group(2))
                                    if result_peer_self_point_code:
                                        self.add_unique_header(result_peer_self_point_code.group(1),
                                                               peer_server_headers)
                                        peer_server_info.append(result_peer_self_point_code.group(2))

                                    # parsing psp params
                                    if result_peer_psp_instance:
                                        test_arr = []
                                        a = []
                                        b = []
                                        c = []
                                        self.add_unique_header(result_peer_psp_instance.group(1), peer_server_headers)
                                        self.add_unique_header(result_peer_server_id.group(1), psp_instance_headers)
                                        self.add_unique_header(result_peer_psp_instance.group(1), psp_instance_headers)
                                        peer_server_info.append(result_peer_psp_instance.group(2))

                                        a.append(result_peer_server_id.group(2))
                                        a.append(result_peer_psp_instance.group(2))
                                        psp_instance_block_start_index = ss7_routing_block.index(i)

                                        for j in ss7_routing_block[psp_instance_block_start_index:]:

                                            if 'exit' in j:
                                                break
                                            result_psp_mode = regex_psp_mode.search(j)
                                            result_associate_asp_instance = regex_associate_asp_instance.search(j)
                                            result_psp_endpoint_address = regex_psp_endpoint_address.search(j)
                                            result_psp_endpoint_port = regex_psp_endpoint_port.search(j)

                                            if result_psp_mode:
                                                self.add_unique_header(result_psp_mode.group(1), psp_instance_headers)
                                                self.add_unique_header('exchange-mode', psp_instance_headers)

                                                b = a + [result_psp_mode.group(2)] + ['-']

                                            if result_psp_endpoint_port:
                                                self.add_unique_header(result_psp_endpoint_port.group(1),
                                                                       psp_instance_headers)
                                                if not b:
                                                    b = a + ['-'] + ['-']

                                                c = b + [result_psp_endpoint_port.group(2)]

                                            if result_psp_endpoint_address:
                                                tmp_arr = []
                                                self.add_unique_header(result_psp_endpoint_address.group(1),
                                                                       psp_instance_headers)
                                                tmp_arr.append(result_psp_endpoint_address.group(2))

                                                if not b:
                                                    b = a + ['-'] + ['-']
                                                if not c:
                                                    c = b + ['-']
                                                d = c + tmp_arr
                                                # print(d)
                                                test_arr.append(d)

                                            if result_associate_asp_instance:
                                                self.add_unique_header(result_associate_asp_instance.group(1),
                                                                       psp_instance_headers)

                                                for list_item in test_arr:
                                                    e = list_item + [result_associate_asp_instance.group(2)]
                                                    e = self.reorder_list([0, 1, 2, 3, 5, 6, 4], e)
                                                    psp_instance_values.append(e)

                                peer_server_values.append(peer_server_info)
                break

        return dict_ss7_routing_domain


    def parse_ss7_routing_domain_2(self, file_content_2):
        pattern_routing_domain = '^(ss7-routing-domain)\\s([0-9]+)\\s(variant)\\s([a-zA-Z]+)'
        pattern_description = '^(description)\\s(\"[.*]\")'
        pattern_ssf = '^(ssf)\\s([a-zA-Z]+)'
        pattern_routing_context = '^(routing-context)\\s([0-9]+)'

        pattern_asp_instance = '^(asp instance)\\s([0-9]+)'
        pattern_end_point_addr = '^(end-point address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)\\s(context)\\s(.*)'
        pattern_end_point_port = '^(end-point port)\\s([0-9]+)'
        pattern_end_point_bind = '^(end-point bind)'

        pattern_peer_server_id = '^(peer-server id)\\s([0-9]+)'
        pattern_peer_name = '^(name)\\s(.*)'
        pattern_peer_mode = '^(mode)\\s(.*)'
        pattern_peer_routing_context = '^(routing-context)\\s([0-9]+)'
        pattern_peer_self_point_code = '^(self-point-code)\\s([0-9]+)'
        pattern_peer_psp_instance = '^(psp instance)\\s([0-9]+)'

        pattern_psp_mode = '^(psp-mode)\\s(.*)'
        pattern_psp_endpoint_port = '^(end-point port)\\s([0-9]+)'
        pattern_psp_endpoint_address = '^(end-point address)\\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        pattern_associate_asp_instance = '^(associate asp instance)\\s([0-9]+)'

        regex_routing_domain = self.get_regex_value(pattern_routing_domain)
        regex_description = self.get_regex_value(pattern_description)
        regex_ssf = self.get_regex_value(pattern_ssf)
        regex_routing_context = self.get_regex_value(pattern_routing_context)
        regex_asp_instance = self.get_regex_value(pattern_asp_instance)
        regex_end_point_addr = self.get_regex_value(pattern_end_point_addr)
        regex_end_point_port = self.get_regex_value(pattern_end_point_port)
        regex_end_point_bind = self.get_regex_value(pattern_end_point_bind)

        regex_peer_server_id = self.get_regex_value(pattern_peer_server_id)
        regex_peer_name = self.get_regex_value(pattern_peer_name)
        regex_peer_mode = self.get_regex_value(pattern_peer_mode)
        regex_peer_routing_context = self.get_regex_value(pattern_peer_routing_context)
        regex_peer_self_point_code = self.get_regex_value(pattern_peer_self_point_code)
        regex_peer_psp_instance = self.get_regex_value(pattern_peer_psp_instance)

        regex_psp_mode = self.get_regex_value(pattern_psp_mode)
        regex_psp_endpoint_port = self.get_regex_value(pattern_psp_endpoint_port)
        regex_psp_endpoint_address = self.get_regex_value(pattern_psp_endpoint_address)
        regex_associate_asp_instance = self.get_regex_value(pattern_associate_asp_instance)

        dict_ss7_routing_domain = {}
        ss7_routing_tables = []

        dict_ss7_info = {}
        ss7_headers = []
        ss7_values = []
        dict_ss7_info['table_name'] = [
            'SS7 Routing Domain to Support IP Signaling for SIGTRAN for IUPS -C  interface , this configuration will be done in the global configuration mode']
        dict_ss7_info['headers'] = ss7_headers
        dict_ss7_info['values'] = ss7_values
        ss7_routing_tables.append(dict_ss7_info)

        dict_asp_instance = {}
        asp_headers = []
        asp_values = []
        dict_asp_instance['table_name'] = ['Asp Instance']
        dict_asp_instance['headers'] = asp_headers
        dict_asp_instance['values'] = asp_values
        ss7_routing_tables.append(dict_asp_instance)

        dict_peer_server = {}
        peer_server_headers = []
        peer_server_values = []
        dict_peer_server['table_name'] = ['Peer Server Id']
        dict_peer_server['headers'] = peer_server_headers
        dict_peer_server['values'] = peer_server_values
        ss7_routing_tables.append(dict_peer_server)

        dict_psp_instance = {}
        psp_instance_headers = []
        psp_instance_values = []
        dict_psp_instance['table_name'] = ['PSP Parameters Server Id']
        dict_psp_instance['headers'] = psp_instance_headers
        dict_psp_instance['values'] = psp_instance_values
        ss7_routing_tables.append(dict_psp_instance)

        dict_ss7_routing_domain['sheet'] = 'SS7 Routing Domain IUPSC'
        dict_ss7_routing_domain['label'] = ['Context Local']
        dict_ss7_routing_domain['sheet_tables'] = ss7_routing_tables

        for group in file_content_2:
            if block_ss7_routing_2 in group[0]:
                for i, ss7_routing_block in enumerate(get_groups(group, block_ss7_routing_2)):
                    if block_ss7_routing_2 in ss7_routing_block[0]:
                        for line in ss7_routing_block:

                            # parse asp instance
                            result_asp_instance = regex_asp_instance.search(line)
                            result_peer_server_id = regex_peer_server_id.search(line)
                            asp_instance_info = []

                            if result_asp_instance:
                                a = []
                                b = []
                                self.add_unique_header(result_asp_instance.group(1), asp_headers)
                                a.append(result_asp_instance.group(2))
                                asp_block_start_index = ss7_routing_block.index(line)

                                for i in ss7_routing_block[asp_block_start_index:]:
                                    if 'exit' in i:
                                        break
                                    result_end_point_port = regex_end_point_port.search(i)
                                    result_end_point_addr = regex_end_point_addr.search(i)
                                    result_end_point_bind = regex_end_point_bind.search(i)

                                    if result_end_point_port:
                                        self.add_unique_header(result_end_point_port.group(1), asp_headers)
                                        b = a + [result_end_point_port.group(2)]

                                    if result_end_point_addr:
                                        tmp_arr = []

                                        for item in result_end_point_addr.groups():
                                            if result_end_point_addr.groups().index(item) % 2 == 0:
                                                self.add_unique_header(item, asp_headers)
                                            else:
                                                tmp_arr.append(item)
                                                if not b:
                                                    b = a + ['-']
                                        asp_instance_info.append(b + tmp_arr)

                                    if result_end_point_bind:
                                        self.add_unique_header(result_end_point_bind.group(1), asp_headers)
                                        for list_item in asp_instance_info:
                                            c = list_item + [result_end_point_bind.group(1).split(' ')[1]]
                                            c = self.reorder_list([0, 2, 3, 4, 1], c)
                                            asp_values.append(c)

                            # parsing peer server
                            if result_peer_server_id:
                                peer_server_info = []

                                self.add_unique_header(result_peer_server_id.group(1), peer_server_headers)

                                peer_server_info.append(result_peer_server_id.group(2))

                                peer_server_block_start_index = ss7_routing_block.index(line)

                                for i in ss7_routing_block[peer_server_block_start_index + 1:]:
                                    if block_peer_server in i:
                                        # print(i)
                                        break
                                    result_peer_name = regex_peer_name.search(i)
                                    result_peer_mode = regex_peer_mode.search(i)
                                    result_peer_routing_context = regex_peer_routing_context.search(i)
                                    result_peer_self_point_code = regex_peer_self_point_code.search(i)
                                    result_peer_psp_instance = regex_peer_psp_instance.search(i)

                                    if result_peer_name:
                                        self.add_unique_header(result_peer_name.group(1), peer_server_headers)
                                        peer_server_info.append(result_peer_name.group(2))

                                    if result_peer_mode:
                                        self.add_unique_header(result_peer_mode.group(1), peer_server_headers)
                                        peer_server_info.append(result_peer_mode.group(2))

                                    if result_peer_routing_context:
                                        self.add_unique_header(result_peer_routing_context.group(1),
                                                               peer_server_headers)
                                        peer_server_info.append(result_peer_routing_context.group(2))
                                    if result_peer_self_point_code:
                                        self.add_unique_header(result_peer_self_point_code.group(1),
                                                               peer_server_headers)
                                        peer_server_info.append(result_peer_self_point_code.group(2))

                                    # parsing psp params
                                    if result_peer_psp_instance:
                                        test_arr = []
                                        a = []
                                        b = []
                                        c = []
                                        self.add_unique_header(result_peer_psp_instance.group(1), peer_server_headers)
                                        self.add_unique_header(result_peer_server_id.group(1), psp_instance_headers)
                                        self.add_unique_header(result_peer_psp_instance.group(1), psp_instance_headers)
                                        peer_server_info.append(result_peer_psp_instance.group(2))

                                        a.append(result_peer_server_id.group(2))
                                        a.append(result_peer_psp_instance.group(2))
                                        psp_instance_block_start_index = ss7_routing_block.index(i)

                                        for j in ss7_routing_block[psp_instance_block_start_index:]:

                                            if 'exit' in j:
                                                break
                                            result_psp_mode = regex_psp_mode.search(j)
                                            result_associate_asp_instance = regex_associate_asp_instance.search(j)
                                            result_psp_endpoint_address = regex_psp_endpoint_address.search(j)
                                            result_psp_endpoint_port = regex_psp_endpoint_port.search(j)

                                            if result_psp_mode:
                                                self.add_unique_header(result_psp_mode.group(1), psp_instance_headers)
                                                self.add_unique_header('exchange-mode', psp_instance_headers)

                                                b = a + [result_psp_mode.group(2)] + ['-']

                                            if result_psp_endpoint_port:
                                                self.add_unique_header(result_psp_endpoint_port.group(1),
                                                                       psp_instance_headers)
                                                if not b:
                                                    b = a + ['-'] + ['-']

                                                c = b + [result_psp_endpoint_port.group(2)]

                                            if result_psp_endpoint_address:
                                                tmp_arr = []
                                                self.add_unique_header(result_psp_endpoint_address.group(1),
                                                                       psp_instance_headers)
                                                tmp_arr.append(result_psp_endpoint_address.group(2))

                                                if not b:
                                                    b = a + ['-'] + ['-']
                                                if not c:
                                                    c = b + ['-']
                                                d = c + tmp_arr
                                                # print(d)
                                                test_arr.append(d)

                                            if result_associate_asp_instance:
                                                self.add_unique_header(result_associate_asp_instance.group(1),
                                                                       psp_instance_headers)

                                                for list_item in test_arr:
                                                    e = list_item + [result_associate_asp_instance.group(2)]
                                                    e = self.reorder_list([0, 1, 2, 3, 5, 6, 4], e)
                                                    psp_instance_values.append(e)

                                peer_server_values.append(peer_server_info)
                break

        return dict_ss7_routing_domain
