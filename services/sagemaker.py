
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# SageMaker Notebook Instances Checking
def sagemaker(region):
    sagecon = boto3.client('sagemaker', region_name=region)
    sage = sagecon.list_notebook_instances()
    running_sage = []
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
    return running_sage