# Lab NetDevOps v2 - Containerlab & FRRouting (eBGP)

Este repositório contém um laboratório de Infraestrutura como Código (IaC) focado em redes modernas. O projeto simula um ambiente de provedor/corporativo com roteamento dinâmico e hosts de teste isolados utilizando **Containerlab** e **Docker** [INDEX].

O objetivo principal deste projeto é demonstrar a configuração nativa de **eBGP** usando a stack open-source **FRRouting (FRR)** e validar a conectividade de ponta a ponta entre subredes de clientes [INDEX].

---

##  Por que Containerlab + FRRouting (FRR)?

A escolha da stack tecnológica deste laboratório foi baseada em **eficiência de recursos de hardware** e **aderência às práticas modernas de NetDevOps**:

1. **Eficiência de RAM Extrema:** Roteadores tradicionais virtualizados (Cisco IOS, Arista EOS, Juniper vMX) em ambientes como GNS3 ou EVE-NG exigem de 512MB a 2GB de memória RAM *por nó*. O FRR roda nativamente como um container estável gastando apenas **~25MB de RAM por instância**, permitindo simular cenários complexos de eBGP em computadores convencionais ou instâncias gratuitas na nuvem.
2. **Superação das Limitações do Packet Tracer:** Ambientes simulados como o Cisco Packet Tracer possuem limitações severas de sintaxe, suporte parcial a features avançadas de BGP e comportamento irreal de Kernel. O FRR entrega uma pilha real de produção Linux de alta performance.
3. **Foco em Produção Moderna (Cloud Native):** O FRRouting é a base de roteamento utilizada em grandes data centers e sistemas operacionais de redes abertas (como o SONiC e Cumulus Linux). Estudar FRR prepara o profissional para o mercado real de Cloud, Data Center e Provedores modernos.

---

##  Arquitetura da Topologia

* **Core da Rede:** 4 Roteadores FRRouting configurados em anel, onde cada roteador atua como um Sistema Autônomo (AS) independente executando eBGP.
* **Borda (Clientes):** 4 PCs (`network-multitool`) simulando subredes locais (`192.168.X.0/24`) conectadas a cada roteador correspondente.
* **Rede de Gerência:** Uma rede Out-of-Band (`clab-mgmt`) isolada na subrede `172.20.20.0/24` para futura integração de telemetria.

---

## Como Instalar as Ferramentas Básicas (Se necessário)

Se você estiver rodando este laboratório em uma máquina virtual limpa na nuvem (como Ubuntu em VPS, Play with Docker ou GitHub Codespaces), execute os comandos abaixo para garantir que o Docker e o Containerlab estejam instalados [INDEX]:

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

---

##  Como Rodar o Laboratório

Siga o passo a passo abaixo no seu terminal para clonar e inicializar todo o ambiente de forma automática:

### 1. Clonar o Repositório
```bash
git clone git@github.com:Kelverton/containerlab-frr-ebgp.git
cd containerlab-frr-ebgp
```

### 2. Ajustar as Permissões dos Arquivos do FRR
O processo do Containerlab exige permissões estritas de leitura nos arquivos de configuração do FRR:
```bash
sudo chmod 644 frr/frr-router*.conf
```

### 3. Subir a Topologia com o Containerlab
```bash
sudo clab deploy -t lab.clab.yml
```

---

##  Desafios Técnicos Superados & Aprendizados (Troubleshooting)

Durante o desenvolvimento deste laboratório autônomo, foram enfrentados e mitigados 5 grandes desafios que integram a infraestrutura de redes ao comportamento de sistemas operacionais:

1. **Conflito Zebra vs Shell Linux:** A injeção de IPs via shell (`exec` no YAML) entra em conflito com o daemon `zebra` do FRR, que limpa a pilha de rede. Solucionado com o mapeamento nativo de arquivos `frr.conf` via volumes permanentes do Docker [INDEX].
2. **Bloqueio de Permissão no Docker:** Arquivos montados como `:ro` impediam a execução do comando `write memory`. Corrigido alterando as flags de mapeamento para `:rw`.
3. **Mecanismo de Segurança rp_filter:** O filtro de caminho reverso do Kernel do Linux descartava os pacotes eBGP assumindo risco de IP Spoofing. Mitigado desativando o filtro operacional via `sysctl -w net.ipv4.conf.all.rp_filter=0`.
4. **Política Estrita do eBGP (Missing Policy):** O FRRouting (versões > 7.4) proíbe tráfego eBGP por padrão se não houver filtros explícitos. Solucionado implementando um `route-map PERMIT-ALL` nas direções `in` e `out` dos vizinhos.
5. **Sequestro do Gateway nos Computadores de Teste:** O Containerlab injeta uma interface `eth0` automática de gerenciamento, que roubava a rota padrão dos PCs. Resolvido reconfigurando a tabela de rotas internas dos hosts para apontarem obrigatoriamente para a interface de dados `eth1`.

---

##  Comandos Úteis de Validação

### Verificar o Status do eBGP no Router 01 (Deve exibir `Established`)
```bash
docker exec -i clab-lab-netdevops-v2-frr-router01 vtysh << EOF
show bgp summary
EOF
```

### Verificar a Tabela de Rotas no Router 01 (Deve exibir o marcador `B>`)
```bash
docker exec -i clab-lab-netdevops-v2-frr-router01 vtysh << EOF
show ip route bgp
EOF
```

### Testar Conectividade de Ponta a Ponta (PC1 para PC3)
```bash
docker exec -it clab-lab-netdevops-v2-pc1 ping -c 3 192.168.2.10
```

---

##  Como Destruir o Laboratório
```bash
sudo clab destroy -t lab.clab.yml --cleanup
```

---

##  Roadmap do Projeto (Próximas Fases)
* [ ] **Fase 2:** Automação de deploy e validação de checagem de rotas usando scripts em Python (**Netmiko/Ansible**) [INDEX].
* [ ] **Fase 3:** Telemetria e Observabilidade integrando **Prometheus** (`frr-exporter`), Blackbox e dashboards no **Grafana** [INDEX].
* [ ] **Fase 4:** Expansão massiva da topologia para 10 roteadores e mais de 20 hosts utilizando múltiplos protocolos de roteamento.

---
💡 *Desenvolvimento assistido e acelerado utilizando Engenharia de Prompt com LLMs como copilotos de infraestrutura.*
