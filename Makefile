.DEFAULT_GOAL := help

help:
	@echo "Instance-Watcher-${PROJECT}"
	@echo "${DESCRIPTION}"
	@echo ""
	@echo "Deploy using this order:"
	@echo "	layer - prepare the layer"
	@echo "	package - prepare the package"
	@echo "	artifacts - create s3 bucket"
	@echo "	verify-sender - verify SES Sender email"
	@echo "	deploy - deploy the lambda function"
	@echo "	---"
	@echo "	destroy - destroy the CloudFormation stack"
	@echo "	clean - clean the build folder"
	@echo "	clean-layer - clean the layer folder"
	@echo "	cleaning - clean build and layer folders"

####################### Project #######################
PROJECT ?= discover
DESCRIPTION ?= Instance Watcher Stack
#######################################################

###################### Variables ######################
S3_BUCKET ?= instance-watcher-${PROJECT}-artifacts
AWS_REGION ?= eu-west-1
# Recipients are space delimited (ie: john@doe.com david@doe.com)
RECIPIENTS := victor.grenu@external.engie.com
SENDER := victor.grenu@external.engie.com
ENV ?= dev
#######################################################

artifacts:
	@echo "Creation of artifacts bucket"
	@aws s3 mb s3://$(S3_BUCKET)
	@aws s3api put-bucket-encryption --bucket $(S3_BUCKET) \
		--server-side-encryption-configuration \
		'{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
	@aws s3api put-bucket-versioning --bucket $(S3_BUCKET) --versioning-configuration Status=Enabled

verify-sender:
	@echo "Verifing sender email address"
	@aws ses verify-email-identity --email-address $(SENDER)
	@echo "Done; Check your Inbox to validate the link!"

package: clean
	@echo "Consolidating python code in ./build"
	mkdir -p build

	cp -R *.py ./build/

	@echo "zipping python code, uploading to S3 bucket, and transforming template"
	aws cloudformation package \
		--template-file sam.yml \
		--s3-bucket ${S3_BUCKET} \
		--output-template-file build/template-lambda.yml

	@echo "Copying updated cloud template to S3 bucket"
	aws s3 cp build/template-lambda.yml 's3://${S3_BUCKET}/template-lambda.yml'

layer: clean-layer
	pip3 install \
		--isolated \
		--disable-pip-version-check \
		-Ur requirements.txt -t ./layer/

deploy:
	aws cloudformation deploy \
		--template-file build/template-lambda.yml \
		--region ${AWS_REGION} \
		--stack-name "instance-watcher-${PROJECT}-${ENV}" \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			ENV=${ENV} \
			RECIPIENTS="${RECIPIENTS}" \
			SENDER=${SENDER} \
			PROJECT=instance-watcher-${PROJECT} \
			AWSREGION=${AWS_REGION} \
		--no-fail-on-empty-changeset

tear-down:
	@read -p "Are you sure that you want to destroy stack 'instance-watcher-${PROJECT}-${ENV}'? [y/N]: " sure && [ $${sure:-N} = 'y' ]
	aws cloudformation delete-stack --stack-name "instance-watcher-${PROJECT}-${ENV}"

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
