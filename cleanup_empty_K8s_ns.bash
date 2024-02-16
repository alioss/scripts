#!/bin/bash

is_namespace_empty() {
    local ns=$1
    local resources=$(kubectl api-resources --namespaced=true --verbs=list -o name)
    
    for resource in $resources; do
        local count=$(kubectl -n "$ns" get "$resource" --no-headers --ignore-not-found | wc -l)
        if [ "$count" -ne 0 ]; then
            return 1
        fi
    done
    
    return 0
}

namespaces=$(kubectl get ns --no-headers | grep -vE '^(default|kube-system|kube-public)' | awk '{print $1}')

for ns in $namespaces; do
    if is_namespace_empty "$ns"; then
        echo "Del empty ns: $ns"
        kubectl delete ns "$ns"
    else
        echo "Namespace $ns is not empty"
    fi
done