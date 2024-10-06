import sys
import os

import AIM_bharti_details
import AIM_bharti_match
import utils


if __name__ == "__main__":
    configs = utils.Config().config
    logger = utils.Logger(configs['log_file_path']).main()
    logger.info('\n\n'+'#'*30 + 'Bharti Executor process started' + '#'*30)

    try:
        logger.info('\n'+'#'*20 + 'Starting execution of AIM_bharti_details' + '#'*20)
        AIM_bharti_details.main()
        logger.info('#'*20 + 'Finished execution of AIM_bharti_details' + '#'*20+'\n\n')
    except Exception as e:
        logger.error('Failed to execute AIM_bharti_details')
        logger.error('Error: {}'.format(e))
        logger.error('#' * 20 + 'Failed execution of AIM_bharti_details' + '#' * 20)
        sys.exit(1)

    try:
        logger.info('#'*20 + 'Starting execution of AIM_bharti_match' + '#'*20)
        AIM_bharti_match.main()
        logger.info('#'*20 + 'Finished execution of AIM_bharti_match' + '#'*20 + '\n\n')
    except Exception as e:
        logger.error('Failed to execute AIM_bharti_match')
        logger.error('Error: {}'.format(e))
        logger.error('#' * 20 + 'Failed execution of AIM_bharti_match' + '#' * 20)
        sys.exit(1)

    # remove the details excel sheet as it is not needed
    try:
        logger.info('Removing the excel: [{}]'.format(configs['details_sheet_path']))
        os.remove(os.path.join(os.getcwd(), configs['details_sheet_path']))
        logger.info('Successfully removed the excel: [{}]'.format(configs['details_sheet_path']))
    except Exception as e:
        logger.error('Error: {}'.format(e))
        logger.error('#' * 20 + 'Failed to remove excel file: [{}]'.format(configs['details_sheet_path'])
                     + '#' * 20)

    logger.info('\n'+'#'*30 + 'Bharti Executor process completed successfully' + '#'*30 + '\n\n\n')
