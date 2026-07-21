from netmiko import ConnectHandler

routers = {
    "frr-router01": {
        "host": "172.20.20.10",
        "ip_commands": [
            "ip addr add 10.12.0.1/30 dev eth1",
            "ip addr add 10.13.0.1/30 dev eth2",
            "ip addr add 10.14.0.1/30 dev eth3",
            "ip addr add 192.168.1.1/24 dev lo",
        ],
        "bgp_commands": [
            "router bgp 65001",
            "bgp router-id 1.1.1.1",
            "neighbor 10.12.0.2 remote-as 65001",
            "neighbor 10.12.0.2 description iBGP-R2",
            "neighbor 10.13.0.3 remote-as 65002",
            "neighbor 10.13.0.3 description eBGP-R3",
            "neighbor 10.14.0.4 remote-as 65003",
            "neighbor 10.14.0.4 description eBGP-R4-diagonal",
            "network 192.168.1.0/24",

        ]
    },
    "frr-router02": {
        "host": "172.20.20.20",
        "ip_commands": [
            "ip addr add 10.12.0.2/30 dev eth1",
            "ip addr add 10.24.0.2/30 dev eth2",
            "ip addr add 192.168.2.1/24 dev lo",
        ],
        "bgp_commands": [
            "router bgp 65001",
            "bgp router-id 2.2.2.2",
            "neighbor 10.12.0.1 remote-as 65001",
            "neighbor 10.12.0.1 description iBGP-R1",
            "neighbor 10.24.0.4 remote-as 65003",
            "neighbor 10.24.0.4 description eBGP-R4",
            "network 192.168.2.0/24",

        ]
    },
    "frr-router03": {
        "host": "172.20.20.30",
        "ip_commands": [
            "ip addr add 10.34.0.3/30 dev eth1",
            "ip addr add 10.13.0.3/30 dev eth2",
            "ip addr add 192.168.3.1/24 dev lo",

        ],
        "bgp_commands": [
            "router bgp 65002",
            "bgp router-id 3.3.3.3",
            "neighbor 10.13.0.1 remote-as 65001",
            "neighbor 10.13.0.1 description eBGP-R1",
            "neighbor 10.34.0.4 remote-as 65003",
            "neighbor 10.34.0.4 description eBGP-R4",
            "network 192.168.3.0/24",

        ]
    },
    "frr-router04": {
        "host": "172.20.20.40",
        "ip_commands": [
            "ip addr add 10.24.0.4/30 dev eth1",
            "ip addr add 10.34.0.4/30 dev eth2",
            "ip addr add 10.14.0.4/30 dev eth3",
            "ip addr add 192.168.4.1/24 dev lo",
        ],
        "bgp_commands": [
            "router bgp 65003",
            "bgp router-id 4.4.4.4",
            "neighbor 10.14.0.1 remote-as 65001",
            "neighbor 10.14.0.1 description eBGP-R1-diagonal",
            "neighbor 10.24.0.2 remote-as 65001",
            "neighbor 10.24.0.2 description eBGP-R2",
            "neighbor 10.34.0.3 remote-as 65002",
            "neighbor 10.34.0.3 description eBGP-R3",
            "network 192.168.4.0/24",


        ]
    },
}

for nome, dados in routers.items():
    print(f"\n{'=*20'} {nome} {'='*20}")
    conn = ConnectHandler(
        device_type ="linux",
        host=dados["host"],
        username="root",
        password="netdevops",

    )

    print(" Endereçando interfaces...")
    for cmd in dados["ip_commands"]:
        conn.send_command(cmd, expect_string=r"#", read_timeout=10 )
        print(" IPs configurados ")

        print("configurando bgp")
        vtysh_cmds = " ".join([f'-c "{cmd}"' for cmd in dados["bgp_commands"]])
        full_cmd = f'vtysh -c "configure terminal" {vtysh_cmds} -c "write memory"'
        conn.send_command(full_cmd, expect_string=r"#", read_timeout=30)
        print("bgp configurado")

        conn.disconnect()
    print("\n==== Setup completo! ====")
    print("\nVerificando sessões BGP...")
    import subprocess
    result = subprocess.run(
        ["docker", "exec", "clab-lab-netdevops-v2-frr-router01",
          "vtysh", "-c", "show ip bgp summary"],
         capture_output=True, text=True
)
print(result.stdout)