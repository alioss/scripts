#!/bin/bash

# Get a list of all namespaces 
namespaces=$(kubectl get namespaces --no-headers -o custom-columns=:metadata.name | grep -vE '^(default|kube-system|kube-public)$')

for ns in $namespaces; do
    # Check if the namespace is empty
    resource_count=$(kubectl get all --namespace="$ns" --no-headers | wc -l)

    if [ "$resource_count" -eq 0 ]; then
        read -p "Namespace $ns is unused. Do you want to delete it? (y/n): " answer
        if [ "$answer" == "y" ]; then
            echo "Deleting unused namespace: $ns"
            kubectl delete namespace "$ns"
        else
            echo "Skipping deletion of namespace: $ns"
        fi
    else
        echo "Namespace $ns is not empty, skipping..."
    fi
done
