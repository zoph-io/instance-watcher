#!/usr/bin/python3
# -*- coding: utf-8 -*-

def speak(SlackWebHook, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift):
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
        slack.post(text="""""".join([f"\n • RDS: {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']}" for r in running_rds]) + """""")
    if len(running_glue) > 0:
        slack.post(text="""""".join([f"\n • Glue: {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']}" for r in running_glue]) + """""")
    if len(running_sage) > 0:
        slack.post(text="""""".join([f"\n • SageMaker: {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']}" for r in running_sage]) + """""")
    if len(running_redshift) > 0:
        slack.post(text="""""".join([f"\n • Redshift: {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']}" for r in running_redshift]) + """""")