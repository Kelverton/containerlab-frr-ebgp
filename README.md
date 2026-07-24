# Lab NetDevOps v2 - Containerlab & FRRouting (eBGP)

Este repositório contém um laboratório de Infraestrutura como Código (IaC) focado em redes modernas. O projeto simula um ambiente de provedor/corporativo com roteamento dinâmico e hosts de teste isolados utilizando **Containerlab** e **Docker**.

O objetivo principal é demonstrar a configuração nativa de **eBGP** usando a stack open-source **FRRouting (FRR)** e validar a conectividade de ponta a ponta entre subredes de clientes.

---

## Por que Containerlab + FRRouting (FRR)?

A escolha da stack tecnológica foi baseada em **eficiência de recursos** e **aderência às práticas modernas de NetDevOps**:

1. **Eficiência de RAM Extrema:** Roteadores tradicionais virtualizados (Cisco IOS, Arista EOS, Juniper vMX) em ambientes como GNS3 ou EVE-NG exigem de 512MB a 2GB de RAM *por nó*. O FRR roda nativamente como container gastando apenas **~25MB de RAM por instância**, permitindo simular cenários complexos em computadores convencionais ou instâncias gratuitas na nuvem.
2. **Superação das Limitações do Packet Tracer:** Ambientes simulados como o Cisco Packet Tracer possuem limitações severas de sintaxe, suporte parcial a features avançadas de BGP e comportamento irreal de Kernel. O FRR entrega uma pilha real de produção Linux.
3. **Foco em Produção Moderna (Cloud Native):** O FRRouting é a base de roteamento utilizada em grandes data centers e sistemas operacionais de redes abertas (como SONiC e Cumulus Linux). Estudar FRR prepara o profissional para o mercado real de Cloud, Data Center e Provedores modernos.

---

## Arquitetura da Topologia

* **Core da Rede:** 4 Roteadores FRRouting configurados em anel, onde cada roteador atua como um Sistema Autônomo (AS) independente executando eBGP.
* **Borda (Clientes):** 4 PCs (`network-multitool`) simulando subredes locais (`192.168.X.0/24`) conectadas a cada roteador correspondente.
* **Rede de Gerência:** Uma rede Out-of-Band (`clab-mgmt`) isolada na subrede `172.20.20.0/24` para futura integração de telemetria.

---

## Como Instalar as Ferramentas (Se necessário)

Se você estiver rodando em máquina virtual limpa (Ubuntu em VPS, Play with Docker ou GitHub Codespaces):

### 1. Instalar o Docker Engine
```bash
curl -fsSL https://docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
```

### 2. Instalar o Containerlab
```bash
curl -sL https://containerlab.dev | sudo bash -s -- install-containerlab
```
OU
```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
```

---

## Como Rodar o Laboratório

### 1. Clonar o Repositório
```bash
git clone git@github.com:Kelverton/containerlab-frr-ebgp.git
cd containerlab-frr-ebgp
```

### 2. Ajustar as Permissões dos Arquivos do FRR
```bash
sudo chmod 644 frr/frr-router*.conf
```

### 3. Subir a Topologia
```bash
sudo clab deploy -t lab.clab.yml
```

---

## Desafios Técnicos Superados & Troubleshooting

Durante o desenvolvimento foram enfrentados e resolvidos 5 desafios que integram infraestrutura de redes ao comportamento do sistema operacional:

1. **Conflito Zebra vs Shell Linux:** A injeção de IPs via shell (`exec` no YAML) entra em conflito com o daemon `zebra` do FRR, que limpa a pilha de rede. Solucionado com mapeamento nativo de arquivos `frr.conf` via volumes permanentes do Docker.
2. **Bloqueio de Permissão no Docker:** Arquivos montados como `:ro` impediam a execução do `write memory`. Corrigido alterando para `:rw`.
3. **Mecanismo de Segurança rp_filter:** O filtro de caminho reverso do Kernel descartava pacotes eBGP assumindo risco de IP Spoofing. Mitigado desativando via `sysctl -w net.ipv4.conf.all.rp_filter=0`.
4. **Política Estrita do eBGP (Missing Policy):** O FRRouting (versões > 7.4) proíbe tráfego eBGP por padrão sem filtros explícitos. Solucionado implementando `route-map PERMIT-ALL` nas direções `in` e `out` dos vizinhos.
5. **Sequestro do Gateway nos Hosts:** O Containerlab injeta uma interface `eth0` automática de gerenciamento que roubava a rota padrão dos PCs. Resolvido reconfigurando a tabela de rotas para apontar para a interface de dados `eth1`.

---

## Comandos de Gerenciamento do Lab

### Containerlab
```bash
# Subir o lab
sudo clab deploy -t lab.clab.yml

# Subir forçando recriar containers
sudo clab deploy -t lab.clab.yml --reconfigure

# Destruir o lab
sudo clab destroy -t lab.clab.yml

# Destruir com limpeza completa
sudo clab destroy -t lab.clab.yml --cleanup

# Listar labs rodando
sudo clab inspect --all

# Ver topologia atual
sudo clab inspect -t lab.clab.yml

# Gerar diagrama visual da topologia
sudo clab graph -t lab.clab.yml

# Salvar configuração de todos os nós
sudo clab save -t lab.clab.yml
```

### Docker
```bash
# Listar containers rodando
docker ps

# Listar todos incluindo parados
docker ps -a

# Ver logs de um container
docker logs clab-lab-netdevops-v2-frr-router01
docker logs -f clab-lab-netdevops-v2-frr-router01   # follow (tempo real)

# Entrar num container
docker exec -it clab-lab-netdevops-v2-frr-router01 sh

# Parar / iniciar / reiniciar
docker stop clab-lab-netdevops-v2-frr-router01
docker start clab-lab-netdevops-v2-frr-router01
docker restart clab-lab-netdevops-v2-frr-router01

# Ver uso de recursos em tempo real
docker stats

# Ver redes Docker
docker network ls
docker network inspect clab-mgmt

# Limpar containers, imagens e volumes não usados
docker system prune -f

# Ver espaço usado pelo Docker
docker system df

# Forçar remoção de containers (útil em caso de erro de redeploy)
docker rm -f $(docker ps -aq --filter "name=clab")
docker network rm clab-mgmt
```

### Aliases úteis (adicionar ao ~/.bashrc)
```bash
alias r1="docker exec -it clab-lab-netdevops-v2-frr-router01 vtysh"
alias r2="docker exec -it clab-lab-netdevops-v2-frr-router02 vtysh"
alias r3="docker exec -it clab-lab-netdevops-v2-frr-router03 vtysh"
alias r4="docker exec -it clab-lab-netdevops-v2-frr-router04 vtysh"
alias lab="cd ~/telemetria-arista && source .venv/bin/activate"
```

Após adicionar, recarregar:
```bash
source ~/.bashrc
```

---

## Comandos de Validação

### Verificar status do eBGP (deve exibir `Established`)
```bash
docker exec -i clab-lab-netdevops-v2-frr-router01 vtysh << EOF
show bgp summary
EOF
```

### Verificar tabela de rotas BGP (deve exibir marcador `B>`)
```bash
docker exec -i clab-lab-netdevops-v2-frr-router01 vtysh << EOF
show ip route bgp
EOF
```

### Ver todos os daemons ativos
```bash
docker exec -it clab-lab-netdevops-v2-frr-router01 vtysh -c "show daemons"
```

### Testar conectividade de ponta a ponta (PC1 → PC3)
```bash
docker exec -it clab-lab-netdevops-v2-pc1 ping -c 3 192.168.2.10
```

### Ver rotas completas
```bash
docker exec -it clab-lab-netdevops-v2-frr-router01 vtysh -c "show ip route"
```

### Ver neighbors BGP
```bash
docker exec -it clab-lab-netdevops-v2-frr-router01 vtysh -c "show ip bgp summary"
```

---

## Monitoramento (Telemetria)

```bash
# Verificar saúde do Prometheus
curl http://172.20.20.100:9090/-/healthy

# Ver targets ativos
curl http://172.20.20.100:9090/api/v1/targets | python3 -m json.tool

# Testar blackbox exporter (ICMP)
curl "http://172.20.20.101:9115/probe?target=172.20.20.10&module=icmp"

# Grafana — acessar pelo navegador
# http://172.20.20.102:3000
# usuário: admin / senha: admin
```

---

## Destruir o Laboratório
```bash
sudo clab destroy -t lab.clab.yml --cleanup
```

---

## Roadmap do Projeto (Próximas Fases)
* [ ] **Fase 2:** Automação de deploy e validação de rotas usando scripts Python (Netmiko/Ansible)
* [ ] **Fase 3:** Telemetria e Observabilidade com Prometheus (`frr-exporter`), Blackbox e dashboards no Grafana
* [ ] **Fase 4:** Expansão para 10 roteadores e mais de 20 hosts com múltiplos protocolos de roteamento
---
💡 *Desenvolvimento assistido e acelerado utilizando Engenharia de Prompt com LLMs como copilotos de infraestrutura.*
