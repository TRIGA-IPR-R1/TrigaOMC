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
import time

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

for i in range(1,4):
    print(f"####### {i} #######")

    libTrigaIprR1.mkdir(voltar=False if i ==1 else True, nome=f"divisoes_{i**3}")
    inicio_gerar_reator = time.time()
    triga.materiais(comb_divisions_r=i,comb_divisions_theta=i,comb_divisions_z=i)
    triga.geometria(load=libTrigaIprR1_load.core_atual, tipo_geometria="cilindrica")
    triga.configuracoes(particulas=100000, ciclos=100)
    fim_gerar_reator = time.time()

    # Plotanto geometria
    libTrigaIprR1.mkdir(voltar=False, nome="plots")
    inicio_plotar = time.time()
    triga.plot2D_secao_transversal()
    triga.plot2D_secao_transversal(basis="xz")
    triga.plot2D_secao_transversal(basis="yz")
    fim_plotar = time.time()


    # Simulação de autovalor (keff, fulga, etc)
    libTrigaIprR1.mkdir(voltar=True, nome="keff")
    inicio_autovalor = time.time()
    triga.simulacao_autovalor()
    fim_autovalor = time.time()


    # Simulação de queima
    libTrigaIprR1.mkdir(voltar=True, nome="queima")
    inicio_queima = time.time()
    triga.configuracoes(particulas=10000, ciclos=100)
    triga.simulacao_queima(precisao=1)
    fim_queima = time.time()

    tempo_gerar_reator = fim_gerar_reator - inicio_gerar_reator
    tempo_plotar = fim_plotar - inicio_plotar
    tempo_autovalor = fim_autovalor - inicio_autovalor
    tempo_queima = fim_queima - inicio_queima

    libTrigaIprR1.chdir("..")

    with open("../tempos.txt", "a") as f:
        f.write(f"comb_divisions_r={i}, comb_divisions_theta={i}, comb_divisions_z={i} ; ")
        f.write(f"{tempo_gerar_reator:.2f} ; ")
        f.write(f"{tempo_plotar:.2f} ; ")
        f.write(f"{tempo_autovalor:.2f} ; ")
        f.write(f"{tempo_queima:.2f} \n")

libTrigaIprR1.chdir("..")

for i in range(1,4):
    print(f"####### {i} #######")

    libTrigaIprR1.mkdir(voltar=False if i ==1 else True, nome=f"divisoes_z_{i**3}")
    inicio_gerar_reator = time.time()
    triga.materiais(comb_divisions_r=1,comb_divisions_theta=1,comb_divisions_z=i**3)
    triga.geometria(load=libTrigaIprR1_load.core_atual, tipo_geometria="cilindrica")
    triga.configuracoes(particulas=100000, ciclos=100)
    fim_gerar_reator = time.time()

    # Plotanto geometria
    libTrigaIprR1.mkdir(voltar=False, nome="plots")
    inicio_plotar = time.time()
    triga.plot2D_secao_transversal()
    triga.plot2D_secao_transversal(basis="xz")
    triga.plot2D_secao_transversal(basis="yz")
    fim_plotar = time.time()


    # Simulação de autovalor (keff, fulga, etc)
    libTrigaIprR1.mkdir(voltar=True, nome="keff")
    inicio_autovalor = time.time()
    triga.simulacao_autovalor()
    fim_autovalor = time.time()


    # Simulação de queima
    libTrigaIprR1.mkdir(voltar=True, nome="queima")
    inicio_queima = time.time()
    triga.configuracoes(particulas=10000, ciclos=100)
    triga.simulacao_queima(precisao=1)
    fim_queima = time.time()

    tempo_gerar_reator = fim_gerar_reator - inicio_gerar_reator
    tempo_plotar = fim_plotar - inicio_plotar
    tempo_autovalor = fim_autovalor - inicio_autovalor
    tempo_queima = fim_queima - inicio_queima

    libTrigaIprR1.chdir("..")

    with open("../tempos.txt", "a") as f:
        f.write(f"comb_divisions_r=1, comb_divisions_theta=1, comb_divisions_z={i**3} ; ")
        f.write(f"{tempo_gerar_reator:.2f} ; ")
        f.write(f"{tempo_plotar:.2f} ; ")
        f.write(f"{tempo_autovalor:.2f} ; ")
        f.write(f"{tempo_queima:.2f} \n")
