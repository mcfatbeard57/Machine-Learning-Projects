#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob, os, re, fnmatch
import pandas as pd
from zipfile import *
import datetime


# In[2]:


from concurrent.futures import ProcessPoolExecutor, as_completed


# In[4]:

START_TIME = datetime.datetime.now()
dd=START_TIME.strftime("%Y%m%d%H%M%S")
#dd= '20210628180459'


# In[5]:


dd


# In[6]:


input_dir_all_cbp = r'C:\Users\eyugpua\OneDrive - Ericsson\Downloads\customer_data' 
output_dir = r'C:\Users\eyugpua\OneDrive - Ericsson\Downloads\customer_data'


# In[7]:


def read_data(target_folders,file_type, column_names, required_columns=None):
    try:
        df = None
        file = glob.glob1(target_folders, file_type)
        # print()
        if file:
            file_df = []
            for f in file:
                df = pd.read_csv(os.path.join(target_folders, f), 
                              sep='|', header=None, compression='gzip',
                             names=column_names, usecols=required_columns, index_col=False)  
                file_df.append(df)
            final_df = pd.concat(file_df)
        
    except Exception as e:
        print(e)
    return final_df


# In[8]:


def initialize_schema_dict():
    # each key of schema_dict contains data in form of [file_type, column_names, interesting_columns]
    schema_dict = {    
        'BC_SUB_IDEN': 
        ['BC_SUB_IDEN*.unl.gz', # 'BC_SUB_IDEN*.unl.gz', 
         ['SUB_IDEN_ID','SUB_ID','CUST_ID','NETWORK_TYPE','SUB_IDEN_TYPE','SUB_IDENTITY','PRIMARY_FLAG','EFF_DATE','EXP_DATE'], 
         ['EFF_DATE','CUST_ID','EXP_DATE','SUB_ID','SUB_IDEN_TYPE','SUB_IDENTITY']], #

        'BC_SUBSCRIBER': 
        ['BC_SUBSCRIBER*.unl.gz', # 'BC_SUBSCRIBER*.unl.gz',
         ['SUB_ID','CUST_ID','U_CUST_ID','TP_SUB_KEY','SUB_CLASS','NETWORK_TYPE','SUB_PWD','FIRST_SETPWD_FLAG','SUB_P_LANG','SUB_W_LANG','SUB_LEVEL','DUNNING_FLAG','REGION_ID','BE_ID','STATUS','STATUS_DETAIL','STATUS_DATE','EFF_DATE','EXP_DATE','ACTIVE_LIMIT','ACTIVE_TIME'], 
         ['SUB_ID', 'SUB_P_LANG','STATUS','EFF_DATE','EXP_DATE','ACTIVE_TIME']],# 'CUST_ID',

        'CM_SS_EXP_DATE_INST': 
        ['CM_SS_EXP_DATE_INST*.unl.gz', # 'CM_SS_EXP_DATE_INST*.unl.gz', 
         ['SUB_ID','S1_EXP_DATE','S2_EXP_DATE','S3_EXP_DATE','S4_EXP_DATE','S5_EXP_DATE','S6_EXP_DATE','S7_EXP_DATE','S8_EXP_DATE','S9_EXP_DATE'], 
         ['SUB_ID', 'S2_EXP_DATE','S3_EXP_DATE','S4_EXP_DATE','S8_EXP_DATE','S9_EXP_DATE']],

        'BC_SUB_DFT_ACCT': 
        ['BC_SUB_DFT_ACCT*.unl.gz', # 'BC_SUB_DFT_ACCT*.unl.gz', 
         ['SUB_ID','PAYMENT_MODE','PRE_ACCT_ID','POST_ACCT_ID','DFT_ACCT_ID','EFF_DATE','EXP_DATE'], 
         ['SUB_ID', 'PAYMENT_MODE','DFT_ACCT_ID','EFF_DATE','EXP_DATE']],\

        'BC_ACCT_BILL_CYCLE': 
        ['BC_ACCT_BILL_CYCLE*.unl.gz',  # 'BC_ACCT_BILL_CYCLE*.unl.gz',
         ['ACCT_ID','CUST_ID','BILL_CYCLE_TYPE','EFF_DATE','EXP_DATE','BE_ID'], 
         ['ACCT_ID', 'BILL_CYCLE_TYPE','EFF_DATE','EXP_DATE']],# 'CUST_ID',

        'BC_OFFERING_INST': 
        ['BC_OFFERING_INST*.unl.gz', # 'BC_OFFERING_INST*.unl.gz', 
         ['O_INST_ID','CUST_ID','O_ID','PURCHASE_SEQ','PRIMARY_FLAG','BUNDLE_FLAG','O_CLASS','P_O_INST_ID','R_GO_INST_ID','R_GROUP_ID','OWNER_TYPE','OWNER_ID','ACTIVE_MODE','ACTIVE_LIMIT_TIME','ACTIVE_TIME','TRIAL_S_DATE','TRIAL_E_DATE','STATUS','STATUS_DETAIL','STATUS_DATE','EFF_DATE','EXP_DATE','CREATE_TIME'], 
         ['O_INST_ID','O_ID','PRIMARY_FLAG','ACTIVE_TIME','STATUS','EFF_DATE','EXP_DATE','OWNER_ID']],#'CUST_ID','O_CLASS','OWNER_TYPE',

        'CM_ACCT_BALANCE': 
        ['CM_ACCT_BALANCE*.unl.gz',  # 'CM_ACCT_BALANCE*.unl.gz',
         ['ACCT_BALANCE_ID','ACCT_ID','SECOND_OWNER_TYPE','SECOND_OWNER_ID','BALANCE_TYPE_ID','AMOUNT','INITIAL_AMOUNT','RESERVE_AMOUNT','SETTLE_AMOUNT','ORIGIN_TYPE','ORIGIN_ID','INITIAL_TYPE','INITIAL_ID','INITIAL_ACCT_BALANCE_ID','EFF_DATE','EXP_DATE','CREATE_TIME','LAST_UPDATE_TIME','PRE_BC_AMOUNT','POLICY_CYCLE_ID','SUB_ID','PPRE_BC_AMOUNT','RENEWAL_POLICY_ID','RENEWAL_FLAG','ALREADY_RENEWAL_TIMES','MAX_RENEWAL_TIMES','RESERVE_VALID_TIME','MONETARY_FLAG','OWNER_TYPE','OWNER_ID','TARIFF_CODE','USAGE_PRIORITY','CUST_ID'], 
         ['BALANCE_TYPE_ID', 'ACCT_ID', 'AMOUNT','EFF_DATE','EXP_DATE']],# 'CUST_ID', 

        'PE_ACCM': 
        ['PE_ACCM*.unl.gz', # 'PE_ACCM*.unl.gz',
         ['ACCM_ID','CUST_ID','ACCM_OWNER_ID','ACCM_TYPE_ID','BALANCE','PRE_BALANCE','BEGIN_DATE','END_DATE','CREATE_DATE','DATA_PRODUCT_ID','CLEAN_DATE','LAST_UPDATE_TIME'], 
         ['ACCM_OWNER_ID', 'ACCM_TYPE_ID',  'BALANCE','BEGIN_DATE','END_DATE']],# 'CUST_ID',

        'BC_G_MEMBER': 
        ['BC_G_MEMBER*.unl.gz', # 'BC_G_MEMBER*.unl.gz'
         ['MEMBER_ID','GROUP_ID','GROUP_CUST_ID','SUB_ID','PRI_IDENTITY','SUB_CUST_ID','NETWORK_TYPE','MEMBER_CODE','EFF_DATE','EXP_DATE','STATUS','STATUS_DETAIL','STATUS_DATE'], 
         ['SUB_ID', 'GROUP_ID','PRI_IDENTITY','MEMBER_CODE', 'EFF_DATE','EXP_DATE']]
        }
    
    return schema_dict


# In[9]:


def read_target_folders_all():
    subfolders = [f.path for f in os.scandir(input_dir_all_cbp) if f.is_dir()]
    target_folders_all = []
    for input_path in subfolders:
        head, tail = os.path.split(input_path)    
        if re.match('cbp',tail):
            target_folders_all.append(input_path)
    return target_folders_all


# In[10]:


def read_E_temp_offering_tables_path():
    onlyfiles = [os.path.join(input_dir_all_cbp, f) for f in os.listdir(input_dir_all_cbp) if os.path.isfile(os.path.join(input_dir_all_cbp, f))]
    target_files_all = []
    for input_files in onlyfiles:
        head, tail = os.path.split(input_files)    
        # print(head,tail)
        if re.match('E_TEMP_OFFERING',tail):
            target_files_all.append(input_files)
    return target_files_all


# In[11]:


def read_E_temp_offering_tables():
    column_names_e_temp = ['SUBSCRIBER_ID','OLD_PRI_OFFER_ID','NEW_PRI_OFFER_ID','CHANGE_TIME','EXPIRE_DATE','REV_PRI_OFFERID']
    required_columns_e_temp = ['SUBSCRIBER_ID', 'CHANGE_TIME','EXPIRE_DATE','REV_PRI_OFFERID']
    temp_offering_df_list = []
    
    for target_files in target_files_all:
        # print(target_files)
        df = pd.read_csv(target_files, sep='|', #compression='gzip',
                            header=None, names=column_names_e_temp, 
                            usecols=required_columns_e_temp, index_col=False)
    
        df['EXPIRE_DATE'] = pd.to_datetime(df['EXPIRE_DATE'], format='%Y%m%d%H%M%S')
        df = df[df['EXPIRE_DATE'] > dd]
        temp_offering_df_list.append(df)
        
    df_temp_offering = pd.concat(temp_offering_df_list)
    df_temp_offering = df_temp_offering.add_suffix('_E_TEMP_OFFERING')
    
    return df_temp_offering


# In[12]:


def edit_join_tables(schema_dict):
    # Editing tables
    # print('Editing tables in ', tail)
    # BC_SUB_IDEN
    (schema_dict['BC_SUB_IDEN']) = (schema_dict['BC_SUB_IDEN'])[(schema_dict['BC_SUB_IDEN'])['EXP_DATE'] > dd]
    (schema_dict['BC_SUB_IDEN']) = (schema_dict['BC_SUB_IDEN'])[(schema_dict['BC_SUB_IDEN'])['SUB_IDEN_TYPE'] == 1]
    (schema_dict['BC_SUB_IDEN']) = (schema_dict['BC_SUB_IDEN']).add_suffix('_BC_SUB_IDEN')

    # BC_SUBSCRIBER
    (schema_dict['BC_SUBSCRIBER']) = (schema_dict['BC_SUBSCRIBER'])[(schema_dict['BC_SUBSCRIBER'])['EXP_DATE'] > dd]
    (schema_dict['BC_SUBSCRIBER']) = (schema_dict['BC_SUBSCRIBER']).add_suffix('_BC_SUBSCRIBER')

    # CM_SS_EXP_DATE_INST
    (schema_dict['CM_SS_EXP_DATE_INST']) = (schema_dict['CM_SS_EXP_DATE_INST']).add_suffix('_CM_SS_EXP_DATE_INST')

    # BC_SUB_DFT_ACCT
    (schema_dict['BC_SUB_DFT_ACCT']) = (schema_dict['BC_SUB_DFT_ACCT'])[(schema_dict['BC_SUB_DFT_ACCT'])['EXP_DATE'] > dd]
    (schema_dict['BC_SUB_DFT_ACCT'])['DFT_ACCT_ID'] = (schema_dict['BC_SUB_DFT_ACCT'])['DFT_ACCT_ID'].astype('int64')
    (schema_dict['BC_SUB_DFT_ACCT']) = (schema_dict['BC_SUB_DFT_ACCT']).add_suffix('_BC_SUB_DFT_ACCT')

    # BC_ACCT_BILL_CYCLE
    (schema_dict['BC_ACCT_BILL_CYCLE']) = (schema_dict['BC_ACCT_BILL_CYCLE'])[(schema_dict['BC_ACCT_BILL_CYCLE'])['EXP_DATE'] > dd]
    (schema_dict['BC_ACCT_BILL_CYCLE']) = (schema_dict['BC_ACCT_BILL_CYCLE']).add_suffix('_BC_ACCT_BILL_CYCLE')
                       
    # BC_OFFERING_INST
    (schema_dict['BC_OFFERING_INST']) = (schema_dict['BC_OFFERING_INST'])[(schema_dict['BC_OFFERING_INST'])['EXP_DATE'] > dd]
    (schema_dict['BC_OFFERING_INST'])['O_INST_ID;O_ID; PRIMARY_FLAG; ACTIVE_TIME; STATUS; EFF_DATE; EXP_DATE'] =         (schema_dict['BC_OFFERING_INST'])['O_INST_ID'].map(str) + ";" +         (schema_dict['BC_OFFERING_INST'])['O_ID'].map(str) + ";" +         (schema_dict['BC_OFFERING_INST'])['PRIMARY_FLAG'].map(str)+ ";" +         (schema_dict['BC_OFFERING_INST'])['ACTIVE_TIME'].map(str) + ";" +         (schema_dict['BC_OFFERING_INST'])['STATUS'].map(str) + ";" +         (schema_dict['BC_OFFERING_INST'])['EFF_DATE'].map(str) + ";" +         (schema_dict['BC_OFFERING_INST'])['EXP_DATE'].map(str)
    (schema_dict['BC_OFFERING_INST']) = (schema_dict['BC_OFFERING_INST']).groupby(['OWNER_ID'], as_index=False).agg({
                                                'O_INST_ID;O_ID; PRIMARY_FLAG; ACTIVE_TIME; STATUS; EFF_DATE; EXP_DATE': '|'.join})
    (schema_dict['BC_OFFERING_INST']) = (schema_dict['BC_OFFERING_INST']).add_suffix('_BC_OFFERING_INST')

    # CM_ACCT_BALANCE
    (schema_dict['CM_ACCT_BALANCE']) = (schema_dict['CM_ACCT_BALANCE'])[(schema_dict['CM_ACCT_BALANCE'])['EXP_DATE'] > dd]
    (schema_dict['CM_ACCT_BALANCE'])['BALANCE_TYPE_ID; AMOUNT; EFF_DATE; EXP_DATE'] =         (schema_dict['CM_ACCT_BALANCE'])['BALANCE_TYPE_ID'].map(str) + ";" +         (schema_dict['CM_ACCT_BALANCE'])['AMOUNT'].map(str) + ";" +         (schema_dict['CM_ACCT_BALANCE'])['EFF_DATE'].map(str) + ";" +         (schema_dict['CM_ACCT_BALANCE'])['EXP_DATE'].map(str)
    (schema_dict['CM_ACCT_BALANCE']) = (schema_dict['CM_ACCT_BALANCE']).groupby(['ACCT_ID'], as_index=False).agg({
                                                'BALANCE_TYPE_ID; AMOUNT; EFF_DATE; EXP_DATE': '|'.join})
    (schema_dict['CM_ACCT_BALANCE']) = (schema_dict['CM_ACCT_BALANCE']).add_suffix('_CM_ACCT_BALANCE')

    # PE_ACCM
    # (schema_dict['PE_ACCM']) = (schema_dict['PE_ACCM'])[(schema_dict['PE_ACCM'])['END_DATE'] > dd]
    (schema_dict['PE_ACCM'])['ACCM_TYPE_ID; BALANCE; BEGIN_DATE; END_DATE'] =         (schema_dict['PE_ACCM'])['ACCM_TYPE_ID'].map(str) + ";" +         (schema_dict['PE_ACCM'])['BALANCE'].map(str) + ";" +         (schema_dict['PE_ACCM'])['BEGIN_DATE'].map(str) + ";" +         (schema_dict['PE_ACCM'])['END_DATE'].map(str)
    (schema_dict['PE_ACCM']) = (schema_dict['PE_ACCM']).groupby(['ACCM_OWNER_ID'], as_index=False).agg({
                                        'ACCM_TYPE_ID; BALANCE; BEGIN_DATE; END_DATE' : '|'.join})
    (schema_dict['PE_ACCM']) = (schema_dict['PE_ACCM']).add_suffix('_PE_ACCM')

    # BC_G_MEMBER
    (schema_dict['BC_G_MEMBER']) = (schema_dict['BC_G_MEMBER'])[(schema_dict['BC_G_MEMBER'])['EXP_DATE'] > dd]
    (schema_dict['BC_G_MEMBER'])['GROUP_ID; PRI_IDENTITY; MEMBER_CODE'] =         (schema_dict['BC_G_MEMBER'])['GROUP_ID'].map(str) + ";" +         (schema_dict['BC_G_MEMBER'])['PRI_IDENTITY'].map(str) + ";" +         (schema_dict['BC_G_MEMBER'])['MEMBER_CODE'].map(str)
            
    (schema_dict['BC_G_MEMBER']).groupby(['SUB_ID'], as_index=False).agg({
                                            'GROUP_ID; PRI_IDENTITY; MEMBER_CODE' : '|'.join})            
    (schema_dict['BC_G_MEMBER']).drop(['GROUP_ID', 'PRI_IDENTITY', 'MEMBER_CODE'], axis = 1, inplace = True)      
    (schema_dict['BC_G_MEMBER']) = (schema_dict['BC_G_MEMBER']).add_suffix('_BC_G_MEMBER')



    # JOINS

    # BC_SUB_IDEN and BC_SUBSCRIBER
    merged_left = pd.merge(left=(schema_dict['BC_SUB_IDEN']), right=(schema_dict['BC_SUBSCRIBER']), 
                                        how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='SUB_ID_BC_SUBSCRIBER')
    merged_left.drop(['SUB_ID_BC_SUBSCRIBER'], axis = 1, inplace = True)

    # merged_left and CM_SS_EXP_DATE_INST
    merged_left = pd.merge(left=merged_left, right=(schema_dict['CM_SS_EXP_DATE_INST']), 
                                        how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='SUB_ID_CM_SS_EXP_DATE_INST')
    merged_left.drop(['SUB_ID_CM_SS_EXP_DATE_INST'], axis = 1, inplace = True)

    # merged_left and BC_SUB_DFT_ACCT
    merged_left = pd.merge(left=merged_left, right=(schema_dict['BC_SUB_DFT_ACCT']), 
                                        how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='SUB_ID_BC_SUB_DFT_ACCT')
    merged_left.drop(['SUB_ID_BC_SUB_DFT_ACCT'], axis = 1, inplace = True)

    # merged_left and BC_ACCT_BILL_CYCLE
    merged_left = pd.merge(left=merged_left, right=(schema_dict['BC_ACCT_BILL_CYCLE']), 
                                        how='left',left_on='DFT_ACCT_ID_BC_SUB_DFT_ACCT', right_on='ACCT_ID_BC_ACCT_BILL_CYCLE')
    merged_left.drop(['ACCT_ID_BC_ACCT_BILL_CYCLE'], axis = 1, inplace = True)

    # merged_left and BC_OFFERING_INST
    merged_left = pd.merge(left=merged_left, right=(schema_dict['BC_OFFERING_INST']), 
                                        how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='OWNER_ID_BC_OFFERING_INST')
    merged_left.drop(['OWNER_ID_BC_OFFERING_INST'], axis = 1, inplace = True)

    # merged_left and CM_ACCT_BALANCE
    merged_left = pd.merge(left=merged_left, right=(schema_dict['CM_ACCT_BALANCE']), 
                                        how='left', left_on='DFT_ACCT_ID_BC_SUB_DFT_ACCT', right_on='ACCT_ID_CM_ACCT_BALANCE')
    merged_left.drop(['ACCT_ID_CM_ACCT_BALANCE'], axis = 1, inplace = True)

    # merged_left and PE_ACCM
    merged_left = pd.merge(left=merged_left, right=(schema_dict['PE_ACCM']), 
                                   how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='ACCM_OWNER_ID_PE_ACCM')
    merged_left.drop(['ACCM_OWNER_ID_PE_ACCM'], axis = 1, inplace = True)

    # merged_left and BC_G_MEMBER
    merged_left = pd.merge(left=merged_left, right=(schema_dict['BC_G_MEMBER']), 
                                    how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='SUB_ID_BC_G_MEMBER')
    merged_left.drop(['SUB_ID_BC_G_MEMBER'], axis = 1, inplace = True)
    
    return merged_left


# In[13]:


def read_write_CBP(target_folders,df_temp_offering):
    if os.listdir(target_folders):
        head, tail = os.path.split(target_folders)
        print('reading ',tail)
        schema_dict = initialize_schema_dict()
        print('schema dict initalized')
        for key in schema_dict.keys():
            schema_dict[key] = read_data(target_folders,schema_dict[key][0], schema_dict[key][1], schema_dict[key][2])  
        print('reading cbp in schema dict complete')
            
        # Editing tables
        print('Editing tables in ', tail)
        merged_left = edit_join_tables(schema_dict)
            
        # merged_left and E_TEMP_OFFERING
        merged_left = pd.merge(left=merged_left, right=df_temp_offering, 
                                   how='left',left_on='SUB_ID_BC_SUB_IDEN', right_on='SUBSCRIBER_ID_E_TEMP_OFFERING')
        merged_left.drop(['SUBSCRIBER_ID_E_TEMP_OFFERING'], axis = 1, inplace = True)
            
        print('Editing Done in ', tail)

        # Writing to csv
        print('Wrting {} to ouptut CSV'.format(tail))
        output_file = output_dir + '/subsfile_' + tail + '.txt'
        merged_left.to_csv(output_file, index=False, header=True)
        print('Writing of {} is complete'.format(tail))
        # print(type(merged_left))
        # print(merged_left.head(1))
        # return merged_left


# In[17]:


if __name__ == "__main__":
    
    # Getting all target CBP directories path
    print('Scanning all CBP directories')
    target_folders_all = read_target_folders_all()
    # print('CBP directories are:')
    # print(target_folders_all)
    
    # Getting all target e_temp_offering files path
    print('Scanning all E_temp_offering table files')
    target_files_all = read_E_temp_offering_tables_path()
    # print('CBP directories are:')
    # print(target_files_all)
    
    # Reading E_temp_offering files
    print('reading e_temp_offering files')
    df_temp_offering = read_E_temp_offering_tables()
    print('reading of e_temp_offering files is complete')
    # print('shape of df_temp_offering is ', df_temp_offering.shape)
    
    # Start reading CBP by CBP
    
    pool = ProcessPoolExecutor(max_workers=5)
    list1 = []
    for target_folders in target_folders_all:
        head, tail = os.path.split(target_folders)  
        # read_write_CBP(target_folders,df_temp_offering)
#         print('head and tail of each target folders')
#         print(head)
#         print(tail)

        try:
            list1.append(pool.submit(read_write_CBP, target_folders,df_temp_offering))
        except Exception as e:
            print(f'ERROR :: {e}')
    
    for futures in as_completed(list1):
        print(f'completed multi processor instance {list1.index(futures) + 1}')

    # merged_left = read_write_CBP(target_folders)
    
    print('Script Executed Succesfully')
    print(f'Total execution time :: {(datetime.datetime.now() - START_TIME).seconds} seconds')


# In[ ]:
