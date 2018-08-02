#!/usr/bin/env python

import argparse
import boto3
import logging

def entry():
    config = parse_config()
    ssmClient = boto3.client('ssm', region_name=config['region'])
    runDoc = file_handle(config)
    if config['action'] == "Create":
      create_cmd(ssmClient,runDoc,config)
      
    if config['action'] == "Update":
      update_cmd(ssmClient,runDoc,config)

def parse_config():
    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('ACTION', metavar='[ACTION]', choices=['Update', 'Create'], help='Action to be taken')
    parser.add_argument('TYPE', metavar='[TYPE]', choices=['Command', 'Policy', 'Automation'], help='Type of document to be uploaded')
    parser.add_argument('FORMAT', metavar='[FORMAT]', choices=['YAML','JSON'], help='Location/Name of the Script')
    parser.add_argument('FILE', metavar='[FILE]', help='Location/Name of the Script')
    parser.add_argument('--REGION', metavar='[REGION]', help='AWS region where this document will or does reside')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = {}

    config['action'] = args.ACTION
    config['docType'] = args.TYPE
    config['docFormat'] = args.FORMAT.upper()
    config['file'] = args.FILE
    config['name'] = args.FILE.split('/')[-1].split('.')[0]
    config['region'] = args.REGION.lower()

    #print config
    return config

def file_handle(config):
  open_obj = open(config['file'], 'r')
  file_obj = open_obj.read()
  open_obj.close()
  return file_obj

def create_cmd(ssmClient,content,config):
  response = ssmClient.create_document(
    Content=content,
    Name=config['name'],
    DocumentType=config['docType'],
    DocumentFormat=config['docFormat'],
    TargetType='/AWS::EC2::Instance'
  )
  #return response

def update_cmd(ssmClient,content,config):
  response = ssmClient.update_document(
    Content=content,
    Name=config['name'],
    DocumentVersion='$LATEST',
    DocumentFormat=config['docFormat'],
    TargetType='/AWS::EC2::Instance'
  )
  #print response

if __name__ == "__main__":
  entry()