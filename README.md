# vnx-kubespray

VNX scenario that deploys a production-ready three-node Kubernetes cluster using kubespray utilities.

By default Calico network plugin is used.

## Requirements

- Baremetal Linux OS (_Tested on Ubuntu LTS 18.04_)
- VNX software -> [VNX Installation Recipe](https://web.dit.upm.es/vnxwiki/index.php/Vnx-install)
- Internet connection
- Hardware requirments: minimum 4GB RAM and 4 CPU cores

**IMPORTANT NOTE:** This VNX scenario **cannot be deployed on a VirtualBox VM** since the virtualized nodes in the scenario are KVM-based virtual machines.

## Setup

Install Ansible among other utilities needed by kubespray

```bash
cd ansible/kubespray
sudo pip3 install -r requirements.txt
```

## Getting Started

First of all deploy VNX scenario:

```bash
sudo vnx -f tutorial_kubespray.xml -v --create
```

Then run ansible playbook to setup a Kubernetes cluster on the three virtual machines:

```bash
cd ansible
ansible-playbook playbooks/site.yml
```

The execution of ansible playbook will take 10 minutes roughly. Once this playbook has finished successfully, we will have a Kubernetes cluster ready to play with.

## Interacting with the cluster

### Node Management

VNX creates a point-to-point link for VM management access and dynamically updates `/etc/hosts`. Hence, our Kubernetes nodes can be easily accessed by using the hostnames and the SSH key that have been defined in VNX:

```bash
# Master node
ssh -i config/ssh/id_rsa root@k8s-master

# Worker nodes
ssh -i config/ssh/id_rsa root@k8s-worker1
ssh -i config/ssh/id_rsa root@k8s-worker2
```
This is how Ansible would access the nodes in the scenario.

### Kubectl usage

Kubespray installs `kubectl` client for us in the master node. Kube config file used by the client is stored in `/root/.kube/config`. This is a copy of `/etc/kubernetes/admin.conf` file.

Alternatively, kubespray could install the `kubectl` and/or copy the config file in the host machine for remote interaction with Kubernetes API. This feature has been tested out yet.

### Helm client

Helm client is installed in the master node. In addition, kubespray configures the stable registry for us.


## Cleanup

To destroy the VNX scenario, run the following command:

```bash
sudo vnx -f tutorial_kubespray.xml -v --destroy
```