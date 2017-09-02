#!/usr/bin/env python
#: Script: Set_AWS_S3Config.py
#: Description: Takes AWS Creds name for account identification, gets list of regions, puts config rules for s3 buckets.
#: Author: Dustin Harrell

import argparse
import boto3

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--PROFILE', metavar='[PROFILE]', help='AWS Cred Profile Name')
ARGS = PARSER.parse_args()

region_list = []

def get_regions(profile):
    ec2 = boto3.client('ec2', profile_name=profile)
    regions = ec2.describe_regions()
    for region in regions['Regions']:
        region_list.append(region['RegionName'])

def put_config(rule_name, profile, region):
    config = boto3.client('config', profile_name=profile, region_name=region)
    rule = config.put_config_rule(
        ConfigRule={
            'ConfigRuleName': rule_name,
            'Scope': {
                'ComplianceResourceTypes': [
                    'AWS::S3::BUCKET'
                ]
            },
            'Source': {
                'Owner': 'AWS',
                'SourceIdentifier': rule_name
            }
        }
    )

def 