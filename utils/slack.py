#!/usr/bin/python3
# -*- coding: utf-8 -*-

def speak_slack(SlackWebHook, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift):
    try:
        slack = Slack(url=SlackWebHook)
        
        slack.post(text="""
            AWS Account: """ + str(account) + """ - """ + str(alias) + """\n
            :money_with_wings: Current Spend MTD (USD): """ + str(spend) + """\n
            :arrow_right: Total number of running EC2 instance(s): """ + str(len(running_ec2)) + """\n
            :arrow_right: Total number of running RDS instance(s): """ + str(len(running_rds)) + """\n
            :arrow_right: Total number of running Glue Dev Endpoint(s): """ + str(len(running_glue)) + """\n
            :arrow_right: Total number of running SageMaker Notebook instance(s): """ + str(len(running_sage)) + """\n
            :arrow_right: Total number of running Redshift Cluster(s): """ + str(len(running_redshift)) + """\n""")
        if len(running_ec2) > 0:
            slack.post(text="""""".join([f"\n • EC2: {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']}" for r in running_ec2]) + """""")
        if len(running_rds) > 0:
            slack.post(text="""""".join([f"\n • RDS: {r['db_instance_name']}  {r['db_engine']}  {r['db_type']}  {r['db_storage']}  {r['region']}  {r['launch_time']}" for r in running_rds]) + """""")
        if len(running_glue) > 0:
            slack.post(text="""""".join([f"\n • Glue: {r['glue_endpointname']}  {r['glue_status']}  {r['glue_numberofnodes']}  {r['region']}  {r['glue_createdtimestamp']}" for r in running_glue]) + """""")
        if len(running_sage) > 0:
            slack.post(text="""""".join([f"\n • SageMaker: {r['sage_notebookinstancename']}  {r['sage_notebookinstancestatus']}  {r['sage_instancetype']}  {r['region']}  {r['sage_creationtime']}" for r in running_sage]) + """""")
        if len(running_redshift) > 0:
            slack.post(text="""""".join([f"\n • Redshift: {r['rs_clusteridentifier']}  {r['rs_status']}  {r['rs_numberofnodes']}  {r['region']}  {r['rs_creation_time']}" for r in running_redshift]) + """""")
    except Exception as e:
        logging.error("Failed posting to Slack: ", e)