#!/usr/bin/python3
# -*- coding: utf-8 -*-

# RDS Checking
def rds(region, running_rds, whitelist_tag):
    rdscon = boto3.client('rds', region_name=region)
    rds = rdscon.describe_db_instances()
    rds_hidden_count = 0
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_db_instances
    # dict
    for r in rds['DBInstances']:
        logging.debug("%s", r)
        db_status = r['DBInstanceStatus'] # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.DBInstance.Status.html
        if db_status != "creating":
            db_instance_name = r['DBInstanceIdentifier']
            db_instance_arn = r['DBInstanceArn']
            db_engine =  r['Engine']
            db_type = r['DBInstanceClass']
            db_storage = r['AllocatedStorage']
            db_creation_time = r['InstanceCreateTime'].strftime("%Y-%m-%d %H:%M:%S")
            db_publicly_accessible = r['PubliclyAccessible']

            # Whitelist checking
            instance_tags = rdscon.list_tags_for_resource(ResourceName=db_instance_arn)
            rds_tags = instance_tags['TagList']
            rds_hidden = 0
            for tags in rds_tags or []:
                logging.debug("%s", tags)
                if tags["Key"] == whitelist_tag and tags["Value"] == 'off':
                    rds_hidden = 1
                    rds_hidden_count += 1
                    break
            if rds_hidden != 1:
                if db_status == "available" \
                    or db_status == "backing-up" \
                    or db_status == "failed" \
                    or db_status == "backtracking" \
                    or db_status == "modifying" \
                    or db_status == "storage-full" \
                    or db_status == "storage-optimization" \
                    or db_status == "upgrading":
                    running_rds.append({
                        "db_instance_name": r['DBInstanceIdentifier'],
                        "db_engine": r['Engine'],
                        "db_type": r['DBInstanceClass'],
                        "db_storage": r['AllocatedStorage'],
                        "db_publicly_accessible": r['PubliclyAccessible'],
                        "region": region,
                        "launch_time": r['InstanceCreateTime'].strftime("%Y-%m-%d %H:%M:%S")
                    })
                    logging.info("RDS Match!: %s %s %s %s %s %s %s", db_instance_name, db_status, db_engine, db_type, db_storage, db_creation_time, db_publicly_accessible)
        else:
            logging.info("An RDS instance is creating")
    return running_rds