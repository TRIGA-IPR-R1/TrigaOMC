#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma classe, importe ela ao invés de a executar diretamente...")
    exit(1)

"""
Classe principal para definir o reator TRIGA IPR-R1

O cronstrutor (init) define o reator com configurações padrão.

Para alterar as configurações do reator, crie materiais, geometrias, etc, nos locais adequados, e as chame depois de criar o objeto.

Exemplo de simulção de 2 geometrias com materiais diferentes:
import libTrigaIprR1
triga = libTrigaIprR1.TrigaIprR1()
triga.geo.nucleo1960()
triga.run()
triga.geo.nucleoImaginario(mat1="Pu239", mat1_porcentagem=20, mat2="Th232", mat2_porcentagem=80)
triga.run()
"""

import os
os.system('clear') #Limpe o terminal
    
import openmc

import libTrigaFuncionalidades as func

import libTrigaConfiguracoes
import libTrigaGeometria
import libTrigaPlot

class TrigaIprR1:

    def __init__(self,
                simu=True,
                verbose=True,
                particulas=1000,
                ciclos=100,
                inativo=10,
                n_atrasados=True,
                foton=False,
                ):
        
        #Definindo variáveis controle
        func.simu = simu
        func.verbose = verbose
        
        #Definindo reator: material e geometria
        self.geo = libTrigaGeometria.TrigaGeometria(simu, verbose)
        self.geo.geometriaPadrao("comb_fresco")

        #Definindo simulação
        self.conf = libTrigaConfiguracoes.TrigaConfiguracoes(simu, verbose)
        self.conf = self.conf.configuracoes(particulas, ciclos, inativo, n_atrasados, foton)
        
        #Criando objeto para plotagens
        self.plot = libTrigaPlot.TrigaPlot(simu, verbose)
        
    def __del__(self):
        func.printv(f"Objeto destruído.")

    def simulacao_autovalor(self):
        func.printv("################################################")
        func.printv("#########     Executando simulação     #########")
        func.printv("#########        de autovalores        #########")
        func.printv("################################################")
        if func.simu:
            openmc.run()

    
    