#!/usr/bin/python3
# -*- coding: utf-8 -*-

# EC2 Checking V2
def ec2(region, running_ec2, whitelist_tag):
    ec2con = boto3.client('ec2', region_name=region)
    reservations = ec2con.describe_instances()['Reservations']
    ec2_hidden_count = 0
    custom_tags_dict = []
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
    # dict
    for reservation in reservations:
        for r in reservation['Instances']:
            logging.debug("%s", r)
            ec2_state = r['State']['Name']
            ec2_type = r['InstanceType']
            ec2_id = r['InstanceId']
            ec2_launch_time = r['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S")

            # Whitelist checking
            if 'Tags' in r:
                ec2_tags = r['Tags']
            else:
                ec2_tags = []
            ec2_hidden = 0
            instance_name = "no name"

            # CustomTags Management
            CustomTags = os.environ['CustomTags'].split(",")
            for tag in ec2_tags or []:
                logging.debug("%s", tag)
                if tag["Key"] == 'Name':
                    instance_name = tag["Value"]
                if tag["Key"] == whitelist_tag and tag["Value"] == 'off':
                    ec2_hidden = 1
                    ec2_hidden_count += 1
                    break
                if tag["Key"] in CustomTags:
                    custom_tags_dict.append({
                        tag["Key"]: tag["Value"]
                    })

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

                    logging.info("EC2 Match!: %s %s %s %s %s %s / %s", instance_name, ec2_state, ec2_type, ec2_id, region, ec2_launch_time, custom_tags_dict)
    return running_ec2, custom_tags_dict