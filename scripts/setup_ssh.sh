#!/bin/bash

ROUTERS=(
  "clab-lab-netdevops-v2-frr-router02"
  "clab-lab-netdevops-v2-frr-router03"
  "clab-lab-netdevops-v2-frr-router04"
)

for router in "${ROUTERS[@]}"; do
  echo "====== Configurando SSH em $router ======"
  docker exec "$router" apk update -q
  docker exec "$router" apk add openssh -q
  docker exec "$router" ssh-keygen -A
  docker exec "$router" mkdir -p /run/sshd
  docker exec "$router" sh -c "echo 'root:netdevops' | chpasswd"
  docker exec "$router" sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
  docker exec "$router" sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
  docker exec "$router" /usr/sbin/sshd
  echo "$router OK"
done

echo "====== Todos configurados ======"
