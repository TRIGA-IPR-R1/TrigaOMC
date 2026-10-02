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

libTrigaIprR1.simu = True
libTrigaIprR1.plot = False
libTrigaIprR1.verbose = False

if __name__ != '__main__':
    exit(1)

libTrigaIprR1.entra_resultados()
UP = libTrigaIprR1.TrigaIprR1.posição_barra_up
DOWN = libTrigaIprR1.TrigaIprR1.posição_barra_down

print("""
###########################
# Coeficientes cineticos core1 (fresco) com barras extraidas:
# - Médoto K-prompt: Beff = 1 - Kp/K
# - Método IFP: Lambda_eff, beta_i,eff
# - Método direto: beta_i e lambda_i (nao adjunto)
###########################
""")

# Criando diretório de resultados de coeficientes cineticos e copiando inputs
libTrigaIprR1.mkdir(voltar=False, nome="coeficientes_cineticos", data=True, cpinputs=True)


# Simulando Kp (atrasados=False)
libTrigaIprR1.mkdir(voltar=False, nome="kp_atrasados_false", data=False)
triga = libTrigaIprR1.TrigaIprR1()
triga.geometria(
    load=libTrigaIprR1_load.core1,
    tipo_geometria="circular",
    posição_barra_controle=UP,
    posição_barra_regulação=UP,
    posição_barra_segurança=UP,
)
triga.simulacao_autovalor(
    particulas=10000,
    ciclos=100,
    inativo=50,
    n_atrasados=False,
)
# Coletando resultados de Kp
kp = triga.get_keff()



# Simulando Keff, IFP e cinetica (atrasados=True)
libTrigaIprR1.mkdir(voltar=True, nome="atrasados_true", data=False)
triga = libTrigaIprR1.TrigaIprR1()
triga.geometria(
    load=libTrigaIprR1_load.core1,
    tipo_geometria="circular",
    posição_barra_controle=UP,
    posição_barra_regulação=UP,
    posição_barra_segurança=UP,
)
triga.contagem_cinetica_metodo_ifp()
triga.contagem_cinetica_metodo_direto()
triga.simulacao_autovalor(
    particulas=10000,
    ciclos=100,
    inativo=50,
    n_atrasados=True,
)

# Coletando resultados de Keff, IFP e cinetica
k = triga.get_keff()
print(f"keff (atrasados_true): {k}")
ifp = triga.contagem_cinetica_metodo_ifp(get=True, processar=True)
cin = triga.contagem_cinetica_metodo_direto(get=True, processar=True)






# Calculando beff pelo método k-prompt
beff_kprompt = 1.0 - kp / k


# Imprimindo resultados
print("")
print("###########################")
print("# Resumo coeficientes cineticos")
print("###########################")
print(f"K  (atrasados=True ): {k}")
print(f"Kp (atrasados=False): {kp}")
print(f"Beff (método K-prompt)       : {beff_kprompt}  ({beff_kprompt * 1e5} pcm)")
if ifp is not None:
    print(f"Beff (método IFP)            : {ifp['beta_eff']}  ({ifp['beta_eff'] * 1e5} pcm)")
    print(f"Lambda_eff (método IFP)          : {ifp['Lambda_eff']} [s]")
    print(f"ell (método IFP)                 : {ifp['ell']} [s]")
if cin is not None:
    print(f"beff (método direto)         : {cin['beta']}  ({cin['beta'] * 1e5} pcm)")
