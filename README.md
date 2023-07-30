## AWS Cost and CloudWatch Metrics Dashboard

The AWS Cost and CloudWatch Metrics Dashboard is a simple web application built with Flask that provides insights into AWS cost data and CloudWatch metrics for EC2 instances. The app fetches AWS cost data and CPU utilization metrics from CloudWatch, inserts the data into a PostgreSQL database, and displays it in an interactive HTML dashboard.

## Features

- Fetches AWS cost data for a specified time period and displays it in a tabular format.
- Retrieves CPU utilization, NetworkIn, NetworkOut, MemoryUtilization, VolumeReadBytes, and VolumeWriteBytes metrics for each EC2 instance.
- Identifies idle or underutilized instances based on their average CPU utilization.
- Utilizes SQLAlchemy for database interaction, allowing data to be stored efficiently in a PostgreSQL database.
- Gracefully handles AWS credentials errors to ensure uninterrupted execution.

## Getting Started

1. Install the required libraries using `pip`:

```
pip install flask boto3 pandas psycopg2 sqlalchemy
```

2. Set the following environment variables:

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `POSTGRES_USERNAME`: PostgreSQL database username
- `POSTGRES_PASSWORD`: PostgreSQL database password
- `POSTGRES_HOST`: PostgreSQL database host
- `POSTGRES_DATABASE`: PostgreSQL database name

3. Run the Flask app:

```
python app.py
```

4. Visit `http://127.0.0.1:5000/` in your web browser to explore the AWS cost and CloudWatch metrics data.

## Notes

- The app fetches AWS cost data for a specified time period (e.g., last 30 days).
- CloudWatch metrics data is fetched for the last 7 days.
- The app uses pagination to efficiently fetch large amounts of CloudWatch data.

This app serves as a proof of concept to demonstrate how to collect and analyze AWS cost data and CloudWatch metrics for EC2 instances, allowing users to make informed decisions to optimize their cloud costs.
