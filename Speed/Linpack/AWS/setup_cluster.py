import sys
import subprocess
import boto3
import time


def create_cluster(client,cluster_name,instance_type,key_name):
	subprocess.run("ecs-cli up --keypair "
			+ key_name
			+ " --capability-iam"
			+ " --size 1"
			+ " --security-group sg-963034f1"
			+ " --subnets subnet-0a079e52,subnet-da4817ac"
			+ " --vpc vpc-098e196d"
			+ " --instance-type "
			+ instance_type,shell=True)

def wait_instance_running(cluster_name):
	data = ""
	while len(data) < 130:
		response = subprocess.run("aws ecs list-container-instances"
					+ "--cluster " 
					+ cluster_name 
					+ " > cluster.txt",shell=True)
		with open('cluster.txt', 'r') as myfile:
    			data=myfile.read().replace(" ","")

def register_task(client,cluster_name,image_name):
	response = client.register_task_definition(
    		family=cluster_name,
    		networkMode='bridge',
    		containerDefinitions=[
        	{
			'name': cluster_name,
            		'image': image_name,
            		'cpu': 10,
            		'memory': 300,
            		'memoryReservation': 123,
           		'essential': True,
			'portMappings': [
				{
					"hostPort": 80,
					"containerPort": 80,
					"protocol": "tcp"
				},
			],
        	},
		
    		],

	)
def start_task_service(client,cluster_name,image_name):	
	print("Task registered")
	time.sleep(20)
	response = client.create_service(
    		cluster=cluster_name,
    		serviceName=cluster_name,
   		taskDefinition=cluster_name + ':1',
    		desiredCount=1,
    		deploymentConfiguration={
        		'maximumPercent': 200,
        		'minimumHealthyPercent': 50
    		},
	)
	print("Service Created")
	time.sleep(20)
	
def run_task(client,cluster_name):
	response = client.run_task(
    		cluster=cluster_name,
    		taskDefinition=cluster_name+':1',
	)
	print("Task Started")
	time.sleep(20)
def end_service(client,cluster_name):
	response = client.update_service(
    		cluster=cluster_name,
    		service=cluster_name,
    		desiredCount=0,
    
	)
	response = client.delete_service(
    		cluster=cluster_name,
    		service=cluster_name,
	)
	response = subprocess.run("aws ecs delete-service --service " 
				+ cluster_name,shell = True)
		
def delete_cluster(cluster_name):
	response = subprocess.run('ecs-cli down --force',shell = True)
