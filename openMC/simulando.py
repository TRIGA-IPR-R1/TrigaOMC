#!/bin/python

#######################################################################
####                                                               ####
####    Centro de Desenvolvimento da Tecnologia Nuclear - CDTN     ####
####           Serviço de Tecnologia de Reatores - SETRE           ####
####                  Thalles Oliveira Campagnani                  ####
####                                                               ####
#######################################################################


import libTrigaIprR1
import libTrigaIprR1_load

libTrigaIprR1.simu = True     #Altere conforme necessidade
libTrigaIprR1.plot = True     #Altere conforme necessidade
libTrigaIprR1.verbose = True  #Altere confrome necessidade

if __name__ != '__main__': #Caso seja importado como biblioteca
    exit(1)


# Criando pasta para armazenar todos resultados (com data e copiando as entradas)
libTrigaIprR1.mkdir(voltar=False, nome="resultados", data=True, cpinputs=True)

# Criando reator
triga = libTrigaIprR1.TrigaIprR1()
triga.materiais(comb_divisions_z=25)
triga.geometria(load=libTrigaIprR1_load.core_atual, tipo_geometria="cilindrica")
triga.configuracoes(particulas=10000, ciclos=100)

# Plotanto geometria
libTrigaIprR1.mkdir(voltar=False, nome="plots")
triga.plot2D_secao_transversal(basis="xy")
triga.plot2D_secao_transversal(basis="xz")
triga.plot2D_secao_transversal(basis="yz")

# Simulação de autovalor (keff, fulga, etc)
libTrigaIprR1.mkdir(voltar=True, nome="keff")
triga.simulacao_autovalor()

# Simulação de queima
libTrigaIprR1.mkdir(voltar=True, nome="queima")
triga.simulacao_queima(precisao=1)
