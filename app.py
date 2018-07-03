import random
import time

import boto3
from prometheus_client import start_http_server, Gauge

PORT = 8000
INTERVAL_IN_SECONDS = 1

class EBSVolumeCount(object):
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc
        self.total = Gauge(self.name + '_total', self.desc)
        self.in_use = Gauge(self.name + '_in_use', self.desc)
        self.ec2 = boto3.resource('ec2')

    def emit(self):
        all_volumes = list(self.ec2.volumes.all())

        in_use_count = 0
        for volume in all_volumes:
            if volume.state == 'in-use':
                in_use_count += 1

        self.total.set(len(all_volumes))
        self.in_use.set(in_use_count)

class S3BucketCount(object):
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc
        self.gauge = Gauge(self.name, self.desc)
        self.s3 = boto3.resource('s3')

    def emit(self):
        bucket_count = len(list(self.s3.buckets.all()))
        self.gauge.set(bucket_count)


class RandomNumber(object):
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc
        self.gauge = Gauge(self.name, self.desc)

    def emit(self):
        self.gauge.set(random.random())


metrics = [
    RandomNumber('random_number', 'A random number'),
    EBSVolumeCount('ebs_volumes', 'lol'),
    #S3BucketCount('s3_bucket_count', 'The total number of s3 Buckets')
]


def update_metrics():
    for m in metrics:
        m.emit()


def main():
    print("Running on port {}".format(PORT))
    start_http_server(PORT)

    while True:
        update_metrics()
        time.sleep(INTERVAL_IN_SECONDS)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    main()
