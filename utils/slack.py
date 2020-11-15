#!/usr/bin/python3
# -*- coding: utf-8 -*-

def speak_slack(SlackWebHook, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift):
    try:
        slack = Slack(url=SlackWebHook)
        if len(running_ec2) == 0 and len(running_rds) == 0 and len(running_glue) == 0 and len(running_sage) == 0 and len(running_redshift) == 0:
            slack.post(text="""
                AWS Account: `""" + str(account) + """` - `""" + str(alias) + """`\n
                :money_with_wings: Current MTD Spend (`USD`): `""" + str(spend[0]) + """`\n
                :money_with_wings: Forecasted Monthly Spend (`USD`):  `""" + str(spend[1]) + """`\n
                :white_check_mark: No instance mistakenly left running \n""")
        else:
            slack.post(text="""
                AWS Account: `""" + str(account) + """` - `""" + str(alias) + """`\n
                :money_with_wings: Current MTD Spend (`USD`): `""" + str(spend[0]) + """`\n
                :money_with_wings: Forecasted Monthly Spend (`USD`):  `""" + str(spend[1]) + """`\n
                :arrow_right: EC2 instance(s): """ + str(len(running_ec2)) + """\n
                :arrow_right: RDS instance(s): """ + str(len(running_rds)) + """\n
                :arrow_right: Glue Dev Endpoint(s): """ + str(len(running_glue)) + """\n
                :arrow_right: SageMaker Notebook instance(s): """ + str(len(running_sage)) + """\n
                :arrow_right: Redshift Cluster(s): """ + str(len(running_redshift)) + """\n""")
        if len(running_ec2) > 0:
            slack.post(text="""""".join([f"\n • EC2: `{r['ec2_id']}`  `{r['ec2_type']}`  `{r['ec2_state']}`  `{r['region']}`  `{r['ec2_launch_time']}`  `{r['ec2_name']}`" for r in running_ec2]) + """""")
        if len(running_rds) > 0:
            slack.post(text="""""".join([f"\n • RDS: `{r['db_engine']}`  `{r['db_type']}`  `{r['db_storage']}`  `{r['region']}`  `{r['launch_time']}`  `{r['db_instance_name']}`" for r in running_rds]) + """""")
        if len(running_glue) > 0:
            slack.post(text="""""".join([f"\n • Glue: `{r['glue_status']}`  `{r['glue_numberofnodes']}`  `{r['region']}`  `{r['glue_createdtimestamp']}` `{r['glue_endpointname']}`" for r in running_glue]) + """""")
        if len(running_sage) > 0:
            slack.post(text="""""".join([f"\n • SageMaker: `{r['sage_notebookinstancestatus']}`  `{r['sage_instancetype']}`  `{r['region']}`  `{r['sage_creationtime']}`  `{r['sage_notebookinstancename']}`" for r in running_sage]) + """""")
        if len(running_redshift) > 0:
            slack.post(text="""""".join([f"\n • Redshift: `{r['rs_clusteridentifier']}`  `{r['rs_status']}`  `{r['rs_numberofnodes']}`  `{r['region']}`  `{r['rs_creation_time']}`" for r in running_redshift]) + """""")
    except Exception as e:
        logging.error("Failed posting to Slack: %s", e)