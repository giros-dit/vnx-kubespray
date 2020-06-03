
## Check all documentation here : https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CustomObjectsApi.md
from kubernetes import client, config
# Load Service Account Token
config.load_incluster_config()

group = "helm.fluxcd.io"
namespace = "flux"
version = "v1"
plural = "helmreleases"
api_instance = client.CustomObjectsApi()
api_response = api_instance.list_namespaced_custom_object(group, version, namespace, plural, pretty=True, watch=False)

## Alternatively 
api_response = api_instance.list_cluster_custom_object(group, version, plural, pretty=True, watch=False)

## Now lets deploy NGINX by using its Helm Release declaration
# it's my custom resource defined as Dict
my_resource = {
    "apiVersion": "helm.fluxcd.io/v1",
    "kind": "HelmRelease",
    "metadata": {
        "name": "nginx",
        "namespace": "default"
    },
    "spec": {
        "chart": {
            "repository": "https://charts.bitnami.com/bitnami",
            "name": "nginx",
            "version": "5.6.1"
        }
    }
}

api_instance.create_namespaced_custom_object(
        group="helm.fluxcd.io",
        version="v1",
        namespace="default",
        plural="helmreleases",
        body=my_resource,
    )