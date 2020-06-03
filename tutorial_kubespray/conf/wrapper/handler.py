from kubernetes import client, config
import json


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    config.load_incluster_config()

    request = json.loads(req)
    chart_repository = request["repository"]
    chart_name = request["name"]
    chart_version = request["version"]

    group = "helm.fluxcd.io"
    api_version = "v1"
    plural = "helmreleases"
    namespace = "default"
    api_instance = client.CustomObjectsApi()

    helmrelease = {
        "apiVersion": "helm.fluxcd.io/v1",
        "kind": "HelmRelease",
        "metadata": {
            "name": chart_name,
            "namespace": "default"
        },
        "spec": {
            "chart": {
                "repository": chart_repository,
                "name": chart_name,
                "version": chart_version
            }
        }
    }

    api_response = api_instance.create_namespaced_custom_object(
        group=group,
        version=api_version,
        plural=plural,
        namespace=namespace,
        body=helmrelease,
    )

    return json.dumps(api_response)
