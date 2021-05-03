#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
import os
import logging
from datetime import datetime, timedelta
import calendar
from slack_webhook import Slack
import pymsteams

# Import Python files

## AWS Services
exec(open("./services/ec2.py").read())
exec(open("./services/rds.py").read())
exec(open("./services/glue.py").read())
exec(open("./services/sagemaker.py").read())
exec(open("./services/redshift.py").read())

## Utils
exec(open("./utils/slack.py").read())
exec(open("./utils/teams.py").read())
exec(open("./utils/mailer.py").read())
exec(open("./utils/spend.py").read())

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

# Catch Parameters (using environment variables)
aws_region = os.environ['AWSRegion']
whitelist_tag = os.environ['WhitelistTag']


# Notifications
enable_mail = int(os.environ['EnableMail'])
## Slack
enable_slack = int(os.environ['EnableSlack'])
slack_webhook = os.environ['SlackWebHook']
## Teams
enable_teams = int(os.environ['EnableTeams'])
teams_webhook = os.environ['TeamsWebHook']
# Other
environment = os.environ['Environment']


session = boto3.Session(region_name=aws_region)
ec2r = session.client('ec2')
ses = session.client('ses')
sts = session.client('sts')

# Email Settings
recipients = os.environ['Recipients'].split()
subject = '[AWS] Instance Watcher 👀 - '
sender = "Instance Watcher <" + os.environ['Sender'] + ">"
charset = "UTF-8"


def main(event, context):
    account = sts.get_caller_identity().get('Account')
    alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]
    spend = spending()
    if environment == "sandbox":
        ec2_regions = ["eu-west-1"] # Reduce to only one region, for faster troubleshooting
    else:
        ec2_regions = [region['RegionName'] for region in ec2r.describe_regions()['Regions']]

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
        custom_tags_dict = running_ec2[1]

        if custom_tags_dict == []:
            custom_tags_dict = "No Custom tag"

        logging.debug("Checking RDS")
        running_rds = rds(region, running_rds, whitelist_tag)
        logging.debug("Checking Glue")
        running_glue = glue(region, running_glue, whitelist_tag, account)
        logging.debug("Checking SageMaker")
        if region == "ap-northeast-3":
            pass
        else:
            running_sage = sagemaker(region, running_sage, whitelist_tag)
        logging.debug("Checking Redshift")
        running_redshift = redshift(region, running_redshift, whitelist_tag)
        logging.info("End: Done for: %s", region)


    # Exec Summary (logging)
    logging.info("===== Summary =====")
    logging.info("Current MTD Spend (USD): %s", spend[0])
    logging.info("Forecast (Month) Spend (USD): %s", spend[1])
    logging.info("Total number of running EC2 instance(s): %s", len(running_ec2[0]))
    logging.info("Total number of running RDS instance(s): %s", len(running_rds))
    logging.info("Total number of running Glue Dev Endpoint(s): %s", len(running_glue))
    logging.info("Total number of running SageMaker Notebook instance(s): %s", len(running_sage))
    logging.info("Total number of running Redshift Cluster(s): %s", len(running_redshift))

    # Email Integration
    if enable_mail == 1:
        mailer(region, alias, account, spend, running_ec2, custom_tags_dict, running_rds, running_glue, running_sage, running_redshift)
    else:
        logging.info("Email notification feature is disabled")

    # Slack & Teams Integrations
    if enable_slack == 1:
        logging.info("Posting Slack message")
        speak_slack(slack_webhook, alias, account, spend, running_ec2, custom_tags_dict, running_rds, running_glue, running_sage, running_redshift)
    else:
        logging.info("Slack feature is disabled")

    if enable_teams == 1:
        logging.info("Posting MS Teams message")
        speak_teams(teams_webhook, alias, account, spend, running_ec2, custom_tags_dict, running_rds, running_glue, running_sage, running_redshift)
    else:
        logging.info("Teams feature is disabled")


if __name__ == '__main__':
    main(0,0)

