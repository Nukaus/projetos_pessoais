import socket
import sys

def escanear_porta(alvo, porta):
    #1. Resolução de Nome (Se o alvo for um domínio)
    try:
        # Tenta resolver o nome para um IP
        ip_alvo = socket.gethostbyname(alvo)
    except socket.gaierror:
        # Se falhar, o dominio ou IP é inválido
        print(f"Não foi possível resolver o endereço:{alvo}")
        return
    
    print(f"Escaneando o alvo:{alvo} ({ip_alvo}) na porta {porta}...")

    # 2. Criação e Configuração do Socket 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1) # Define o timeout para 1 segundo

    #3. Tentativa de conexão
    try:
        # conect_ex retorna 0 se a conecão for bem-sucedida, e um código de erro se não for
        resultado = s.connect_ex((ip_alvo, porta))
        if resultado == 0:
            print(f"Porta {porta} aberta")
        else:
            print(f"Porta {porta} fechada/filtrada. (Erro: {resultado})")
        
    except Exception as e:
        print(f"Ocorreu um erro ao escanear a porta {porta}: {e}")

    finally:
        # Fecha a conexão do socket
        s.close()


def varrer_intervalo(alvo, inicio_porta, fim_porta):
    # Trate a resolução de nome fora do loop para evitar repetição
    try:
        ip_alvo = socket.gethostbyname(alvo)
    except socket.gaierror:
        print(f"❌ Não foi possível resolver o endereço: {alvo}")
        return alvo, [] # Retorna alvo e uma lista vazia

    print(f"\n✨ Iniciando varredura em {alvo} ({ip_alvo}) das portas {inicio_porta} a {fim_porta}...\n")
    
    portas_abertas = []

    for porta in range(inicio_porta, fim_porta + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)

        resultado = s.connect_ex((ip_alvo, porta))

        if resultado == 0:
            # --- 1. CHAMAR obter_banner AQUI ---
            # Chamamos a função para capturar o banner/versão
            banner_servico = obter_banner(ip_alvo, porta) 
            # ------------------------------------

            # Opcional: Tenta obter o nome do serviço conhecido para a porta
            try:
                nome_servico = socket.getservbyport(porta, 'tcp')
            except OSError:
                nome_servico = "Desconhecido"
            
            # 2. Armazena a informação, INCLUINDO o banner
            portas_abertas.append({
                "porta": porta,
                "servico_comum": nome_servico,
                "banner": banner_servico # <-- NOVO CAMPO ADICIONADO
            })
            
            print(f"  [+] {porta}/TCP: Aberta ({nome_servico}) - Banner: {banner_servico[:50]}...")
        
        s.close()

    return ip_alvo, portas_abertas

def obter_banner(ip, porta):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    
    try:
        s.connect((ip, porta))
        
        # Tenta ler a resposta do servidor. 
        # Para HTTP (80), pode ser necessário enviar uma requisição GET básica.
        # Mas vamos começar apenas lendo o que ele envia por padrão (como SSH, FTP, etc.)
        
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        return banner if banner else "Sem Banner Detectado"
        
    except Exception:
        return "Falha ao Obter Banner"
    finally:
        s.close()

if __name__ == "__main__":
    # Removemos o escanear_porta simples e vamos testar a varredura completa
    target = "google.com" # Exemplo: Domínio
    # target = "192.168.1.1" # Exemplo: IP (substitua pelo IP do seu roteador ou um alvo permitido)

    # Defina um intervalo de portas para teste (ex: as portas mais comuns)
    # CUIDADO: Escaneie apenas alvos que você tem permissão (ex: sua rede local)
    inicio = 75
    fim = 90

    ip_final, resultados = varrer_intervalo(target, inicio, fim)
    
    print("\n--- RESUMO DO SCAN ---")
    print(f"Alvo: {target} (IP: {ip_final})")
    for r in resultados:
        print(f"Porta: {r['porta']}, Serviço: {r['servico_comum']}, Banner: {r['banner'][:50]}...")