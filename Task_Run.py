#!/usr/bin/env python

import argparse
import boto3
import time
import logging



def main():
    config = parse_config()
    ecsClient = boto3.client('ecs', region_name=config['aws_region'])
    serviceArn = get_service_arn(ecsClient,config)
    taskArn = get_task_definition_arn(ecsClient,config,serviceArn)
    taskObject = build_task_definition_object(ecsClient,config,taskArn)
    createdTaskArn = create_task(ecsClient,config,taskObject)

    run_task(ecsClient,config,createdTaskArn)

def parse_config():
    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('FAMILY', metavar='[FAMILY]', help='Who owns the APP?')
    parser.add_argument('LANDSCAPE', metavar='[LANDSCAPE]', help='Location name of the APP?')
    parser.add_argument('ENVIRONMENT', metavar='[ENVIRONMENT]', help='Is this pre-prod or prod?')
    parser.add_argument('PRODUCT', metavar='[PRODUCT]', help='Name of the application?')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument('--REGION', metavar='[REGION]', help='AWS region where this task will be run?')
    parser.add_argument('--IMAGE_VERSION', metavar='[IMAGE_VERSION]', help='Docker Image version? To be prefixed with "v"')
    parser.add_argument('--PARAM_VERSION', metavar='[PARAM_VERSION]', help='Verion of parameters? To be prefixed with "v"')
    parser.add_argument('--RAKE', metavar='[RAKE]', help='Full rake command encapsulated with double quotes')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = {}

    config['rake'] = args.RAKE.lower()
    config['family'] = args.FAMILY.lower()
    config['landscape'] = args.LANDSCAPE.lower()
    config['environment'] = args.ENVIRONMENT.lower()
    config['product'] = args.PRODUCT.lower().replace("_", "-")
    config['silver_square'] = "-".join([config['landscape'],config['environment'],config['family'],config['product']])
    config['aws_region'] = args.REGION
    config['param_version'] = args.PARAM_VERSION
    config['cluster_name'] = "-".join([config['landscape'],config['environment'],config['family'],"ecs-cluster"])
    config['migration_log'] = "/".join(
        [
            config['landscape'],
            config['environment'],
            config['family'],
            config['product'].replace("-", "_"),
            "migration.log"
        ]
    )
    config['image_url'] = "700326549305.dkr.ecr.{}.amazonaws.com/{}/{}:{}".format(
        config['aws_region'],
        config['family'],
        config['product'].replace("-", "_"),
        args.IMAGE_VERSION
    )

    #print config
    return config

def get_service_arn(ecsClient,config,token=''):
    response = ecsClient.list_services(
        cluster=config['cluster_name'],
        nextToken=token
    )

    for service in response['serviceArns']:
        #print service
        if config['silver_square'] in service:
            #print service
            return service
    try:
        pageToken = response['nextToken']
        return get_service_arn(ecsClient,config,token=pageToken)
    except KeyError:
        pass

def get_task_definition_arn(ecsClient,config,serviceArn):
    response = ecsClient.describe_services(
        cluster=config['cluster_name'],
        services=[
            serviceArn
        ]
    )
    for tasks in response['services']:
        return tasks['taskDefinition']

def build_task_definition_object(ecsClient,config,taskArn):
    response = ecsClient.describe_task_definition(
        taskDefinition=taskArn
    )

    task_object = response['taskDefinition']
    #task_object = taskArn['networkConfiguration']
    
    for containers in task_object['containerDefinitions']:
        if containers['name'] == config['product']:
            task_object['containerDefinitions'] = containers

    for envVar in task_object['containerDefinitions']['environment']:
        if envVar['name'] in ['VERSION', 'PARAM_VERSION']:
            envVar['value'] = config['param_version']

    if "stripe" in config['product']:
        task_object['containerDefinitions']['command'] = [config['rake']]

    task_object['containerDefinitions']['image'] = config['image_url']
    task_object['containerDefinitions']['logConfiguration']['options']['awslogs-group'] = config['migration_log']

    print task_object
    return task_object

# Need to create a task before you can run it. :)
# Task Role and Execution Role need to be created before hand. DEPENDS
def create_task(ecsClient,config,taskObject):
    response = ecsClient.register_task_definition(
        family="-".join([config['silver_square'],"migration"]), 
        taskRoleArn=taskObject['taskRoleArn'],
        networkMode=taskObject['networkMode'],
        requiresCompatibilities=taskObject['requiresCompatibilities'],
        containerDefinitions=[
            taskObject['containerDefinitions']
        ]
    )

    #print response['taskDefinition']['taskDefinitionArn']
    return response['taskDefinition']['taskDefinitionArn']

def run_task(ecsClient,config,createdTaskArn):
    response = ecsClient.run_task(
        cluster=config['cluster_name'],
        taskDefinition=createdTaskArn,
        count=1,
        launchType='EC2'
    )
    print response
if __name__ == "__main__":
    main()