import pandas as pd
import numpy as np
import xlsxwriter, openpyxl

import utils
import re
import os
from datetime import timedelta, time, datetime
import sys


def main():
    configs = utils.Config().config

    logger = utils.Logger(configs['log_file_path']).main()

    logger.info('#' * 10 + 'Building Complete AIM file for date: {}'.format(configs['date']) + '#' * 10)

    '''
    try:
        df_node_list = pd.read_excel(configs['node_list_Path'],
                                     sheet_name=configs['node_sheet_name'],
                                     engine='openpyxl')
        logger.info('Successfully read the node file: {}'.format(configs['node_list_Path']))
    except Exception as e:
        logger.error('Faied to read the node file: {}'.format(configs['node_list_Path']))
        logger.error('Exiting the process due to node file error: {}'.format(e))
        sys.exit(1)
    '''
    '''
    try:
        if re.search(r'xlsx+', configs['TTdump_sheet_path']) is not None:
            df_TTdump = pd.read_excel(os.path.join(os.getcwd(), configs['TTdump_sheet_path']),
                                      sheet_name=configs['TTdump_sheet_name'],
                                      engine='openpyxl')

        elif re.search(r'xlsb+', configs['TTdump_sheet_path']) is not None:
            df_TTdump = pd.read_excel(os.path.join(os.getcwd(), configs['TTdump_sheet_path']),
                                      sheet_name=configs['TTdump_sheet_name'],
                                      engine='pyxlsb')

        logger.info('Successfully read the dump file: {}'.format(configs['TTdump_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the dump file: {}'.format(configs['TTdump_sheet_path']))
        logger.error('Exiting the process due to dump file error: {}'.format(e))
        sys.exit(1)
    '''

    try:
        tt_details = pd.read_excel(configs['details_sheet_path'],
                                   sheet_name=configs['details_sheet_name'],
                                   engine='openpyxl')
        details_headers = ['TT ID', 'ENB', 'SITE', 'Unit type', 'TT Creation Time IST', 'TT Symptom Description',
                           'Created By', 'Status', 'Resolved date & time', 'Valid?']
        tt_details.rename(columns={'Associate Trouble Ticket ID': 'TT ID', 'Network Element Name - Alarm': 'ENB',
                                   'Site - Alarm': 'SITE', 'Network Element Type - Alarm': 'Unit type',
                                   'Ttcreationtime': 'TT Creation Time IST', 'Ttclosuretime': 'Resolved date & time',
                                   'Specific Problem': 'TT Symptom Description', }, inplace=True)
        tt_details['Created By'] = ''
        tt_details = tt_details[details_headers]
        logger.info('Successfully read the details file: {}'.format(configs['details_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the details file: {}'.format(configs['details_sheet_path']))
        logger.error('Exiting the process due to details file error: {}'.format(e))
        sys.exit(1)

    tt_details_new = tt_details[tt_details['Valid?'] == 'Yes']
    logger.info('Read all those entries from [TT_details] where [Valid?] == [Yes]')

    try:
        df_incident = pd.read_excel(os.path.join(os.getcwd(), configs['incident_sheet_path']),
                                    sheet_name=configs['incident_sheet_name'],
                                    engine='openpyxl')
        logger.info('Successfully read the incident file: {}'.format(configs['incident_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the incident file: {}'.format(configs['incident_sheet_path']))
        logger.error('Exiting the process due to incident file error: {}'.format(e))
        sys.exit(1)

    try:
        df_event = pd.read_excel(os.path.join(os.getcwd(), configs['event_sheet_path']),
                                 sheet_name=configs['event_sheet_name'],
                                 engine='openpyxl')
        logger.info('Successfully read the events file: {}'.format(configs['event_sheet_path']))
    except Exception as e:
        logger.error('Faied to read the events file: {}'.format(configs['event_sheet_path']))
        logger.error('Exiting the process due to events file error: {}'.format(e))
        sys.exit(1)
    # tt_details_new.to_excel('C:/Users/eyugpua/Desktop/output/test_config1_details_new.xlsx')

    # ## Incident and TT sheet 5th sheet

    # In[63]:

    try:
        incident_and_tt = df_incident.iloc[:, :9].copy()
        incident_and_tt = pd.concat([incident_and_tt, df_incident.iloc[:, -1]], axis=1)

        incidents_dict = {}

        # ## Analysis Sheet

        analysis = pd.DataFrame()


        # ## Logic


        # iterate over all the TTid values of dump and look if any incident was created
        # for the node and given ttid within last 2 hours

        # Dump sheet and Incident sheet
        match_list = []
        # create a copy of event sheet
        # group event sheet by node names
        df_event_copy = df_event.copy()
        df_event = df_event.groupby('Node')

        logger.info('Starting the processing of all [TT_details] entries where [Valid?] == [Yes] and sheet [analysis]')
        for i in range(tt_details_new.index.size):

            # Creation time from TT dump
            time_dump_high = tt_details_new.iloc[i]['TT Creation Time IST']
            # Node name
            nodes_dump = tt_details_new.iloc[i]['ENB']
            # TT id
            tt_id = tt_details_new.iloc[i]['TT ID']

            # logger.info('Processing record:\n TT ID: {}\n Node Name: {}\n Creation time: {}'.format(tt_id, nodes_dump, time_dump_high))

            interesting_incident_list = set()

            # incident df node list
            interesting_node_list = []
            analysis = analysis.append(tt_details_new.iloc[i])

            if incidents_dict.get(tt_id) is None:
                incidents_dict[tt_id] = set()

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

            # Check if any incident is generated between high and low
            while len(interesting_node_list) > 0:
                node_val = interesting_node_list.pop()
                time_list_incident = list(df_event.get_group(node_val)['Creation Time'])
                date_list_incident = list(df_event.get_group(node_val)['Creation Date'])
                incident_list = list(df_event.get_group(node_val)['Incident'])

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
                            match_list.append({'TT ID': '{}'.format(tt_id), 'AIM INCIDENTS': '{}'.format(incident_list[j])})
                            # print(tt_id, incident_list[j])
                            incidents_dict[tt_id].add(incident_list[j])
                            interesting_incident_list.add(incident_list[j])

                    elif time_incident_date != time_dump_high_date:
                        if time_incident_date == time_dump_low_date:
                            time_dump_high = time(23, 59, 59)
                            if time_dump_low <= time_incident <= time_dump_high:
                                is_scope = 1
                                match_list.append({'TT ID': '{}'.format(tt_id), 'AIM INCIDENTS': '{}'.format(incident_list[j])})
                                incidents_dict[tt_id].add(incident_list[j])
                                interesting_incident_list.add(incident_list[j])
                if is_scope == 0:
                    logger.info('Following [Valid?] entry was manually changed to [Yes]')
                    logger.info('Listing all the available incidents')
                    for incidents in incident_list:
                        logger.info('Incidents: {}'.format(incidents))
                        interesting_incident_list.add(incidents)
                        incidents_dict[tt_id].add(incidents)
                        match_list.append({'TT ID': '{}'.format(tt_id), 'AIM INCIDENTS': '{}'.format(incidents)})

                # Add Match/Multi Match rows on the basis of incidents available for a particular tt id
                if len(interesting_incident_list) > 1:
                    analysis = analysis.append({'TTMatch': 'MultiMatch'}, ignore_index=True)
                    analysis = analysis.append({'Conclusion': 'AIM matches with the TT.'
                                                                 ' Additionally there are other incidents'
                                                                 ' recorded by AIM for similar problem. '
                                                                 'TT might not have been generated as the actual problem'},ignore_index=True)
                else:
                    analysis = analysis.append({'TTMatch': 'Match'}, ignore_index=True)
                    analysis = analysis.append({'Conclusion': 'AIM matches with the TT'}, ignore_index=True)

                # Append all the valid events corresponding to incident and node name to analysis sheet
                analysis = analysis.append(df_event.get_group(node_val).iloc[:, :8][df_event.get_group(node_val)['Incident'].isin(interesting_incident_list)])
        analysis.drop(columns=['Created By'], inplace=True)
        tt_details.reset_index(drop=True, inplace=True)
        logger.info('Processing of all [TT_details] entries where [Valid?] == [Yes] and sheet [analysis] completed successfully')
    except Exception as e:
        logger.error('Failed to complete execution for sheet [TT_details] and [analysis]')
        logger.error('Error:{}'.format(e))
        logger.error('Exiting the process')
        sys.exit(1)
        # # Final Excels

        # ### Sumamry sheet 2nd sheet

    try:
        logger.info('Starting final processing for sheet: [summary]')
        summary = tt_details[['TT ID', 'Valid?']]
        summary['Counts'] = summary.groupby(['Valid?'])['TT ID'].transform('count')
        summary = summary.groupby(['Valid?', 'Counts']).apply(lambda x: x.sort_values('TT ID'))
        valid_value_counts = summary['Valid?'].value_counts()
        summary.drop(columns=['Valid?', 'Counts'], axis=1, inplace=True)
        logger.info('Final processing for sheet: [summary] completed')
    except Exception as e:
        logger.error('Failed to complete execution for sheet summary')
        logger.error('Error:{}'.format(e))


        # ### Match analysis - 3rd sheet
    try:
        logger.info('Starting final processing for sheet: [match]')
        match_list = list(map(dict, set(tuple(sorted(matches.items())) for matches in match_list)))
        match = pd.DataFrame(match_list, columns=['TT ID', 'AIM INCIDENTS'])
        match['TTMatch'] = match.groupby(['TT ID'])['AIM INCIDENTS'].transform('count')
        match['TTMatch'] = match['TTMatch'].astype(str)

        for ind in match.index.values:
            match.at[ind, 'TTMatch'] = 'MultiMatch' if int(match.iloc[ind]['TTMatch']) > 1 else 'Match'

        match = match.groupby(['TT ID', 'TTMatch']).apply(lambda x: x.sort_values('AIM INCIDENTS'))
        match.drop(columns=['TT ID', 'TTMatch'], axis=1, inplace=True)
        logger.info('Final processing for sheet: [match] completed')
    except Exception as e:
        logger.error('Failed to complete execution for sheet: [match]')
        logger.error('Error:{}'.format(e))


        # ### Incident and TT 5th sheet
    try:
        logger.info('Starting final processing for sheet: [incident_and_tt]')
        incident_and_tt['Ttmatch'] = incident_and_tt.apply(lambda row: utils.match_tt(row['Incident'], incidents_dict), axis=1)
        logger.info('Final processing for sheet: [incident_and_tt] completed')
    except Exception as e:
        logger.error('Failed to complete execution for sheet: [incident_and_tt]')
        logger.error('Error:{}'.format(e))


        # ### Top AIM Incidents and TT 7th sheet
    try:
        logger.info('Starting final processing for sheet: [Top AIM Incidents and TT]')
        df_topAim_incidentsandTt = incident_and_tt.copy()
        df_topAim_incidentsandTt = df_topAim_incidentsandTt[pd.isnull(df_topAim_incidentsandTt['Ttmatch'])]

        df_topAim_incidentsandTt = df_topAim_incidentsandTt[df_topAim_incidentsandTt['Source'].isin(configs['source_filter_1'].split(','))]
        df_topAim_incidentsandTt.sort_values(by=['Priority Sc'], ascending=False, inplace=True)
        df_topAim_incidentsandTt = df_topAim_incidentsandTt.head(3)
        top_incidents = pd.Series(df_topAim_incidentsandTt['Incident'])
        df_event_copy.rename(columns={'Incident': 'Incidents', 'Creation Date': 'Creation Dates', 'Creation Time': 'Creation Times'}, inplace=True)
        df_topAim_incidentsandTt = df_topAim_incidentsandTt.append(df_event_copy[df_event_copy['Incidents'].isin(top_incidents)].iloc[:, :8])
        df_topAim_incidentsandTt = df_topAim_incidentsandTt.append(incident_and_tt[incident_and_tt['Source'].isin(configs['source_filter_1'].split(','))].sort_values(by=['Priority Sc'], ascending=False).head(50))
        df_topAim_incidentsandTt = df_topAim_incidentsandTt.append(incident_and_tt[incident_and_tt['Source'].isin(configs['source_filter_2'].split(','))].sort_values(by=['Priority Sc'], ascending=False).head(3))
        logger.info('Final processing for sheet: [Top AIM Incidents and TT] completed')
    except Exception as e:
        logger.error('Failed to complete execution for sheet: [Top AIM Incidents and TT]')
        logger.error('Error:{}'.format(e))


    # 7th sheet AIM Incident & Event
    try:
        logger.info('Starting final processing for sheet: [AIM Incident & Event]')
        df_AimIncident_and_Event = df_event_copy.groupby(['Name']).agg({'Incidents': pd.Series.nunique,
                                                                        'Event': 'count'})
        logger.info('Final processing for sheet: [AIM Incident & Event] completed')
    except Exception as e:
        logger.error('Failed to complete execution for sheet: [AIM Incident & Event]')
        logger.error('Error:{}'.format(e))


    # Process for doing calculations of  result sheet
    logger.info('#'*10 + 'Starting processing for sheet: [Result]' + '#'*10)
    result_dict = {}

    try:
        param = 'overall_result'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        result_dict[param]['AIM_false_positive'] = incident_and_tt.shape[0]
        result_dict[param]['AIM_true_positive'] = incident_and_tt['Ttmatch'].count()
        result_dict[param]['BHARTI_out_of_scope'] = valid_value_counts['Out of Scope']
        result_dict[param]['BHARTI_true_positive'] = valid_value_counts['Yes']
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'exclude_list_on'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Source'].isin(configs['result_source_filter'].split(','))]
        test_incident = test_incident[test_incident['Events'].isin(int(x) for x in configs['result_events_filter'].split(','))]
        if configs['result_exclusion_filter'] == 'FALSE':
            test_incident = test_incident[~test_incident.Exclusion]
        elif configs['result_exclusion_filter'] == 'TRUE':
            test_incident = test_incident[test_incident.Exclusion]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'priority >= 1'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Priority Sc'] >= float(configs['result_priority_filter'])]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'utilization_impact'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Source'].isin(configs['result_utilization_source_filter'].split(','))]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'priority >= 2'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Priority Sc'] >= float(configs['result_priority_filter_2'])]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'severity >= 0.5'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Severity Sc'] >= float(configs['result_severity_filter'])]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'severity >= 1'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Severity Sc'] >= float(configs['result_severity_filter_2'])]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))


    try:
        param = 'exclude_list_on + priority>=1'
        logger.info('Started processing for section: [{}]'.format(param))
        result_dict[param] = {}
        test_incident = incident_and_tt.copy()
        test_incident = test_incident[test_incident['Source'].isin(configs['result_source_filter_exclude&priority'].split(','))]
        test_incident = test_incident[test_incident['Events'].isin(int(x) for x in configs['result_events_filter_exclude&priority'].split(','))]
        if configs['result_exclusion_filter_exclude&priority'] == 'FALSE':
            test_incident = test_incident[~test_incident.Exclusion]
        elif configs['result_exclusion_filter_exclude&priority'] == 'TRUE':
            test_incident = test_incident[test_incident.Exclusion]
        test_incident = test_incident[test_incident['Priority Sc'] >= float(configs['result_priority_filter_exclude&priority'])]
        result_dict = utils.update_result_dict(result_dict, param, test_incident, valid_value_counts)
        logger.info('Finished processing for section: [{}]'.format(param))
    except Exception as e:
        logger.error('Failed to complete processing of section: [{}]'.format(param))
        logger.error('Error: {}'.format(e))

    logger.info('#' * 10 + 'Finished processing for sheet: [Result]' + '#' * 10)
    df_result = pd.DataFrame.from_dict(result_dict, orient='index')

    try:

        frames = {'TT_Details': tt_details,
                 'TT_Summary': summary,
                 'TT_Matching': match,
                 'TT_Analysis': analysis,
                 'Incident and TT': incident_and_tt,
                 'Top AIM Incidents and TT': df_topAim_incidentsandTt,
                 'AIM Incident & Event': df_AimIncident_and_Event,
                  'Result': df_result}
        sheets_drop_index = ['TT_Details', 'TT_Analysis', 'Incident and TT', 'Top AIM Incidents and TT']

        logger.info('#'*10 + 'Writing to excel: {}'.format(configs['output_excel_path']) + '#'*10)

        writer = pd.ExcelWriter('{}'.format(os.path.join(os.getcwd(), configs['output_excel_path'])), engine='xlsxwriter')

        for sheet, frame in frames.items():
            if sheet not in sheets_drop_index:
                frame.to_excel(writer, sheet_name=sheet)
            else:
                frame.to_excel(writer, sheet_name=sheet, index=False)
            logger.info('Written the sheet: {} to excel'.format(sheet))
        writer.save()

        logger.info('Successfully written all sheets to excel')
        logger.info('#'*10 + 'Process for creating Bharti_AIM finished successfully' + '#'*10)
    except Exception as e:
        logger.error('Writing to excel failed')
        logger.error('Exiting the process due to Error: {}'.format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

