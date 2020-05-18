#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Redshift Checking
def redshift(region):
    redshiftcon = boto3.client('redshift', region_name=region)
    redshift = redshiftcon.describe_clusters()
    running_redshift = []
    rs_hidden_count = 0
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Client.describe_clusters
    # dict

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
    return running_redshift