# Instance Watcher :eyes:

## Description

Instance Watcher will send you once a day a recap email with the list of the running instances on all AWS regions for a given AWS Account.

It covers the following AWS Services:

- EC2 Instances
- RDS Instances
- SageMaker Notebook Instances
- Glue Development Endpoints
- Redshift Clusters

I'm using this for `non-prod`, `lab/training`, `sandbox`, or `personal` AWS accounts, to get a kindly reminder of what I've left running. :money_with_wings:

## Sneak Peek

![Mail Sample](assets/mail-sample.png)

## Requirements

> Before you can send an email using Amazon SES, you must verify the address or domain that you are sending the email from to prove that you own it. If you do not have production access yet, you also need to verify any email addresses that you send emails to except for email addresses provided by the Amazon SES mailbox simulator.

## Deployment

Change default settings in `Makefile` or use command-line.

> Nb: Recipients are **space-delimited**

### Parameters

```bash
PROJECT ?= my_project_name
RECIPIENTS := my_target_email@domain.com my_second_target@domain.com
SENDER := my_source_email@domain.com
ENABLEMAIL := 1
WHITELISTTAG := watcher
```

> You will need to verify email received from AWS SES (for SENDER) using `make verify-sender`

        $ make layer
        $ make package PROJECT=<your_project_name>
        $ make verify-sender
        $ make deploy \
                ENV=<your_env_name> \
                AWSREGION=<your_aws_region> \
                PROJECT=<your_project_name> \
                SENDER=<your_sender@your_domain.com> \
                RECIPIENTS='target_email@your_domain.com target_email2@your_domain.com'

*Nb: Use emails in the command line is optional if you've already set up in the `Makefile`*

## Destroy

        $ make tear-down

## Whitelisting

If you want to whitelist a specific instance to be hidden from the daily report, you will need to add the following tag to the instance.

| Key | Value |
|:---:|:-----:|
| `watcher` | `off` |

*nb: Tag `Key` is customizable in `Makefile`*

## Todo

* ~~Add `SageMaker Notebook instances`~~
  * Whitelist
* ~~Add `Glue Dev Endpoints`~~
  * Whitelist