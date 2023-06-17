## AWS EC2 Instance Monitoring

This script allows you to monitor and analyze the CPU and memory usage of Amazon EC2 instances in a specific AWS region.

### Prerequisites

- Python 3.6 or above
- boto3 library (install via pip install boto3)
- tabulate library (install via pip install tabulate)
- AWS credentials with appropriate permissions to access EC2 instances and CloudWatch metrics

### Setup

1. Clone the repository or download the script file: aws-cli.py.
2. Install the required Python libraries mentioned in the prerequisites.
3. Configure your AWS credentials using one of the following methods:

   - [Shared credentials file](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
   - [Environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)

### Usage

1. Open a terminal or command prompt.
2. Navigate to the directory where the script is located.
3. Run the script using the following command: python aws-cli.py.
4. Enter the AWS region when prompted.
5. Choose one of the available options:
   1. Print running services: Displays a table of running EC2 instances, their IP addresses, associated services, status, CPU usage, and memory usage.
   2. Print average CPU and memory of services: Calculates and displays the average CPU and memory usage of instances grouped by service.
   3. Print flagged services: Lists services with fewer than 2 healthy instances.
   4. Track CPU/Memory of instances for a service: Tracks and prints the CPU and memory usage of instances for a specific service over time.
   5. Exit: Exits the script.

Follow the instructions based on your chosen option.
**Note**: The script relies on the boto3 library and AWS credentials for accessing EC2 instances and CloudWatch metrics. Ensure that your credentials have appropriate permissions to retrieve the required information.
