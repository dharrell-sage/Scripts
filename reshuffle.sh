#!/bin/bash

name="arn:aws:lambda:eu-west-1:700326549305:function:move-sqs-messages"
invoketype="Event"
payload="{}"

x=1
while [ $x -le 1000 ]
do
  aws lambda invoke --function-name $name --invocation-type $invoketype --payload $payload --region eu-west-1 testresult.log
  echo $x
  cmd="$(aws lambda invoke --function-name $name --invocation-type $invoketype --payload $payload --region eu-west-1 testresult.log)"

  x=$(( $x + 1 ))
  sleep 1
done
