# VNX Kubespray

VNX scenario that deploys a production-ready three-node Kubernetes cluster using [Kubespray](https://kubespray.io/#/) utilities.

![kubespray](tutorial_kubespray/docs/kubespray-logo.png)

For this version of the scenario [Flannel CNI](https://github.com/flannel-io/flannel) network plugin is used.

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
**IMPORTANT NOTE:** This VNX scenario cannot be deployed on virtual machines on older VirtualBox/VMware virtualization environments that do not support nested virtualization as the virtualized nodes in the scenario are KVM-based virtual machines. Despite this, the latest versions of VirtualBox/VMware support nested virtualization.

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

**NOTE:** If you get a `WARNING: UNPROTECTED PRIVATE KEY FILE!` error, make sure you only give read and write permissions to your user for the files in [`./tutorial_kubespray/conf/ssh/`](./tutorial_kubespray/conf/ssh/) folder.

## Checking cluster operation
- Cluster node availability:
```bash
root@k8s-master:~# kubectl get nodes
NAME          STATUS   ROLES                  AGE    VERSION
k8s-master    Ready    control-plane          5m1s   v1.26.11
k8s-worker1   Ready    <none>                 4m     v1.26.11
k8s-worker2   Ready    <none>                 4m     v1.26.11
```

- Kubernetes system pods status:
```bash
root@k8s-master:~# kubectl get pods -n kube-system
NAME                                 READY   STATUS    RESTARTS   AGE
coredns-8474476ff8-bgbsk             1/1     Running   0          43m
coredns-8474476ff8-hg7fh             1/1     Running   0          43m
dns-autoscaler-7df78bfcfb-zchrw      1/1     Running   0          43m
kube-apiserver-k8s-master            1/1     Running   0          45m
kube-controller-manager-k8s-master   1/1     Running   0          45m
kube-flannel-c2f8h                   1/1     Running   0          44m
kube-flannel-nzbfw                   1/1     Running   0          44m
kube-flannel-pwzrd                   1/1     Running   0          44m
kube-multus-ds-amd64-6nqmf           1/1     Running   0          44m
kube-multus-ds-amd64-8bqbm           1/1     Running   0          44m
kube-multus-ds-amd64-qh5gb           1/1     Running   0          44m
kube-proxy-7d688                     1/1     Running   0          44m
kube-proxy-fvb2c                     1/1     Running   0          44m
kube-proxy-wslw8                     1/1     Running   0          44m
kube-scheduler-k8s-master            1/1     Running   0          45m
nginx-proxy-k8s-worker1              1/1     Running   0          44m
nginx-proxy-k8s-worker2              1/1     Running   0          44m
nodelocaldns-b5nkp                   1/1     Running   0          43m
nodelocaldns-htsjr                   1/1     Running   0          43m
nodelocaldns-tx97n                   1/1     Running   0          43m
registry-n4jfj                       1/1     Running   0          43m
registry-proxy-dw2jq                 1/1     Running   0          43m
registry-proxy-whlbp                 1/1     Running   0          43m
```

> **NOTE:** The installation also include the [Multus](https://github.com/k8snetworkplumbingwg/multus-cni) networking plugin to allow adding additional interfaces to deployed pods.
  
For the interconnection between Kubernetes pods and external systems (i.e., external virtual machines or containers outside Kubernetes cluster), we can define VLANs with `Multus`. Follow the steps below:

1. Create `eth2` subinterfaces in `k8s-worker1` and `k8s-worker2` Kubernetes cluster nodes (the `eth2` interfaces within Kubernetes nodes defined in the [tutorial_kubespray.xml](./tutorial_kubespray/vnx/tutorial_kubespray.xml) VNX scenario are connected to a dedicated network for VLANs):
```bash
ssh k8s-worker1 ip link add link eth2 name eth2.1000 type vlan id 1000
ssh k8s-worker1 ip link add link eth2 name eth2.1001 type vlan id 1001
ssh k8s-worker2 ip link add link eth2 name eth2.1000 type vlan id 1000
ssh k8s-worker2 ip link add link eth2 name eth2.1001 type vlan id 1001
ssh k8s-worker1 ip link set eth2.1000 up
ssh k8s-worker1 ip link set eth2.1001 up
ssh k8s-worker2 ip link set eth2.1000 up
ssh k8s-worker2 ip link set eth2.1001 up
```
2. Start example pods in VLANs 1000 and 10001:
```bash
cd tutorial_kubespray/examples/multus
kubectl create -f vlan1000-dhcp.yml
kubectl create -f vma3-dhcp.yml
kubectl create -f vma4-dhcp.yml
kubectl create -f vlan1001-dhcp.yml
kubectl create -f vmb3-dhcp.yml
kubectl create -f vmb4-dhcp.yml
```
3. For the Multus configuration, we create Kubernetes objects of type `NetworkAttachmentDefinition` to assign new interfaces to the pods that belong to VLANs 1000 and 1001. We create an object of type `NetworkAttachmentDefinition` for each VLAN. To check the creation of resources of type `NetworkAttachmentDefinition` for VLANs 1000 and 1001 we can execute the following commands:
```bash
kubectl describe net-attach-def vlan1000
kubectl describe net-attach-def vlan1001
```   
4. Deploy an additional VNX demo scenario with LXC containers (i.e., `vmA2` and `vmB2`) deployed in VLANs 1000 and 1001, and a router container (i.e., `vlan-router`) for performing Inter-VLAN routing:
```bash
cd tutorial_kubespray/vnx
sudo vnx -f openstack_lab-vms-vlan --create
```
5. Check connectivity from Kubernetes pods to VNX LXC containers. For example:
```bash
kubectl exec -it vma3 -- ping 10.1.3.100
kubectl exec -ti vmb3 -- ping 10.1.2.100
```
6. Destroy Kubernetes pods and VLAN networks with:
```bash
kubectl delete net-attach-def vlan1000
kubectl delete pod --grace-period=0 --force vma3
kubectl delete pod --grace-period=0 --force vma4
kubectl delete net-attach-def vlan1001
kubectl delete pod --grace-period=0 --force vmb3
kubectl delete pod --grace-period=0 --force vmb4
```

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

## Cleanup

To destroy the VNX scenario, run the following command:

```bash
cd tutorial_kubespray
sudo vnx -f tutorial_kubespray.xml -v --destroy
```
