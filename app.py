from prometheus_client import start_http_server, Summary, Gauge
import random
import time

class TotalMounted(object):
    def __init__(self, name='total_mounted', desc=''):
        self.name = name
        self.desc = desc
        self.gauge = Gauge(self.name, self.desc)
    
    def emmit(self):
        result = self.aws_call()
        self.gauge.set(result)

    def aws_call(self):
        return random.random()


metrics = [TotalMounted()]

# Decorate function with metric.
def process_request(t):
    for m in metrics:
        m.emmit()

    time.sleep(t)

def main():
    start_http_server(8000)
    # Generate some requests.
    while True:
        process_request(5)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    main()
