#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ES Checking v1
def es(region, running_es, whitelist_tag):
    esclient = boto3.client("es", region_name=region)
    domains = esclient.list_domain_names()["DomainNames"]  # Getting list of domains
    prep = []
    for domain in domains:  # Preparing for getting details
        prep.append(domain["DomainName"])
    adv_domains = esclient.describe_elasticsearch_domains(DomainNames=prep)[
        "DomainStatusList"
    ]

    for oneDomain in adv_domains:
        if not oneDomain["Deleted"]:
            running_es.append(
                {
                    "es_domain_name": oneDomain["DomainName"],
                    "es_deleted_status": oneDomain["Deleted"],
                    "es_domain_version": oneDomain["ElasticsearchVersion"],
                    "es_instance_type": oneDomain["ElasticsearchClusterConfig"][
                        "InstanceType"
                    ],
                    "es_instance_count": oneDomain["ElasticsearchClusterConfig"][
                        "InstanceCount"
                    ],
                    "region": region,
                    "es_storage_size": oneDomain["EBSOptions"]["VolumeSize"],
                }
            )

    return running_es
