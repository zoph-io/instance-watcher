#!/usr/bin/python3
# -*- coding: utf-8 -*-

# RDS Checking
def rds(region):
    rdscon = boto3.client('rds', region_name=region)
    rds = rdscon.describe_db_instances()
    running_rds = []
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
        logger.info("%s %s %s %s %s %s %s", db_instance_name, db_status, db_engine, db_type, db_storage, db_creation_time, db_publicly_accessible)
    return running_rds