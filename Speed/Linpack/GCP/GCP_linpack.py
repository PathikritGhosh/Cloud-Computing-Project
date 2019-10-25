import subprocess
import sys
import time

#from util.gcp_node_configs import *
#asia.gcr.io/enhanced-pen-177514/linpack_asia
#eu.gcr.io/enhanced-pen-177514/linpack_europe
#us.gcr.io/enhanced-pen-177514/linpack_us
#gcr.io/enhanced-pen-177514/linpack
#gcloud config set compute/zone 'asia-east1-a'

machine_types=['n1-standard-2','n1-standard-4','n1-standard-8']
zones=['asia-east1-a','us-central1-a','us-central1-a']
num_nodes = 1
user_name = 'pathikrit'

def create_cluster(cluster_name, instance_type, instance_zone):
    subprocess.check_call('gcloud config set compute/zone %s' %(instance_zone),shell=True)
    subprocess.check_call('gcloud container clusters create %s -m %s -z %s --num-nodes=%s' % (cluster_name, instance_type, instance_zone, str(num_nodes)), shell=True)
    subprocess.check_call('gcloud container clusters get-credentials ' + cluster_name, shell=True)

def deploy_benchmark():
    subprocess.check_call('kubectl run linpack --image=gcr.io/enhanced-pen-177514/linpack --port=8080', shell=True)
    subprocess.check_call('kubectl get deployments', shell=True)
    print("Deployments got")
    subprocess.check_call('kubectl get pods', shell=True)
    print("Pods got")

def get_response():
    node_desc = dict()
    active_nodes = list()
    response = subprocess.run('kubectl describe nodes', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for line in response.stdout.split('\n'):
        print(line)
        if 'Name:' in line:
            node_desc['Name'] = line.split(':')[1].strip()
            node_desc['Task'] = node_desc['Name'].split('-')[1]
        if 'instance-type=' in line:
            node_desc['Type'] = line.split("=")[-1]
        if 'zone=' in line:
            node_desc['Zone'] = line.split("=")[-1]
        if 'ExternalIP:' in line:
            node_desc['IP'] = line.split(':')[1].strip().split(',')[-1]
            active_nodes.append(node_desc)
    return node_desc, active_nodes

def record_data(node_desc, active_nodes):
    for node_desc in active_nodes:
        cmd_to_exec = "'docker logs $(docker ps -l -q)'"
        response = subprocess.run(['ssh -i "~/.ssh/google_compute_engine" -o StrictHostKeyChecking=no %s@%s ' % (node_desc['Name'], node_desc['IP']) + cmd_to_exec],
                               shell=True, universal_newlines=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        with open("data_linpack/gcp_%s_%s.txt" % (node_desc['Type'], node_desc['Zone']), 'w') as txt_file:
        txt_file.write("".join(response.stdout.readlines()))

def main():
    for x in range(3):
        cluster_name = "lp-%s-%s-%s" %(machine_types[x], zones[x], str(num_nodes))
        create_cluster(cluster_name, machine_types[x], zones[x])
        deploy_benchmark()
        get_response()
        print("Waiting for Linpack benchmark to execute...")
        time.sleep(300)
        print("Done:Waiting for Linpack benchmark to execute...")
        node_desc, active_nodes = get_response()
        record_data(node_desc, active_nodes)
        subprocess.check_call('gcloud container clusters delete %s' % cluster_name, shell=True)

if __name__ == '__main__':
    main()
