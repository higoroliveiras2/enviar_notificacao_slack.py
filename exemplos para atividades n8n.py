# ===================================================================
# enviar_notificacao_slack.py
# Envia notificacoes para o Slack via n8n
# ===================================================================

import requests
from datetime import datetime

def enviar_slack(canal, mensagem, nivel="info"):
    """
    Envia mensagem para Slack via webhook n8n
    
    Args:
        canal: Nome do canal (#geral, #alertas, etc)
        mensagem: Texto da mensagem
        nivel: info, warning, error, success
    """
    
    webhook_url = "https://seu-n8n.com/webhook/slack-notification"
    
    # Emojis por nivel
    emojis = {
        "info": ":information_source:",
        "warning": ":warning:",
        "error": ":x:",
        "success": ":white_check_mark:"
    }
    
    dados = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "canal": canal,
        "mensagem": f"{emojis.get(nivel, '')} {mensagem}",
        "nivel": nivel,
        "usuario": "Sistema Automatico"
    }
    
    try:
        response = requests.post(webhook_url, json=dados)
        
        if response.status_code == 200:
            print(f"[OK] Mensagem enviada para {canal}")
            return True
        else:
            print(f"[ERRO] Falha ao enviar: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return False


# Exemplos de uso
if __name__ == "__main__":
    # Notificacao de sucesso
    enviar_slack("#geral", "Deploy realizado com sucesso!", "success")
    
    # Alerta
    enviar_slack("#alertas", "Uso de CPU acima de 80%", "warning")
    
    # Erro
    enviar_slack("#ti", "Falha no backup noturno", "error")


# ===================================================================
# processar_planilha.py
# Le planilha Excel/CSV e envia dados para n8n
# ===================================================================

import csv
import json
import requests
from datetime import datetime

def processar_csv(arquivo_csv, webhook_url):
    """
    Le arquivo CSV e envia linha por linha para n8n
    
    Args:
        arquivo_csv: Caminho do arquivo CSV
        webhook_url: URL do webhook n8n
    """
    
    print(f"[INICIO] Processando: {arquivo_csv}\n")
    
    linhas_processadas = 0
    erros = 0
    
    try:
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for linha in reader:
                dados = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "linha": linhas_processadas + 1,
                    "dados": linha
                }
                
                try:
                    response = requests.post(webhook_url, json=dados)
                    
                    if response.status_code == 200:
                        print(f"[OK] Linha {linhas_processadas + 1} processada")
                        linhas_processadas += 1
                    else:
                        print(f"[ERRO] Linha {linhas_processadas + 1}: {response.status_code}")
                        erros += 1
                
                except Exception as e:
                    print(f"[ERRO] Linha {linhas_processadas + 1}: {str(e)}")
                    erros += 1
        
        print(f"\n{'='*50}")
        print(f"RESUMO:")
        print(f"Total processado: {linhas_processadas}")
        print(f"Erros: {erros}")
        print(f"{'='*50}")
        
        return linhas_processadas, erros
    
    except Exception as e:
        print(f"[ERRO] Falha ao processar CSV: {str(e)}")
        return 0, 0


# Exemplo de uso
if __name__ == "__main__":
    processar_csv(
        arquivo_csv="funcionarios.csv",
        webhook_url="https://seu-n8n.com/webhook/importar-dados"
    )


# ===================================================================
# agendar_tarefa.py
# Agenda tarefas e envia lembretes via n8n
# ===================================================================

import requests
from datetime import datetime, timedelta

def agendar_tarefa(titulo, data_hora, responsavel, prioridade="media"):
    """
    Agenda uma tarefa e configura lembretes
    
    Args:
        titulo: Nome da tarefa
        data_hora: Data/hora no formato "YYYY-MM-DD HH:MM"
        responsavel: Nome do responsavel
        prioridade: baixa, media, alta
    """
    
    webhook_url = "https://seu-n8n.com/webhook/agendar-tarefa"
    
    # Converter string para datetime
    try:
        dt = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
    except:
        print("[ERRO] Formato de data invalido. Use: YYYY-MM-DD HH:MM")
        return False
    
    # Calcular lembretes
    lembrete_1h = dt - timedelta(hours=1)
    lembrete_1dia = dt - timedelta(days=1)
    
    dados = {
        "titulo": titulo,
        "data_hora": data_hora,
        "responsavel": responsavel,
        "prioridade": prioridade,
        "lembretes": {
            "1_hora_antes": lembrete_1h.strftime("%Y-%m-%d %H:%M"),
            "1_dia_antes": lembrete_1dia.strftime("%Y-%m-%d %H:%M")
        },
        "status": "agendada",
        "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(webhook_url, json=dados)
        
        if response.status_code == 200:
            print(f"[OK] Tarefa agendada com sucesso!")
            print(f"Titulo: {titulo}")
            print(f"Data/Hora: {data_hora}")
            print(f"Responsavel: {responsavel}")
            print(f"Prioridade: {prioridade.upper()}")
            print(f"\nLembretes configurados:")
            print(f"  - 1 dia antes: {lembrete_1dia.strftime('%d/%m/%Y %H:%M')}")
            print(f"  - 1 hora antes: {lembrete_1h.strftime('%d/%m/%Y %H:%M')}")
            return True
        else:
            print(f"[ERRO] Falha ao agendar: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return False


# Exemplos de uso
if __name__ == "__main__":
    # Agendar reuniao
    agendar_tarefa(
        titulo="Reuniao de planejamento",
        data_hora="2024-12-15 14:00",
        responsavel="Eng. Alan Oliveira",
        prioridade="alta"
    )
    
    # Agendar entrega
    agendar_tarefa(
        titulo="Entrega do projeto OP-085509",
        data_hora="2024-12-20 10:00",
        responsavel="Equipe Patrimonio",
        prioridade="alta"
    )


# ===================================================================
# monitorar_apis.py
# Monitora disponibilidade de APIs e notifica n8n
# ===================================================================

import requests
import time
from datetime import datetime

def verificar_api(url, nome_api, timeout=10):
    """
    Verifica se uma API esta respondendo
    
    Returns:
        dict com status da API
    """
    
    try:
        inicio = time.time()
        response = requests.get(url, timeout=timeout)
        tempo_resposta = round((time.time() - inicio) * 1000, 2)
        
        return {
            "nome": nome_api,
            "url": url,
            "status": "online",
            "codigo_http": response.status_code,
            "tempo_resposta_ms": tempo_resposta,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except requests.exceptions.Timeout:
        return {
            "nome": nome_api,
            "url": url,
            "status": "timeout",
            "erro": "Tempo de resposta excedido",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        return {
            "nome": nome_api,
            "url": url,
            "status": "offline",
            "erro": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def monitorar_multiplas_apis(apis, intervalo=60):
    """
    Monitora multiplas APIs continuamente
    
    Args:
        apis: Lista de tuplas (nome, url)
        intervalo: Intervalo entre verificacoes em segundos
    """
    
    webhook_url = "https://seu-n8n.com/webhook/status-api"
    
    print(f"[INICIO] Monitorando {len(apis)} APIs")
    print(f"Intervalo: {intervalo} segundos\n")
    
    while True:
        try:
            for nome, url in apis:
                resultado = verificar_api(url, nome)
                
                # Exibir status
                if resultado["status"] == "online":
                    print(f"[OK] {nome}: {resultado['tempo_resposta_ms']}ms")
                else:
                    print(f"[ERRO] {nome}: {resultado['status']}")
                
                # Enviar para n8n
                try:
                    requests.post(webhook_url, json=resultado)
                except:
                    pass
            
            print(f"\nProxima verificacao em {intervalo}s...\n")
            time.sleep(intervalo)
        
        except KeyboardInterrupt:
            print("\n[FIM] Monitoramento encerrado")
            break


# Exemplo de uso
if __name__ == "__main__":
    apis = [
        ("API Principal", "https://api.exemplo.com/health"),
        ("API Pagamentos", "https://api.pagamentos.com/status"),
        ("API Integracao", "https://api.integracao.com/ping")
    ]
    
    monitorar_multiplas_apis(apis, intervalo=300)  # 5 minutos


# ===================================================================
# sincronizar_calendario.py
# Sincroniza eventos de calendario com n8n
# ===================================================================

import requests
from datetime import datetime, timedelta

def criar_evento_calendario(titulo, data_inicio, data_fim, descricao="", participantes=[]):
    """
    Cria evento no calendario via n8n
    
    Args:
        titulo: Titulo do evento
        data_inicio: Data/hora inicio (YYYY-MM-DD HH:MM)
        data_fim: Data/hora fim (YYYY-MM-DD HH:MM)
        descricao: Descricao do evento
        participantes: Lista de emails dos participantes
    """
    
    webhook_url = "https://seu-n8n.com/webhook/criar-evento"
    
    dados = {
        "titulo": titulo,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "descricao": descricao,
        "participantes": participantes,
        "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": "reuniao"
    }
    
    try:
        response = requests.post(webhook_url, json=dados)
        
        if response.status_code == 200:
            print(f"[OK] Evento criado: {titulo}")
            print(f"Inicio: {data_inicio}")
            print(f"Fim: {data_fim}")
            if participantes:
                print(f"Participantes: {', '.join(participantes)}")
            return True
        else:
            print(f"[ERRO] Falha ao criar evento: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return False


def listar_proximos_eventos(dias=7):
    """
    Lista eventos dos proximos N dias
    """
    
    webhook_url = "https://seu-n8n.com/webhook/listar-eventos"
    
    data_inicio = datetime.now().strftime("%Y-%m-%d")
    data_fim = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    
    dados = {
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }
    
    try:
        response = requests.post(webhook_url, json=dados)
        
        if response.status_code == 200:
            eventos = response.json()
            
            print(f"\n{'='*60}")
            print(f"EVENTOS DOS PROXIMOS {dias} DIAS")
            print(f"{'='*60}\n")
            
            if not eventos:
                print("Nenhum evento agendado")
            else:
                for evento in eventos:
                    print(f"Titulo: {evento.get('titulo')}")
                    print(f"Data: {evento.get('data_inicio')}")
                    print(f"Participantes: {len(evento.get('participantes', []))}")
                    print("-" * 60)
            
            return eventos
        else:
            print(f"[ERRO] Falha ao listar eventos: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return []


# Exemplo de uso
if __name__ == "__main__":
    # Criar reuniao
    criar_evento_calendario(
        titulo="Reuniao Semanal - Departamento Patrimonio",
        data_inicio="2024-12-16 09:00",
        data_fim="2024-12-16 10:00",
        descricao="Revisao de orcamentos e planejamento",
        participantes=["alan@exemplo.com", "daniel@exemplo.com"]
    )
    
    # Listar proximos eventos
    listar_proximos_eventos(dias=7)


# ===================================================================
# enviar_relatorio_email.py
# Gera e envia relatorios por email via n8n
# ===================================================================

import requests
from datetime import datetime

def gerar_relatorio_html(dados):
    """
    Gera relatorio em HTML
    """
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .footer {{ margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>Relatorio Automatico - {datetime.now().strftime('%d/%m/%Y')}</h1>
        
        <h2>Resumo de Atividades</h2>
        <table>
            <tr>
                <th>Metrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Tarefas Concluidas</td>
                <td>{dados.get('concluidas', 0)}</td>
            </tr>
            <tr>
                <td>Tarefas Pendentes</td>
                <td>{dados.get('pendentes', 0)}</td>
            </tr>
            <tr>
                <td>Em Andamento</td>
                <td>{dados.get('em_andamento', 0)}</td>
            </tr>
        </table>
        
        <h2>Observacoes</h2>
        <p>{dados.get('observacoes', 'Nenhuma observacao.')}</p>
        
        <div class="footer">
            <p>Relatorio gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    return html


def enviar_relatorio_email(destinatarios, assunto, dados_relatorio):
    """
    Envia relatorio por email via n8n
    
    Args:
        destinatarios: Lista de emails
        assunto: Assunto do email
        dados_relatorio: Dicionario com dados do relatorio
    """
    
    webhook_url = "https://seu-n8n.com/webhook/enviar-email"
    
    html_relatorio = gerar_relatorio_html(dados_relatorio)
    
    dados = {
        "destinatarios": destinatarios,
        "assunto": assunto,
        "corpo_html": html_relatorio,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(webhook_url, json=dados)
        
        if response.status_code == 200:
            print(f"[OK] Relatorio enviado para {len(destinatarios)} destinatario(s)")
            for email in destinatarios:
                print(f"  - {email}")
            return True
        else:
            print(f"[ERRO] Falha ao enviar: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return False


# Exemplo de uso
if __name__ == "__main__":
    dados = {
        'concluidas': 12,
        'pendentes': 5,
        'em_andamento': 3,
        'observacoes': 'Substituicao de luminarias programada para proxima semana. Orcamento OP-085509 aprovado.'
    }
    
    enviar_relatorio_email(
        destinatarios=["alan@exemplo.com", "gerencia@exemplo.com"],
        assunto=f"Relatorio Diario - {datetime.now().strftime('%d/%m/%Y')}",
        dados_relatorio=dados
    )