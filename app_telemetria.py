import time
import sqlite3
import re
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess

# Configurações de Caminhos de Arquivos
DB_PATH = "/home/kelverton/telemetria-arista/banco_rede.db"
GRAPH_PATH = "/home/kelverton/telemetria-arista/grafico_trafego.png"

def init_db():
    """Inicializa o banco SQLite em modo WAL para evitar travamentos de concorrência."""
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_util REAL,
            ram_util REAL,
            tx_rate REAL,
            rx_rate REAL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON metricas(timestamp);')
    conn.commit()
    conn.close()

def coletar_dados_frr():
    """Coleta contadores brutos direto do kernel de rede do container ativo (Infalível)."""
    try:
        # Executa comando direto no container para pegar estatísticas reais de hardware
        res = subprocess.check_output("docker exec clab-netdevops-lab-frr-router01 cat /proc/net/dev", shell=True).decode()
        rx_bytes, tx_bytes = 0.0, 0.0
        
        for linha in res.splitlines():
            if "eth1" in linha:
                # Separa os contadores da interface por espaço
                partes = linha.replace("eth1:", "").split()
                if len(partes) >= 9:
                    rx_bytes = float(partes[0])  # Index 0 do /proc/net/dev = Bytes Recebidos
                    tx_bytes = float(partes[8])  # Index 8 do /proc/net/dev = Bytes Transmitidos
                break
        
        # Simula consumo de hardware estável do container (2% CPU, 10% RAM)
        return 2.0, 10.0, tx_bytes, rx_bytes
    except Exception as e:
        print(f"[{datetime.now()}] Erro ao acessar contadores do container: {e}")
        return None

def salvar_e_podar(cpu, ram, tx, rx):
    """Insere dados e remove registros antigos mantendo o teto de 100 linhas."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            "INSERT INTO metricas (timestamp, cpu_util, ram_util, tx_rate, rx_rate) VALUES (?, ?, ?, ?, ?)",
            (timestamp, cpu, ram, tx, rx)
        )
        
        cursor.execute('''
            DELETE FROM metricas WHERE id NOT IN (
                SELECT id FROM metricas ORDER BY timestamp DESC LIMIT 100
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[{datetime.now()}] Erro no SQLite: {e}")

def gerar_grafico():
    """Busca o histórico e atualiza a imagem PNG temporal no SSD."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, tx_rate, rx_rate FROM metricas ORDER BY id DESC LIMIT 20")
        dados = cursor.fetchall()[::-1]
        conn.close()
        
        if not dados:
            return

        timestamps = [row[0].split()[1] for row in dados] # Pega apenas hh:mm:ss
        tx_values = [row[1] for row in dados]
        rx_values = [row[2] for row in dados]

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, tx_values, label='TX (Bytes)', color='blue', marker='o')
        plt.plot(timestamps, rx_values, label='RX (Bytes)', color='orange', marker='x')
        
        plt.title('Telemetria Automatizada Cisco/FRR - Interface eth1')
        plt.xlabel('Hora da Coleta')
        plt.ylabel('Tráfego Acumulado (Bytes)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(GRAPH_PATH)
        plt.close()
    except Exception as e:
        print(f"[{datetime.now()}] Erro ao renderizar gráfico Matplotlib: {e}")

if __name__ == "__main__":
    init_db()
    print("Iniciando loop de telemetria Cisco/FRR (20s)...")
    
    while True:
        metricas = coletar_dados_frr()
        if metricas:
            cpu, ram, tx, rx = metricas
            salvar_e_podar(cpu, ram, tx, rx)
            gerar_grafico()
            print(f"[{datetime.now()}] Telemetria atualizada: TX {tx} B | RX {rx} B")
        time.sleep(20)
