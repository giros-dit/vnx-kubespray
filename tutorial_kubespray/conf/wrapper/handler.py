from kubernetes import client, config
import json


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    config.load_incluster_config()

    group = "helm.fluxcd.io"
    version = "v1"
    plural = "helmreleases"
    namespace = "default"
    api_instance = client.CustomObjectsApi()

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

    api_response = api_instance.create_namespaced_custom_object(
        group=group,
        version=version,
        plural=plural,
        namespace=namespace,
        body=my_resource,
    )

    return json.dumps(api_response)