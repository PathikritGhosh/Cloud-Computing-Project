import boto.ec2
from boto.manage.cmdshell import sshclient_from_instance
from boto.manage.cmdshell import FakeServer
from boto.manage.cmdshell import SSHClient
from get_ipaddr import get_instanceid


# Connect to your region of choice

def connect_ec2instance(instance_id,command):
	print("Trying to connect to " + instance_id)
	conn = boto.ec2.connect_to_region("ap-northeast-1")
	# Find the instance object related to my instanceId
	instance = conn.get_all_instances([instance_id])[0].instances[0]
	# Create an SSH client for our instance
	# key_path is the path to the SSH private key associated with instance
	# user_name is the user to login as on the instance (e.g. ubuntu, ec2-user, etc.)
	ssh_client = sshclient_from_instance(instance,
                                    	'./key1.pem',
                                     	user_name='ec2-user')
	#server = FakeServer(instance,'./key1.pem')
	#ssh_client = SSHClient(server, './key1.pem', 'ec2-user')
	# Run the command. Returns a tuple consisting of:
	#    The integer status of the command
	#    A string containing the output of the command
	#    A string containing the stderr output of the command
	status, stdout, stderr = ssh_client.run(command)
	print(stderr)
	return stdout

def main():
	response = connect_ec2instance('i-085cf8aa9c17b157a','ls -l') 
	print(response)
	print("done")
if __name__ == '__main__':
	main()
	
