# Instance Watcher :eyes:

## Description

This AWS Lambda function will send you once a day a recap email with the list of the running instances on all AWS regions for a giver AWS Account.

It covers actually:

- EC2 Instances
- RDS Instances
- SageMaker Notebook Instances
- Glue Development Endpoints

I'm using this for `non-prod`, `lab`, `sandbox`, and `personal` AWS accounts, to get a kindly reminder of what I've left running. :money_with_wings:

## Core features

* List running EC2 instances across all AWS Regions.
  * Check `name`, `instance-id`, `instance_type`, `key_name`, `region`, `launch_time`
* List running RDS instances across all AWS Regions.
  * Check `db_instance_name`, `db_engine`, `db_type`, `db_storage`, `region`, `launch_time`
* White list capability using the `iw` [tag](#Whitelisting)
* Send summary by email once a day if any running instance
* Serverless Architecture using AWS Lambda + layer and SES

## Requirements

* [Verify](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html) your **sender** and **recipient** (in sandbox mode) SES email
* Create `<your_project_name>-artifacts` s3 bucket (default is `instance-watcher-artifacts`)

## Deployment

Change emails settings and project name in `Makefile` or use command-line

> Nb: Recipients are **space-delimited**

```bash
PROJECT ?= my_project_name
RECIPIENTS := my_target_email@domain.com my_second_target@domain.com
SENDER := my_source_email@domain.com
```

> You will need to verify email received from AWS SES (for SENDER) using `make verify-sender`

        $ make layer
        $ make package PROJECT=<your_project_name>
        $ make verify-sender
        $ make deploy \
                ENV=<your_env_name> \
                AWSREGION=<your_aws_region> \
                PROJECT=<your_project_name> \
                SENDER=sender@youremail.com \
                RECIPIENTS='targetemail@youremail.com targetemail2@youremail.com'

*Nb: Use emails in command line is optional if your already set up in the `Makefile`*

## Destroy

        $ make tear-down

## Whitelisting

If you want to whitelist a specific instance to be hidden from the daily report, you will need to add the following tag to the instance.

| Key | Value |
|:---:|:-----:|
| `iw` | `off` |

## Todo

* ~~Add `SageMaker Notebook instances`~~
  * Whitelist
* ~~Add `Glue Dev Endpoints`~~
  * Whitelist
* Add `Redshift Cluster`
  * Whitelist
* ~~Add SES setup built-in~~
* Whitelist for `RDS Instances`
* Add python unit tests
* Multi AWS Account Support
* Add `Instance Profile` column (EC2)
* Add pricing column
