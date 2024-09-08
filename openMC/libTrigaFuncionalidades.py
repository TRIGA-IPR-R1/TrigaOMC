#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)
    
import os
from datetime import datetime


"""
Bibilhoteca com as variáveis de controle e alguma funções úteis.

Variável simu: Controla se os XML serão gerados, se a simulação será executada, e se os plots serão gerados

Variável verbose: Controla se a função printv imprimirá no terminal

Função printv: imprime no terminal se verbose é verdadeiro

Função mkdir: cria uma pasta (com data ou não) (voltando para o diretorio anterior antes de criar ou não)

Função chdir: muda para a pasta informada (se nenhuma pasta informada, procura a mais recente e muda para ela)
"""

simu = True

verbose = True

def printv(inp):
    if verbose:
        print(inp)

def mkdir(nome="teste_sem_nome", data=False, voltar=True, cpinputs=False, on=True):
    if on:
        if (voltar==True):
            os.chdir("../")
        if (data==True):
            agora = datetime.now()
            nome = agora.strftime(nome+"_%Y%m%d_%H%M%S")
        if not os.path.exists(nome):
            os.makedirs(nome)
        os.chdir(nome)
        if cpinputs:
            os.system("cp ../*.py .")
    
def chdir(nome=None):
    if (nome != None):
        os.chdir(nome)
    else:
        diretorio_atual = os.getcwd()
        diretorios = [diretorio for diretorio in os.listdir(diretorio_atual) if os.path.isdir(os.path.join(diretorio_atual, diretorio))]

        data_mais_recente = 0
        pasta_mais_recente = None

        for diretorio in diretorios:
            data_criacao = os.path.getctime(os.path.join(diretorio_atual, diretorio))
            if data_criacao > data_mais_recente:
                data_mais_recente = data_criacao
                pasta_mais_recente = diretorio

        if pasta_mais_recente:
            os.chdir(os.path.join(diretorio_atual, pasta_mais_recente))
            print("Diretório mais recente encontrado:", pasta_mais_recente)
        else:
            print("Não foi possível encontrar um diretório mais recente.")
