#!/usr/bin/python3
# -*- coding: utf-8 -*-

def mailer(region, alias, account, spend, running_ec2, running_rds, running_glue, running_sage, running_redshift):
    if (len(running_ec2) == 0 and len(running_rds) == 0 and len(running_glue) == 0 and len(running_sage) == 0 and len(running_redshift) == 0):
        logger.info("Nothing to see here, no running instance")
    else:
        if mail_enabled == 1:
            logger.info("Sending email to: %s", str(recipients))
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
                    <p>AWS AccountID: <a href="https://""" + account + """.signin.aws.amazon.com/console">""" + account + """</a> - <a href=https://""" + alias + """.signin.aws.amazon.com/console>""" + alias + """</a> - Current Spend: <a href="https://console.aws.amazon.com/cost-management/home?#/dashboard">$""" + str(spend) + """</a></p>"""
            
            # Crafting EC2 html table
            if len(running_ec2) > 0:
                ec2_table = """
                    <h3>Running EC2 Instance(s): </h3>
                    <table cellpadding="4" cellspacing="4">
                    <tr><td><strong>Name</strong></td><td><strong>Instance ID</strong></td><td><strong>Intsance Type</strong></td><td><strong>State</strong></td><td><strong>Region</strong></td><td><strong>Launch Time</strong></td></tr>
                    """ + \
                        "\n".join([f"<tr><td>{r['ec2_name']}</td><td>{r['ec2_id']}</td><td>{r['ec2_type']}</td><td>{r['ec2_state']}</td><td>{r['region']}</td><td>{r['ec2_launch_time']}</td></tr>" for r in running_ec2]) \
                        + """
                    </table>
                    <p>Total number of running EC2 instance(s): """ + str(len(running_ec2)) + """"""
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

            footer = """
                    <p><a href="https://github.com/z0ph/instance-watcher">Instance Watcher 🖤</a></p>
                </body>
            </html>
            """

            # Concatenate html email
            body_html = header + ec2_table + rds_table + sage_table + glue_table + rs_table + footer

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
            logger.info("Email sent! Message ID: %s", response['MessageId'])
        else:
            logger.info("Email Notification Disabled")