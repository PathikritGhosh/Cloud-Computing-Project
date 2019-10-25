import sys
import subprocess
import boto3
import time
from AWS.get_ipaddr import get_ipaddress
from AWS.get_ipaddr import get_instanceid
from AWS.get_ipaddr import get_container_instanceid
from AWS.setup_cluster import register_task
from AWS.setup_cluster import create_cluster
from AWS.setup_cluster import wait_instance_running
from AWS.setup_cluster import start_task_service
from AWS.setup_cluster import end_service
from AWS.setup_cluster import delete_cluster
from AWS.connect_ec2 import connect_ec2instance

key_name = "key1"
num_nodes = 1
regions = 'ap-northeast-1'
instance_type_list = ["t2.micro"]#,"t2.medium","m4.2xlarge"]
cluster_name = "linpack"
image_name = '993993.dkr.ecr.ap-northeast-1.amazonaws.com/linpack:linpack'
#print("Enter the Access key")
#ACCESS_KEY = input().strip()
#print("Enter the Secret Key")
#SECRET_KEY = input().strip()


def get_linpack_logs(cluster_name,instance_type):
	command = 'docker logs $(docker ps -l -q)'
	print(command)
	c_instanceid = get_container_instanceid(cluster_name)
	instance_id = get_instanceid(c_instanceid,cluster_name)
	print("Getting docker logs")
	response = connect_ec2instance(instance_id,command)
	text_file = open(cluster_name + "_" + instance_type, "wb")
	text_file.write(response)
	text_file.close()

def main():
	client = boto3.client('ecs')
	for instance_type in instance_type_list:
		cluster_name = "linpack" + instance_type[0:2] +"2"+ instance_type[3:]
		response = subprocess.run("ecs-cli configure --cluster " 
					+ cluster_name,shell = True)
		create_cluster(client,cluster_name,instance_type,key_name)
		time.sleep(60)
		register_task(client,cluster_name,image_name)
		start_task_service(client,cluster_name,image_name)
		time.sleep(60)
		get_linpack_logs(cluster_name,instance_type)
		end_service(client,cluster_name)
		delete_cluster(cluster_name)
	
if __name__ == '__main__':
	main()


