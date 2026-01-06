#!/usr/bin/python

# Cancele caso seja executado diretamente.
if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)

import os
os.system('clear') #Limpe o terminal
from datetime import datetime
import numpy as np
import math
import matplotlib.pyplot as plt

import openmc

import libTrigaIprR1_load as load

"""
Variáveis de controle:

    simu: Controla se os XMLs serão gerados e a simulação será executada

    plot: Controla se os XMLs serão gerados e serão plotadas figuras

    verbose: Controla se a função printv imprimirá no terminal

"""


simu = True
plot = True
verbose = True


"""
Funções:
    printv: imprime no terminal se verbose é verdadeiro

    mkdir: cria uma pasta (com data ou não) (voltando para o diretorio anterior antes de criar ou não)

    chdir: muda para a pasta informada (se nenhuma pasta informada, procura a mais recente e muda para ela)
"""

def printv(inp):
    if verbose:
        print(inp)

def mkdir(nome="teste_sem_nome", data=False, voltar=True, cpinputs=False, on=True):
    if on:
        if (voltar==True):
            os.chdir("../")
        if (data==True):
            agora = datetime.now()
            nome = agora.strftime(nome+"_%Y%m%d_%H%M%S")
        if not os.path.exists(nome):
            os.makedirs(nome)
        os.chdir(nome)
        if cpinputs:
            os.system("cp ../*.py .")
    
def chdir(nome=None):
    if (nome != None):
        os.chdir(nome)
    else:
        diretorio_atual = os.getcwd()
        diretorios = [diretorio for diretorio in os.listdir(diretorio_atual) if os.path.isdir(os.path.join(diretorio_atual, diretorio))]

        data_mais_recente = 0
        pasta_mais_recente = None

        for diretorio in diretorios:
            data_criacao = os.path.getctime(os.path.join(diretorio_atual, diretorio))
            if data_criacao > data_mais_recente:
                data_mais_recente = data_criacao
                pasta_mais_recente = diretorio

        if pasta_mais_recente:
            os.chdir(os.path.join(diretorio_atual, pasta_mais_recente))
            print("Diretório mais recente encontrado:", pasta_mais_recente)
        else:
            print("Não foi possível encontrar um diretório mais recente.")


"""

"""


class DadosElementos:
    x: float             #Coordenada carteziana x
    y: float             #Coordenada carteziana y
    r: float             #Coordenada polar r
    theta: float         #Coordenada polar theta
    load: str = "água"   #Tipo de carregamento. Por padrão, não carregado (água)

def cria_elementos_com_coordenadas(
        qtd_aneis = 6,
        pitch_radial = 10.5
        ):

    elemento = {}
    for n_radial in range(qtd_aneis):               # Iterando sobre o número de anéis
        letra_anel = chr(65 + n_radial)             # Calcula a letra do respectivo anel (65 é o código ASCII para 'A')
        r = pitch_radial * n_radial                 # Calcula raio de acordo com n_radial
        qtd_elementos = 6 * n_radial                # Cada anel tem uma quantidade de elementos multiplo de 6, proporcial ao n_radial
        if qtd_elementos == 0:                      # Com excessão do primeiro anel
            qtd_elementos = 1                       # Que tem um único elemento (tubo central)
        for n_elemento in range(qtd_elementos):     # Iterando sobre o número de elementos do respectivo anel
            theta    = math.radians(90 + (360 / qtd_elementos) * n_elemento) # Calcula coordenanda theta em radianos # Nota: Girando 90 graus para corresponder a orientação padrão
            elemento[f"{letra_anel}{n_elemento}"] = DadosElementos(          # Salva coordenadas no elemento
                r       = r,
                theta   = theta,
                x       = r * math.cos(theta),
                y       = r * math.sin(theta)
                )
    return elemento

"""
Classe principal para definir o reator TRIGA IPR-R1

O construtor (init) define o reator com configurações padrão.

Para alterar as configurações do reator, crie materiais, geometrias, etc, nos locais adequados, e as chame depois de criar o objeto.

Exemplo de uso padrão:
    import libTrigaIprR1
    triga = libTrigaIprR1.TrigaIprR1()
    triga.run()
"""
class TrigaIprR1:

    def __init__(self):
        printv("Objeto iniciado.")
        self.materiais()
        self.geometria_cilindrica()
        self.configuracoes()
        
    def __del__(self):
        printv("Objeto destruído.")

    def mat_comb_fresco(
        self,
        #Número de série, Massa de ZrH (g), Massa de Urânio (g), Massa de U235 (g)
        num_serie,
        massa_zirconio  = 2050.0607,
        massa_uranio    = 154.90+38.2500,
        massa_u235      = 38.2500,
        hidretação      = 22.6445
        ):
            
        combustivel = openmc.Material(name = 'comb_' + num_serie)
        combustivel.add_nuclide('U235', massa_u235)
        combustivel.add_nuclide('U238', massa_uranio-massa_u235)
        combustivel.add_nuclide('Zr',   massa_zirconio)
        combustivel.add_nuclide('H1',   hidretação)
        combustivel.set_density('g/cm3', 18)
        
        return combustivel
        
    def materiais(
        self,
        comb='fresco'
        ):
        """
        Função para definir todos materiais da simulação.
            Materiais padrões são os materiais não queimáveis (revestimento, estruturas, refletor, refrigente, etc.)
            Meteriais combustíveis são queimados, portanto pode-se definílos como combistíveis frescos, ou queimados.
                No caso de queimados, é preciso passar o path para o arquivo de materiais.
                
        Args:
            comb (str, optional): 'fresco' ou 'queimado'
        """
        printv("################################################")
        printv("############ Definição dos Materiais ###########")
        printv("############     materiais_padrão    ###########")
        printv("################################################")
        
        self.Materials = openmc.Materials()
        self.colors = {}
        
        self.m_refrigerante = openmc.Material(name='Água Leve')
        self.m_refrigerante.add_nuclide('H1',  1.1187E-01, percent_type='wo')
        self.m_refrigerante.add_nuclide('H2',  3.3540E-05, percent_type='wo')
        self.m_refrigerante.add_nuclide('O16', 8.8574E-01, percent_type='wo')
        self.m_refrigerante.add_nuclide('O17', 3.5857E-04, percent_type='wo')
        self.m_refrigerante.add_nuclide('O18', 1.9982E-03, percent_type='wo')
        self.m_refrigerante.set_density('g/cm3', 1)
        self.Materials.append(self.m_refrigerante)
        self.colors[self.m_refrigerante] = 'blue'
        
        
        self.m_ar = openmc.Material(name='Ar')
        self.m_ar.add_nuclide('N14',  7.7826E-01, percent_type='ao')
        self.m_ar.add_nuclide('N15',  2.8589E-03, percent_type='ao')
        self.m_ar.add_nuclide('O16',  1.0794E-01, percent_type='ao')
        self.m_ar.add_nuclide('O17',  1.0156E-01, percent_type='ao')
        self.m_ar.add_nuclide('O18',  3.8829E-05, percent_type='ao')
        self.m_ar.add_nuclide('Ar36', 2.6789E-03, percent_type='ao')
        self.m_ar.add_nuclide('Ar38', 3.4177E-03, percent_type='ao')
        self.m_ar.add_nuclide('Ar40', 3.2467E-03, percent_type='ao')
        self.m_ar.set_density('g/cm3', 0.001225)
        self.Materials.append(self.m_ar)
        self.colors[self.m_ar] = 'white'
        
        
        self.m_aluminio = openmc.Material(name='Alúminio')
        self.m_aluminio.add_nuclide('Al27', 1, percent_type ='wo')
        self.m_aluminio.set_density('g/cm3', 2.7)
        self.Materials.append(self.m_aluminio)
        self.colors[self.m_aluminio] = 'gray'
        
        
        self.m_SS304 = openmc.Material(name='Aço INOX',)
        self.m_SS304.add_element('C',  4.3000E-04, percent_type = 'wo')
        self.m_SS304.add_element('Cr', 1.9560E-01, percent_type = 'wo')
        self.m_SS304.add_element('Ni', 9.6600E-02, percent_type = 'wo')
        self.m_SS304.add_element('Mo', 8.9000E-03, percent_type = 'wo')
        self.m_SS304.add_element('Mn', 5.4000E-04, percent_type = 'wo')
        self.m_SS304.add_element('Si', 5.0000E-04, percent_type = 'wo')
        self.m_SS304.add_element('Cu', 2.0000E-05, percent_type = 'wo')
        self.m_SS304.add_element('Co', 3.0000E-05, percent_type = 'wo')
        self.m_SS304.add_element('P',  2.7000E-04, percent_type = 'wo')
        self.m_SS304.add_element('S',  1.0000E-04, percent_type = 'wo')
        self.m_SS304.add_element('N',  1.4000E-04, percent_type = 'wo')
        self.m_SS304.add_element('Fe', 6.9687E-01, percent_type = 'wo')
        self.m_SS304.set_density('g/cm3', 7.92)
        self.Materials.append(self.m_SS304)
        self.colors[self.m_SS304] = 'silver'
        
        if(comb=='fresco'):
            printv("################################################")
            printv("############ Definição dos Materiais ###########")
            printv("############       comb_fresco       ###########")
            printv("################################################")
            
            #Semente: Valores originais de cada elemento cobustível na data da compra.
            
            self.m_comb = {}
            #Número de série, Massa de ZrH (g), Massa de Urânio (g), Massa de U235 (g)
            #Elementos de alumínio. Comprados em 1960.
            self.m_comb['1314']   =  self.mat_comb_fresco('1314',   2252.84, 195.10, 38.65)
            self.m_comb['1188']   =  self.mat_comb_fresco('1188',   2240.47, 194.47, 38.52)
            self.m_comb['1289']   =  self.mat_comb_fresco('1289',   2246.71, 194.12, 38.46)
            self.m_comb['1286']   =  self.mat_comb_fresco('1286',   2243.74, 193.19, 38.27)
            self.m_comb['1230']   =  self.mat_comb_fresco('1230',   2256.41, 193.15, 38.26)
            self.m_comb['1297']   =  self.mat_comb_fresco('1297',   2247.20, 192.59, 38.15)
            self.m_comb['1298']   =  self.mat_comb_fresco('1298',   2252.94, 191.05, 37.85)
            self.m_comb['7194']   =  self.mat_comb_fresco('7194',   2293.00, 193.00, 38.00)
            self.m_comb['1315']   =  self.mat_comb_fresco('1315',   2250.96, 190.66, 37.77)
            self.m_comb['7192']   =  self.mat_comb_fresco('7192',   2292.00, 192.00, 38.00)
            self.m_comb['1235']   =  self.mat_comb_fresco('1235',   2249.97, 190.35, 37.71)
            self.m_comb['1222']   =  self.mat_comb_fresco('1222',   2250.27, 190.15, 37.67)
            self.m_comb['7193']   =  self.mat_comb_fresco('7193',   2297.00, 193.00, 38.00)
            self.m_comb['1351']   =  self.mat_comb_fresco('1351',   2247.30, 189.67, 37.57)
            self.m_comb['7191']   =  self.mat_comb_fresco('7191',   2299.00, 193.00, 38.00)
            self.m_comb['1311']   =  self.mat_comb_fresco('1311',   2247.79, 189.49, 37.54)
            self.m_comb['1269']   =  self.mat_comb_fresco('1269',   2258.19, 191.04, 37.85)
            self.m_comb['1254']   =  self.mat_comb_fresco('1254',   2255.42, 189.46, 37.53)
            self.m_comb['1206']   =  self.mat_comb_fresco('1206',   2256.61, 189.10, 37.46)
            self.m_comb['1303']   =  self.mat_comb_fresco('1303',   2253.14, 189.04, 37.45)
            self.m_comb['1287']   =  self.mat_comb_fresco('1287',   2253.43, 188.84, 37.41)
            self.m_comb['1296']   =  self.mat_comb_fresco('1296',   2266.11, 188.77, 37.40)
            self.m_comb['1282']   =  self.mat_comb_fresco('1282',   2251.75, 188.70, 37.38)
            self.m_comb['1343']   =  self.mat_comb_fresco('1343',   2251.75, 188.47, 37.34)
            self.m_comb['1196']   =  self.mat_comb_fresco('1196',   2247.79, 188.36, 37.31)
            self.m_comb['1212']   =  self.mat_comb_fresco('1212',   2249.97, 190.35, 37.71)
            self.m_comb['1199']   =  self.mat_comb_fresco('1199',   2250.17, 188.34, 37.31)
            self.m_comb['1347']   =  self.mat_comb_fresco('1347',   2248.19, 188.17, 37.28)
            self.m_comb['1220']   =  self.mat_comb_fresco('1220',   2239.58, 187.90, 37.22)
            self.m_comb['1218']   =  self.mat_comb_fresco('1218',   2255.02, 187.84, 37.21)
            self.m_comb['1209']   =  self.mat_comb_fresco('1209',   2251.46, 187.72, 37.19)
            self.m_comb['1280']   =  self.mat_comb_fresco('1280',   2253.43, 187.71, 37.19)
            self.m_comb['1350']   =  self.mat_comb_fresco('1350',   2245.72, 187.74, 37.19)
            self.m_comb['1272']   =  self.mat_comb_fresco('1272',   2257.69, 186.94, 37.03)
            self.m_comb['1348']   =  self.mat_comb_fresco('1348',   2256.61, 186.62, 36.97)
            self.m_comb['1197']   =  self.mat_comb_fresco('1197',   2247.50, 186.54, 36.95)
            self.m_comb[' 989']   =  self.mat_comb_fresco('0989',   2251.50, 186.42, 36.93)
            self.m_comb['1228']   =  self.mat_comb_fresco('1228',   2244.82, 186.10, 36.87)
            self.m_comb['1173']   =  self.mat_comb_fresco('1173',   2246.51, 186.01, 36.85)
            self.m_comb['1205']   =  self.mat_comb_fresco('1205',   2252.25, 185.81, 36.81)
            self.m_comb['1195']   =  self.mat_comb_fresco('1195',   2244.53, 184.73, 36.60)
            self.m_comb['1028']   =  self.mat_comb_fresco('1028',   2255.32, 184.71, 36.59)
            self.m_comb['1130']   =  self.mat_comb_fresco('1130',   2219.08, 184.18, 36.49)
            self.m_comb['1342']   =  self.mat_comb_fresco('1342',   2256.41, 184.12, 36.47)
            self.m_comb['1025']   =  self.mat_comb_fresco('1025',   2246.90, 183.12, 36.28)
            self.m_comb['1128']   =  self.mat_comb_fresco('1128',   2248.09, 183.22, 36.30)
            self.m_comb['1114']   =  self.mat_comb_fresco('1114',   2247.60, 185.65, 36.78)
            self.m_comb['1219']   =  self.mat_comb_fresco('1219',   2249.38, 185.57, 36.76)
            self.m_comb['1301']   =  self.mat_comb_fresco('1301',   2254.23, 185.52, 36.75)
            self.m_comb['1171']   =  self.mat_comb_fresco('1171',   2250.76, 185.46, 36.74)
            self.m_comb['1224']   =  self.mat_comb_fresco('1224',   2263.63, 185.39, 36.73)
            self.m_comb['1179']   =  self.mat_comb_fresco('1179',   2257.79, 182.20, 36.09)
            self.m_comb['1214']   =  self.mat_comb_fresco('1214',   2244.03, 191.19, 37.87)
            self.m_comb['1012']   =  self.mat_comb_fresco('1012',   2241.85, 184.93, 36.64)
            self.m_comb['1162']   =  self.mat_comb_fresco('1162',   2237.60, 184.38, 36.53)
            self.m_comb['1223']   =  self.mat_comb_fresco('1223',   2250.76, 184.34, 36.52)
            self.m_comb['1147']   =  self.mat_comb_fresco('1147',   2241.46, 182.46, 36.15)
            self.m_comb['1005']   =  self.mat_comb_fresco('1005',   2225.02, 185.34, 36.72)
            self.m_comb['1137']   =  self.mat_comb_fresco('1137',   2248.59, 185.06, 36.66)
            self.m_comb['1330']   =  self.mat_comb_fresco('1330',   2258.49, 190.84, 37.81)
            self.m_comb['1345']   =  self.mat_comb_fresco('1345',   2281.06, 190.47, 37.73)
            self.m_comb['1263']   =  self.mat_comb_fresco('1263',   2252.84, 190.14, 37.67)
            self.m_comb['1274']   =  self.mat_comb_fresco('1274',   2243.74, 189.60, 37.56)
            # Elementos de Inox. Comprados em 1972.
            self.m_comb['7198']   =  self.mat_comb_fresco('7198',   2297.00, 193.00, 38.00)
            self.m_comb['7197']   =  self.mat_comb_fresco('7197',   2297.00, 193.00, 38.00)
            self.m_comb['7196']   =  self.mat_comb_fresco('7196',   2294.00, 193.00, 38.00)
            self.m_comb['7195']   =  self.mat_comb_fresco('7195',   2295.00, 193.00, 38.00)
            self.m_comb['6821']   =  self.mat_comb_fresco('6821TC', 2305.00, 193.00, 38.00)
            
            #Adicionar todos combustíveis na lista, e definir uma cor para eles
            for material in self.m_comb.values():
                self.Materials.append(material)
                self.colors[material] = 'yellow'
            



    def geometria_cilindrica(
        self,
        load = load.core1
        ):
        
        
        cord_x_elem, cord_y_elem = calc_cordenadas()
        #for chave, x in cord_x_elem.items():
        #    y = cord_y_elem[chave] # Pega o valor de Y correspondente à mesma chave
        #    print(f"{chave}_x = {x:.4f}, {chave}_y = {y:.4f}")


        
        # Exemplo de como definir uma geometria com um material
        universo = openmc.Universe()
        celula = openmc.Cell()
        celula.fill = self.m_comb[load['B1']]
        universo.add_cell(celula)
        #self.geometrias.append(universo)

        
        # Criar a geometria contendo 
        self.geometrias = openmc.Geometry()
        self.geometrias.root_universe = universo
        


    def configuracoes(
        self,
        particulas=1000,
        ciclos=100,
        inativo=10,
        n_atrasados=True,
        foton=False
        ):
        printv("################################################")
        printv("########### Definição da Simulação  ############")
        printv("################################################")

        # Declarando settings como pertencente a self pois algumas variáveis podem ser ultilizadas depois, como por exemplo: settings.batches
        self.settings = openmc.Settings()
        self.settings.particles = particulas
        self.settings.batches = ciclos
        #self.settings.statepoint = {'batches': range(5, n + 5, 5)} #Use para gerar statepoint.#.h5 intermediários
        self.settings.create_delayed_neutrons = n_atrasados
        self.settings.photon_transport = foton
        self.settings.inactive = inativo
        self.settings.source = openmc.IndependentSource(space=openmc.stats.Point())
        self.settings.output = {'tallies': False} #Esta linha desabilita a geração do arquivo tallies.out
        printv(self.settings)



    def plot2D_secao_transversal(
        self,
        geometria,
        colors,
        basis="xz",
        width=[150,150],
        pixels=[5000,5000],
        origin=(0,0,0)
        ):
        print("################################################")
        print("############        Plot 2D         ############")
        print("################################################")
        if plot:
            ############ Plotar Secão Transversal
            secao_transversal = openmc.Plot.from_geometry(geometria)
            secao_transversal.type = 'slice'
            secao_transversal.basis = basis
            secao_transversal.width = width
            secao_transversal.origin = origin
            secao_transversal.filename = 'plot_' + basis + '_' + str(width) + '_' + str(pixels) + '_' + str(origin)
            secao_transversal.pixels = pixels
            secao_transversal.color_by = 'material'
            secao_transversal.colors = colors
        
            ############ Exportar Plots e Plotar
            plotagem = openmc.Plots(secao_transversal)
            plotagem.export_to_xml()
            self.materiais.export_to_xml()
            self.geometrias.export_to_xml()
            openmc.plot_geometry()

    def plot3D(
        self,
        geometria,
        colors,
        width=(150., 150., 150.),
        pixels=(500, 500, 500),
        origin=(0,0,0)
        ):
        print("################################################")
        print("############        Plot 3D         ############")
        print("################################################")
        if plot:
            ############ Plotar em 3D
            plot_3d = openmc.Plot.from_geometry(geometria)
            plot_3d.type = 'voxel'
            plot_3d.width = width
            plot_3d.origin = origin
            plot_3d.filename = 'plot_voxel_' + str(width) + '_' + str(pixels) + '_' + str(origin)
            plot_3d.pixels = pixels
            plot_3d.color_by = 'material'
            plot_3d.colors = colors
            
            ############ Exportar Plots e Plotar
            plotagem = openmc.Plots(plot_3d)
            plotagem.export_to_xml()  
            openmc.plot_geometry()
            self.materiais.export_to_xml()
            self.geometrias.export_to_xml()
            openmc.voxel_to_vtk(plot_3d.filename+'.h5', plot_3d.filename)



    def simulacao_autovalor(self):
        printv("################################################")
        printv("#########     Executando simulação     #########")
        printv("#########        de autovalores        #########")
        printv("################################################")
        if simu:
            self.materiais.export_to_xml()
            self.geometrias.export_to_xml()
            self.settings.export_to_xml()
            openmc.run()

    
    