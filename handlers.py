import boto3
import os

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
    running_ec2 = []
    running_rds = []
    running_sage = []
    running_glue = []
    running_redshift = []

    account = sts.get_caller_identity().get('Account')
    alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]
    #ec2_regions = [region['RegionName'] for region in ec2r.describe_regions()['Regions']]
    ec2_regions = ["eu-west-1"] # Troubleshooting only
    # For all AWS Regions
    for region in ec2_regions:
        print("Checking running instances in: " + region)
        
        # Glue Development Endpoint Checking
        gluecon = boto3.client('glue', region_name=region)
        glue = gluecon.get_dev_endpoints()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html#Glue.Client.get_dev_endpoints
        # dict
        for r in glue['DevEndpoints']:
            glue_endpointname = r['EndpointName']
            glue_status = r['Status']
            glue_numberofnodes = r['NumberOfNodes']
            glue_createdtimestamp = r['CreatedTimestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            if glue_status == "READY":
                running_glue.append({
                    "glue_endpointname": r['EndpointName'],
                    "glue_status": r['Status'],
                    "glue_numberofnodes": r['NumberOfNodes'],
                    "region": region,
                    "glue_createdtimestamp": r['CreatedTimestamp'].strftime("%Y-%m-%d %H:%M:%S")
                })
                print(glue_endpointname,glue_status,glue_numberofnodes,glue_createdtimestamp)
        
        # SageMaker Notebook Instances Checking
        sagecon = boto3.client('sagemaker', region_name=region)
        sage = sagecon.list_notebook_instances()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.list_notebook_instances
        # dict
        for r in sage['NotebookInstances']:
            sage_notebookinstancename = r['NotebookInstanceName']
            sage_notebookinstancestatus = r['NotebookInstanceStatus']
            sage_instancetype = r['InstanceType']
            sage_creationtime = r['CreationTime'].strftime("%Y-%m-%d %H:%M:%S")

            if sage_notebookinstancestatus == "InService":
                running_sage.append({
                    "sage_notebookinstancename": r['NotebookInstanceName'],
                    "sage_notebookinstancestatus": r['NotebookInstanceStatus'],
                    "sage_instancetype": r['InstanceType'],
                    "region": region,
                    "sage_creationtime": r['CreationTime'].strftime("%Y-%m-%d %H:%M:%S")
                })
                print(sage_notebookinstancename,sage_notebookinstancestatus,sage_instancetype,sage_creationtime)

        # RDS Checking
        rdscon = boto3.client('rds', region_name=region)
        rds = rdscon.describe_db_instances()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_db_instances
        # dict
        for r in rds['DBInstances']:
            db_instance_name = r['DBInstanceIdentifier']
            db_engine =  r['Engine']
            db_status = r['DBInstanceStatus']
            db_type = r['DBInstanceClass']
            db_storage = r['AllocatedStorage']
            db_creation_time = r['InstanceCreateTime'].strftime("%Y-%m-%d %H:%M:%S")
            db_publicly_accessible = r['PubliclyAccessible']

            if db_status == "available" or "backing-up" or "failed":
                running_rds.append({
                    "db_instance_name": r['DBInstanceIdentifier'],
                    "db_engine": r['Engine'],
                    "db_type": r['DBInstanceClass'],
                    "db_storage": r['AllocatedStorage'],
                    "db_publicly_accessible": r['PubliclyAccessible'],
                    "region": region,
                    "launch_time": r['InstanceCreateTime'].strftime("%Y-%m-%d %H:%M:%S")
                })
                print(db_instance_name,db_status,db_engine,db_type,db_storage,db_creation_time,db_publicly_accessible)
        
        # Redshift Checking
        redshiftcon = boto3.client('redshift', region_name=region)
        redshift = redshiftcon.describe_clusters()
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Client.describe_clusters
        # dict
        rs_hidden_count = 0
        for r in redshift['Clusters']:
            rs_clusteridentifier = r['ClusterIdentifier']
            rs_status = r['ClusterStatus']
            rs_type = r['NodeType']
            rs_numberofnodes = r['NumberOfNodes']
            rs_creation_time = r['ClusterCreateTime'].strftime("%Y-%m-%d %H:%M:%S")

            # Whitelist checking
            rs_tags = r['Tags']
            rs_hidden = 0
            for tags in rs_tags or []:
                if tags["Key"] == 'iw' and tags["Value"] == 'off':
                    rs_hidden = 1
                    rs_hidden_count += 1
                    break
            if rs_hidden != 1:
                if rs_status == "available" or "storage-full" or "resizing":
                    running_redshift.append({
                        "rs_clusteridentifier": r['ClusterIdentifier'],
                        "rs_status": r['ClusterStatus'],
                        "rs_type": r['NodeType'],
                        "rs_numberofnodes": r['NumberOfNodes'],
                        "region": region,
                        "rs_creation_time": r['ClusterCreateTime'].strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(rs_clusteridentifier,rs_status,rs_type,rs_numberofnodes,region,rs_creation_time)

        # EC2 Checking
        ec2con = boto3.resource('ec2', region_name=region)
        ec2 = ec2con.instances.filter()
        # For every instances in region
        ec2_hidden_count = 0
        for instance in ec2:
            if instance.state["Name"] == "running":
                # For all instances tags
                ec2_hidden = 0
                instancename = "n/a"
                for tags in instance.tags or []:
                    if tags["Key"] == 'Name':
                        instancename = tags["Value"]
                    if tags["Key"] == 'iw' and tags["Value"] == 'off':
                        ec2_hidden = 1
                        ec2_hidden_count += 1
                        break
                if ec2_hidden != 1:
                    print(instancename, instance.id)
                    # fill the list
                    running_ec2.append({
                        "instance_name": instancename,
                        "id": instance.id,
                        "instance_type": instance.instance_type,
                        "key_pair": instance.key_name,
                        "region": region,
                        "launch_time": instance.launch_time.strftime("%Y-%m-%d %H:%M:%S")
                    })
            else:
                print("No running EC2 instance, but some exist (Pending, Stopped, Terminated or Whitelisted): ", instance.id)
    
    # Exec Summary (Logging)
    print("===== Summary =====")
    print("Total number of running EC2 instance(s):", len(running_ec2))
    print("Total number of hidden EC2 instance(s):", ec2_hidden_count)
    print("Total number of running RDS instance(s):", len(running_rds))
    #print("Total number of hidden RDS instance(s):", len(rds_hidden_count))
    print("Total number of running Glue Dev Endpoint(s):", len(running_glue))
    #print("Total number of hidden Glue Dev Endpoint(s):", ec2_hidden_count)
    print("Total number of running SageMaker Notebook instance(s):", len(running_sage))
    #print("Total number of hidden SageMaker Notebook instance(s):", ec2_hidden_count)
    print("Total number of running Redshift Cluster(s):", len(running_redshift))
    print("Total number of hidden Redshift Cluster(s):", rs_hidden_count)
    print("==="*10)

    if (len(running_ec2) == 0 and len(running_rds) == 0 and len(running_glue) == 0 and len(running_sage) == 0 and len(running_redshift) == 0):
        print("Nothing to see here, no running instance")
    else:
        if mail_enabled == 1:
            print("Sending email to: " + str(recipients))
            body_text = (
                        """
                        Instance Watcher\r\n
                        Running EC2 Instances {ec2}
                        Running RDS Instances {rds}
                        Running SageMaker Notebook Instances {sage}
                        Running Glue Dev Endpoints {glue}
                        Running Redshift Clusters {rs}
                        """).format(
                                ec2=len(running_ec2),
                                rds=len(running_rds),
                                sage=len(running_sage),
                                glue=len(running_glue),
                                rs=len(running_redshift)
                            )
            header = """
            <html>
                <head>
                    <style>
                        table, th, td {
                        border: 3px solid black;
                        border-collapse: collapse;
                        }
                    </style>
                </head>
                <body>
                    <h1>Instance Watcher 👀</h1>
                    <p>AWS AccountID: <a href="https://""" + account + """.signin.aws.amazon.com/console">""" + account + """</a> - <a href=https://""" + alias + """.signin.aws.amazon.com/console>""" + alias + """</a></p>"""
            
            # Crafting EC2 html table
            if len(running_ec2) > 0:
                ec2_table = """
                    <h3>Running EC2 Instance(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Instance ID</strong></td><td><strong>Intsance Type</strong></td><td><strong>Key Name</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['instance_name']}</td><td>{r['id']}</td><td>{r['instance_type']}</td><td>{r['key_pair']}</td><td>{r['region']}</td><td>{r['launch_time']}</td></tr>" for r in running_ec2]) \
                        + """
                    </table>
                    <p>Total number of running EC2 instance(s): """ + str(len(running_ec2)) + """
                """
            else:
                ec2_table = """"""
            
            # Crafting RDS html table
            if len(running_rds) > 0:
                rds_table = """
                    <h3>Running RDS Instance(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Engine</strong></td><td><strong>DB Type</strong></td><td><strong>Volume (GB)</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['db_instance_name']}</td><td>{r['db_engine']}</td><td>{r['db_type']}</td><td>{r['db_storage']}</td><td>{r['region']}</td><td>{r['launch_time']}</td></tr>" for r in running_rds]) \
                        + """
                    </table>
                    <p>Total number of running RDS instance(s): """ + str(len(running_rds)) + """"""
            else:
                rds_table = """"""
            
            footer = """
                    <p><a href="https://github.com/z0ph/instance-watcher">Instance Watcher 🖤</a></p>
                </body>
            </html>
            """

            # Crafting SageMaker html table
            if len(running_sage) > 0:
                sage_table = """
                    <h3>Running SageMaker Notebook Instance(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Status</strong></td><td><strong>Instance Type</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['sage_notebookinstancename']}</td><td>{r['sage_notebookinstancestatus']}</td><td>{r['sage_instancetype']}</td><td>{r['region']}</td><td>{r['sage_creationtime']}</td></tr>" for r in running_sage]) \
                        + """
                    </table>
                    <p>Total number of running SageMaker Notebook instance(s): """ + str(len(running_sage)) + """"""
            else:
                sage_table = """"""

            # Crafting Glue html table
            if len(running_glue) > 0:
                glue_table = """
                    <h3>Running Glue Development Endpoint(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Status</strong></td><td><strong>Number of nodes (DPU)</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['glue_endpointname']}</td><td>{r['glue_status']}</td><td>{r['glue_numberofnodes']}</td><td>{r['region']}</td><td>{r['glue_createdtimestamp']}</td></tr>" for r in running_glue]) \
                        + """
                    </table>
                    <p>Total number of running Glue Development Endpoint(s): """ + str(len(running_glue)) + """"""
            else:
                glue_table = """"""
            
            footer = """
                    <p><a href="https://github.com/z0ph/instance-watcher">Instance Watcher 🖤</a></p>
                </body>
            </html>
            """

            # Crafting Redshift html table
            if len(running_redshift) > 0:
                rs_table = """
                    <h3>Running Redshift Cluster(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Status</strong></td><td><strong>Number of nodes</strong></td><td><strong>Node Type</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['rs_clusteridentifier']}</td><td>{r['rs_status']}</td><td>{r['rs_numberofnodes']}</td><td>{r['rs_type']}</td><td>{r['region']}</td><td>{r['rs_creation_time']}</td></tr>" for r in running_redshift]) \
                        + """
                    </table>
                    <p>Total number of running Redshift Cluster(s): """ + str(len(running_redshift)) + """"""
            else:
                rs_table = """"""
            
            hidden_table = """
                <br />Total number of hidden EC2 instance(s): """ + str(ec2_hidden_count) + """</p>
                <br />Total number of hidden Redshift Cluster(s): """ + str(rs_hidden_count) + """</p>
            """

            footer = """
                    <p><a href="https://github.com/z0ph/instance-watcher">Instance Watcher 🖤</a></p>
                </body>
            </html>
            """

            # Concatenate html email
            body_html = header + ec2_table + rds_table + sage_table + glue_table + rs_table + hidden_table + footer

            response = ses.send_email(
                Destination={
                    'ToAddresses': recipients,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': charset,
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject + account,
                    },
                },
                Source=sender,
            )
            print("Email sent! Message ID: " + response['MessageId'])
        else:
            print("Email Notification Disabled")

if __name__ == '__main__':
    main(0,0)
