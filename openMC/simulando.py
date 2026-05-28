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
import openmc

libTrigaIprR1.simu = True     #Altere conforme necessidade
libTrigaIprR1.plot = True     #Altere conforme necessidade
libTrigaIprR1.verbose = True  #Altere confrome necessidade

if __name__ != '__main__': #Caso seja importado como biblioteca
    exit(1)


# Criando pasta para armazenar todos resultados (com data e copiando as entradas)
libTrigaIprR1.mkdir(voltar=False, nome="resultados", data=True, cpinputs=True)

vector_keff = []
vector_position = []

up = 38
down = 0
passo = 5
for position in range(down,up,passo):
    # Criando reator
    triga = libTrigaIprR1.TrigaIprR1()
    triga.materiais(comb_divisions_z=25)
    triga.geometria(
        load=libTrigaIprR1_load.core1,
        tipo_geometria="hexagonal",
        posição_barra_controle=position,
        posição_barra_regulação=up,
        posição_barra_segurança=up
        )
    triga.configuracoes(particulas=1000, ciclos=300, inativo=150)

    # Plotanto geometria
    #libTrigaIprR1.mkdir(voltar=False, nome="plots")
    #triga.plot2D_secao_transversal(basis="xy")
    #triga.plot2D_secao_transversal(basis="xz",width=[169,112.24])
    #triga.plot2D_secao_transversal(basis="yz",width=[169,112.24])

    # Simulação de autovalor (keff, fuga, etc)
    #libTrigaIprR1.mkdir(voltar=True, nome="keff")
    triga.simulacao_autovalor()

    sp = openmc.StatePoint('statepoint.'+str(triga.Settings.batches)+'.h5')

    # Retirando o keff
    print('')
    keff = sp.keff
    vector_keff.append(keff)
    vector_position.append(position)

    sp.close()

    # Simulação de queima
    #libTrigaIprR1.mkdir(voltar=True, nome="queima")
    #triga.simulacao_queima(precisao=1)

print(vector_keff)
print(vector_position)