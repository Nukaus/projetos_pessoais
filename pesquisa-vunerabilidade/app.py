from flask import Flask, render_template, request, redirect, url_for
import socket
import sys # Não é estritamente necessário para o Flask, mas manteremos.

# Mapeamento simples de SERVIÇO e VERSÃO para VULNERABILIDADES (CVEs)
VULNERABILIDADES_CONHECIDAS = {
    "Apache/2.4.41": [
        "CVE-2021-42013: Path Traversal and RCE",
        "CVE-2021-41773: Path Traversal (Baixa Gravidade)"
    ],
    "Nginx/1.18.0": [
        "CVE-2021-36109: Information Disclosure"
    ],
    "OpenSSH_7.9p1": [
        "CVE-2020-15778: Command Injection via ProxyCommand"
    ],
    "Microsoft IIS/10.0": [
        "CVE-2017-7269: WebDAV ScStoragePathFromUrl Buffer Overflow"
    ],
    "vsftpd 2.3.4": [
        "CVE-2011-2523: Backdoor Command Execution"
    ],
    "ProFTPD 1.3.5": [
        "CVE-2015-3306: mod_copy Unauthenticated RCE"
    ],
    "Exim 4.89": [
        "CVE-2019-10149: RCE (The Return of the WIZard)"
    ],
    "Apache Tomcat/9.0.30": [
        "CVE-2020-1938: 'Ghostcat' AJP File Read/Inclusion"
    ],
    "PHP/7.3.11": [
        "CVE-2019-11043: RCE in php-fpm"
    ],
    # A detecção de Log4j via banner é imprecisa, mas pode pegar em alguns casos.
    # A vulnerabilidade real está na biblioteca, não no serviço exposto.
    "log4j": [
        "CVE-2021-44228: 'Log4Shell' Remote Code Execution"
    ],
    # A chave deve ser a string exata ou parte da string que você espera no banner.
}

# (O seu código das Fases 1 e 2 entraria aqui)
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
            # 1. Captura do Banner e Serviço Comum
            banner_servico = obter_banner(ip_alvo, porta)
            try:
                nome_servico = socket.getservbyport(porta, 'tcp')
            except OSError:
                nome_servico = "Desconhecido"
            
            # --- 2. CHAMAR A FUNÇÃO DE VULNERABILIDADE AQUI ---
            cves_encontradas = buscar_vulnerabilidades(banner_servico)
            # ----------------------------------------------------

            # 3. Armazena a informação, INCLUINDO as vulnerabilidades
            portas_abertas.append({
                "porta": porta,
                "servico_comum": nome_servico,
                "banner": banner_servico,
                "vulnerabilidades": cves_encontradas # <-- NOVO CAMPO ADICIONADO
            })

    return ip_alvo, portas_abertas

def obter_banner(ip, porta):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    
    try:
        s.connect((ip, porta))
        
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        return banner if banner else "Sem Banner Detectado"
        
    except Exception:
        return "Falha ao Obter Banner"
    finally:
        s.close()

def buscar_vulnerabilidades(banner):
    vulnerabilidades = []
    if not banner or banner == "Sem Banner Detectado" or banner == "Falha ao Obter Banner":
        return vulnerabilidades
    
    # Itera sobre o dicionário de vulnerabilidades conhecidas
    for servico_versao, cves in VULNERABILIDADES_CONHECIDAS.items():
        # Verifica se o banner contém a string exata do serviço/versão
        # Usamos .lower() para fazer uma busca insensível a maiúsculas/minúsculas
        if servico_versao.lower() in banner.lower():
            # Se encontrar uma correspondência, adiciona as CVEs à lista de resultados
            vulnerabilidades.extend(cves)
            
    # Retorna uma lista, que pode estar vazia se nada for encontrado
    return vulnerabilidades
# ----------------------------------------------------



app = Flask(__name__)

# Rota principal (Formulário e Processamento)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recebe o valor do campo 'alvo' do formulário
        alvo = request.form.get('alvo')
        
        if not alvo:
            return render_template('index.html', erro="Por favor, forneça um IP ou Domínio.")

        try:
            # DEFINA O INTERVALO DE PORTAS AQUI. 
            # Sugestão: 1 a 100 para testes rápidos.
            inicio_porta = 1
            fim_porta = 100 

            # Chama a função principal de varredura
            ip_final, resultados = varrer_intervalo(alvo, inicio_porta, fim_porta)
            
            # Renderiza a página de resultados, passando os dados
            return render_template('resultados.html', 
                                   alvo=alvo, 
                                   ip=ip_final, 
                                   portas=resultados,
                                   range_portas=f"{inicio_porta}-{fim_porta}")

        except Exception as e:
            # Em caso de erro geral
            return render_template('index.html', erro=f"Erro interno do scanner: {e}")

    # Método GET: Apenas mostra o formulário
    return render_template('index.html')

if __name__ == '__main__':
    # Roda a aplicação Flask no modo debug
    app.run(debug=True)