#!/usr/bin/python
#!/bin/python

#######################################################################
####                                                               ####
####    Centro de Desenvolvimento da Tecnologia Nuclear - CDTN     ####
####           Serviço de Tecnologia de Reatores - SETRE           ####
####                  Thalles Oliveira Campagnani                  ####
####                                                               ####
#######################################################################


import libTrigaIprR1

libTrigaIprR1.simu = True     #Altere conforme necessidade
libTrigaIprR1.plot = True     #Altere conforme necessidade
libTrigaIprR1.verbose = True  #Altere confrome necessidade

if __name__ != '__main__': #Caso seja importado como biblioteca
    libTrigaIprR1.simu = False    #Nunca altere essa linha!!
    libTrigaIprR1.plot = False    #Nunca altere essa linha!!
    libTrigaIprR1.verbose = False #Nunca altere essa linha!!


# Criando pasta para armazenar todos resultados (com data e copiando as entradas)
libTrigaIprR1.mkdir(voltar=False, nome="resultados", data=True, cpinputs=True)

# Criando reator
triga = libTrigaIprR1.TrigaIprR1()
#triga.geometria(tipo_geometria="hexagonal")

# Plotanto geometria
libTrigaIprR1.mkdir(voltar=False, nome="plots", data=False)
triga.plot2D_secao_transversal()
triga.plot2D_secao_transversal(basis="xz")
triga.plot2D_secao_transversal(basis="yz")

# Simulação de autovalor (keff, fulga, etc)
libTrigaIprR1.mkdir(voltar=True, nome="keff", data=False)
triga.simulacao_autovalor()
