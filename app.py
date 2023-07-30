import os
import boto3
import pandas as pd
from flask import Flask, render_template, g
from sqlalchemy import create_engine
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

app = Flask(__name__)

# AWS Credentials and Region
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = 'us-east-1'

# PostgreSQL Database Credentials
db_username = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_host = os.environ.get('POSTGRES_HOST')
db_name = os.environ.get('POSTGRES_DATABASE')

# SQLAlchemy Database Connection
engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}')

# Helper function to fetch AWS cost data using Boto3 with generators
def fetch_aws_cost_data():
    try:
        ce = boto3.client('ce', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Set the time period for which you want to fetch the cost data (e.g., last 30 days)
        time_period = {
            'Start': '2023-06-26',
            'End': '2023-07-26'
        }

        # Fetch AWS cost data with generators
        paginator = ce.get_paginator('get_cost_and_usage')
        response_iterator = paginator.paginate(
            TimePeriod=time_period,
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                },
                {
                    'Type': 'DIMENSION',
                    'Key': 'INSTANCE_TYPE'
                }
            ]
        )

        for response in response_iterator:
            for group in response['ResultsByTime'][0]['Groups']:
                service, instance_type = group['Keys']
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                yield {'Service': service, 'Instance_Type': instance_type, 'Cost': cost}

    except ClientError as e:
        print("Error fetching AWS cost data:", e)

# Helper function to fetch CPU utilization and additional metrics data from CloudWatch with generators
def fetch_cpu_metrics_data():
    try:
        # Initialize CloudWatch client
        cloudwatch = boto3.client('cloudwatch', region_name=region_name,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)

        # Get the list of all EC2 instances in your account and region
        ec2 = boto3.resource('ec2', region_name=region_name,
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)
        instances = ec2.instances.all()

        # Set the time range for which you want to fetch metric data (e.g., last 7 days)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        # Fetch metric data from CloudWatch with generators
        for instance in instances:
            # Skip instances that are not running
            if instance.state['Name'] != 'running':
                continue

            instance_id = instance.id

            paginator = cloudwatch.get_paginator('get_metric_data')
            response_iterator = paginator.paginate(
                MetricDataQueries=[
                    {
                        'Id': 'cpu_utilization',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'CPUUtilization',
                                'Dimensions': [
                                    {
                                        'Name': 'InstanceId',
                                        'Value': instance_id
                                    },
                                ]
                            },
                            'Period': 3600,  # 1 hour intervals
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                    {
                        'Id': 'network_in',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'NetworkIn',
                                'Dimensions': [
                                    {
                                        'Name': 'InstanceId',
                                        'Value': instance_id
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                    {
                        'Id': 'network_out',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EC2',
                                'MetricName': 'NetworkOut',
                                'Dimensions': [
                                    {
                                        'Name': 'InstanceId',
                                        'Value': instance_id
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                    {
                        'Id': 'memory_utilization',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'CWAgent',
                                'MetricName': 'MemoryUtilization',
                                'Dimensions': [
                                    {
                                        'Name': 'InstanceId',
                                        'Value': instance_id
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                    {
                        'Id': 'volume_read_bytes',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EBS',
                                'MetricName': 'VolumeReadBytes',
                                'Dimensions': [
                                    {
                                        'Name': 'VolumeId',
                                        'Value': instance.block_device_mappings[0]['Ebs']['VolumeId']
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                    {
                        'Id': 'volume_write_bytes',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/EBS',
                                'MetricName': 'VolumeWriteBytes',
                                'Dimensions': [
                                    {
                                        'Name': 'VolumeId',
                                        'Value': instance.block_device_mappings[0]['Ebs']['VolumeId']
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Average',
                        },
                        'ReturnData': True,
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
            )

            for response in response_iterator:
                for metric_data_result in response['MetricDataResults']:
                    data = {
                        'Instance_ID': instance_id,
                        'Timestamp': metric_data_result['Timestamps'][0],
                        'CPU_Utilization': metric_data_result['Values'][0],
                        'NetworkIn': metric_data_result['Values'][1],
                        'NetworkOut': metric_data_result['Values'][2],
                        'MemoryUtilization': metric_data_result['Values'][3],
                        'VolumeReadBytes': metric_data_result['Values'][4],
                        'VolumeWriteBytes': metric_data_result['Values'][5],
                    }
                    yield data

    except Exception as e:
        print("Error fetching metrics data from CloudWatch:", e)

# Helper function for identifying idle or underutilized resources with generators
def identify_underutilized_instances(cpu_metrics_data):
    try:
        underutilized_instances = []
        instance_data = {}

        for data in cpu_metrics_data:
            instance_id = data['Instance_ID']
            if instance_id not in instance_data:
                instance_data[instance_id] = {'count': 0, 'cpu_sum': 0}

            instance_data[instance_id]['count'] += 1
            instance_data[instance_id]['cpu_sum'] += data['CPU_Utilization']

        for instance_id, metrics in instance_data.items():
            average_cpu_utilization = metrics['cpu_sum'] / metrics['count']
            if average_cpu_utilization < 5.0:
                underutilized_instances.append({'Instance_ID': instance_id, 'CPU_Utilization': average_cpu_utilization})

        return underutilized_instances

    except Exception as e:
        print("Error identifying underutilized instances:", e)

# Function to fetch data from the database or cache using generators
def get_data():
    data = g.get('data')
    if data is None:
        data = fetch_data()
        g.data = data
    return data

# Function to fetch data from the database using generators
def fetch_data():
    try:
        with engine.connect() as connection:
            aws_cost_data = pd.read_sql_table('aws_ec2_cost', connection)
            cpu_metrics_data = pd.read_sql_table('cpu_metrics', connection)
            underutilized_instances = pd.read_sql_table('underutilized_instances', connection)

        return {
            'aws_cost_data': aws_cost_data.to_dict(orient='records'),
            'cpu_metrics_data': cpu_metrics_data.to_dict(orient='records'),
            'underutilized_instances': underutilized_instances.to_dict(orient='records')
        }

    except Exception as e:
        print("Error fetching data from PostgreSQL database:", e)

@app.route('/')
def index():
    data = get_data()
    return render_template('index.html', **data)

if __name__ == "__main__":
    # Create the engine and connect to the PostgreSQL database
    engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}')
    app.run(debug=True)
