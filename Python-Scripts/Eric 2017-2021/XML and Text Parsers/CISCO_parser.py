from pandas import ExcelWriter
import pandas as pd
import numpy as np
from re import search

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



input_file = 'vSPG01.txt'
block_identifier = '  #exit' 
content_groups = read_file_content_2(input_file, block_identifier)



# substring for each table
sub_APN_4 = 'apn lucpostpaidairtelgprs.com'
sub_APN_3 = 'apn airtelgprs.com'

res_APN = []

for i in content_groups:
    # print(i)
    if (sub_APN_3 in i ) or sub_APN_4 in i:
        res_APN.append(i)
        
res_APN = res_APN[0]


start_index_string = 'apn airtelgprs.com'
end_index_string = 'ip route static bfd Gi_3/10_vlan110 192.168.20.1'

for i in range(len(res_APN)):
    if start_index_string == res_APN[i]:
        start_index = i
    if end_index_string == res_APN[i]:
        end_index = i-4
        
res_APN = res_APN[start_index:end_index]

# apn airtelgprs.com
# apn lucpostpaidairtelgprs.com
# apn lucpostpaidairtelgprslbo.com
# apn lucprepaidairtelgprs.com
# apn lucprepaidairtelgprslbo.com
# apn lucprepaidairtellte.com
# apn lucprepaidairtelltelbo.com
# apn testugw

index_sub_list = []

for i in range(len(res_APN)):
    if res_APN[i] == 'exit':
        index_sub_list.append(i+1)
        
index_sub_list




df_columns = ['apn','gtpp group','accounting-context',
              'virtual-apn','apn-name-to-be-included','ims-auth-service',
              'dns primary','dns secondary','ip address pool name',
              'cc-home','cc-visiting','cc-roaming',
              'ipv6 dns primary','ipv6 dns secondary',
              'cc-profile','credit-control-group',
              'active-charging rulebase']




df_APN = pd.DataFrame(columns = df_columns, index = np.arange(10))
df_APN.head()

count = -1
for i in res_APN:
    string_check = i.split(' ')
    if string_check[0] == 'apn':
        count = count + 1
        df_APN.at[count, 'apn'] = string_check[1]
    elif string_check[0] == 'gtpp':
        df_APN.at[count, 'gtpp group'] = string_check[2]
        df_APN.at[count, 'accounting-context'] = string_check[-1]
    elif string_check[0] == 'virtual-apn':
        df_APN.at[count, 'virtual-apn'] = string_check[1]
        df_APN.at[count, 'apn-name-to-be-included'] = string_check[-1]
    elif string_check[0] == 'ims-auth-service':
        df_APN.at[count, 'ims-auth-service'] = string_check[-1]
    elif (string_check[0] == 'dns') and (string_check[1] == 'primary'):
        df_APN.at[count, 'dns primary'] = string_check[-1]
    elif (string_check[0] == 'dns') and (string_check[1] == 'secondary'):
        df_APN.at[count, 'dns secondary'] = string_check[-1]
    elif (string_check[0] == 'ip') and (string_check[1] == 'address'):
        df_APN.at[count, 'ip address pool name'] = string_check[-1]
    elif string_check[0] == 'cc-home':
        df_APN.at[count, 'cc-home'] = " ".join(string_check[1:])
    elif string_check[0] == 'cc-visiting':
        df_APN.at[count, 'cc-visiting'] = " ".join(string_check[1:])
    elif string_check[0] == 'cc-roaming':
        df_APN.at[count, 'cc-roaming'] = " ".join(string_check[1:])
    elif (string_check[0] == 'ipv6') and (string_check[2] == 'primary'):
        df_APN.at[count, 'ipv6 dns primary'] = string_check[-1]
    elif (string_check[0] == 'ipv6') and (string_check[2] == 'secondary'):
        df_APN.at[count, 'ipv6 dns secondary'] = string_check[-1]
    elif string_check[0] == 'cc-profile':
        df_APN.at[count, 'cc-profile'] = string_check[1]
        df_APN.at[count, 'credit-control-group'] = string_check[-1]
    elif string_check[0] == 'active-charging':
        df_APN.at[count, 'active-charging rulebase'] = string_check[-1]





# ======================================================CONTEXT===============================
# context local
# context GnS5S8


# context SGi
# context GaGz
# context GxGy
# context Li
# context IMS

res_Context_local = []
for i in content_groups:
    if ('context local' in i ):
        res_Context_local.append(i)
        
res_Context_local = res_Context_local[0]
res_Context_local = res_Context_local[6:11]


df_Context_local_columns = ['Context Name',
                            'Interface',
                            'Ipaddress',
                            'router ospf'
                           ]
df_Context_local = pd.DataFrame(columns = df_Context_local_columns, index = np.arange(3))
df_Context_local


count = -1
for i in res_Context_local:
    string_check = i.split(' ')
    if string_check[0] == 'context':
        count = count + 1
        df_Context_local.at[count, 'Context Name'] = string_check[-1]
    elif string_check[0] == 'ip' and string_check[1] == 'routing':
         df_Context_local.at[count, 'router ospf'] = string_check[-1]
    elif string_check[0] == 'interface':
         df_Context_local.at[count, 'Interface'] = string_check[-1]
    elif string_check[0] == 'ip' and string_check[1] == 'address' :
         df_Context_local.at[count, 'Ipaddress'] = " ".join(string_check[2:])


# context GnS5S8
res_context_GnS5S8 = []
for i in content_groups:
    if ('context GnS5S8' in i ):
        res_context_GnS5S8.append(i)
        
res_context_GnS5S8 = res_context_GnS5S8[0]


context_GnS5S8_neighbor_list = []
context_GnS5S8_network_list = []
context_GnS5S8_subnet_list = []
context_GnS5S8_interface_list = []
for i in res_context_GnS5S8:
    if i.split(' ')[0] == 'neighbor':
        context_GnS5S8_neighbor_list.append(i)
    elif i.split(' ')[0] == 'network':
        context_GnS5S8_network_list.append(i)
    elif (i.split(' ')[0] == 'ip') and (i.split(' ')[1] == 'address'):
        context_GnS5S8_subnet_list.append(i)
    elif (i.split(' ')[0] == 'interface'):
        context_GnS5S8_interface_list.append(i.split(' ')[1])


df_context_GnS5S8_columns = [
'Context Name',
    'Interface',
    'Ipaddress',
    'subnet',
    'router <dynamic value bgp>',
        'neighbor',
        'network',
        'routing'
]
df_context_GnS5S8 = pd.DataFrame(columns = df_context_GnS5S8_columns, index = np.arange(37))
df_context_GnS5S8.head()


for i in range(len(context_GnS5S8_neighbor_list)):
    df_context_GnS5S8.at[i,'neighbor'] =context_GnS5S8_neighbor_list[i]

for i in range(len(context_GnS5S8_network_list)):
    df_context_GnS5S8.at[i,'network'] =context_GnS5S8_network_list[i]
    
df_context_GnS5S8['routing'] = 'maximum-paths 64'

df_context_GnS5S8['router <dynamic value bgp>'] = 'router bgp 64995'

count = 0
for i in context_GnS5S8_subnet_list:
    df_context_GnS5S8.at[count, 'Ipaddress'] = i.split(' ')[-2]
    df_context_GnS5S8.at[count, 'subnet'] = i.split(' ')[-1]
    count = count + 1
    
count = 0
for i in context_GnS5S8_interface_list:
    df_context_GnS5S8.at[count, 'Interface'] = i.split(' ')[-1]
    count = count + 1
    
df_context_GnS5S8['Context Name']= 'GnS5S8'


# ==================================Host Pool=======================================
res_host_pool = []
for i in content_groups:
    if ('host-pool 410_encrypt_1' in i ):
        res_host_pool.append(i)

res_host_pool = res_host_pool[0]

for i in range(len(res_host_pool)):
    if res_host_pool[i] == 'host-pool 403_encrypt_1':
        start_index_host_pool = i
    if res_host_pool[i] == 'port-map sip_signal_ports':
        end_index_host_pool = i
        
res_host_pool = res_host_pool[start_index_host_pool:end_index_host_pool]

df_host_pool_columns = ['name','ip-pool']

# count = 0
# for i in range(len(res_host_pool)):
#     if res_host_pool[i] == '#exit':
#         count = count +1

df_host_pool = pd.DataFrame(columns = df_host_pool_columns, index = np.arange(155))
df_host_pool.head()


count = 0
host_pool_ip_list = []
for i in range(len(res_host_pool)):
    if 'host-pool' in res_host_pool[i]:
        df_host_pool.at[count, 'name'] = res_host_pool[i]
        
    if res_host_pool[i].split(' ')[0] == 'ip':
        host_pool_ip_list.append(res_host_pool[i])
    if res_host_pool[i] == '#exit':
        df_host_pool.at[count, 'ip-pool'] = host_pool_ip_list
        count = count +1
        host_pool_ip_list = []


#======================================operator-policy===============================
df_operator_policy_columns = ['operator-policy name',
                      'associate call control profile']

df_operator_policy = pd.DataFrame(columns = df_operator_policy_columns, index = np.arange(3))
df_operator_policy.head()


res_operator_policy = []
for i in content_groups:
    if 'operator-policy name ROAMING' in i:
        res_operator_policy.append(i)
    if 'operator-policy name HOME' in i:
        res_operator_policy.append(i)

df_operator_policy.at[0,'operator-policy name'] = res_operator_policy[0][-2].split(' ')[-1]
df_operator_policy.at[0,'associate call control profile'] = res_operator_policy[0][-1].split(' ')[-1]

df_operator_policy.at[1,'operator-policy name'] = res_operator_policy[1][1].split(' ')[-1]
df_operator_policy.at[1,'associate call control profile'] = res_operator_policy[1][-1].split(' ')[-1]


#=================================LTE Policy==========================================


df_lte_policy_column = ['subscriber-map',
                        'operator-policy-name',
                        'precedence',
                        'match-criteria',
                        'mcc',
                        'mnc'
]
df_lte_policy = pd.DataFrame(columns = df_lte_policy_column, index = np.arange(3))
df_lte_policy



res_lte_policy = []
for i in content_groups:
    if 'lte-policy' in i:
        res_lte_policy.append(i)
        
res_lte_policy = res_lte_policy[0]
res_lte_policy = res_lte_policy[1:7]

count = 0
for i in res_lte_policy:
    if 'subscriber-map' in i:
        df_lte_policy['subscriber-map'] = i.split(' ')[1]
    if i.split(' ')[0] == 'precedence':
        df_lte_policy.at[count,'operator-policy-name'] = i.split(' ')[-1]
        df_lte_policy.at[count,'precedence'] = i.split(' ')[1]
        df_lte_policy.at[count,'match-criteria'] = i.split(' ')[3]
        if i.split(' ')[1] != '200':
            df_lte_policy.at[count,'mcc'] = i.split(' ')[5]
            df_lte_policy.at[count,'mnc'] = i.split(' ')[7]
        count = count + 1



# ==============================CARD==============================================

df_card_coulmns = ['Card',
                   'Mode' 
]
df_card = pd.DataFrame(columns = df_card_coulmns, index = np.arange(15))
df_card.head()


list_card = ['card 3','card 4','card 5','card 6','card 7',
            'card 8','card 9','card 10','card 11','card 12',
            'card 13','card 14','card 15','card 16',]
res_card = []
for i in content_groups:
    for j in list_card:
        if j in i:
            res_card.append(i)
            
res_card = [res_card[0][-2:]] + res_card[1:]



for i in range(len(res_card)):
    if i == 0:
        df_card.at[i,'Card'] = res_card[i][0]
        df_card.at[i,'Mode'] = res_card[i][1].split(' ')[1]
    if i != 0:
        df_card.at[i,'Card'] = res_card[i][1]
        df_card.at[i,'Mode'] = res_card[i][2].split(' ')[1]



# ==================================================Port Ethernet=========================


df_port_ethernet_columns = ['port','vlan','interface']
df_port_ethernet = pd.DataFrame(columns = df_port_ethernet_columns, index = np.arange(15))
df_port_ethernet.head()


res_port_ethernet = []
list_port_ethernet = ['port ethernet 3/10','port ethernet 3/11','port ethernet 4/10',
'port ethernet 4/11','port ethernet 5/10','port ethernet 5/11',
'port ethernet 6/10','port ethernet 6/11','port ethernet 7/10','port ethernet 7/11',
'port ethernet 8/10','port ethernet 8/11','port ethernet 9/10',
'port ethernet 9/11','port ethernet 10/10','port ethernet 10/11','port ethernet 11/10','port ethernet 11/11',
'port ethernet 12/10','port ethernet 12/11','port ethernet 13/10','port ethernet 13/11',
'port ethernet 14/10','port ethernet 14/11',
'port ethernet 15/10','port ethernet 15/11','port ethernet 16/10','port ethernet 16/11',]

for i in content_groups:
    for j in list_port_ethernet:
        if j in i:
            res_port_ethernet.append(i)



count = -1
port_value = 'ethernet 3/10'
for i in res_port_ethernet:
    for j in i:
        if j ==  '#exit':
            count = count + 1
        if j.split(' ')[0] == 'port':
            port_value = " ".join(j.split(' ')[1:])
        df_port_ethernet.at[count, 'port'] = port_value
        if j.split(' ')[0] == 'vlan':
            df_port_ethernet.at[count, 'vlan'] = j.split(' ')[1]
        if j.split(' ')[0] == 'bind':
            df_port_ethernet.at[count, 'interface'] = j.split(' ')[2]


# =======================================call-control-profile===================================


df_call_control_profile_columns = ['aconting context',
                                   'gtpp group',
                                   'accounting mode']
df_call_control_profile = pd.DataFrame(columns = df_call_control_profile_columns, index = np.arange(3))
df_call_control_profile.head()



res_call_control_profile = []
for i in content_groups:
    if 'call-control-profile CCP-HOME' in i:
        res_call_control_profile.append(i)
    if 'call-control-profile CCP-ROAMING' in i:
        res_call_control_profile.append(i)

        
df_call_control_profile.at[0,'aconting context'] = res_call_control_profile[0][-2].split(' ')[2]
df_call_control_profile.at[0,'gtpp group'] = res_call_control_profile[0][-2].split(' ')[-1]
df_call_control_profile.at[0,'accounting mode'] = res_call_control_profile[0][-1].split(' ')[-1]

df_call_control_profile.at[1,'aconting context'] = res_call_control_profile[1][-2].split(' ')[2]
df_call_control_profile.at[1,'gtpp group'] = res_call_control_profile[1][-2].split(' ')[-1]
df_call_control_profile.at[1,'accounting mode'] = res_call_control_profile[1][-1].split(' ')[-1]




# ===========================FIN==============================================================

df_list = [df_APN,
df_Context_local,
df_context_GnS5S8,
df_host_pool,
df_operator_policy,
df_lte_policy,
df_card,
df_port_ethernet,
df_call_control_profile]



df_list_name = ['APN', 'Context_local', 'Context_GnS5S8','host_pool',
               'operator_policy','lte_policy','card', 'port_ethernet', 'call_control_profile'  ]



xls_path = "output.xlsx"




def save_xls(list_dfs, xls_path):
    with ExcelWriter(xls_path) as writer:
        for n,df in enumerate(list_dfs):
            df.to_excel(writer,'S_%s' % n, index = False)
        writer.save()


save_xls(df_list,xls_path)