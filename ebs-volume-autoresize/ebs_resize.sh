#!/usr/bin/env bash

region=$1
volume_id=$2

THRESHOLD_PERCENT=90
usage_percent=$(df -h | grep <ebs_volume> | awk '{print $5}' | tr -d '%')
initial_size=$(lsblk -b | grep <ebs_volume> | awk '{print $4/1024/1024/1024}')
device=$(df -h | grep <ebs_volume> | awk '{print $1}')

if [ $usage_percent -gt $THRESHOLD_PERCENT ];then

  echo "$(date +'%c') - <ebs_volume> filesystem usage is ${usage_percent}%. Adding some space."
  new_size=$(echo $initial_size | awk 'function ceil(x,y){y=int(x); return(x>y?y+1:y)} {print ceil($0*1.1)}')
  new_iops=$(echo $new_size | awk '{iops=$0 > 1000 ? $0 * 3 : 3000; iops=iops < 16000 ? iops: 16000; print(iops)}')
  echo "$(date +'%c') - Initial size: ${initial_size}GB, new size: ${new_size}GB and ${new_iops} IOPS."
  aws ec2 modify-volume --size ${new_size} --iops ${new_iops} --volume-id ${volume_id} --region ${region}
  current_size=$(lsblk -b | grep <ebs_volume> | awk '{print $4/1024/1024/1024}')

  while [ "${current_size}" == "${initial_size}" ]; do
    echo "$(date +'%c') - EBS volume modification is in progress. Waiting 5 sec..."
    sleep 5
    current_size=$(lsblk -b | grep <ebs_volume> | awk '{print $4/1024/1024/1024}')
  done

  echo "$(date +'%c') - Current volume size is ${current_size}. Resizing file system on ${device}..."
  /sbin/resize2fs ${device}
else
  echo "$(date +'%c') - <ebs_volume> filesystem usage is ${usage_percent}%. Doing nothing."
fi