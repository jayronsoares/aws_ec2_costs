

CREATE TABLE public.aws_ec2_cost (
    id SERIAL PRIMARY KEY,
    Service TEXT NOT NULL,
    Instance_Type TEXT NOT NULL,
    Cost NUMERIC NOT NULL
);

CREATE TABLE public.cpu_metrics (
    id SERIAL PRIMARY KEY,
    Instance_ID TEXT NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    CPU_Utilization NUMERIC NOT NULL,
    NetworkIn NUMERIC NOT NULL,
    NetworkOut NUMERIC NOT NULL,
    MemoryUtilization NUMERIC NOT NULL,
    VolumeReadBytes NUMERIC NOT NULL,
    VolumeWriteBytes NUMERIC NOT NULL
);

CREATE TABLE public.underutilized_instances (
    id SERIAL PRIMARY KEY,
    Instance_ID TEXT NOT NULL,
    CPU_Utilization NUMERIC NOT NULL
);


INSERT INTO public.aws_ec2_cost (Service, Instance_Type, Cost)
VALUES
    ('Amazon S3', 't2.micro', 10.50),
    ('Amazon EC2', 'm5.large', 25.20),
    ('Amazon RDS', 'db.t2.small', 15.80),
    ('Amazon DynamoDB', 'd2.xlarge', 5.40),
    ('Amazon S3', 't2.nano', 5.10),
    ('Amazon EC2', 't3.medium', 20.30),
    ('Amazon RDS', 'db.t3.micro', 12.40),
    ('Amazon DynamoDB', 'd2.large', 4.80),
    ('Amazon S3', 't3.nano', 6.20),
    ('Amazon EC2', 'm5.xlarge', 30.10);

INSERT INTO public.cpu_metrics (Instance_ID, Timestamp, CPU_Utilization, NetworkIn, NetworkOut, MemoryUtilization, VolumeReadBytes, VolumeWriteBytes)
VALUES
    ('i-12345abcd', '2023-07-25 12:00:00', 15.2, 1000.5, 200.2, 35.5, 1200000, 800000),
    ('i-67890efgh', '2023-07-25 13:00:00', 7.3, 750.2, 150.5, 28.9, 900000, 500000),
    ('i-12345abcd', '2023-07-25 14:00:00', 17.5, 900.8, 180.2, 40.1, 1300000, 850000),
    ('i-67890efgh', '2023-07-25 15:00:00', 9.8, 800.5, 160.1, 30.6, 950000, 550000),
    ('i-12345abcd', '2023-07-25 16:00:00', 12.1, 1100.3, 220.4, 38.2, 1350000, 880000),
    ('i-67890efgh', '2023-07-25 17:00:00', 6.5, 700.1, 140.8, 26.4, 880000, 460000),
    ('i-12345abcd', '2023-07-25 18:00:00', 19.3, 950.6, 190.5, 43.7, 1400000, 920000),
    ('i-67890efgh', '2023-07-25 19:00:00', 8.9, 850.2, 170.3, 31.8, 920000, 510000),
    ('i-12345abcd', '2023-07-25 20:00:00', 14.6, 1050.4, 210.3, 36.9, 1250000, 830000),
    ('i-67890efgh', '2023-07-25 21:00:00', 10.2, 780.7, 156.6, 29.1, 920000, 490000);

INSERT INTO public.underutilized_instances (Instance_ID, CPU_Utilization)
VALUES
    ('i-67890efgh', 4.7),
    ('i-98765ijkl', 3.8),
    ('i-54321zyxw', 2.5),
    ('i-78901wxyz', 4.2),
    ('i-12345abcd', 3.1),
    ('i-67890efgh', 5.8),
    ('i-54321zyxw', 4.5),
    ('i-78901wxyz', 3.9),
    ('i-12345abcd', 5.3),
    ('i-67890efgh', 2.9);
