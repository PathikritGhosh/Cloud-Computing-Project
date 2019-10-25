import time
import subprocess

types = 3
vCPUs = [1,2,4]
mem = [4096,8192,15360]
tot_containers = [5,10]

subprocess.run('rm SL_scalability_result.txt',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

path='/home/clouduser/benchmarks/httpd.tar'
fp = open("SL_scalability_result.txt","a+")

for x in range(types):
	print('Creating master docker-machine')
	subprocess.run('docker-machine create --driver virtualbox --virtualbox-cpu-count %s --virtualbox-memory %s master' %(vCPUs[x],mem[x]),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('docker-machine env master',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('eval \"$(docker-machine env master)\"',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	print('Docker master machine created')
	subprocess.run('docker-machine scp %s master:/home/docker/' %(path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	subprocess.run('docker-machine ssh master docker image load -i httpd.tar',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	print('Initialization Completed')

	for y in range(2):
		processes = list()
		start_time=time.time()
		for index in range(tot_containers[y]):
			processes.append(subprocess.Popen('docker-machine ssh master docker run -it pathikrit/httpd',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE))
		for pr in processes:
			pr.wait()
		fp.write('Scaling time for %s containers of type --- %s --- is : %s seconds \n' %(tot_containers[y],x,time.time()-start_time))
		subprocess.run('docker rm -f $(docker ps -a -q)',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		print('Scalability test done for %d containers' %tot_containers[y])

	subprocess.run('docker-machine rm -f master',shell=True)
	print('Master docker-machine deleted')
fp.close()
print('Succesfully completed')