#!/bin/python

#######################################################################
####                                                               ####
####    Centro de Desenvolvimento da Tecnologia Nuclear - CDTN     ####
####           Serviço de Tecnologia de Reatores - SETRE           ####
####                  Thalles Oliveira Campagnani                  ####
####                                                               ####
#######################################################################


import numpy as np
import openmc
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
# Captura radiativa (n,gamma)
# - U235 e U238
# - combustível fresco (core1)
# - barras extraídas
###########################
""")

libTrigaIprR1.mkdir(voltar=False, nome="captura_radiativa", data=True, cpinputs=True)

triga = libTrigaIprR1.TrigaIprR1()
triga.geometria(
    load=libTrigaIprR1_load.core1,
    tipo_geometria="circular",
    posição_barra_controle=UP,
    posição_barra_regulação=UP,
    posição_barra_segurança=UP,
)

tally = openmc.Tally(name='Captura e fissão U235 U238')
tally.scores = ['(n,gamma)', 'fission']
tally.nuclides = ['U235', 'U238']
triga.lista_contagens.append(tally)

tally_total = openmc.Tally(name='Captura radiativa total')
tally_total.scores = ['(n,gamma)']
triga.lista_contagens.append(tally_total)

triga.simulacao_autovalor(
    particulas=10000,
    ciclos=100,
    inativo=50,
)

k = triga.get_keff()
sp = openmc.StatePoint(f"statepoint.{triga.Settings.batches}.h5")
t = sp.get_tally(name='Captura e fissão U235 U238')
t_tot = sp.get_tally(name='Captura radiativa total')

nuclideos = ['U235', 'U238']
print("")
print("###########################")
print("# Frações de captura radiativa")
print("###########################")
print(f"keff: {k}")
print()

gamma_total = float(t_tot.mean.ravel()[0])
gamma_total_std = float(t_tot.std_dev.ravel()[0])
print(f"(n,gamma) total: {gamma_total:.6e} +/- {gamma_total_std:.6e} [1/fonte]")
print()

linhas = []
for nuc in nuclideos:
    g = float(t.get_values(scores=['(n,gamma)'], nuclides=[nuc]).ravel()[0])
    g_std = float(t.get_values(scores=['(n,gamma)'], nuclides=[nuc], value='std_dev').ravel()[0])
    f = float(t.get_values(scores=['fission'], nuclides=[nuc]).ravel()[0])
    f_std = float(t.get_values(scores=['fission'], nuclides=[nuc], value='std_dev').ravel()[0])
    linhas.append((nuc, g, g_std, f, f_std))

g_u = sum(g for _, g, _, _, _ in linhas)
print(f"{'nuclídeo':8s}  {'(n,γ)/fonte':>14s}  {'std':>12s}  {'fissão/fonte':>14s}  {'α=γ/f':>8s}  {'γ/(γ+f) %':>10s}  {'% do γ U':>10s}  {'% do γ tot':>12s}")
for nuc, g, g_std, f, f_std in linhas:
    alpha = g / f if f else float('nan')
    frac_abs = 100.0 * g / (g + f) if (g + f) else float('nan')
    print(f"{nuc:8s}  {g:14.6e}  {g_std:12.6e}  {f:14.6e}  {alpha:8.4f}  {frac_abs:10.4f}  {100*g/g_u:10.4f}  {100*g/gamma_total:12.4f}")

print()
print(f"U235+U238 / (n,γ) total do núcleo: {100*g_u/gamma_total:.4f} %")
sp.close()
