#!/usr/bin/python

#######################################################################
####                                                               ####
####    Centro de Desenvolvimento da Tecnologia Nuclear - CDTN     ####
####           Serviço de Tecnologia de Reatores - SETRE           ####
####                  Thalles Oliveira Campagnani                  ####
####                                                               ####
#######################################################################

import libTrigaFuncionalidades as func

if __name__ == '__main__': #Caso seja executado no terminal
    simu = True     #Altere conforme necessidade
    verbose = True  #Altere confrome necessidade
else:                      #Caso seja importado
    simu = False    #Não altere essa linha!!
    verbose = False #Não altere essa linha!!

import libTrigaIprR1



# Criando pasta para armazenar todos resultados (com data e copiando as entradas)
func.mkdir(voltar=False, nome="resultados", data=True, cpinputs=True, on=simu)

# Criando reator
triga = libTrigaIprR1.TrigaIprR1(
    simu=simu,
    verbose=verbose,
    particulas=1000,
    ciclos=100,
    inativo=10,
    n_atrasados=True,
    foton=False
    )

# Criando uma pasta para armazenar os plots 
libTrigaIprR1.func.mkdir(voltar=False, nome="plots", data=False, cpinputs=False, on=simu)

# Plotando 3 vistas
triga.plot.plot2D_secao_transversal(
    geometria=triga.geo.geometrias,
    colors=triga.geo.mat.colors,
    basis="xy",
    width=[142,170],
    pixels=[5000,5000],
    origin=(0,0,0)
    )
triga.plot.plot2D_secao_transversal(
    geometria=triga.geo.geometrias,
    colors=triga.geo.mat.colors,
    basis='xz',
    )
triga.plot.plot2D_secao_transversal(
    geometria=triga.geo.geometrias,
    colors=triga.geo.mat.colors,
    basis='yz',
    )

# Voltando uma pasta acima e criando uma pasta para armazenar os resultados da simulação
libTrigaIprR1.func.mkdir(voltar=True, nome="keff", data=False, cpinputs=False, on=simu)

# Simulação de autovalor (keff, fulga, etc)
triga.simulacao_autovalor()
