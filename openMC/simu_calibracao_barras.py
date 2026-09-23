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

libTrigaIprR1.simu = False    # Ativa/Desativa todas simulações
libTrigaIprR1.plot = True     # Ativa/Desativa todos plots
libTrigaIprR1.verbose = True  # Ativa/Desativa todos print verbosos

if __name__ != '__main__': #Caso seja importado como biblioteca
    exit(1)

# Lógica para criar uma nova simulação ou trabalhar com os dados da última simulação realizada
if not libTrigaIprR1.simu and not libTrigaIprR1.plot:
    print("""
###########################
# Trabalhando dados da última simulação realizada
###########################
""")
    libTrigaIprR1.chdir("resultados_calibracao_barras", ultimo=True) # Volta para ultima simulação realizada
else:
    print("""
###########################
# Calibração das barras de controle, regulacao e seguranca
# - variando a posição de cada barra da posição mais inferior para a mais superior
# - outras barras fixas nas posições superiores
###########################
""")
    libTrigaIprR1.mkdir(voltar=False, nome="resultados_calibracao_barras", data=True, cpinputs=True)




# Laço para calibrar cada barra
voltar_diretorio = False
for barra in ["controle","regulacao","seguranca"]:
    libTrigaIprR1.mkdir(voltar=voltar_diretorio, nome=barra)
    voltar_diretorio = True

    # Vetor para armazenar os keffs
    vector_keff = []
    vector_position = []
    
    # Definindo as posições iniciais de cada barra
    barra_controle =  libTrigaIprR1.TrigaIprR1.up
    barra_regulação = libTrigaIprR1.TrigaIprR1.up
    barra_segurança = libTrigaIprR1.TrigaIprR1.up
    
    # Definindo a forma como será variada a barra
    up = libTrigaIprR1.TrigaIprR1.up
    down = libTrigaIprR1.TrigaIprR1.down
    passo = 5

    # Laço para calibrar a barra da vez
    voltar_diretorio = False
    for position in list(range(down, up, passo)) + [up]:
        libTrigaIprR1.mkdir(voltar=voltar_diretorio, nome=barra+"_"+str(position))
        voltar_diretorio = True

        # Definindo qual barra vai variar
        if barra == "controle":
            barra_controle = position
        elif barra == "regulacao":
            barra_regulação = position
        elif barra == "seguranca":
            barra_segurança = position
        else:
            print("Erro: barra inválida")
            exit(1)

        # Criando reator
        triga = libTrigaIprR1.TrigaIprR1()
        triga.geometria(
            load=libTrigaIprR1_load.core1,
            tipo_geometria="circular",
            posição_barra_controle =barra_controle,
            posição_barra_regulação=barra_regulação,
            posição_barra_segurança=barra_segurança
            )

        # Plotanto geometria
        libTrigaIprR1.mkdir(voltar=False, nome="plots")
        triga.plot2D_secao_transversal(basis="xy")
        triga.plot2D_secao_transversal(basis="xz",width=[169,112.24])
        triga.plot2D_secao_transversal(basis="yz",width=[169,112.24])

        # Simulação de autovalor (keff, fuga, etc)
        libTrigaIprR1.mkdir(voltar=True, nome="estado_estacionario")
        triga.simulacao_autovalor(particulas=1000, ciclos=300, inativo=150)


        # Trabalhando dados da simulação
        ## Não entra aqui se estiver no modo de SOMENTE plotagem
        if not (libTrigaIprR1.plot and not libTrigaIprR1.simu):

            # Retirando o keff
            print('')
            keff = triga.get_keff()
            vector_keff.append(keff)
            vector_position.append(position)

        libTrigaIprR1.chdir("..")
    
    print(vector_keff)
    print(vector_position)
    libTrigaIprR1.chdir("..")