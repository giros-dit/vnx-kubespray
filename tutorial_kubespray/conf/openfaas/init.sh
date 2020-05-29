# Add OPENFAASn helm repo
helm repo add openfaas https://openfaas.github.io/faas-netes/

# OPENFAAS does not support multi-namespace yet
# Deploy core components in the default namespace
helm repo update \
 && helm upgrade openfaas --install openfaas/openfaas \
    --set functionNamespace=openfaas-fn \
    --set generateBasicAuth=true 

# Set gateway url to interface IP. 
# Service bind to localhost not working with Calico thus far
export OPENFAAS_URL=http://10.10.20.10:31112

# Set pass and login with faas-cli
curl -sSL https://cli.openfaas.com | sh
export PASSWORD=$(kubectl -n default get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
echo -n $PASSWORD | faas-cli login -g $OPENFAAS_URL -u admin --password-stdin