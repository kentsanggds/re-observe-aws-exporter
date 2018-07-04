# re-observe-aws-exporter

A spike into getting some of potentially interesting metrics from the AWS API that aren't surfaced through CloudWatch.

## Credentials

You'll need to make sure boto3 can make API calls. It reads this from the environment. This means you'll probably need to set the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` and possibly `AWS_SESSION_TOKEN` environment variables.

## Running

You can run it locally with `python app.py`. You can spin up a Prometheus, Grafana and instance of the app with `docker-compose up`
