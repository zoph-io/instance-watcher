#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Glue Development Endpoint Checking
def glue(region, running_glue, whitelist_tag, account):
    gluecon = boto3.client('glue', region_name=region)
    glue = gluecon.get_dev_endpoints()
    glue_hidden_count = 0
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html#Glue.Client.get_dev_endpoints
    # dict
    for r in glue['DevEndpoints']:
        logging.debug("%s", r)
        glue_status = r['Status'] # https://docs.aws.amazon.com/glue/latest/dg/console-development-endpoint.html
        glue_endpointname = r['EndpointName']
        glue_arn = "arn:aws:glue:" + region + ":" + account + ":devEndpoint/" + glue_endpointname
        glue_numberofnodes = r['NumberOfNodes']
        glue_createdtimestamp = r['CreatedTimestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Whitelist checking
        instance_tags = gluecon.get_tags(ResourceArn=glue_arn)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html#Glue.Client.get_tags
        glue_tags = instance_tags['Tags']
        if whitelist_tag in glue_tags:
            if whitelist_tag == 'off':
                glue_hidden_count += 1
        else:
            if glue_status == "READY":
                running_glue.append({
                    "glue_endpointname": r['EndpointName'],
                    "glue_status": r['Status'],
                    "glue_numberofnodes": r['NumberOfNodes'],
                    "region": region,
                    "glue_createdtimestamp": r['CreatedTimestamp'].strftime("%Y-%m-%d %H:%M:%S")
                })
                logging.info("Matched!: %s %s %s %s", glue_endpointname, glue_status, glue_numberofnodes, glue_createdtimestamp)
    return running_glue