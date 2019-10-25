import sys
import subprocess
import time
import re

concurrency = 10
account_id = "99390903"
region = "ap-northeast-1"
image_name = '9939030.dkr.ecr.ap-northeast-1.amazonaws.com/apache5:httpd'
def get_container_instanceid(cluster_name):
	response = subprocess.run("aws ecs list-container-instances"
				+ " --cluster " 
				+ cluster_name 
				+ " > cluster.txt",shell = True)
	with open('cluster.txt', 'r') as myfile:
		data=myfile.read().replace('\n', '')
		"".join(data.split())
	#print(data)
	start_index = (len("{\"containerInstanceArns\":[\"arn:aws:ecs:")
			+ len(region) + 14 + len(account_id)
			+ len(':container-instance/'))
	c_instance_id = data[start_index:-7]
	print(c_instance_id)
	return c_instance_id


def get_instanceid(c_instance_id,cluster_name):
	response = subprocess.run("aws ecs describe-container-instances"
				+ " --cluster " + cluster_name 
				+ " --container-instances " 
				+ c_instance_id 
				+ " > c_instance.txt",shell = True)
	with open('c_instance.txt', 'r') as myfile:
    		data3=myfile.read().replace('\n', ' ')
	"".join(data3.split())
	data4_list = data3.split()
	instance_id = ""
	for i in range(len(data4_list)):
		if(data4_list[i] == "\"ec2InstanceId\":"):
			instance_id = instance_id + data4_list[i + 1]
	instance_id = instance_id[1:-2]
	print(instance_id)
	return instance_id



def get_ipaddress(cluster_name):
	c_instance_id = get_container_instanceid(cluster_name)
	instance_id = get_instanceid(c_instance_id,cluster_name)
	response = subprocess.run("aws ec2 wait instance-running --instance-ids " 
				+ "\"" + instance_id + "\"",shell=True)
	response = subprocess.run("aws ec2 describe-instances --instance-ids " 
				+ instance_id + " > instance_id.txt",shell = True)
	with open('instance_id.txt', 'r') as myfile:
    		data=myfile.read().replace('\n', ' ')
	data.strip()
	data_list = data.split()
	ip_address = ""
	for i in range(len(data_list)):
		if(data_list[i] == "\"PublicIp\""):
			ip_address = ip_address + data_list[i + 1]
			break
	ip_address = ip_address[1:-1]
	return ip_address

def main():
	cluster_name = 'linpackt23micro'
	id1 = get_container_instanceid(cluster_name)
	id2 = get_instanceid(id1,cluster_name)

if __name__ == '__main__':
	main()



