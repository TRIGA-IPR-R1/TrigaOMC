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

UP = libTrigaIprR1.TrigaIprR1.posição_barra_up
DOWN = libTrigaIprR1.TrigaIprR1.posição_barra_down

# Regulacao e seguranca inseridas: unico estacionamento em que
# mover so a barra de controle atravessa k=1 nos dois nucleos.
Z_REG = DOWN
Z_SEG = DOWN


def montar(load, z_controle):
    openmc.reset_auto_ids()
    libTrigaIprR1.TrigaIprR1.lista_contagens = openmc.Tallies()
    triga = libTrigaIprR1.TrigaIprR1()
    triga.geometria(
        load=load,
        tipo_geometria="circular",
        posição_barra_controle=z_controle,
        posição_barra_regulação=Z_REG,
        posição_barra_segurança=Z_SEG,
    )
    return triga


def keff_busca(load, z_controle):
    triga = montar(load, z_controle)
    triga.simulacao_autovalor(
        particulas=20000,
        ciclos=60,
        inativo=30,
        n_atrasados=True,
    )
    return triga.get_keff()


def busca_posicao_critica(load, nome):
    print(f"\n==== Busca de criticidade: {nome} ====")
    print("  regulacao e seguranca inseridas; ajusta so a barra de controle")
    k_down = keff_busca(load, DOWN)
    k_up = keff_busca(load, UP)
    print(f"  controle z={DOWN:.2f} (inserida)  k={k_down}")
    print(f"  controle z={UP:.2f} (extraida)   k={k_up}")

    if k_down.nominal_value > 1.0 and k_up.nominal_value > 1.0:
        print("  k>1 mesmo com controle inserido. Usando z=0.")
        return DOWN, k_down
    if k_down.nominal_value < 1.0 and k_up.nominal_value < 1.0:
        print("  k<1 mesmo com controle extraido. Usando z=up.")
        return UP, k_up

    lo, hi = DOWN, UP
    k_lo, k_hi = k_down, k_up
    z, k = lo, k_lo
    for i in range(5):
        z = lo + (1.0 - k_lo.nominal_value) / (k_hi.nominal_value - k_lo.nominal_value) * (hi - lo)
        z = max(DOWN, min(UP, z))
        k = keff_busca(load, z)
        print(f"  iter {i+1}: z={z:.3f}  k={k}")
        if abs(k.nominal_value - 1.0) < 0.001:
            break
        if k.nominal_value < 1.0:
            lo, k_lo = z, k
        else:
            hi, k_hi = z, k
    return z, k


def cinetica_em(load, z_controle, etiqueta):
    libTrigaIprR1.verbose = True
    libTrigaIprR1.mkdir(voltar=False, nome=etiqueta, data=False)

    libTrigaIprR1.mkdir(voltar=False, nome="atrasados_true", data=False)
    triga = montar(load, z_controle)
    triga.contagem_ifp()
    triga.contagem_cinetica()
    triga.simulacao_autovalor(
        particulas=100000,
        ciclos=100,
        inativo=50,
        n_atrasados=True,
    )
    k = triga.get_keff()
    print(f"keff (atrasados_true): {k}")
    ifp = triga.contagem_ifp(get=True, processar=True)
    cin = triga.contagem_cinetica(get=True, processar=True)

    libTrigaIprR1.mkdir(voltar=True, nome="atrasados_false", data=False)
    triga = montar(load, z_controle)
    triga.simulacao_autovalor(
        particulas=100000,
        ciclos=100,
        inativo=50,
        n_atrasados=False,
    )
    kp = triga.get_keff()
    print(f"keff (atrasados_false): {kp}")
    libTrigaIprR1.chdir("..")
    libTrigaIprR1.verbose = False
    return k, kp, ifp, cin


print("""
###########################
# Coeficientes cineticos em criticidade
# So a barra de controle e ajustada.
# Regulacao e seguranca ficam inseridas (unico
# estacionamento em que k=1 e alcancavel nos dois nucleos).
# 100000 particulas, 100 ativos, 50 inativos
###########################
""")

libTrigaIprR1.entra_resultados()
libTrigaIprR1.mkdir(voltar=False, nome="coeficientes_cineticos_critico", data=True, cpinputs=True)

casos = [
    ("core1", libTrigaIprR1_load.core1),
    ("core_atual", libTrigaIprR1_load.core_atual),
]

resumo = []
voltar = False
for nome, load in casos:
    libTrigaIprR1.mkdir(voltar=voltar, nome=f"busca_{nome}", data=False)
    voltar = True
    z_crit, k_busca = busca_posicao_critica(load, nome)
    print(f"Posicao critica {nome}: z_controle={z_crit:.3f}  k_busca={k_busca}")
    libTrigaIprR1.chdir("..")

    k, kp, ifp, cin = cinetica_em(load, z_crit, nome)
    beff_kprompt = 1.0 - kp / k
    resumo.append((nome, z_crit, k, kp, beff_kprompt, ifp, cin))

print("")
print("###########################")
print("# Resumo criticidade (ajuste so da barra de controle)")
print("# regulacao e seguranca inseridas")
print("###########################")
for nome, z_crit, k, kp, beff_kprompt, ifp, cin in resumo:
    print(f"\n--- {nome}  z_controle={z_crit:.3f} cm ---")
    print(f"k  (atrasados=True ): {k}")
    print(f"kp (atrasados=False): {kp}")
    print(f"beff k-prompt       : {beff_kprompt}  ({beff_kprompt * 1e5} pcm)")
    if ifp is not None:
        print(f"beff IFP            : {ifp['beta_eff']}  ({ifp['beta_eff'] * 1e5} pcm)")
        print(f"Lambda_eff          : {ifp['Lambda_eff']} [s]")
        print(f"ell                 : {ifp['ell']} [s]")
    if cin is not None:
        print(f"beff caso 1         : {cin['beta']}  ({cin['beta'] * 1e5} pcm)")
