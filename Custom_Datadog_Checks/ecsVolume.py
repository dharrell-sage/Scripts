#!/usr/bin/env python

import json
from checks import AgentCheck
from subprocess import check_output

class ecsVolume(AgentCheck):
    def check(self, instance):
      metric_prefix = self.init_config.get('metric_prefix', 'ecsVolume')
      ecsSpaceAvailable = self.get_docker_volume_info()
      instanceTags = self.get_instance_info()
      self.gauge('{}.ecsVolumeAvailable'.format(metric_prefix), ecsSpaceAvailable, tags=instanceTags)

    def get_docker_volume_info(self):
      docker_path = self.init_config.get('docker_path', '/usr/bin/docker')
      docker_output = dict(json.loads(check_output(["sudo", docker_path, "info", "--format", "{{json .DriverStatus}}"])))
      ecsVolumeAvail = ecsVolume.parseSize(docker_output['Data Space Available'])
      return ecsVolumeAvail

    def get_instance_info(self):
      curl_path = self.init_config.get('curl_path', '/usr/bin/curl')
      instanceId = check_output([curl_path, "http://169.254.169.254/latest/meta-data/instance-id/"])
      ecsCluster = check_output(["cat", "/etc/ecs/ecs.config"]).replace("=", ":")
      return [
        'instance_id:{}'.format(instanceId),
        ecsCluster
      ]
    
    @staticmethod
    def parseSize(size):
      sizeSpaced = size[:-2] + " " + size[-2:]
      units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}
      number, unit = [string.strip() for string in sizeSpaced.split()]
      return int(float(number)*units[unit])

if __name__ == '__main__':
    check.check(instance)