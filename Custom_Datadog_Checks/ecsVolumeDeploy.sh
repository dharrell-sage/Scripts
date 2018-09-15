#!/bin/bash
if [ ! -f /etc/dd-agent/conf.d/ecsVolume.yaml ] && [ ! -f /etc/dd-agent/checks.d/ecsVolume.py ]
then
    echo "dd-agent ALL=NOPASSWD: /usr/bin/docker" >> /etc/sudoers
    cat >> /etc/dd-agent/checks.d/ecsVolume.py <<EOF1
#!/usr/bin/env python

import json
from checks import AgentCheck
    from subprocess import check_output

class ecsVolume(AgentCheck):
    def check(self, instance):
      metric_prefix = self.init_config.get('metric_prefix', 'ecsVolume')
      EcsStats = self.get_docker_volume_info()
      instanceTags = self.get_instance_info()
      self.gauge('{}.ecsVolumeAvailable'.format(metric_prefix), EcsStats['EcsVA'], tags=instanceTags)
      self.gauge('{}.ecsVolumeTotal'.format(metric_prefix), EcsStats['EcsVT'], tags=instanceTags)
      self.gauge('{}.ecsVolumeUsed'.format(metric_prefix), EcsStats['EcsVU'], tags=instanceTags)

    def get_docker_volume_info(self):
      docker_path = self.init_config.get('docker_path', '/usr/bin/docker')
      docker_output = dict(json.loads(check_output(["sudo", docker_path, "info", "--format", "{{json .DriverStatus}}"])))
      ecsVolumeUsed = ecsVolume.parseSize(docker_output['Data Space Used'])
      ecsVolumeTotal = ecsVolume.parseSize(docker_output['Data Space Total'])
      ecsVolumeAvail = ecsVolume.parseSize(docker_output['Data Space Available'])
      return {'EcsVA': ecsVolumeAvail, 'EcsVT': ecsVolumeTotal, 'EcsVU': ecsVolumeUsed}

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
      units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
      number, unit = [string.strip() for string in sizeSpaced.split()]
      return int(float(number)*units[unit])

if __name__ == '__main__':
    check.check(instance)
EOF1
    cat >> /etc/dd-agent/conf.d/ecsVolume.yaml <<EOF2
init_config:
  metric_prefix: ecsVolume
  docker_path: /usr/bin/docker
  curl_path: /usr/bin/curl

instances:
    [{}]
EOF2
service datadog-agent restart
else
    exit 0
fi
