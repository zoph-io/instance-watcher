
def speak_teams(teams_webhook, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift):
    try:
        teams = pymsteams.connectorcard(teams_webhook)
        if len(running_ec2) == 0 and len(running_rds) == 0 and len(running_glue) == 0 and len(running_sage) == 0 and len(running_redshift) == 0:
            teams.text("""
**AWS Account: """ + str(account) + """ - """ + str(alias) + """**

* Current Spend - Month to Date (USD): """ + str(spend[0]) + """
* Forecasted Monthly Spend (USD): """ + str(spend[1]) + """

​​​​​​​​​​​​​​&#x2705; No instance mistakenly left running""")
            teams.send()
        else:
            teams.text("""
**AWS Account: """ + str(account) + """ - """ + str(alias) + """**

* Current Spend - Month to Date (USD): """ + str(spend[0]) + """
* Forecasted Monthly Spend (USD): """ + str(spend[1]) + """
* Running EC2 instance(s): """ + str(len(running_ec2)) + """
* Running RDS instance(s): """ + str(len(running_rds)) + """
* Running Glue Dev Endpoint(s): """ + str(len(running_glue)) + """
* Running SageMaker Notebook instance(s): """ + str(len(running_sage)) + """
* Running Redshift Cluster(s): """ + str(len(running_redshift)) + """""")
            teams.send()
        if len(running_ec2) > 0:
            teams.title("EC2 Instances (" + str(account) + ")")
            teams.text("""""".join([f"\n * {r['ec2_name']}  {r['ec2_id']}  {r['ec2_type']}  {r['ec2_state']}  {r['region']}  {r['ec2_launch_time']} {r['custom_tags']}" for r in running_ec2]) + """""")
            teams.send()
        if len(running_rds) > 0:
            teams.title("RDS Instances (" + str(account) + ")")
            teams.text("""""".join([f"\n * RDS: {r['db_instance_name']}  {r['db_engine']}  {r['db_type']}  {r['db_storage']}  {r['region']}  {r['launch_time']}" for r in running_rds]) + """""")
            teams.send()
        if len(running_glue) > 0:
            teams.title("Glue Dev Endpoints (" + str(account) + ")")
            teams.text("""""".join([f"\n * Glue: {r['glue_endpointname']}  {r['glue_status']}  {r['glue_numberofnodes']}  {r['region']}  {r['glue_createdtimestamp']}" for r in running_glue]) + """""")
            teams.send()
        if len(running_sage) > 0:
            teams.title("SageMaker Notebook Instances (" + str(account) + ")")
            teams.text("""""".join([f"\n * SageMaker: {r['sage_notebookinstancename']}  {r['sage_notebookinstancestatus']}  {r['sage_instancetype']}  {r['region']}  {r['sage_creationtime']}" for r in running_sage]) + """""")
            teams.send()
        if len(running_redshift) > 0:
            teams.title("Redshift Cluster (" + str(account) + ")")
            teams.text("""""".join([f"\n * Redshift: {r['rs_clusteridentifier']}  {r['rs_status']}  {r['rs_numberofnodes']}  {r['region']}  {r['rs_creation_time']}" for r in running_redshift]) + """""")
            teams.send()
    except Exception as e:
        logging.error("Failed posting MS Teams Message %s", e)