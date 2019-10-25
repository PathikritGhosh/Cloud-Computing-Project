import subprocess
from util.gcp_node_configs import *

user_name = 'xxsxx'
num_nodes = 1
concurrency = 100
machine_zone_pairs = [('n1-standard-4', 'us-central1-a'), ('n1-standard-8','europe-west1-b')]

def deploy(cluster_name, machine_type, zone):
    subprocess.run('gcloud auth application-default login', shell=True)
    subprocess.run('gcloud container clusters create %s -m %s -z %s --num-nodes=%s' % (cluster_name, machine_type, zone, str(num_nodes)), shell=True)
    subprocess.run('gcloud container clusters get-credentials ' + cluster_name, shell=True)
    subprocess.run('kubectl run httpd-node --image=asia.gcr.io/my-project-1470428279137/httpd --port=8080', shell=True)
    subprocess.run('kubectl get deployments && kubectl get pods', shell=True)
    subprocess.run('kubectl expose deployment httpd-node --port=80 --target-port=80 --type="LoadBalancer"', shell=True)

def parse_response():
    response = subprocess.run('kubectl get services httpd-node', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    external_ip = None
    for line in response.stdout.split('\n'):
        if 'httpd-node' in line:
            external_ip = line.split()[2]
            break
    if external_ip is None:
        print("ERROR: Deployment not exposed!")
        exit()
    return external_ip

def record(external_ip):
    for num_conn in [100000]:
        print("Benchmarking httpd server at %s with %d connections..." % (external_ip, num_conn))
        response = subprocess.Popen(['ab -n %d -c %d %s/' % (num_conn, concurrency, external_ip)],
                               shell=True, universal_newlines=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        response.wait()
        with open("data_apache/gcp_%s_%s_n%d_c%d.txt" % (node_type, node_zone, num_conn, concurrency), 'w') as txt_file:
            txt_file.write("".join(response.stdout.readlines()))

def clean_up(cluster_name):
    subprocess.Popen('gcloud container clusters delete %s' % cluster_name, shell=True)

def main():
    for node_pair in machine_zone_pairs:
        cluster_name = "ap-%s-%s-%s" %(node_type, node_zone, str(num_nodes))
        deploy(cluster_name, node_type, node_zone)
        external_ip = parse_response()
        record(external_ip)
        clean_up(cluster_name)


if __name__ == '__main__':
    main()
