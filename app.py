import random
import time

import boto3
from prometheus_client import start_http_server, Gauge

PORT = 8000
INTERVAL_IN_SECONDS = 1

class EIPTotal(object):
    def __init__(self, prefix='eip', desc='Total number of EIPs'):
        self.prefix = prefix
        self.desc = desc
        self.total = Gauge(self.prefix + '_total', self.desc)
        self.in_use_total = Gauge(self.prefix + '_in_use_total', self.desc)
        self.ec2 = boto3.client('ec2')

    def emit(self):
        all_ips = self.ec2.describe_addresses()['Addresses']

        in_use_total = 0
        for ip in all_ips:
            if 'AssociationId' in ip:
                in_use_total += 1

        self.total.set(len(all_ips))
        self.in_use_total.set(in_use_total)


class EBSVolumeTotal(object):
    def __init__(self, prefix='ebs_volumes', desc='Total number of EBS volumes'):
        self.prefix = prefix
        self.desc = desc
        self.total = Gauge(self.prefix + '_total', self.desc)
        self.in_use_total = Gauge(self.prefix + '_in_use_total', self.desc)
        self.ec2 = boto3.resource('ec2')

    def emit(self):
        all_volumes = list(self.ec2.volumes.all())

        in_use_total = 0
        for volume in all_volumes:
            if volume.state == 'in-use':
                in_use_total += 1

        self.total.set(len(all_volumes))
        self.in_use_total.set(in_use_total)

class EBSEncryptedVolumeTotal(object):
    def __init__(self, prefix='ebs_volumes_encrypted', desc='Total number of encrypted EBS volumes'):
        self.prefix = prefix
        self.desc = desc
        self.encrypted_total = Gauge(self.prefix + '_total', self.desc)
        self.ec2 = boto3.resource('ec2')

    def emit(self):
        all_volumes = list(self.ec2.volumes.all())

        encrypted_count = 0
        for volume in all_volumes:
            if volume.encrypted:
                encrypted_count += 1

        self.encrypted_total.set(encrypted_count)


class S3BucketTotal(object):
    def __init__(self, prefix='s3_bucket', desc='Total number of S3 Buckets'):
        self.prefix = prefix
        self.desc = desc
        self.total= Gauge(self.prefix + "total", self.desc)
        self.s3 = boto3.resource('s3')

    def emit(self):
        bucket_count = len(list(self.s3.buckets.all()))
        self.total.set(bucket_count)


class RandomNumber(object):
    def __init__(self, prefix='random_number', desc='A random number'):
        self.prefix = prefix
        self.desc = desc
        self.gauge = Gauge(self.prefix, self.desc)

    def emit(self):
        self.gauge.set(random.random())


metrics = [
    RandomNumber(),
    EIPTotal(),
    EBSVolumeTotal(),
    EBSEncryptedVolumeTotal(),
    S3BucketTotal()
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
