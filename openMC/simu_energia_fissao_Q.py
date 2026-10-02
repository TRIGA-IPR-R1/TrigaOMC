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

libTrigaIprR1.simu = True
libTrigaIprR1.plot = False
libTrigaIprR1.verbose = False

if __name__ != '__main__':
    exit(1)

libTrigaIprR1.entra_resultados()
UP = libTrigaIprR1.TrigaIprR1.posição_barra_up

print("""
###########################
# Energia recuperável por fissão (Q)
# - kappa-fission / fission
# - combustível fresco (core1)
# - barras extraídas
###########################
""")

libTrigaIprR1.mkdir(voltar=False, nome="energia_fissao_Q", data=True, cpinputs=True)

triga = libTrigaIprR1.TrigaIprR1()
triga.geometria(
    load=libTrigaIprR1_load.core1,
    tipo_geometria="circular",
    posição_barra_controle=UP,
    posição_barra_regulação=UP,
    posição_barra_segurança=UP,
)
triga.contagem_global_Q()
triga.simulacao_autovalor(
    particulas=10000,
    ciclos=100,
    inativo=50,
)

k = triga.get_keff()
q = triga.contagem_global_Q(get=True, processar=True)

print("")
print("###########################")
print("# Resumo Q")
print("###########################")
print(f"keff: {k}")
Q_mean = float(q['Q'].mean.ravel()[0])
Q_std = float(q['Q'].std_dev.ravel()[0])
print(f"Q: {Q_mean:.6e} +/- {Q_std:.6e} [eV/fissão]")
print(f"Q: {Q_mean/1e6:.6f} +/- {Q_std/1e6:.6f} [MeV/fissão]")
