import random
import time
import boto3
import argparse
from prometheus_client import start_http_server, Gauge, generate_latest
from functools import reduce

PORT = 8000
INTERVAL_IN_SECONDS = 5

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

class EBS(object):
    def __init__(self, prefix='ebs', desc='EBS metrics'):
       self.prefix = prefix
       self.desc = desc
       self.ec2 = boto3.resource('ec2')

       self.metrics = {
               'Total':{
                'Gauge': Gauge(self.prefix + '_total', 'Total number of EBS volumes'),
                'Reducer': (lambda acc, y: acc + 1),
                },
               'EncryptedTotal': {
                'Gauge': Gauge(self.prefix + '_encrypted_total', 'Total number of encrypted EBS volumes'),
                'Reducer': (lambda acc, y: acc + (1 if y.encrypted else 0)),
                },
               'InUseTotal': {
                'Gauge': Gauge(self.prefix + '_in_use_total', 'Total number of in-use EBS volumes'),
                'Reducer': (lambda acc, y: acc + (1 if y.state == 'in-use' else 0)),
                },
        }

    def emit(self):
        all_volumes = list(self.ec2.volumes.all())

        for k in self.metrics:
            x = reduce(self.metrics[k]['Reducer'], all_volumes, 0)
            self.metrics[k]['Gauge'].set(x)


class S3BucketTotal(object):
    def __init__(self, prefix='s3_bucket', desc='Total number of S3 Buckets'):
        self.prefix = prefix
        self.desc = desc
        self.total= Gauge(self.prefix + "_total", self.desc)
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
    EBS(),
    S3BucketTotal()
]


def update_metrics():
    for m in metrics:
        m.emit()


def run_interactive():
    update_metrics()
    print(generate_latest().decode("utf-8"))


def run_daemon():
    print("Running on port {}".format(PORT))
    start_http_server(PORT)

    while True:
        update_metrics()
        time.sleep(INTERVAL_IN_SECONDS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemonize",
                        help="run metrics exporter as a daemon",
                        action="store_true")
    args = parser.parse_args()
    if args.daemonise:
        run_daemon()
    else:
        run_interactive()


if __name__ == '__main__':
    main()
