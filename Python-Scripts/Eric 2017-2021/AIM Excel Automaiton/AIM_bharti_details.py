import pandas as pd
import utils
import re
import numpy as np
from datetime import timedelta, datetime, time
import os
import sys
import pyxlsb, openpyxl


def main():
    configs = utils.Config().config
    logger = utils.Logger(configs['log_file_path']).main()

    logger.info('#'*10 + 'Building TT_details for date: {}'.format(configs['date']) + '#'*10)

    try:
        df_node_list = pd.read_excel(configs['node_list_Path'],
                                     sheet_name=configs['node_sheet_name'],
                                     engine='openpyxl')
        node_list = list(df_node_list[configs['node_column_name']])
        logger.info('Successfully read the node file: {}'.format(configs['node_list_Path']))
    except Exception as e:
        logger.error('Faied to read the node file: {}'.format(configs['node_list_Path']))
        logger.error('Exiting the process due to node file error: {}'.format(e))
        sys.exit(1)


    # #### Incident df
    # No need to read in this script
    '''
    try:
        df_incident = pd.read_excel(os.path.join(os.getcwd(), configs['incident_sheet_path']),
                                    sheet_name=configs['incident_sheet_name'],
                                    engine='openpyxl')
        logger.info('Successfully read the incident file: {}'.format(configs['incident_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the incident file: {}'.format(configs['incident_sheet_path']))
        logger.error('Exiting the process due to incident file error: {}'.format(e))
        sys.exit(1)
    '''

    # #### Events df

    try:
        df_event = pd.read_excel(os.path.join(os.getcwd(), configs['event_sheet_path']),
                                 sheet_name=configs['event_sheet_name'],
                                 engine='openpyxl')
        logger.info('Successfully read the event file: {}'.format(configs['event_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the event file: {}'.format(configs['event_sheet_path']))
        logger.error('Exiting the process due to event file error: {}'.format(e))
        sys.exit(1)


    # #### TT dump df

    try:
        if re.search(r'xlsx+', configs['TTdump_sheet_path']) is not None:
            df_TTdump = pd.read_excel(os.path.join(os.getcwd(), configs['TTdump_sheet_path']),
                                      sheet_name=configs['TTdump_sheet_name'],
                                      engine='openpyxl')

        elif re.search(r'xlsb+', configs['TTdump_sheet_path']) is not None:
            df_TTdump = pd.read_excel(os.path.join(os.getcwd(), configs['TTdump_sheet_path']),
                                      sheet_name=configs['TTdump_sheet_name'],
                                      engine='pyxlsb')

        df_TTdump_copy = df_TTdump.copy()
        logger.info('Successfully read the dump file: {}'.format(configs['TTdump_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the dump file: {}'.format(configs['TTdump_sheet_path']))
        logger.error('Exiting the process due to dump file error: {}'.format(e))
        sys.exit(1)

    try:
        df_TTdumpTime = pd.read_excel(os.path.join(os.getcwd(), configs['TTdumpTime_sheet_path']),
                                      parse_dates=[1],
                                     engine='openpyxl')
        logger.info('Successfully read the dump time file: {}'.format(configs['TTdumpTime_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the dump time file: {}'.format(configs['TTdumpTime_sheet_path']))
        logger.error('Exiting the process due to dump time file error: {}'.format(e))
        sys.exit(1)

    try:
        df_TTdump_copy.drop(columns=['Ttcreationtime', 'Ttclosuretime'], axis = 1, inplace = True)
        df_TTdump_copy = pd.concat([df_TTdump_copy, df_TTdumpTime], axis=1)
        logger.info("Successfully combined the date time formatted columns to dump dataframe")


        # Converting the old time to CET time
        df_TTdump_copy['Ttcreationtime'] = df_TTdump_copy.apply(lambda row: utils.convert_timezone(row['Ttcreationtime'], int(configs['time_zone_diff'])), axis=1)
        logger.info('Converted the CET timezone to IST for column Ttcreationtime')


        # #### drop rows having blank 'Associate Trouble Ticket ID' in df_TTdump

        df_TTdump_copy['Associate Trouble Ticket ID'].replace(' ', np.NaN, regex=True, inplace=True)
        df_TTdump_copy.dropna(inplace=True)
        logger.info('Dropped the rows having empty TT ID values')

        # #### remove rows where Circle not equal to 'Rajasthan'

        df_TTdump_copy = df_TTdump_copy[df_TTdump_copy['Circle'].isin(configs['circle_val'].split(','))]
        logger.info('Applied the filter to Circle column in TT_dump')


        # #### # remove rows where Network Element Type - Alarm is neither 'LTE eNode B Indoor' nor 'SDO-4G'

        df_TTdump_copy = df_TTdump_copy[df_TTdump_copy['Network Element Type - Alarm'].isin(configs['network_element_type'].split(','))]
        logger.info('Applied the filter to Network Element Type - Alarm column in TT_dump')

        # #### clear the node_names starting with 'e_' or 'RJ_E'

        df_TTdump_copy['Network Element Name - Alarm'] = df_TTdump_copy.apply(lambda row: utils.clearNodes(row['Network Element Name - Alarm'], node_list), axis=1)
        logger.info('Removed the prefix/suffix from Network Element Name - Alarm column in TT_dump')

        # #### drop rows where node name is empty
        df_TTdump_copy.dropna(inplace=True)

        # #### drop rows which have same values of 'Associate Trouble Ticket ID', 'Network Element Name - Alarm'


        df_TTdump_copy = df_TTdump_copy.groupby(by=['Associate Trouble Ticket ID', 'Network Element Name - Alarm'], as_index=False).agg({'Specific Problem': ', '.join,
                                                                                                  'Site - Alarm': 'first',
                                                                                                  'Network Element Type - Alarm': 'first',
                                                                                                  'Ttcreationtime': 'first',
                                                                                                  'Ttclosuretime': 'first'})

        logger.info('Applied groupby on basis of TT_ID and Network Element Name - Alarm column in TT_dump')
        # In[56]:


        df_TTdump_copy['Specific Problem'] = df_TTdump_copy.apply(lambda row: utils.remove_duplicate(row['Specific Problem']), axis=1)
        logger.info('Applied remove_duplicates function on Specific Problem column')


        # #### if 'Ttclosuretime' has 1970 as year, set status as 'Open' else 'Close'

        df_TTdump_copy['Status'] = df_TTdump_copy.apply(lambda row: utils.check_status(row['Ttclosuretime']), axis=1)
        logger.info('Created a new column named Status')

        df_TTdump_copy.sort_values(by=['Network Element Name - Alarm'])


        # group events sheet by node names
        df_event_copy = df_event.copy()
        df_event = df_event.groupby('Node')

        date_time_current = datetime.strptime(configs['date'], '%Y-%m-%d')

        logger.info('Starting the processing of rows remaining in TT_dump one by one and create Valid? column')
        for i in range(df_TTdump_copy.index.size):

            # Creating time from TT dump
            time_dump_high = df_TTdump_copy.iloc[i]['Ttcreationtime']
            # Node name
            nodes_dump = df_TTdump_copy.iloc[i]['Network Element Name - Alarm']
            # TT id
            tt_id = df_TTdump_copy.iloc[i]['Associate Trouble Ticket ID']

            # incident df node list
            interesting_node_list = []

            # check each node in tt_details in incident df
            for key in df_event.groups.keys():
                if re.search('{}+'.format(nodes_dump), key):
                    interesting_node_list.append(key)

            # Check time limit
            time_dump_low = time_dump_high - timedelta(minutes=int(configs['time_diff']))
            time_dump_high_date = time_dump_high.day
            time_dump_low_date = time_dump_low.day
            time_dump_high = time_dump_high.time()
            time_dump_low = time_dump_low.time()

            is_scope = 0

            #     print(nodes_dump)
            #     print(interesting_node_list)

            # Check if any incident is generated between high and low
            while len(interesting_node_list) > 0:
                node_val = interesting_node_list.pop()
                time_list_incident = list(df_event.get_group(node_val)['Creation Time'])
                date_list_incident = list(df_event.get_group(node_val)['Creation Date'])

                # Compare Date time
                for j in range(len(time_list_incident)):
                    time_incident = (datetime.strptime(time_list_incident[j], '%H:%M:%S')).time()
                    time_incident_date = date_list_incident[j].day

                    # Check datetime. does handle date change
                    if time_incident_date == time_dump_high_date:
                        if time_incident_date != time_dump_low_date:
                            time_dump_low = time(0, 0, 0)
                        if time_dump_low <= time_incident <= time_dump_high:
                            is_scope = 1

                    elif time_incident_date != time_dump_high_date:
                        if time_incident_date == time_dump_low_date:
                            time_dump_high = time(23, 59, 59)
                            if time_dump_low <= time_incident <= time_dump_high:
                                is_scope = 1

            if is_scope == 1:
                df_TTdump_copy.at[i, 'Valid?'] = 'Yes'
            else:
                df_TTdump_copy.at[i, 'Valid?'] = 'Out of Scope'
        logger.info('Process for creating Valid? column finished successfully')

        logger.info('Removing all the rows where Ttcreationtime does not correspond with current date')
        df_TTdump_copy = df_TTdump_copy[df_TTdump_copy['Ttcreationtime'].dt.day == date_time_current.day]
    except Exception as e:
        logger.info('Exiting the process due to error: {}'.format(e))
        sys.exit(1)


    try:
        df_TTdump_copy.to_excel(os.path.join(os.getcwd(), configs['details_sheet_path']), index=False)
        logger.info('Successfully dumped TT_details to an excel file')
        logger.info('#'*10 + 'Process for creating TT_details finished' + '#'*10)

    except Exception as e:
        logger.error('Unable to write TT_details to a file')
        logger.error('Exiting the process due to error: {}'.format(e))
        sys.exit(1)

    # If no record found then exit the process
    if df_TTdump_copy.shape[0] == 0:
        logger.error('TT_details file generated was empty\nExiting the process\n\n')
        sys.exit(1)
    '''
    try:
        frames = {'NE for AIM Analysis': df_node_list,
                  'Incidents': df_incident,
                  'Events': df_event_copy,
                  'TT_DUMP_{}'.format(configs['date']): df_TTdump}

        logger.info('#'*10 + 'Writing to excel: {}'.format(configs['output_excel_path']) + '#'*10)

        writer = pd.ExcelWriter('{}'.format(configs['output_excel_path']), engine='xlsxwriter')

        for sheet, frame in frames.items():
            frame.to_excel(writer, sheet_name=sheet)
            logger.info('Written the sheet: {} to excel'.format(sheet))
        writer.save()

        logger.info('Successfully written all sheets to excel')
        logger.info('#'*10 + 'Process for creating Bharti_AIM finished successfully' + '#'*10)
    except Exception as e:
        logger.error('Writing to excel failed')
        logger.error('Exiting the process due to Error: {}'.format(e))
        sys.exit(1)
    '''

if __name__ == "__main__":
    main()