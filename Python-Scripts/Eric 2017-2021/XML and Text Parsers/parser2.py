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

# ====================================data parsing for desired component blocks====================================#



# substring for each table
sub_Connections = '#\tTable Name : Connections'
sub_Realms = '#\tTable Name : Realms'
sub_ResourceManagement_ASPool = '#\tTable Name : ResourceManagement.ASPool'
sub_System_DnsEnumAssignment = '#\tTable Name : System.DnsEnumAssignment'
sub_IP_CLUSTER_ROUTING = '#\tTable Name : IP_CLUSTER_ROUTING'

# Resulting components
res_Connections = [i for i in content_groups if sub_Connections in i] 
res_Realms = [i for i in content_groups if sub_Realms in i] 
res_ResourceManagement_ASPool = [i for i in content_groups if sub_ResourceManagement_ASPool in i] 
res_System_DnsEnumAssignment = [i for i in content_groups if sub_System_DnsEnumAssignment in i] 
res_IP_CLUSTER_ROUTING = [i for i in content_groups if sub_IP_CLUSTER_ROUTING in i] 



# ====================================data parsing for getting desired table indexes====================================#
def get_index(res_component, current_table_name):
    final_index =[]
    for i in range(len(res_component)):
        count = 0
        for j in range(len(res_component[i])):
            if res_component[i][j] == current_table_name:
                # print(i,j)
                final_index.append(j)
                count = count +1
            if count>0:
                if search('Table Name : ', res_component[i][j+1]):
                    # print(i,j)
                    final_index.append(j+1)
                    break
    return final_index

index_Connections = get_index(res_Connections, sub_Connections)
index_Realms = get_index(res_Realms, sub_Realms)
index_ResourceManagement_ASPool = get_index(res_ResourceManagement_ASPool, sub_ResourceManagement_ASPool)
index_System_DnsEnumAssignment = get_index(res_System_DnsEnumAssignment, sub_System_DnsEnumAssignment)
index_IP_CLUSTER_ROUTING = get_index(res_IP_CLUSTER_ROUTING, sub_IP_CLUSTER_ROUTING)

table_Connections = res_Connections[0][index_Connections[0]:index_Connections[1]]
table_realms = res_Realms[0][index_Realms[0]:index_Realms[1]]
table_ResourceManagement_ASPool = res_ResourceManagement_ASPool[0][index_ResourceManagement_ASPool[0]:index_ResourceManagement_ASPool[1]]
table_System_DnsEnumAssignment = res_System_DnsEnumAssignment[0][index_System_DnsEnumAssignment[0]:index_System_DnsEnumAssignment[1]]
table_IP_CLUSTER_ROUTING = res_IP_CLUSTER_ROUTING[0][index_IP_CLUSTER_ROUTING[0]:index_IP_CLUSTER_ROUTING[1]]


search_Connections = 'Connections'
search_Realms = 'Realms'
search_ResourceManagement_ASPool = 'ResourceManagement.ASPool'
search_System_DnsEnumAssignment = 'System.DnsEnumAssignment'
search_IP_CLUSTER_ROUTING = 'IP_CLUSTER_ROUTING'



# ====================================df for each table====================================#
def create_df(table_component,search_component):
    no_of_rows_component = int(table_component[1][-1])
    set_component = set()
    values_component =[]
    
    if search_component in [search_IP_CLUSTER_ROUTING]:
        no_of_rows_component = int(table_component[1][-3:])
 
    for i in range(2,len(table_component)):   
        if search_component in [search_Connections,search_Realms,search_IP_CLUSTER_ROUTING]:
            if search(search_component, table_component[i]):
                set_component.add(table_component[i].split('.',1)[1].split('=')[0])
                values_component.append([table_component[i].split('.',1)[1].split('=')[0],
                                         table_component[i].split('.',1)[1].split('=')[1]])            
        if search_component in [search_ResourceManagement_ASPool,search_System_DnsEnumAssignment]:
            if search(search_component, table_component[i]):
                set_component.add(table_component[i].split('.',2)[2].split('=')[0])
                values_component.append([table_component[i].split('.',2)[2].split('=')[0],
                                         table_component[i].split('.',2)[2].split('=')[1]])    
            
    df_component = pd.DataFrame(columns = set_component, index = np.arange(0, no_of_rows_component))
    count = 0
    count_multiple = int(len(values_component)/no_of_rows_component)
    j =no_of_rows_component
    new_count_multiple =count_multiple
    for i in range(len(values_component)):
        if i == 0:
            df_component[values_component[i][0]].loc[count] = values_component[i][1]
        if (i == new_count_multiple):
            if j> 0:
                new_count_multiple = new_count_multiple + count_multiple
                j = j-1
            count = count +1
        df_component[values_component[i][0]].loc[count] = values_component[i][1]
    return df_component

# ==================================================================================


df_connetion = create_df(table_Connections,search_component)
df_realm = create_df(table_Realms,search_Realms)
df_ResourceManagement_ASPool = create_df(table_ResourceManagement_ASPool,search_ResourceManagement_ASPool)
df_System_DnsEnumAssignment = create_df(table_System_DnsEnumAssignment,search_System_DnsEnumAssignment)
df_IP_CLUSTER_ROUTING = create_df(table_IP_CLUSTER_ROUTING,search_IP_CLUSTER_ROUTING)

df_list = [df_connetion,df_realm,df_ResourceManagement_ASPool,df_System_DnsEnumAssignment,df_IP_CLUSTER_ROUTING]

# =================================Create Excel sheets with list of df=================================================

def save_xls(list_dfs, xls_path):
    with ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            df.to_excel(writer,'sheet%s' % n, index = False)
        writer.save()


xls_path = 'Output.xlsx'
save_xls(df_list,xls_path)