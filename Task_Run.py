#!/usr/bin/env python

import argparse
import boto3
import time

parser = argparse.ArgumentParser(description='Command line arguments')
parser.add_argument('--LANDSCAPE', metavar='[LANDSCAPE]', help='Location name of the APP?')
parser.add_argument('--ENVIRONMENT', metavar='[ENVIRONMENT]', help='Is this pre-production or production?')
parser.add_argument('--APPLICATION', metavar='[APPLICATION]', help='Name of the application?')
parser.add_argument('--IMAGEURL', metavar='[IMAGEURL]', help='Repository URL for Docker Image?')
parser.add_argument('--REGION', metavar='[REGION]', help='AWS region where this task will be run?')
parser.add_argument('--PARAM_VERSION', metavar='[PARAM_VERSION]', help='Verion of parameters?')
args = parser.parse_args()

landscape = args.LANDSCAPE.lower().replace("_", "-")
environment = args.ENVIRONMENT.lower().replace("_", "-")
application = args.APPLICATION.lower().replace("_", "-")
family = "-".join([landscape, environment, application])
image_url = args.IMAGEURL
aws_region = args.REGION
param_version = args.PARAM_VERSION
log_group = "/".join(["/sageone", application.replace("-", "_"), "migration.log"])


# Need to create a task before you can run it. :)
# Task Role and Execution Role need to be created before hand. DEPENDS
def create_task():
    ecsClient = boto3.client('ecs', region_name=aws_region)
    response = ecsClient.register_task_definition(
        family=family,
        taskRoleArn="-".join([family, "role"]),
        executionRoleArn="-".join([family, "exec-role"]),
        networkMode='awsvpc',
        requiresCompatibilities=[
            'FARGATE'
        ],
        cpu='512',
        memory='1024',
        containerDefinitions=[
            {
                'name': "-".join([application, "migrate"]),
                'image': image_url,
                'cpu': 300,
                'memoryReservation': 800,
                'essential': True,
                'command': [
                    'bundle exec rake db:migrate',
                ],
                'environment': [
                    {
                        'name': 'APPLICATION',
                        'value': application.replace("-", "_")
                    },
                    {
                        'name': 'AWS_REGION',
                        'value': aws_region
                    },
                    {
                        'name': 'ENVIRONMENT',
                        'value': environment
                    },
                    {
                        'name': 'LANDSCAPE',
                        'value': landscape
                    },
                    {
                        'name': 'LOG_LEVEL',
                        'value': 'DEBUG'
                    },
                    {
                        'name': 'LOG_LOCATION',
                        'value': 'STDOUT'
                    },
                    {
                        'name': 'REMOTE_STORE_URL',
                        'value': 'https://param-store.na.preprod.sageone.biz/params'
                    },
                    {
                        'name': 'SINGLE_KEY_MODE',
                        'value': 'true'
                    },
                    {
                        'name': 'TIMESTAMP',
                        'value': time.ctime()
                    },
                    {
                        'name': 'VERSION',
                        'value': param_version
                    }
                ],
                'disableNetworking': False,
                'privileged': False,
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': log_group,
                        'awslogs-region': aws_region,
                        'awslogs-stream-prefix': "/".join([landscape, environment])
                    }
                }
            }
        ],
    )

if __name__ == "__main__":
    create_task()