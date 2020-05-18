#!/usr/bin/python3
# -*- coding: utf-8 -*-

# EC2 Checking V2
def ec2(region):
    ec2con = boto3.client('ec2', region_name=region)
    reservations = ec2con.describe_instances()['Reservations']
    running_ec2 = []
    ec2_hidden_count = 0
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
    # dict

    for reservation in reservations:
        for r in reservation['Instances']:
            ec2_state = r['State']['Name']
            ec2_type = r['InstanceType']
            ec2_id = r['InstanceId']
            ec2_launch_time = r['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S")

            # Whitelist checking
            ec2_tags = r['Tags']
            ec2_hidden = 0
            instance_name = "no name"
            for tags in ec2_tags or []:
                if tags["Key"] == 'Name':
                    instance_name = tags["Value"]
                if tags["Key"] == 'iw' and tags["Value"] == 'off':
                    ec2_hidden = 1
                    ec2_hidden_count += 1
                    break
            if ec2_hidden != 1:
                if ec2_state == "running":
                    running_ec2.append({
                        "ec2_name": instance_name,
                        "ec2_state": r['State']['Name'],
                        "ec2_type": r['InstanceType'],
                        "ec2_id": r['InstanceId'],
                        "region": region,
                        "ec2_launch_time": r['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S")
                    })
                    logger.info("%s %s %s %s %s %s", instance_name, ec2_state, ec2_type, ec2_id, region, ec2_launch_time)
    return running_ec2