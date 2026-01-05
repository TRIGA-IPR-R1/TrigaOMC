#!/usr/bin/python

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


libTrigaIprR1.mkdir(voltar=False, nome="keff", data=False, cpinputs=False)

# Simulação de autovalor (keff, fulga, etc)
triga.simulacao_autovalor()
