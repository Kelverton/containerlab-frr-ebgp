from netmiko import ConnectHandler

r1 = {
    "device_type": "linux",
    "host": "172.20.20.10",
    "username": "root",
    "password": "netdevops",
    "port": 22,
}

print("Conectando ao R1...")
conexao = ConnectHandler(**r1)
print(f"Conectado! Prompt: {conexao.find_prompt()}")

output = conexao.send_command("vtysh -c 'show ip route'")
print(output)

conexao.disconnect()
print("Desconectado.")
