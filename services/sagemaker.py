
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# SageMaker Notebook Instances Checking
def sagemaker(region, running_sage, whitelist_tag):
    sagecon = boto3.client('sagemaker', region_name=region)
    sage = sagecon.list_notebook_instances()
    sage_hidden_count = 0
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.list_notebook_instances
    # dict
    for r in sage['NotebookInstances']:
        sage_notebookinstancestatus = r['NotebookInstanceStatus']
        sage_notebookinstancename = r['NotebookInstanceName']
        sage_instancetype = r['InstanceType']
        sage_creationtime = r['CreationTime'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Whitelist checking
        instance_tags = sagecon.get_tags(ResourceArn=XXX)
        sage_tags = instance_tags['TagList']
        sage_hidden = 0
        for tags in sage_tags or []:
            if tags["Key"] == whitelist_tag and tags["Value"] == 'off':
                sage_hidden = 1
                sage_hidden_count += 1
                break
        if sage_hidden != 1:
            if sage_notebookinstancestatus == "InService":
                running_sage.append({
                    "sage_notebookinstancename": r['NotebookInstanceName'],
                    "sage_notebookinstancestatus": r['NotebookInstanceStatus'],
                    "sage_instancetype": r['InstanceType'],
                    "region": region,
                    "sage_creationtime": r['CreationTime'].strftime("%Y-%m-%d %H:%M:%S")
                })
                logging.info("Matched!: %s %s %s %s", sage_notebookinstancename, sage_notebookinstancestatus, sage_instancetype, sage_creationtime)
    return running_sage