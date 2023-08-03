import boto3
import csv

def get_account_name():
    # Initialize AWS IAM client
    iam_client = boto3.client('iam')

    # Get current AWS account alias (name)
    response = iam_client.list_account_aliases()
    if 'AccountAliases' in response and len(response['AccountAliases']) > 0:
        return response['AccountAliases'][0]
    return "N/A"

def list_all_lambda_functions(lambda_client):
    all_functions = []

    # Initial request to list functions
    response = lambda_client.list_functions()

    # Add functions from the first response
    all_functions.extend(response['Functions'])

    # Continue pagination if more functions are available
    while 'NextMarker' in response:
        next_marker = response['NextMarker']
        response = lambda_client.list_functions(Marker=next_marker)
        all_functions.extend(response['Functions'])

    return all_functions

def list_all_ec2_instances(ec2_client):
    all_instances = []

    # Initial request to list instances
    response = ec2_client.describe_instances()

    # Add instances from the first response
    for reservation in response['Reservations']:
        all_instances.extend(reservation['Instances'])

    # Continue pagination if more instances are available
    while 'NextToken' in response:
        next_token = response['NextToken']
        response = ec2_client.describe_instances(NextToken=next_token)
        for reservation in response['Reservations']:
            all_instances.extend(reservation['Instances'])

    return all_instances

def list_all_rds_instances(rds_client):
    all_instances = []

    # List all RDS instances
    response = rds_client.describe_db_instances()

    # Add instances from the first response
    all_instances.extend(response['DBInstances'])

    # Continue pagination if more instances are available
    while 'Marker' in response:
        marker = response['Marker']
        response = rds_client.describe_db_instances(Marker=marker)
        all_instances.extend(response['DBInstances'])

    return all_instances

def list_resources_with_tags():
    # Initialize AWS clients
    lambda_client = boto3.client('lambda')
    ec2_client = boto3.client('ec2')
    rds_client = boto3.client('rds')

    # Get AWS account name (alias)
    account_name = get_account_name()

    # List all Lambda functions (including pagination)
    all_lambda_functions = list_all_lambda_functions(lambda_client)

    # List all EC2 instances (including pagination)
    all_ec2_instances = list_all_ec2_instances(ec2_client)

    # List all RDS instances (including pagination)
    all_rds_instances = list_all_rds_instances(rds_client)

    # Create a CSV file for writing
    with open('aws_resources.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write header row
        csv_writer.writerow(['Account Name', 'ResourceType', 'Resource Name', 'Technical:PlatformOwner'])

        # Iterate through Lambda functions
        for function in all_lambda_functions:
            function_name = function['FunctionName']
            resource_type = 'Lambda'

            # Get tags for the Lambda function
            tags_response = lambda_client.list_tags(Resource=function['FunctionArn'])

            platform_owner = ''
            if 'Technical:PlatformOwner' in tags_response['Tags']:
                platform_owner = tags_response['Tags']['Technical:PlatformOwner']

            # Write data to CSV file
            csv_writer.writerow([account_name, resource_type, function_name, platform_owner])

        # Iterate through EC2 instances
        for instance in all_ec2_instances:
            instance_id = instance['InstanceId']
            resource_type = 'EC2'

            # Get tags for the EC2 instance
            tags_response = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])

            platform_owner = ''
            for tag in tags_response['Tags']:
                if tag['Key'] == 'Technical:PlatformOwner':
                    platform_owner = tag['Value']
                    break

            # Write data to CSV file
            csv_writer.writerow([account_name, resource_type, instance_id, platform_owner])

        # Iterate through RDS instances
        for rds_instance in all_rds_instances:
            rds_instance_id = rds_instance['DBInstanceIdentifier']
            resource_type = 'RDS'

            # Get tags for the RDS instance
            tags_response = rds_client.list_tags_for_resource(ResourceName=rds_instance['DBInstanceArn'])

            platform_owner = ''
            for tag in tags_response['TagList']:
                if tag['Key'] == 'Technical:PlatformOwner':
                    platform_owner = tag['Value']
                    break

            # Write data to CSV file
            csv_writer.writerow([account_name, resource_type, rds_instance_id, platform_owner])

if __name__ == "__main__":
    list_resources_with_tags()
