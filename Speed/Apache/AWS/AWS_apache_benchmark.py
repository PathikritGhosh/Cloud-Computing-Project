import sys
import subprocess
import boto3
import time
from AWS.get_ipaddr import get_ipaddress
from AWS.get_ipaddr import get_instanceid
from AWS.get_ipaddr import get_container_instanceid
from AWS.setup_cluster import create_cluster
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
instance_type_list = ["t2.micro"]#,"t2.medium","m4.2xlarge"]
cluster_name = "apache"
image_name = '983993923.dkr.ecr.ap-northeast-1.amazonaws.com/apache5:httpd'

def run_ap_benchmark(cluster_name,n,c):
	#n = number of requests,c = concurrency
	#external_ip = get_ipaddress(cluster_name)
	c_instanceid = get_container_instanceid(cluster_name)
	instance_id = get_instanceid(c_instanceid,cluster_name)
	command = 'yum provides /usr/bin/ab'
	response = connect_ec2instance(instance_id,command)
	command = 'sudo yum -y install httpd-tools'
	response = connect_ec2instance(instance_id,command)
	#print("Benchmarking httpd server at %s with %d connections..." % (external_ip, str(n)))
	command = 'ab -n ' + str(n) + ' -c ' + str(c) + ' http://0.0.0.0/'
	response = connect_ec2instance(instance_id,command)
	text_file = open(cluster_name + "_" + str(n), "wb")
	text_file.write(response)
	text_file.close()

def main():
	client = boto3.client(
    		'ecs'	
	)
	"""fp = open("data.txt")
	l = []
	for i,line in enumerate(fp):
		l.append(line)
	fp.close()
	key_name = l[0]
	regions = l[1]
	image_name = l[2]"""
	for instance_type in instance_type_list:
		cluster_name = "apache" + instance_type[0:2] + "2" + instance_type[3:]
		#response = subprocess.run("ecs-cli configure --cluster " 
		#			+ cluster_name,shell = True)
		#create_cluster(client,cluster_name,instance_type,key_name)
		#time.sleep(60)
		#register_task(client,cluster_name,image_name)
		#start_task_service(client,cluster_name,image_name)
		#run_task(client,cluster_name)
		#time.sleep(60)		
		if instance_type == 't2.micro':
			run_ap_benchmark(cluster_name,100,100)
		#	run_ap_benchmark(cluster_name,1000,100)
		if instance_type == 't2.medium':
			run_ap_benchmark(cluster_name,10000,100)
		if instance_type == 'm4.2xlarge':
			run_ap_benchmark(cluster_name,100000,100)
			run_ap_benchmark(cluster_name,1000000,100)
		end_service(client,cluster_name)
		delete_cluster(cluster_name)

if __name__ == '__main__':
	main()

