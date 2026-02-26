import argparse
import os
import sys
from pypdf import PdfReader
 
def limpar_tela():
    """Limpa o terminal de acordo com o Sistema Operacional."""
    os.system('cls' if os.name == 'nt' else 'clear')
 
def processar_intervalo(entrada, total_paginas):
    """Converte '1-3' ou '2' em uma lista de índices [0, 1, 2]."""
    indices = []
    try:
        if '-' in entrada:
            inicio, fim = map(int, entrada.split('-'))
            # Garante que o intervalo está dentro do que o PDF possui
            inicio = max(1, inicio)
            fim = min(total_paginas, fim)
            indices = list(range(inicio - 1, fim))
        else:
            p = int(entrada)
            if 1 <= p <= total_paginas:
                indices = [p - 1]
        return indices
    except:
        return []
 
def extrair_texto(caminho_pdf, lista_indices=None):
    """Extrai texto tratando arquivos protegidos por senha."""
    if not os.path.exists(caminho_pdf):
        print(f"❌ Erro: Arquivo '{caminho_pdf}' não encontrado.")
        return None
       
    try:
        reader = PdfReader(caminho_pdf)
       
        # --- PARTE DE SENHA ---
        if reader.is_encrypted:
            print("\n🔐 Este PDF está protegido por senha.")
            senha = input("👉 Digite a senha para desbloquear: ").strip()
           
            # Tenta descriptografar o arquivo
            sucesso = reader.decrypt(senha)
            if sucesso == 0: # 0 indica falha na autenticação
                print("❌ Senha incorreta! Não foi possível ler o conteúdo.")
                return None
            else:
                print("🔓 Arquivo desbloqueado com sucesso!")
 
        total = len(reader.pages)
       
        # Se não informou páginas, pega todas. Se informou, usa a lista.
        indices = lista_indices if lista_indices is not None else range(total)
       
        texto_final = []
        for i in indices:
            page = reader.pages[i]
            texto_final.append(f"--- Página {i+1} ---\n{page.extract_text() or ''}")
       
        return "\n".join(texto_final).strip()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return None
 
if __name__ == "__main__":
    limpar_tela()
    print("=== 📄 EXTRATOR INTERATIVO v1.1.0 ===\n")
 
    input_pdf = input("👉 Nome do arquivo PDF (ex: documento.pdf): ").strip()
   
    # Validação inicial do arquivo
    if not os.path.exists(input_pdf):
        print(f"❌ O arquivo '{input_pdf}' não existe nesta pasta.")
        sys.exit()
 
    try:
        # Abrimos o reader primeiro para saber o total de páginas
        reader = PdfReader(input_pdf)
       
        # Se estiver com senha, precisamos tentar descriptografar antes de contar páginas
        if reader.is_encrypted:
            print("\n🔐 O arquivo está bloqueado.")
            senha = input("👉 Digite a senha para ver as informações do PDF: ").strip()
            if reader.decrypt(senha) == 0:
                print("❌ Senha incorreta. Encerrando.")
                sys.exit()
 
        total_pags = len(reader.pages)
        print(f"\nO PDF possui {total_pags} páginas.")
    except Exception as e:
        print(f"❌ Erro ao ler o PDF: {e}")
        sys.exit()
 
    print("[1] Ver todas as páginas")
    print("[2] Escolher intervalo ou página única (ex: 1-3 ou 5)")
   
    escolha = input("\nEscolha uma opção: ")
   
    indices_selecionados = None
    if escolha == "2":
        intervalo = input(f"Digite o intervalo (1 a {total_pags}): ")
        indices_selecionados = processar_intervalo(intervalo, total_pags)
 
    # Executa a extração (passando os índices se houver)
    conteudo = extrair_texto(input_pdf, indices_selecionados)
 
    if conteudo:
        limpar_tela()
        print("=== 📖 CONTEÚDO EXTRAÍDO ===\n")
        print(conteudo)
        print("\n" + "="*30)
 
        # Pergunta se deseja salvar após a visualização
        quer_salvar = input("\n💾 Deseja salvar esse conteúdo em um arquivo .txt? (s/n): ").lower()
        if quer_salvar == 's':
            nome_saida = input("👉 Nome para o arquivo (ex: extraido.txt): ").strip()
            with open(nome_saida, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"\n✅ Arquivo '{nome_saida}' salvo com sucesso!")
        else:
            print("\n👋 Programa finalizado.")