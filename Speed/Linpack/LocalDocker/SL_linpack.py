import time
import subprocess

types = 3
vCPUs = [1,2,4]
mem = [4096,8192,15360]

path='/home/clouduser/benchmarks/linpack.tar'

def create_master(machine_type):
	print('Creating master docker-machine')
	subprocess.run('docker-machine create --driver virtualbox --virtualbox-cpu-count %s --virtualbox-memory %s master' %(vCPUs[machine_type],mem[machine_type]),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('docker-machine env master',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('eval \"$(docker-machine env master)\"',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	print('Docker master machine created')

def initialize():
	subprocess.run('docker-machine scp %s master:/home/docker/' %(path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('docker-machine ssh master docker image load -i linpack.tar',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	print('Initialization Completed')

def run_process():
	subprocess.run('docker-machine ssh master docker run -i pathikrit/linpack',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	cmd_to_exec = 'docker-machine ssh master docker logs \'$(docker ps -l -q)\''
	response = subprocess.Popen([cmd_to_exec],shell=True, universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	return response

def write_result(response):
	with open("result_linpack_%s_%s.txt" %(vCPUs[x],mem[x]), 'w') as txt_file:
	    txt_file.write("".join(response.stdout.readlines()))
	print('Speed test done for type --- %s' %x)

def cleanup_process():
	subprocess.run('docker-machine rm -f master',shell=True)
	print('Master docker-machine deleted')

def main():
	for x in range(types):
		create_master(x)
		initialize()
		response = run_process()
		write_result(response)
		cleanup_process()

if __name__ == '__main__':
    main()