#!/usr/bin/env python

import argparse
import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

iam_client = boto3.client('iam')

def main():
    config = parse_config()
    #print config
    deactive_console(config)
    keyObj = get_access_keys(config)
    #print keyObj
    disable_access_keys(keyObj)

def parse_config():
    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('--FILE', metavar='[FILENAME]', help='Filename of AWS user list.')
    parser.add_argument('--USER', metavar='[USERNAME]', help='Single Username of AWS user.')
    args = parser.parse_args()

    config = []

    if args.FILE:
        filename = args.FILE
        userlist = open(filename, "r")
        for user in userlist.readlines():
            config.append(user.rstrip("\n"))
        userlist.close()
    elif args.USER:
        config.append(args.USER)

    return config

# Assumption: Console Deactivation needed for all users passed into this script.
def deactive_console(config):
    for user in config:
        response = iam_client.delete_login_profile(UserName=user)
        logger.info("The password for {user} has been disabled".format(user=user))

# Assumption: All users that have Access Keys should have them disabled.
def get_access_keys(config):
    access_key_list = []
    for user in config:
        response = iam_client.list_access_keys(UserName=user)
        for access_key in response['AccessKeyMetadata']:
            try:
                access_key_list.append({'user': user, 'access_key': access_key['AccessKeyId']})
            except KeyError:
                # pass if there is no access key associated with the user.
                # AccessKeyId key will not exist.
                pass

    return access_key_list

def disable_access_keys(key_object):
    for object in key_object:
        try:
            response = iam_client.update_access_key(
                UserName=object['user'],
                AccessKeyId=object['access_key'],
                Status='Inactive'
            )
            logger.info("{user}: {access_key}".format(user=object['user'], access_key=['access_key']))
        except:
            logger.info("Key deactivation failed for {user}: {access_key}").format(user=object['user'], access_key=['access_key'])

if __name__ == "__main__":
    main()
