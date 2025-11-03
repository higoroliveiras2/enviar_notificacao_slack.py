# ===================================================================
# github_auto_upload.py
# Compacta arquivos em ZIP e faz upload automatico para GitHub
# ===================================================================

import os
import zipfile
import subprocess
from datetime import datetime
import shutil

class GitHubAutoUpload:
    def __init__(self, repositorio_local, branch="main"):
        """
        Inicializa o uploader automatico para GitHub
        
        Args:
            repositorio_local: Caminho da pasta do repositorio git local
            branch: Nome da branch (padrao: main)
        """
        self.repositorio_local = repositorio_local
        self.branch = branch
        
    def criar_zip(self, pasta_origem, nome_zip=None):
        """
        Cria um arquivo ZIP de uma pasta
        
        Args:
            pasta_origem: Pasta que sera compactada
            nome_zip: Nome do arquivo ZIP (opcional)
        
        Returns:
            Caminho do arquivo ZIP criado
        """
        if nome_zip is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_zip = f"backup_{timestamp}.zip"
        
        caminho_zip = os.path.join(self.repositorio_local, nome_zip)
        
        print(f"\n{'='*60}")
        print(f"CRIANDO ARQUIVO ZIP")
        print(f"{'='*60}")
        print(f"Origem: {pasta_origem}")
        print(f"Destino: {caminho_zip}\n")
        
        try:
            with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_arquivos = 0
                
                for raiz, dirs, arquivos in os.walk(pasta_origem):
                    for arquivo in arquivos:
                        caminho_arquivo = os.path.join(raiz, arquivo)
                        caminho_relativo = os.path.relpath(caminho_arquivo, pasta_origem)
                        zipf.write(caminho_arquivo, caminho_relativo)
                        total_arquivos += 1
                        print(f"[+] {caminho_relativo}")
            
            tamanho_mb = os.path.getsize(caminho_zip) / (1024 * 1024)
            
            print(f"\n[OK] ZIP criado com sucesso!")
            print(f"Total de arquivos: {total_arquivos}")
            print(f"Tamanho: {tamanho_mb:.2f} MB")
            print(f"{'='*60}\n")
            
            return caminho_zip
        
        except Exception as e:
            print(f"[ERRO] Falha ao criar ZIP: {str(e)}")
            return None
    
    def adicionar_arquivos_individuais(self, arquivos_lista):
        """
        Copia arquivos individuais para o repositorio
        
        Args:
            arquivos_lista: Lista de caminhos de arquivos para copiar
        """
        print(f"\n{'='*60}")
        print(f"COPIANDO ARQUIVOS INDIVIDUAIS")
        print(f"{'='*60}\n")
        
        for arquivo in arquivos_lista:
            if os.path.exists(arquivo):
                nome_arquivo = os.path.basename(arquivo)
                destino = os.path.join(self.repositorio_local, nome_arquivo)
                
                try:
                    shutil.copy2(arquivo, destino)
                    print(f"[OK] Copiado: {nome_arquivo}")
                except Exception as e:
                    print(f"[ERRO] Falha ao copiar {nome_arquivo}: {str(e)}")
            else:
                print(f"[AVISO] Arquivo nao encontrado: {arquivo}")
        
        print(f"\n{'='*60}\n")
    
    def executar_comando_git(self, comando):
        """
        Executa um comando git e retorna o resultado
        
        Args:
            comando: Lista com o comando git (ex: ['git', 'status'])
        
        Returns:
            Tupla (sucesso, output)
        """
        try:
            resultado = subprocess.run(
                comando,
                cwd=self.repositorio_local,
                capture_output=True,
                text=True,
                check=True
            )
            return True, resultado.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def verificar_repositorio(self):
        """Verifica se o diretorio e um repositorio git valido"""
        if not os.path.exists(os.path.join(self.repositorio_local, '.git')):
            print(f"[ERRO] '{self.repositorio_local}' nao e um repositorio git!")
            print("Execute primeiro: git init")
            return False
        return True
    
    def git_add_all(self):
        """Adiciona todos os arquivos ao staging"""
        print("[GIT] Adicionando arquivos ao staging...")
        sucesso, output = self.executar_comando_git(['git', 'add', '.'])
        
        if sucesso:
            print("[OK] Arquivos adicionados ao staging")
            return True
        else:
            print(f"[ERRO] Falha ao adicionar arquivos: {output}")
            return False
    
    def git_commit(self, mensagem=None):
        """Faz commit das alteracoes"""
        if mensagem is None:
            mensagem = f"Backup automatico - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"[GIT] Fazendo commit: {mensagem}")
        sucesso, output = self.executar_comando_git(['git', 'commit', '-m', mensagem])
        
        if sucesso:
            print("[OK] Commit realizado com sucesso")
            return True
        else:
            if "nothing to commit" in output:
                print("[INFO] Nenhuma alteracao para commitar")
                return True
            print(f"[ERRO] Falha ao fazer commit: {output}")
            return False
    
    def git_push(self):
        """Envia alteracoes para o GitHub"""
        print(f"[GIT] Enviando para GitHub (branch: {self.branch})...")
        sucesso, output = self.executar_comando_git(['git', 'push', 'origin', self.branch])
        
        if sucesso:
            print("[OK] Alteracoes enviadas para GitHub com sucesso!")
            return True
        else:
            print(f"[ERRO] Falha ao enviar para GitHub: {output}")
            print("\n[DICA] Verifique se:")
            print("1. Voce esta autenticado no GitHub")
            print("2. O repositorio remoto esta configurado")
            print("3. Voce tem permissao de push")
            return False
    
    def upload_completo(self, pasta_origem=None, arquivos=None, mensagem_commit=None, criar_zip_backup=True):
        """
        Executa todo o processo de upload para GitHub
        
        Args:
            pasta_origem: Pasta para compactar em ZIP (opcional)
            arquivos: Lista de arquivos individuais (opcional)
            mensagem_commit: Mensagem do commit (opcional)
            criar_zip_backup: Se True, cria ZIP da pasta_origem
        
        Returns:
            True se sucesso, False se erro
        """
        print(f"\n{'#'*60}")
        print(f"# UPLOAD AUTOMATICO PARA GITHUB")
        print(f"{'#'*60}\n")
        
        # Verificar repositorio
        if not self.verificar_repositorio():
            return False
        
        # Criar ZIP se solicitado
        if criar_zip_backup and pasta_origem:
            zip_criado = self.criar_zip(pasta_origem)
            if not zip_criado:
                print("[ERRO] Falha ao criar ZIP. Abortando...")
                return False
        
        # Copiar arquivos individuais
        if arquivos:
            self.adicionar_arquivos_individuais(arquivos)
        
        # Processo Git
        print(f"{'='*60}")
        print("INICIANDO PROCESSO GIT")
        print(f"{'='*60}\n")
        
        # 1. Git Add
        if not self.git_add_all():
            return False
        
        # 2. Git Commit
        if not self.git_commit(mensagem_commit):
            return False
        
        # 3. Git Push
        if not self.git_push():
            return False
        
        print(f"\n{'#'*60}")
        print(f"# PROCESSO CONCLUIDO COM SUCESSO!")
        print(f"{'#'*60}\n")
        
        return True


# ===================================================================
# EXEMPLO 1: Upload simples de arquivos
# ===================================================================
def exemplo_upload_simples():
    """Exemplo basico de upload de arquivos"""
    
    uploader = GitHubAutoUpload(
        repositorio_local="C:/Users/Usuario/automacoes-n8n-python"
    )
    
    arquivos = [
        "processar_emails.py",
        "monitorar_arquivos.py",
        "backup_automatico.py",
        "validar_documentos.py",
        "gerar_relatorio_pdf.py"
    ]
    
    uploader.upload_completo(
        arquivos=arquivos,
        mensagem_commit="Adicionar scripts de automacao com n8n",
        criar_zip_backup=False
    )


# ===================================================================
# EXEMPLO 2: Criar ZIP e fazer upload
# ===================================================================
def exemplo_backup_com_zip():
    """Exemplo de backup com ZIP"""
    
    uploader = GitHubAutoUpload(
        repositorio_local="C:/Users/Usuario/automacoes-n8n-python"
    )
    
    uploader.upload_completo(
        pasta_origem="C:/Projetos/MeuProjeto",
        mensagem_commit=f"Backup do projeto - {datetime.now().strftime('%d/%m/%Y')}",
        criar_zip_backup=True
    )


# ===================================================================
# EXEMPLO 3: Upload completo (ZIP + Arquivos)
# ===================================================================
def exemplo_completo():
    """Exemplo completo com ZIP e arquivos individuais"""
    
    uploader = GitHubAutoUpload(
        repositorio_local="C:/Users/Usuario/automacoes-n8n-python",
        branch="main"
    )
    
    # Lista de scripts Python
    scripts = [
        "processar_emails.py",
        "monitorar_arquivos.py",
        "backup_automatico.py",
        "validar_documentos.py",
        "gerar_relatorio_pdf.py",
        "consultar_api.py",
        "calcular_ferias.py"
    ]
    
    sucesso = uploader.upload_completo(
        pasta_origem="C:/Documentos/ProjetoImportante",  # Sera compactado em ZIP
        arquivos=scripts,  # Arquivos Python individuais
        mensagem_commit="Atualizacao automatica - Scripts + Backup projeto",
        criar_zip_backup=True
    )
    
    if sucesso:
        print("\n[SUCESSO] Todos os arquivos foram enviados para GitHub!")
    else:
        print("\n[FALHA] Ocorreu um erro durante o processo")


# ===================================================================
# EXEMPLO 4: Uso interativo
# ===================================================================
def modo_interativo():
    """Modo interativo para usuario"""
    
    print("="*60)
    print("UPLOAD AUTOMATICO PARA GITHUB")
    print("="*60)
    
    repo_local = input("\nCaminho do repositorio local: ").strip()
    
    if not os.path.exists(repo_local):
        print(f"[ERRO] Caminho nao existe: {repo_local}")
        return
    
    uploader = GitHubAutoUpload(repositorio_local=repo_local)
    
    print("\nO que deseja fazer?")
    print("1 - Criar ZIP de uma pasta e enviar")
    print("2 - Enviar arquivos individuais")
    print("3 - Ambos (ZIP + Arquivos)")
    
    opcao = input("\nEscolha (1/2/3): ").strip()
    
    pasta_origem = None
    arquivos = None
    
    if opcao in ["1", "3"]:
        pasta_origem = input("\nPasta para criar ZIP: ").strip()
    
    if opcao in ["2", "3"]:
        print("\nArquivos individuais (separados por virgula):")
        entrada = input("Ex: arquivo1.py, arquivo2.py: ").strip()
        arquivos = [f.strip() for f in entrada.split(",") if f.strip()]
    
    mensagem = input("\nMensagem do commit (Enter para padrao): ").strip()
    mensagem = mensagem if mensagem else None
    
    print("\n")
    uploader.upload_completo(
        pasta_origem=pasta_origem,
        arquivos=arquivos,
        mensagem_commit=mensagem,
        criar_zip_backup=(opcao in ["1", "3"])
    )


# ===================================================================
# EXECUCAO PRINCIPAL
# ===================================================================
if __name__ == "__main__":
    print("\nEscolha o modo de execucao:")
    print("1 - Exemplo simples")
    print("2 - Exemplo com ZIP")
    print("3 - Exemplo completo")
    print("4 - Modo interativo")
    
    escolha = input("\nOpcao (1/2/3/4): ").strip()
    
    if escolha == "1":
        exemplo_upload_simples()
    elif escolha == "2":
        exemplo_backup_com_zip()
    elif escolha == "3":
        exemplo_completo()
    elif escolha == "4":
        modo_interativo()
    else:
        print("[ERRO] Opcao invalida!")


# ===================================================================
# CONFIGURACAO INICIAL DO GIT (Execute apenas uma vez)
# ===================================================================
"""
# No terminal/prompt de comando, execute:

# 1. Configurar usuario Git (se ainda nao fez)
git config --global user.name "Higor Oliveira"
git config --global user.email "higoroliveiras@gmail.com"

# 2. Inicializar repositorio (se ainda nao fez)
cd C:/caminho/do/seu/repositorio
git init

# 3. Adicionar repositorio remoto
git remote add origin https://github.com/higoroliveiras/automacoes-n8n-python.git

# 4. Criar branch main
git branch -M main

# 5. Primeiro push (apenas na primeira vez)
git push -u origin main

# Depois disso, use este script para uploads automaticos!
"""
