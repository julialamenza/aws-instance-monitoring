import boto3
import random
import datetime
from tabulate import tabulate
import time

def get_ec2_client(region):
    """Create and return an EC2 client for the specified region"""
    return boto3.client('ec2', region_name=region)

def get_ec2_instances(region):
    """Retrieve and return information about EC2 instances in the specified region"""
    ec2_client = get_ec2_client(region)
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'IP': instance['PrivateIpAddress'],
                'SERVICE': instance['Tags'][0]['Value'],  # Assuming service name is stored in a tag
                'STATUS': instance['State']['Name'],
                'CPU': get_instance_cpu_usage(region, instance['InstanceId']),
                'MEMORY': get_instance_memory_usage(region, instance['InstanceId'])
            })
    return instances

def get_instance_cpu_usage(region, instance_id):
    """Retrieve and return CPU usage of an EC2 instance in the specified region"""
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),  # Adjust the time range as needed
        EndTime=datetime.datetime.utcnow(),
        Period=60,  # Adjust the period as needed
        Statistics=['Average'],
        Unit='Percent'
    )
    datapoints = response['Datapoints']
    if datapoints:
        latest_datapoint = sorted(datapoints, key=lambda x: x['Timestamp'], reverse=True)[0]
        cpu_utilization = latest_datapoint['Average']
        return f'{cpu_utilization:.2f}%'
    else:
        return 'N/A'
    
def get_instance_memory_usage(region, instance_id):
    """Retrieve and return memory usage of an EC2 instance in the specified region"""
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    response = cloudwatch_client.get_metric_statistics(
        Namespace='System/Linux',
        MetricName='MemoryUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),  # Adjust the time range as needed
        EndTime=datetime.datetime.utcnow(),
        Period=60,  # Adjust the period as needed
        Statistics=['Average'],
        Unit='Percent'
    )
    datapoints = response['Datapoints']
    if datapoints:
        latest_datapoint = sorted(datapoints, key=lambda x: x['Timestamp'], reverse=True)[0]
        memory_utilization = latest_datapoint['Average']
        return f'{memory_utilization:.2f}%'
    else:
        return 'N/A'

def print_running_services(region):
    """Print the running services and their statistics in the specified region"""
    instances = get_ec2_instances(region)
    headers = ['IP', 'SERVICE', 'STATUS', 'CPU', 'MEMORY']
    rows = []
    for instance in instances:
        rows.append([
            instance['IP'],
            instance['SERVICE'],
            instance['STATUS'],
            instance['CPU'],
            instance['MEMORY']
        ])
    print(tabulate(rows, headers=headers))


def print_average_stats_by_service(region):
    """Print the average CPU and memory of services of the same type in the specified region"""
    instances = get_ec2_instances(region)
    service_stats = {}
    for instance in instances:
        service = instance['SERVICE']
        if service not in service_stats:
            service_stats[service] = {
                'CPU': [],
                'MEMORY': []
            }
        cpu_usage = instance['CPU']
        memory_usage = instance['MEMORY']
        if cpu_usage != 'N/A':
            cpu_usage = float(cpu_usage[:-1])
        else:
            cpu_usage = None
        if memory_usage != 'N/A':
            memory_usage = int(memory_usage[:-1])
        else:
            memory_usage = None
        service_stats[service]['CPU'].append(cpu_usage)
        service_stats[service]['MEMORY'].append(memory_usage)
    headers = ['SERVICE', 'AVERAGE CPU', 'AVERAGE MEMORY']
    rows = []
    for service, stats in service_stats.items():
        cpu_values = [value for value in stats['CPU'] if value is not None]
        average_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else None
        memory_values = [value for value in stats['MEMORY'] if value is not None]
        average_memory = sum(memory_values) / len(memory_values) if memory_values else None
        if average_cpu is not None:
            average_cpu = f'{average_cpu:.2f}%'
        if average_memory is not None:
            average_memory = f'{average_memory:.2f}%'
        rows.append([service, average_cpu, average_memory])
    print(tabulate(rows, headers=headers))
    
def print_flagged_services(region):
    """Print services with fewer than 2 healthy instances in the specified region"""
    instances = get_ec2_instances(region)
    flagged_services = {}
    for instance in instances:
        service = instance['SERVICE']
        if instance['STATUS'] == 'running':
            if service not in flagged_services:
                flagged_services[service] = 0
            flagged_services[service] += 1
    flagged_services = {service: count for service, count in flagged_services.items() if count < 2}
    headers = ['SERVICE']
    rows = [[service] for service in flagged_services.keys()]
    print(tabulate(rows, headers=headers))

def track_service_stats(region, service):
    """Track and print CPU/Memory of all instances of a given service over time in the specified region"""
    print(f"Tracking CPU/Memory of instances for service: {service}")
    while True:
        instances = get_ec2_instances(region)
        filtered_instances = [instance for instance in instances if instance['SERVICE'] == service]
        headers = ['IP', 'SERVICE', 'STATUS', 'CPU', 'MEMORY']
        rows = []
        for instance in filtered_instances:
            rows.append([
                instance['IP'],
                instance['SERVICE'],
                instance['STATUS'],
                instance['CPU'],
                instance['MEMORY']
            ])
        print(tabulate(rows, headers=headers))
        time.sleep(10)  # Adjust the interval as needed

def main():
    region = input("Enter the AWS region: ")
    while True:
        print("1. Print running services")
        print("2. Print average CPU and memory of services")
        print("3. Print flagged services")
        print("4. Track CPU/Memory of instances for a service")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            print_running_services(region)
        elif choice == '2':
            print_average_stats_by_service(region)
        elif choice == '3':
            print_flagged_services(region)
        elif choice == '4':
            service = input("Enter the service to track: ")
            track_service_stats(region, service)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
