import random
import time

import boto3
from prometheus_client import start_http_server, Gauge

PORT = 8000


class GaugeMetric(object):
    def __init__(self, aws_call, name, desc=''):
        self.aws_call = aws_call
        self.name = name
        self.desc = desc
        self.gauge = Gauge(self.name, self.desc)

    def emit(self):
        result = self.aws_call()
        self.gauge.set(result)


def random_number():
    return random.random()


def s3_bucket_count():
    s3 = boto3.resource('s3')
    res = len(list(s3.buckets.all()))
    return res


metrics = [
    GaugeMetric(random_number, 'random_number'),
    GaugeMetric(s3_bucket_count, 's3_bucket_count')
]


# Decorate function with metric.
def process_request(t):
    for m in metrics:
        m.emit()

    time.sleep(t)


def main():
    print("Running on port {}".format(PORT))
    start_http_server(PORT)
    # Generate some requests.
    while True:
        process_request(5)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    main()
