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
libTrigaIprR1.mkdir(voltar=False, nome="resultados_simu_basica", data=True, cpinputs=True)


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
    posição_barra_controle=triga.up,
    posição_barra_regulação=triga.up,
    posição_barra_segurança=triga.up
    )

# Plotanto geometria
libTrigaIprR1.mkdir(voltar=False, nome="plots")
triga.plot2D_secao_transversal(basis="xy")
triga.plot2D_secao_transversal(basis="xz",width=[169,112.24])
triga.plot2D_secao_transversal(basis="yz",width=[169,112.24])

# Simulação de autovalor
libTrigaIprR1.mkdir(voltar=True, nome="keff")
triga.simulacao_autovalor(particulas=1000, ciclos=300, inativo=150)

# Retirando o keff
sp = openmc.StatePoint('statepoint.'+str(triga.Settings.batches)+'.h5')
print('Keff: ', sp.keff)
sp.close()




