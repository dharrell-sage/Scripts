#!/bin/bash
# Name: MeterReader.sh
# Author: Dustin Harrell
# Version: v1.0.0

usage=$(cat <<EOFq
MeterReader.sh [Region] [Landscape] [Environment] [Application] [Version]... [--help]
---
        Example: MeterReader.sh STRING STRING STRING STRING STRING
EOF
)

if [ -z $1 ] || [ $1 == "--help" ]
    then
        echo
        echo "${usage}"
        echo
        exit 1
elif [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ]
    then
        echo
        echo "Error: Too few options:"
        echo
        echo "${usage}"
        echo
        exit 1
fi

get_params () {
aws --region=$1 ssm get-parameters --names $2.$3.$4.$5 --with-decryption --output json | jq ". base64 --decode | gunzip -9 | python -m json.tool
}

get_params $1 $2 $3 $4 $5
