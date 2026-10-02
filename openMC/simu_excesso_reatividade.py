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


libTrigaIprR1.entra_resultados()
UP = libTrigaIprR1.TrigaIprR1.posição_barra_up
libTrigaIprR1.mkdir(voltar=False, nome="excesso_reatividade", data=True, cpinputs=True)


print("""
###########################
# Excesso de reatividade
# - todas as barras extraídas
# - combustível fresco (core1)
# - geometria circular
# - sem divisão interna do elemento combustível
###########################
""")

libTrigaIprR1.mkdir(voltar=False, nome="simu_excesso_reatividade", data=False)
triga = libTrigaIprR1.TrigaIprR1()
triga.geometria(
    load=libTrigaIprR1_load.core1,
    tipo_geometria="circular",
    posição_barra_controle=UP,
    posição_barra_regulação=UP,
    posição_barra_segurança=UP,
    )

# Plotanto geometria
libTrigaIprR1.mkdir(voltar=False, nome="plots")
triga.plot2D_secao_transversal(basis="xy")
triga.plot2D_secao_transversal(basis="xz",width=[169,112.24])
triga.plot2D_secao_transversal(basis="yz",width=[169,112.24])

# Simulação de autovalor
libTrigaIprR1.mkdir(voltar=True, nome="keff")
triga.simulacao_autovalor(particulas=10000, ciclos=250, inativo=50)

keff = triga.get_keff()
rho = (keff - 1.0) / keff
print('Keff: ', keff)
print('Excesso de reatividade ρ: ', rho)
print('Excesso de reatividade ρ (pcm): ', rho * 1e5)
print('Excesso de reatividade ρ ($): ', rho * 1e5 / 800)




