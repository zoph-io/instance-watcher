#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
import os
import logging
from datetime import datetime, timedelta

# Import Python files
exec(open("./services/ec2.py").read())
exec(open("./services/rds.py").read())
exec(open("./services/glue.py").read())
exec(open("./services/sagemaker.py").read())
exec(open("./services/redshift.py").read())
exec(open("./services/mailer.py").read())
exec(open("./services/spend.py").read())

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

aws_region = os.environ['AWSREGION']
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
    ec2_regions = [region['RegionName'] for region in ec2r.describe_regions()['Regions']]
    #ec2_regions = ["eu-west-1"] # Troubleshooting only

    running_ec2 = []
    running_rds = []
    running_glue = []
    running_sage = []
    running_redshift = []

    # For all AWS Regions
    for region in ec2_regions:
        logging.info("Checking running instances in: %s", region)
        running_ec2 = ec2(region, running_ec2)
        running_rds = rds(region, running_rds)
        running_glue = glue(region, running_glue)
        running_sage = sagemaker(region, running_sage)
        running_redshift = redshift(region, running_redshift)
    mailer(region, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift)


    # Exec Summary (logging)

    logging.info("===== Summary =====")
    logging.info("Current Spend (USD): %s", spend)
    logging.info("Total number of running EC2 instance(s): %s", len(running_ec2))
    #logging.info("Total number of hidden EC2 instance(s): %s", ec2_hidden_count)
    logging.info("Total number of running RDS instance(s): %s", len(running_rds))
    #logging.info("Total number of hidden RDS instance(s): %s", len(rds_hidden_count))
    logging.info("Total number of running Glue Dev Endpoint(s): %s", len(running_glue))
    #logging.info("Total number of hidden Glue Dev Endpoint(s): %s", ec2_hidden_count)
    logging.info("Total number of running SageMaker Notebook instance(s): %s", len(running_sage))
    #logging.info("Total number of hidden SageMaker Notebook instance(s): %s", ec2_hidden_count)
    logging.info("Total number of running Redshift Cluster(s): %s", len(running_redshift))
    #logging.info("Total number of hidden Redshift Cluster(s): %s", rs_hidden_count)

if __name__ == '__main__':
    main(0,0)

