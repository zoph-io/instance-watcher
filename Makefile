.DEFAULT_GOAL := help
.PHONY: help

help:
	@echo "Instance-Watcher-${Project}"
	@echo "${Description}"
	@echo ""
	@echo "Deploy using this order:"
	@echo "	layer - prepare the layer"
	@echo "	artifacts - create s3 bucket"
	@echo "	package - prepare the package"
	@echo "	verify-sender - verify SES Sender email"
	@echo "	deploy - deploy the lambda function"
	@echo "	---"
	@echo "	destroy - destroy the CloudFormation stack"
	@echo "	clean - clean the build folder"
	@echo "	clean-layer - clean the layer folder"
	@echo "	cleaning - clean build and layer folders"

####################### Project #######################
Project ?= project
Description ?= Instance Watcher Stack
#######################################################

###################### Parameters ######################
S3Bucket ?= instance-watcher-${Project}-${Env}-artifacts
AWSRegion ?= eu-west-1
Env ?= dev
WhitelistTag := watcher
## Slack
EnableSlack := 0
SlackWebHook := ""
## Microsoft Teams
EnableTeams := 0
TeamsWebHook := ""
# Recipients are space delimited (ie: john@doe.com david@doe.com)
Recipients := 
Sender := 

# Activate Email Notification
EnableMail := 1

# Schedule Instance Watcher (UTC)
CronSchedule := "0 18 * * ? *"
#######################################################

artifacts:
	@echo "Creation of artifacts bucket"
	@aws s3 mb s3://$(S3Bucket)
	@aws s3api put-bucket-encryption --bucket $(S3Bucket) \
		--server-side-encryption-configuration \
		'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
	@aws s3api put-bucket-versioning --bucket $(S3Bucket) --versioning-configuration Status=Enabled

verify-sender:
	@echo "Verifing sender email address"
	@aws ses verify-email-identity --email-address $(Sender)
	@echo "Done; Check your Inbox to validate the link!"

package: clean
	@echo "Consolidating python code in ./build"
	mkdir -p build/services
	mkdir -p build/utils

	cp -R *.py ./build/
	cp -R ./services/*.py ./build/services/
	cp -R ./utils/*.py ./build/utils/

	python3 -m pip install \
		--isolated \
		--prefix="" \
		--disable-pip-version-check \
		-Ur requirements.txt -t ./build/

	@echo "zipping python code, uploading to S3 bucket, and transforming template"
	aws cloudformation package \
		--template-file sam.yml \
		--s3-bucket ${S3Bucket} \
		--output-template-file build/template-lambda.yml

	@echo "Copying updated cloud template to S3 bucket"
	aws s3 cp build/template-lambda.yml 's3://${S3Bucket}/template-lambda.yml'

layer: clean-layer
	python -m pip install \
		--isolated \
		--prefix="" \
		--disable-pip-version-check \
		-Ur requirements-layer.txt -t ./layer/

deploy:
	aws cloudformation deploy \
		--template-file build/template-lambda.yml \
		--region ${AWSRegion} \
		--stack-name "instance-watcher-${Project}-${Env}" \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			Env=${Env} \
			Recipients="${Recipients}" \
			Sender=${Sender} \
			Project=instance-watcher-${Project} \
			AWSRegion=${AWSRegion} \
			WhitelistTag=${WhitelistTag} \
			EnableMail=${EnableMail} \
			EnableSlack=${EnableSlack} \
			TeamsWebHook=${TeamsWebHook} \
			SlackWebHook=${SlackWebHook} \
			EnableTeams=${EnableTeams} \
			CronSchedule=${CronSchedule} \
		--no-fail-on-empty-changeset

tear-down:
	@read -p "Are you sure that you want to destroy stack 'instance-watcher-${Project}-${Env}'? [y/N]: " sure && [ $${sure:-N} = 'y' ]
	aws cloudformation delete-stack --stack-name "instance-watcher-${Project}-${Env}"

clean-layer:
	@rm -fr layer/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

cleaning: clean clean-layer
