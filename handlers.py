#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
import os
import logging
from datetime import datetime, timedelta
from slack_webhook import Slack

# Import Python files

## AWS Services
exec(open("./services/ec2.py").read())
exec(open("./services/rds.py").read())
exec(open("./services/glue.py").read())
exec(open("./services/sagemaker.py").read())
exec(open("./services/redshift.py").read())

## Utils
exec(open("./utils/slack.py").read())
#exec(open("./utils/teams.py").read())
exec(open("./utils/mailer.py").read())
exec(open("./utils/spend.py").read())

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

# Catch Parameters (using environment variables)
aws_region = os.environ['AWSREGION']
whitelist_tag = os.environ['WHITELISTTAG']
EnableSlack = int(os.environ['EnableSlack'])
SlackWebHook = os.environ['SlackWebHook']
EnableTeams = int(os.environ['EnableTeams'])
TeamsWebHook = os.environ['TeamsWebHook']

session = boto3.Session(region_name=aws_region)
ec2r = session.client('ec2')
ses = session.client('ses')
sts = session.client('sts')

# Email Settings
recipients = os.environ['RECIPIENTS'].split()
subject = '[AWS] Instance Watcher 👀 - '
sender = "Instance Watcher <" + os.environ['SENDER'] + ">"
charset = "UTF-8"
mail_enabled = int(os.environ['ENABLEMAIL'])

def main(event, context):
    account = sts.get_caller_identity().get('Account')
    alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]
    spend = spending()
    #ec2_regions = [region['RegionName'] for region in ec2r.describe_regions()['Regions']]
    ec2_regions = ["eu-west-1"] # Troubleshooting only

    running_ec2 = []
    running_rds = []
    running_glue = []
    running_sage = []
    running_redshift = []

    # For all AWS Regions
    for region in ec2_regions:
        logging.info("Start: Checking running instances in: %s", region)
        logging.debug("Checking EC2")
        running_ec2 = ec2(region, running_ec2, whitelist_tag)
        logging.debug("Checking RDS")
        running_rds = rds(region, running_rds, whitelist_tag)
        logging.debug("Checking Glue")
        running_glue = glue(region, running_glue, whitelist_tag)
        logging.debug("Checking SageMaker")
        running_sage = sagemaker(region, running_sage, whitelist_tag)
        logging.debug("Checking Redshift")
        running_redshift = redshift(region, running_redshift, whitelist_tag)
        logging.info("End: Done for: %s", region)
    mailer(region, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift)


    # Exec Summary (logging)
    logging.info("===== Summary =====")
    logging.info("Current Spend (USD): %s", spend)
    logging.info("Total number of running EC2 instance(s): %s", len(running_ec2))
    #logging.info("Total number of hidden EC2 instance(s): %s", ec2_hidden_count)
    logging.info("Total number of running RDS instance(s): %s", len(running_rds))
    #logging.info("Total number of hidden RDS instance(s): %s", rds_hidden_count)
    logging.info("Total number of running Glue Dev Endpoint(s): %s", len(running_glue))
    #logging.info("Total number of hidden Glue Dev Endpoint(s): %s", glue_hidden_count)
    logging.info("Total number of running SageMaker Notebook instance(s): %s", len(running_sage))
    #logging.info("Total number of hidden SageMaker Notebook instance(s): %s", sage_hidden_count)
    logging.info("Total number of running Redshift Cluster(s): %s", len(running_redshift))
    #logging.info("Total number of hidden Redshift Cluster(s): %s", rs_hidden_count)
    if EnableSlack == 1:
        logging.info("Posting Slack message")
        speak(SlackWebHook, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift)
    else:
        logging.info("Slack is disabled")



if __name__ == '__main__':
    main(0,0)

