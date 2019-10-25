import sys
import subprocess
import time

'''
Run these commands beforehand
subprocess.check_call('gcloud auth application-default login', shell=True)
subprocess.check_call('gcloud auth login 'emailid'',shell=True)
subprocess.check_call('gcloud config set compute/zone asia-east1-a',shell=True)
'''

machine_zone_pairs = [('n1-standard-2','asia-east1-a'),('n1-standard-4','asia-east1-a'),('n1-standard-8','asia-east1-a')]


def create_cluster(cluster_name, node_type, node_zone):
    subprocess.check_call('gcloud container clusters create %s -m %s -z %s --num-nodes=%s' % (cluster_name, node_type, node_zone, str(1)), shell=True)
    subprocess.check_call('gcloud container clusters get-credentials ' + cluster_name , shell=True)

def small_scaling(cluster_name):
    start_time = time.time()
    proc = subprocess.check_call('gcloud container clusters resize %s -q --size 5' % cluster_name, shell=True)
    print("Scaling 1 to 5 nodes: --- %s seconds ---" % (time.time() - start_time))
    subprocess.check_call('gcloud container clusters resize %s -q --size 0' % cluster_name, shell=True)

def large_scaling(cluster_name):
    start_time = time.time()
    subprocess.check_call('gcloud container clusters resize %s -q --size 10' % cluster_name, shell=True)
    print("Scaling 1 to 10 nodes: --- %s seconds ---" % (time.time() - start_time))

def clean_up(cluster_name):
    subprocess.check_call('gcloud container clusters delete -q %s' % cluster_name, shell=True)

def main():
    for node_pair in machine_zone_pairs:
        node_type = node_pair[0]
        node_zone = node_pair[1]
        cluster_name = "sc-%s-%s-%s" %(node_type, node_zone, str(1))
        print("cluster_name")
        create_cluster(cluster_name, node_type, node_zone)
        small_scaling(cluster_name)
        large_scaling(cluster_name)
        clean_up(cluster_name)

if __name__ == '__main__':
    main()
