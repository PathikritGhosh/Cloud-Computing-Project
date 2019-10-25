import sys
import subprocess
import boto3
import time
import json
from AWS.get_ipaddr import get_ipaddress
from AWS.get_ipaddr import get_instanceid
from AWS.get_ipaddr import get_container_instanceid
from AWS.setup_cluster import register_task
from AWS.setup_cluster import wait_instance_running
from AWS.setup_cluster import start_task_service
from AWS.setup_cluster import end_service
from AWS.setup_cluster import delete_cluster
from AWS.setup_cluster import run_task
from AWS.connect_ec2 import connect_ec2instance

key_name = "key1"
num_nodes = 1
regions = 'ap-northeast-1'
instance_type_list = ["m4.2xlarge"]#,"t2.medium","m4.2xlarge","t2.micro"]
num_containers = [5]#,10]
cluster_name = "apache"
image_name = '9992030.dkr.ecr.ap-northeast-1.amazonaws.com/apache5:httpd'


def scale_containers(client,cluster_name,scale_to):
	response = subprocess.run("aws ecs describe-clusters --cluster "+cluster_name,shell=True)
	print("Scaling containers")
	flag=0
	end=0
	start = time.time()
	response = client.update_service(
    		cluster=cluster_name,
    		service=cluster_name,
    		desiredCount=scale_to,
	)

	while flag == 0:
		response = subprocess.run("aws ecs describe-clusters --cluster "
					+ cluster_name
					+" > cluster2.txt",shell = True)
		fp = open("cluster2.txt")
		for i,line in enumerate(fp):
			if len(line) > 33:
				if(line[33] ==str(scale_to)):# or line[33:35] == str(scale_to)):
					end = time.time()
					print(line)
					flag = 1
					break
		fp.close()

			
	end = end - start
	response = subprocess.run("aws ecs describe-clusters --cluster "+cluster_name,shell=True)

	text_file = open(cluster_name + "_" + str(scale_to) + "_", "w")
	text_file.write(str(end))
	text_file.close()

def reduce_containers_1(client,cluster_name):
	response = client.update_service(
    		cluster=cluster_name,
    		service=cluster_name,
    		desiredCount=1,
		)
	#response = subprocess.run("aws ecs update-service --service " 
	#			+ cluster_name 
	#			+ " --desired-count 1",shell=True)
    
			
def create_cluster(client,cluster_name,instance_type,key_name,size):
	subprocess.run("ecs-cli up --keypair "
			+ key_name
			+ " --capability-iam"
			+ " --size " + str(size)
			+ " --security-group sg-963034f1"
			+ " --subnets subnet-0a079e52,subnet-da4817ac"
			+ " --vpc vpc-098e196d"
			+ " --instance-type "
			+ instance_type,shell=True)	

def main():
	client = boto3.client('ecs')
	for instance_type in instance_type_list:
		cluster_name = "apache2" + instance_type[0:2] + "4"+ instance_type[3:]
		response = subprocess.run("ecs-cli configure --cluster " 
					+ cluster_name,shell = True)
		create_cluster(client,cluster_name,instance_type,key_name,5)
		time.sleep(90)
		register_task(client,cluster_name,image_name)
		start_task_service(client,cluster_name,image_name)
		time.sleep(30)
		for scale_to in num_containers:
			scale_containers(client,cluster_name,scale_to)
			
		response = subprocess.run("aws ecs describe-clusters --cluster "+cluster_name,shell=True)	
		end_service(client,cluster_name)
		delete_cluster(cluster_name)

if __name__ == '__main__':
	main()




