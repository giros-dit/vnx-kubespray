# VNX Kubespray

VNX scenario that deploys a production-ready three-node Kubernetes cluster using [Kubespray](https://kubespray.io/#/) utilities.

![kubespray](tutorial_kubespray/docs/kubespray-logo.png)

For this version of the scenario [Calico CNI](https://github.com/projectcalico/calico) network plugin is used.

## Scenario topology

![VNX tutorial_kubespray scenario](tutorial_kubespray/docs/scenario.png)

K8s nodes are deployed as KVM virtual machines (running Ubuntu 20.04 LTS), whereas r1 and h1 are LXC containers (running Ubuntu 22.04 LTS). 

## Requirements

- Baremetal Linux OS (_Tested on Ubuntu 20.04 LTS_)
- VNX software -> [VNX Installation Recipe](https://web.dit.upm.es/vnxwiki/index.php/Vnx-install)
- Internet connection
- Hardware requirments: minimum 8GB RAM and 4 CPU cores

The scenario uses two VNX images:
- `vnx_rootfs_kvm_ubuntu64-20.04-v025.qcow2`, used for the KVM virtual machines that deploy the three nodes of the k8s cluster.
- `vnx_rootfs_lxc_ubuntu64-22.04-v025`, used for auxiliary stage containers.

To download them, run the following commands:
```bash
cd /usr/share/vnx/filesystems
vnx_download_rootfs -r vnx_rootfs_kvm_ubuntu64-20.04-v025.qcow2 -y -l
vnx_download_rootfs -r vnx_rootfs_lxc_ubuntu64-22.04-v025 -y -l
cd -
```
**IMPORTANT NOTE:** This VNX scenario **cannot be deployed on a VirtualBox VM** since the virtualized nodes in the scenario are KVM-based virtual machines.

## Setup

Install [Ansible](https://www.ansible.com/) among other utilities needed by kubespray

```bash
cd tutorial_kubespray/ansible/kubespray
sudo pip3 install -r requirements.txt
```


## Getting Started

First of all deploy VNX scenario:

```bash
cd tutorial_kubespray/vnx
sudo vnx -f tutorial_kubespray.xml -v --create
```

Then run Ansible playbook to setup a Kubernetes cluster on the three virtual machines:

```bash
cd tutorial_kubespray/ansible
ansible-playbook playbooks/site.yml
```

The execution of Ansible playbook will take approximately 10 minutes. Once this playbook has finished successfully, we will have a Kubernetes cluster ready to play with.

## Interacting with the cluster

### Node Management

VNX creates a point-to-point link for management access and dynamically builds an SSH config file for the scenario. Such file can be found at `$HOME/.ssh/config.d/vnx/tutorial_kubespray`. As a result, our Kubernetes nodes and the remaining network elements can be easily accessed as follows:

```bash
# Master node
ssh k8s-master

# Worker nodes
ssh k8s-worker1
ssh k8s-worker2

## Router
ssh r1

## End-user
ssh h1
```

This is how Ansible would access the nodes in the scenario.

## Checking cluster operation
- Cluster node availability:
```bash
NAME          STATUS   ROLES                  AGE     VERSION
k8s-master    Ready    control-plane,master   2m56s   v1.21.5
k8s-worker1   Ready    <none>                 2m1s    v1.21.5
k8s-worker2   Ready    <none>                 2m1s    v1.21.5
```

- Kubernetes system pods status:
```bash
root@k8s-master:~# kubectl get pods -n kube-system
NAME                                       READY   STATUS    RESTARTS   AGE
calico-kube-controllers-8575b76f66-j8hbl   1/1     Running   0          107s
calico-node-dqsd5                          1/1     Running   0          119s
calico-node-rq7n9                          1/1     Running   0          119s
calico-node-wtv8m                          1/1     Running   0          119s
coredns-8474476ff8-hd88j                   1/1     Running   0          90s
coredns-8474476ff8-n9v98                   1/1     Running   0          85s
dns-autoscaler-7df78bfcfb-r7r4z            1/1     Running   0          87s
kube-apiserver-k8s-master                  1/1     Running   0          2m57s
kube-controller-manager-k8s-master         1/1     Running   0          2m57s
kube-proxy-89vv4                           1/1     Running   0          2m10s
kube-proxy-bl95v                           1/1     Running   0          2m10s
kube-proxy-p6ws4                           1/1     Running   0          2m10s
kube-scheduler-k8s-master                  1/1     Running   0          2m57s
nginx-proxy-k8s-worker1                    1/1     Running   0          2m11s
nginx-proxy-k8s-worker2                    1/1     Running   0          2m11s
nodelocaldns-5zqdt                         1/1     Running   0          87s
nodelocaldns-6dhzx                         1/1     Running   0          87s
nodelocaldns-7f5gn                         1/1     Running   0          87s
registry-pnpsb                             1/1     Running   0          77s
registry-proxy-zkbgx                       1/1     Running   0          76s
registry-proxy-zrdqq                       1/1     Running   0          76s
```

> *Note*: The installation also include the [Multus](https://github.com/k8snetworkplumbingwg/multus-cni) networking plugin to allow adding additional interfaces to deployed pods.
  
### Kubectl usage

Kubespray installs `kubectl` client for us in the `k8s-master` node. Kube config file used by the client is stored in `/root/.kube/config`. This is a copy of `/etc/kubernetes/admin.conf` file.

Alternatively, you could install the `kubectl` on your host machine and copy the config file from `k8s-master` node for remote interaction with Kubernetes API:
```bash
# Install kubectl
snap install kubectl --classic
kubectl version --client

# Copy kube config file from k8s-master node to localhost:
scp k8s-master:~/.kube/config ~/.kube/config

# Change the following line within the ~/.kube/config local file:
server: https://k8s-master:6443
```

### Helm client

Helm client is installed in the `k8s-master` node.

## Network Management

> *TO-DO*: We use Calico as k8s network plugin. BGP peering is configured from each k8s node to router r1, who runs BIRD daemon providing BGP route reflector_functions to the k8s cluster. By using Calicos BGP feature, our router r1 can dynamically learn pod and service IPs from Kubernetes. As a result, external hosts such as h1 can easily access k8s services without having to manage routing in the network.
> 

## Cleanup

To destroy the VNX scenario, run the following command:

```bash
cd tutorial_kubespray
sudo vnx -f tutorial_kubespray.xml -v --destroy
```