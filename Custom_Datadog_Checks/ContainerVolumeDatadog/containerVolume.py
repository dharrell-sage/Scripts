#!/usr/bin/env python

import json
#import logging
from checks import AgentCheck
from subprocess import check_output

#logging.basicConfig(filename='/tmp/containerVolume.log',level=logging.DEBUG)

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

# create a file handler
#handler = logging.FileHandler('/tmp/containerVolume.log')
#handler.setLevel(logging.DEBUG)

# create a logging format
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)

# add the handlers to the logger
#logger.addHandler(handler)

#logger.info('Hello.baby')

class containerVolume(AgentCheck):
    def check(self, instance):
        #logger.debug('hello.world')
        metric_prefix = self.init_config.get('metric_prefix', 'containerVolume')
        container_DF = self.container_df()
        instanceTags = self.get_instance_info()
        #logger.debug(instanceTags)
        for id, metric in container_DF.iteritems():
            #logger.debug(id,metric)
            TAGS = instanceTags
            CID = 'container_ID:{}'.format(id)
            CN = 'container_Name:{}'.format(metric['container_Name'])
            TAGS.extend([CID, CN])
            #logger.debug(TAGS)
            self.gauge('{}.Available'.format(metric_prefix), metric['volume_Info']['avail'], tags=TAGS)
            self.gauge('{}.Total'.format(metric_prefix), metric['volume_Info']['size'], tags=TAGS)
            self.gauge('{}.Used'.format(metric_prefix), metric['volume_Info']['used'], tags=TAGS)

    def container_df(self):
        docker_path = self.init_config.get('docker_path', '/usr/bin/docker')
        containerData = check_output(["sudo", docker_path, "container", "ls", "--format", "{{json .ID}}"]).replace('"',"").split("\n")
        containerJson = {}
        for id in containerData[:-1]:
            containerJson[id] = json.loads(check_output(["sudo", docker_path, "inspect", "--format", "{{json .}}", id]))

        hostDfStats = []
        df_path = self.init_config.get('df_path', '/bin/df')
        hostDf = check_output(["sudo", df_path])
        for line in hostDf.split("\n"):
            if "devicemapper" in line:
                hostDfStats.append(line)

        hostVolumeData = {}
        for stat in hostDfStats:
            h = stat.split()
            v = {}
            v['fs'] = h[0]
            v['size'] = h[1]
            v['used'] = h[2]
            v['avail'] = h[3]
            v['id'] = h[5].split("/")[-1]
            hostVolumeData[v['id']] = v

        finalForm = {}
        for key, value in containerJson.iteritems():
            deviceId = value['GraphDriver']['Data']['DeviceName'].split("-")[-1]
            containerName = value['Name']
            containerId = value['Id']
            volumeInfo = hostVolumeData[deviceId]
            finalForm[key] = {'device_Id': deviceId, 'container_Name': containerName, 'container_ID': containerId, 'volume_Info': volumeInfo}
            #logger.debug(finalForm)
        return finalForm

    def get_instance_info(self):
        curl_path = self.init_config.get('curl_path', '/usr/bin/curl')
        cat_path = self.init_config.get('cat_path', '/bin/cat')
        instanceId = check_output([curl_path, "http://169.254.169.254/latest/meta-data/instance-id/"])
        ecsCluster = check_output([cat_path, "/etc/ecs/ecs.config"]).replace("=", ":")
        return ['instance_id:{}'.format(instanceId), ecsCluster.split()[0]]

if __name__ == '__main__':
    check.check(instance)
