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
from dataclasses import dataclass

import openmc
import openmc.model
import openmc.deplete

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
Função e classe para criar dicionário de objetos "elementos carregáveis" com suas coordenadas e outros parâmetros
"""

# Essa classe serve apenas para armazenar os dados dos elementos carregaveis de forma estruturada
@dataclass
class DadosElementosCarregaveis:
    # Coordenadas carteziana do elemento
    x: float
    y: float
    
    # Coordenadas polares do elemento
    r: float
    theta: float
    
    # O universo que irá preencher a célula do elemento
    universo = None # Por padrão "None" preencherá com vácuo
    
    # load e mat_combustivel são atualmente para fins de debug, mas poderão ter alguma últilidade posteriormente
    load = None                 # Para armazenar o tipo do elemento que veio do "load"
    mat_combustivel = None      # Para armazenar o material do combustível, caso seja um elemento combustível



def cria_elementosCarregaveis_com_coordenadas(
        tipo_geometria = "cilindrica",
        qtd_aneis = 6,
        pitch = 10.5,
        ):

    """
    # Essa função cria todos os objetos "elementos carregaveis" com suas respectivas coordenadas
    # Nota: Os parãmetros universo, load e mat_combustivel devem ser preenchidos posteriormente
    cilindrica
    hexagonal
    """
    
    elemento = {}                                                                   # Cria dicionário contendo todos elementos
    elemento["A1"] = DadosElementosCarregaveis(                                     # O anel A (n_radial=0), somente existe 1 elemento, o A1, então o crie na posição central
                    r       = 0.0, 
                    theta   = 0.0, 
                    x       = 0.0, 
                    y       = 0.0
                )
    
    if tipo_geometria == "cilindrica":                                              # Considerando geometria cilíndrica
        for n_radial in range(1,qtd_aneis):                                         # Iterando de 1 (anel B) até a quantidade de anéis
            letra_anel = chr(65 + n_radial)                                         # Calcula a letra do respectivo anel (65 é o código ASCII para 'A', logo quando n_radial é 0 a letra é A, e assim sucessivamente)
            r = pitch * n_radial                                                    # Calcula raio de acordo com n_radial baseado no pitch
            qtd_elementos = 6 * n_radial                                            # Cada anel tem uma quantidade de elementos multiplo de 6, proporcial ao n_radial
            for n_elemento in range(0,qtd_elementos):                               # Iterando sobre o número de elementos do respectivo anel
                theta    = math.radians(90 + (360 / qtd_elementos) * -n_elemento)   # Calcula coordenanda theta em radianos para cada elemento pertencente ao atual anel # Nota: Girando 90 graus para corresponder a orientação padrão # Nota2: A variável n_elemento tem que ser negativo para preencher no sentido horário
                elemento[f"{letra_anel}{n_elemento+1}"] = DadosElementosCarregaveis(# Cria objeto contendo os dados do respectivo elemento carregável
                    r       = r,                                                    # Salvando as coordenadas polares no elemento
                    theta   = theta,
                    x       = r * math.cos(theta),                                  # Convertendo e salvando as coordenada cartezianas
                    y       = r * math.sin(theta),
                    )
    
    # Nota: o OpenMC possui função para criar latice hexagonal automáticamente, mas a fim de padronizar a geração de geometria, a geometria hexagonal será gerada manualmente da mesma forma que a geometria cilíndrica
    elif tipo_geometria == "hexagonal":                                             # Considerando geometria hexagonal
        
        for n_radial in range(1,qtd_aneis):                                         # Iterando de 1 (anel B) até a quantidade de anéis
            letra_anel = chr(65 + n_radial)                                         # Calcula a letra do respectivo anel (65 é o código ASCII para 'A', logo quando n_radial é 0 a letra é A, e assim sucessivamente)
            angulos_passo = [-30, -90, -150, 150, 90, 30]                           # Definindo os angulos de cada aresta do hexagono
            n_elemento = 0                                                          # Começando pelo elemento 0 do respectivo anel
            x = 0.0                                                                 # Definindo coordenada carteziana X do elemento 0 de cada anel como 0 (Portanto o hexagono estará alinhado com o eixo Y)
            y = n_radial * pitch                                                    # Definindo coordenada carteziana Y do elemento 0 de cada anel conforme orientação acima
            for angulo in angulos_passo:                                            # Percorrendo cada aresta baseado no seu ângulo
                dx = pitch * math.cos(math.radians(angulo))                         # Calculando o vetor de deslocamento (dx, dy) para a aresta atual (dada pelo ângulo) com comprimento do pitch
                dy = pitch * math.sin(math.radians(angulo))
                for _ in range(n_radial):                                           # Caminhando n_radial vezes ao longo da aresta    #Nota: coincidemente n_radial é igual a quantidade de elementos em uma aresta
                    elemento[f"{letra_anel}{n_elemento+1}"] = DadosElementosCarregaveis(      # Cria objeto contendo os dados do respectivo elemento carregável 
                        x       = x,                                                        # Salva a coordenada carteziana X com o valor atual da variável x
                        y       = y,                                                        # Salva a coordenada carteziana Y com o valor atual da variável y
                        r       = math.hypot(x, y),                                         # Converte x e y para a coordenada polar r
                        theta   = (t := math.atan2(y, x)) + (2 * math.pi if t < 0 else 0)   # Converte x e y para a coordenada polar theta (caso seja negativo, some 2pi)
                    )
                    n_elemento += 1                                                 # Atualiza o valor de n_elemento para próxima execução
                    x += dx                                                         # Move as coordenadas cartesianas para a posição do próximo elemento, para próxima execução
                    y += dy
                        
    else:
        print("Erro na função 'cria_elementosCarregaveis_com_coordenadas()':\n 'geometria' deve receber string 'cilindrica' ou 'hexagonal'.")
        exit(0)
    
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
        self.geometria()
        self.configuracoes()
        
    def __del__(self):
        printv("Objeto destruído.")

    def mat_comb_fresco(
        self,
        num_serie,
        massa_zirconio  = 2050.0607,
        massa_uranio    = 154.90+38.2500,
        massa_u235      = 38.2500,
        hidretação      = 22.6445,
        densidade       = 18,
        ):
        """
        Função para padronizar a criação do material "combustível fresco" com as respectivas composições iniciais.
        Args:
            num_serie           = Número de série
            massa_zirconio      = Massa de total de ZrH (g)
            massa_uranio        = Massa de total de Urânio (g)
            massa_u235          = Massa de somente U235 (g)
            hidretação          = Massa de somente Hidrogênio (g)
        """

        combustivel = openmc.Material(name = 'comb_' + str(num_serie))
        combustivel.add_nuclide('U235',     percent = massa_u235,                  percent_type = "wo") #Nota: é definido o percentural com base na massa. A massa usada na simulação é dada pela densidade e volume.
        combustivel.add_nuclide('U238',     percent = massa_uranio-massa_u235,     percent_type = "wo")
        combustivel.add_element('Zr',       percent = massa_zirconio-hidretação,   percent_type = "wo")
        combustivel.add_element('H',        percent = hidretação,                  percent_type = "wo")
        combustivel.set_density('g/cm3',    densidade)

        combustivel.depletable = True
        if(num_serie>2000):
            combustivel.volume = 100
        else:
            combustivel.volume = 100
        
        return combustivel
        
    def materiais(
        self,
        queimado=None,
        ):
        """
        Função para definir todos materiais da simulação.
            Materiais padrões são os materiais não queimáveis (revestimento, estruturas, refletor, refrigente, etc.)
            Meteriais combustíveis são queimáveis, portanto pode-se definílos como combistíveis frescos, ou já queimados.
                No caso de queimados, é preciso passar o path para o arquivo de materiais na variável queimado.
                
        Args:
            queimado (str, optional): None ou 'path_to_h5'
        """
        printv("################################################")
        printv("############ Definição dos Materiais ###########")
        printv("############     materiais_padrão    ###########")
        printv("################################################")
        
        self.lista_materiais = openmc.Materials()
        self.m_colors = {}
        
        self.m_refrigerante = openmc.Material(name='Água Leve')
        self.m_refrigerante.add_nuclide('H1',  1.1187E-01, percent_type='wo')
        self.m_refrigerante.add_nuclide('H2',  3.3540E-05, percent_type='wo')
        self.m_refrigerante.add_nuclide('O16', 8.8574E-01, percent_type='wo')
        self.m_refrigerante.add_nuclide('O17', 3.5857E-04, percent_type='wo')
        self.m_refrigerante.add_nuclide('O18', 1.9982E-03, percent_type='wo')
        self.m_refrigerante.set_density('g/cm3', 1)
        self.lista_materiais.append(self.m_refrigerante)
        self.m_colors[self.m_refrigerante] = 'blue'
        
        self.m_grafite = openmc.Material(name='Grafite')
        self.m_grafite.add_element('C', 1, percent_type = 'wo')
        self.m_grafite.set_density('g/cm3', 2.15)
        self.lista_materiais.append(self.m_grafite)
        self.m_colors[self.m_grafite] = 'brown'

        
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
        self.lista_materiais.append(self.m_ar)
        self.m_colors[self.m_ar] = 'white'
        
        
        self.m_aluminio = openmc.Material(name='Alúminio')
        self.m_aluminio.add_nuclide('Al27', 1, percent_type ='wo')
        self.m_aluminio.set_density('g/cm3', 2.7)
        self.lista_materiais.append(self.m_aluminio)
        self.m_colors[self.m_aluminio] = 'gray'
        
        
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
        self.lista_materiais.append(self.m_SS304)
        self.m_colors[self.m_SS304] = 'silver'
        
        if(queimado==None):
            printv("################################################")
            printv("############ Definição dos Materiais ###########")
            printv("############       comb_fresco       ###########")
            printv("################################################")
            
            #Semente: Valores originais de cada elemento cobustível na data da compra.
            
            self.m_comb = {} #Dicionário contendo os materiais de todos combustíveis

            #Número de série, Massa de ZrH (g), Massa de Urânio (g), Massa de U235 (g)
            #Elementos de alumínio. Comprados em 1960.
            self.m_comb[1314]   =  self.mat_comb_fresco(1314,   2252.84, 195.10, 38.65)
            self.m_comb[1188]   =  self.mat_comb_fresco(1188,   2240.47, 194.47, 38.52)
            self.m_comb[1289]   =  self.mat_comb_fresco(1289,   2246.71, 194.12, 38.46)
            self.m_comb[1286]   =  self.mat_comb_fresco(1286,   2243.74, 193.19, 38.27)
            self.m_comb[1230]   =  self.mat_comb_fresco(1230,   2256.41, 193.15, 38.26)
            self.m_comb[1297]   =  self.mat_comb_fresco(1297,   2247.20, 192.59, 38.15)
            self.m_comb[1298]   =  self.mat_comb_fresco(1298,   2252.94, 191.05, 37.85)
            self.m_comb[7194]   =  self.mat_comb_fresco(7194,   2293.00, 193.00, 38.00)
            self.m_comb[1315]   =  self.mat_comb_fresco(1315,   2250.96, 190.66, 37.77)
            self.m_comb[7192]   =  self.mat_comb_fresco(7192,   2292.00, 192.00, 38.00)
            self.m_comb[1235]   =  self.mat_comb_fresco(1235,   2249.97, 190.35, 37.71)
            self.m_comb[1222]   =  self.mat_comb_fresco(1222,   2250.27, 190.15, 37.67)
            self.m_comb[7193]   =  self.mat_comb_fresco(7193,   2297.00, 193.00, 38.00)
            self.m_comb[1351]   =  self.mat_comb_fresco(1351,   2247.30, 189.67, 37.57)
            self.m_comb[7191]   =  self.mat_comb_fresco(7191,   2299.00, 193.00, 38.00)
            self.m_comb[1311]   =  self.mat_comb_fresco(1311,   2247.79, 189.49, 37.54)
            self.m_comb[1269]   =  self.mat_comb_fresco(1269,   2258.19, 191.04, 37.85)
            self.m_comb[1254]   =  self.mat_comb_fresco(1254,   2255.42, 189.46, 37.53)
            self.m_comb[1206]   =  self.mat_comb_fresco(1206,   2256.61, 189.10, 37.46)
            self.m_comb[1303]   =  self.mat_comb_fresco(1303,   2253.14, 189.04, 37.45)
            self.m_comb[1287]   =  self.mat_comb_fresco(1287,   2253.43, 188.84, 37.41)
            self.m_comb[1296]   =  self.mat_comb_fresco(1296,   2266.11, 188.77, 37.40)
            self.m_comb[1282]   =  self.mat_comb_fresco(1282,   2251.75, 188.70, 37.38)
            self.m_comb[1343]   =  self.mat_comb_fresco(1343,   2251.75, 188.47, 37.34)
            self.m_comb[1196]   =  self.mat_comb_fresco(1196,   2247.79, 188.36, 37.31)
            self.m_comb[1212]   =  self.mat_comb_fresco(1212,   2249.97, 190.35, 37.71)
            self.m_comb[1199]   =  self.mat_comb_fresco(1199,   2250.17, 188.34, 37.31)
            self.m_comb[1347]   =  self.mat_comb_fresco(1347,   2248.19, 188.17, 37.28)
            self.m_comb[1220]   =  self.mat_comb_fresco(1220,   2239.58, 187.90, 37.22)
            self.m_comb[1218]   =  self.mat_comb_fresco(1218,   2255.02, 187.84, 37.21)
            self.m_comb[1209]   =  self.mat_comb_fresco(1209,   2251.46, 187.72, 37.19)
            self.m_comb[1280]   =  self.mat_comb_fresco(1280,   2253.43, 187.71, 37.19)
            self.m_comb[1350]   =  self.mat_comb_fresco(1350,   2245.72, 187.74, 37.19)
            self.m_comb[1272]   =  self.mat_comb_fresco(1272,   2257.69, 186.94, 37.03)
            self.m_comb[1348]   =  self.mat_comb_fresco(1348,   2256.61, 186.62, 36.97)
            self.m_comb[1197]   =  self.mat_comb_fresco(1197,   2247.50, 186.54, 36.95)
            self.m_comb[ 989]   =  self.mat_comb_fresco( 989,   2251.50, 186.42, 36.93)
            self.m_comb[1228]   =  self.mat_comb_fresco(1228,   2244.82, 186.10, 36.87)
            self.m_comb[1173]   =  self.mat_comb_fresco(1173,   2246.51, 186.01, 36.85)
            self.m_comb[1205]   =  self.mat_comb_fresco(1205,   2252.25, 185.81, 36.81)
            self.m_comb[1195]   =  self.mat_comb_fresco(1195,   2244.53, 184.73, 36.60)
            self.m_comb[1028]   =  self.mat_comb_fresco(1028,   2255.32, 184.71, 36.59)
            self.m_comb[1130]   =  self.mat_comb_fresco(1130,   2219.08, 184.18, 36.49)
            self.m_comb[1342]   =  self.mat_comb_fresco(1342,   2256.41, 184.12, 36.47)
            self.m_comb[1025]   =  self.mat_comb_fresco(1025,   2246.90, 183.12, 36.28)
            self.m_comb[1128]   =  self.mat_comb_fresco(1128,   2248.09, 183.22, 36.30)
            self.m_comb[1114]   =  self.mat_comb_fresco(1114,   2247.60, 185.65, 36.78)
            self.m_comb[1219]   =  self.mat_comb_fresco(1219,   2249.38, 185.57, 36.76)
            self.m_comb[1301]   =  self.mat_comb_fresco(1301,   2254.23, 185.52, 36.75)
            self.m_comb[1171]   =  self.mat_comb_fresco(1171,   2250.76, 185.46, 36.74)
            self.m_comb[1224]   =  self.mat_comb_fresco(1224,   2263.63, 185.39, 36.73)
            self.m_comb[1179]   =  self.mat_comb_fresco(1179,   2257.79, 182.20, 36.09)
            self.m_comb[1214]   =  self.mat_comb_fresco(1214,   2244.03, 191.19, 37.87)
            self.m_comb[1012]   =  self.mat_comb_fresco(1012,   2241.85, 184.93, 36.64)
            self.m_comb[1162]   =  self.mat_comb_fresco(1162,   2237.60, 184.38, 36.53)
            self.m_comb[1223]   =  self.mat_comb_fresco(1223,   2250.76, 184.34, 36.52)
            self.m_comb[1147]   =  self.mat_comb_fresco(1147,   2241.46, 182.46, 36.15)
            self.m_comb[1005]   =  self.mat_comb_fresco(1005,   2225.02, 185.34, 36.72)
            self.m_comb[1137]   =  self.mat_comb_fresco(1137,   2248.59, 185.06, 36.66)
            self.m_comb[1330]   =  self.mat_comb_fresco(1330,   2258.49, 190.84, 37.81)
            self.m_comb[1345]   =  self.mat_comb_fresco(1345,   2281.06, 190.47, 37.73)
            self.m_comb[1263]   =  self.mat_comb_fresco(1263,   2252.84, 190.14, 37.67)
            self.m_comb[1274]   =  self.mat_comb_fresco(1274,   2243.74, 189.60, 37.56)
            # Elementos de Inox. Comprados em 1972.
            self.m_comb[7198]   =  self.mat_comb_fresco(7198,   2297.00, 193.00, 38.00)
            self.m_comb[7197]   =  self.mat_comb_fresco(7197,   2297.00, 193.00, 38.00)
            self.m_comb[7196]   =  self.mat_comb_fresco(7196,   2294.00, 193.00, 38.00)
            self.m_comb[7195]   =  self.mat_comb_fresco(7195,   2295.00, 193.00, 38.00)
            self.m_comb[6821]   =  self.mat_comb_fresco(6821,   2305.00, 193.00, 38.00) # Combustível instrumentado
        
        
        else:
            printv("################################################")
            printv("############ Definição dos Materiais ###########")
            printv("############      comb_queimado      ###########")
            printv("################################################")
            
            # Carregando os materiais queimados 
            resultados = openmc.deplete.Results(queimado)
            
            # Exportando apenas os materiais do último passo de queima (índice -1)
            materiais_queimados = resultados.export_to_materials(-1)
            
            # Criando dicionário de combustíveis
            self.m_comb = {}
            
            # Filtrando apenas os materiais combustíveis e os adicionando ao dicionário
            for mat in materiais_queimados:
                if mat.name.startswith("comb_"): 
                    self.m_comb[int(mat.name.split('_')[1])] = mat # Extrai o número de série do nome e salva no dicionário m_comb
                        
            printv(f"Foram carregados {len(self.m_comb)} elementos combustíveis queimados do arquivo {queimado}!")

        #Adicionar todos combustíveis na lista de materiais, e definir uma cor para eles
        for key in self.m_comb:
            self.lista_materiais.append(self.m_comb[key])

            # Definindo cores do tipo de combustível:
            ## Alumínio = Amarelo escuro
            ## Inox     = Amarelo
            ## Inox TC  = Amarelo claro
            if key < 6000:
                self.m_colors[self.m_comb[key]] = 'yellow'
            elif key == 6821:
                self.m_colors[self.m_comb[key]] = 'yellow'
            else:
                self.m_colors[self.m_comb[key]] = 'yellow'               


    def geometria(
        self,
        load = load.core1,
        tipo_geometria = "cilindrica"
        ):
        printv("################################################")
        printv("############ Definição de Geometria  ###########")
        printv("############      comb_queimado      ###########")
        printv("################################################")

        #
        # Universos elementos que não se repetem
        #

        def cria_universo_elemento_tuboCentralAgua():
            #Dimensões do elemento Tubo Central Agua
            tc_raio = 2
            tc_esp = 0.5
            tc_altura = 50
            
            # Definições das superfícies
            tc_cilindro_ext = openmc.ZCylinder(r= tc_raio+tc_esp)
            tc_cilindro_int = openmc.ZCylinder(r= tc_raio)
            tc_plano_sup = openmc.ZPlane(z0=  tc_altura/2)
            tc_plano_inf = openmc.ZPlane(z0= -tc_altura/2)
            
            # Definições das regiões
            tc_regiao_interna = -tc_cilindro_ext & +tc_cilindro_int & -tc_plano_sup & +tc_plano_inf
            tc_regiao_externa = ~tc_regiao_interna

            # Definições das células e universo
            universo_elemento_tuboCentralAgua           = openmc.Universe()

            tc_celula = openmc.Cell(fill=self.m_aluminio, region=tc_regiao_interna)
            universo_elemento_tuboCentralAgua.add_cell(tc_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=tc_regiao_externa)
            universo_elemento_tuboCentralAgua.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_tuboCentralAgua

        def cria_universo_elemento_fonte():
            #Dimensões do elemento Fonte
            fonte_raio = 2
            fonte_altura = 50
            
            # Definições das superfícies
            fonte_cilindro = openmc.ZCylinder(r= fonte_raio)
            fonte_plano_sup = openmc.ZPlane(z0=  fonte_altura/2)
            fonte_plano_inf = openmc.ZPlane(z0= -fonte_altura/2)
            
            # Definições das regiões
            fonte_regiao_interna = -fonte_cilindro & -fonte_plano_sup & +fonte_plano_inf
            fonte_regiao_externa = ~fonte_regiao_interna

            # Definições das células e universo
            universo_elemento_fonte           = openmc.Universe()

            fonte_celula = openmc.Cell(fill=self.m_aluminio, region=fonte_regiao_interna)
            universo_elemento_fonte.add_cell(fonte_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=fonte_regiao_externa)
            universo_elemento_fonte.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_fonte

        def cria_universo_elemento_terminalPneumático1():
            #Dimensões do elemento Terminal Pneumático
            tp_raio = 2
            tp_esp = 0.5
            tp_altura = 50
            
            # Definições das superfícies
            tp_cilindro_ext = openmc.ZCylinder(r= tp_raio+tp_esp)
            tp_cilindro_int = openmc.ZCylinder(r= tp_raio)
            tp_plano_sup = openmc.ZPlane(z0=  tp_altura/2)
            tp_plano_inf = openmc.ZPlane(z0= -tp_altura/2)
            
            # Definições das regiões
            tp_regiao_interna = -tp_cilindro_ext & +tp_cilindro_int & -tp_plano_sup & +tp_plano_inf
            tp_regiao_externa = ~tp_regiao_interna

            # Definições das células e universo
            universo_elemento_terminalPneumático1           = openmc.Universe()

            tp_celula = openmc.Cell(fill=self.m_aluminio, region=tp_regiao_interna)
            universo_elemento_terminalPneumático1.add_cell(tp_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=tp_regiao_externa)
            universo_elemento_terminalPneumático1.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_terminalPneumático1




        #
        # Universos elementos que se repetem
        #

        def cria_universo_elemento_grafite():
            #Dimensões do elemento combustível de alumínio
            comb_raio = 2
            comb_altura = 50
            
            # Definições das superfícies
            comb_cilindro = openmc.ZCylinder(r= comb_raio)
            comb_plano_sup = openmc.ZPlane(z0=  comb_altura/2)
            comb_plano_inf = openmc.ZPlane(z0= -comb_altura/2)
            
            # Definições das regiões
            comb_regiao_interna = -comb_cilindro & -comb_plano_sup & +comb_plano_inf
            comb_regiao_externa = ~comb_regiao_interna

            # Definições das células e universo
            universo_elemento_combustivel           = openmc.Universe()

            comb_celula = openmc.Cell(fill=self.m_grafite, region=comb_regiao_interna)
            universo_elemento_combustivel.add_cell(comb_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=comb_regiao_externa)
            universo_elemento_combustivel.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_combustivel

        ## As barras de controle são geometricamente iguais, podendo variar suas posiçoes independentemente
        def cria_universo_elemento_barraDeControle(posição_barra):
            #Dimensões do elemento combustível de alumínio
            guia_raio = 2
            guia_esp = 0.5
            guia_altura = 50
            
            # Definições das superfícies
            guia_cilindro_ext = openmc.ZCylinder(r= guia_raio+guia_esp)
            guia_cilindro_int = openmc.ZCylinder(r= guia_raio)
            guia_plano_sup = openmc.ZPlane(z0=  guia_altura/2)
            guia_plano_inf = openmc.ZPlane(z0= -guia_altura/2)
            
            # Definições das regiões
            guia_regiao_interna = -guia_cilindro_ext & +guia_cilindro_int & -guia_plano_sup & +guia_plano_inf
            guia_regiao_externa = ~guia_regiao_interna

            # Definições das células e universo
            universo_elemento_combustivel           = openmc.Universe()

            guia_celula = openmc.Cell(fill=self.m_aluminio, region=guia_regiao_interna)
            universo_elemento_combustivel.add_cell(guia_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=guia_regiao_externa)
            universo_elemento_combustivel.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_combustivel
        
        ## Cada elemento combustível pode ter uma composição diferente
        def cria_universo_elemento_combustivel(fill):
            #Dimensões do elemento combustível de alumínio
            comb_raio = 2
            comb_altura = 50
            
            # Definições das superfícies
            comb_cilindro = openmc.ZCylinder(r= comb_raio)
            comb_plano_sup = openmc.ZPlane(z0=  comb_altura/2)
            comb_plano_inf = openmc.ZPlane(z0= -comb_altura/2)
            
            # Definições das regiões
            comb_regiao_interna = -comb_cilindro & -comb_plano_sup & +comb_plano_inf
            comb_regiao_externa = ~comb_regiao_interna

            # Definições das células e universo
            universo_elemento_combustivel           = openmc.Universe()

            comb_celula = openmc.Cell(fill=fill, region=comb_regiao_interna)
            universo_elemento_combustivel.add_cell(comb_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=comb_regiao_externa)
            universo_elemento_combustivel.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_combustivel
        
        ## Os combustíveis de inox tem uma geometria ligeiramente diferente, e não tem absorvedores
        def cria_universo_elemento_combustivel_inox(fill):
            #Dimensões do elemento combustível de alumínio
            comb_raio = 2
            comb_altura = 50
            
            # Definições das superfícies
            comb_cilindro = openmc.ZCylinder(r= comb_raio)
            comb_plano_sup = openmc.ZPlane(z0=  comb_altura/2)
            comb_plano_inf = openmc.ZPlane(z0= -comb_altura/2)
            
            # Definições das regiões
            comb_regiao_interna = -comb_cilindro & -comb_plano_sup & +comb_plano_inf
            comb_regiao_externa = ~comb_regiao_interna

            # Definições das células e universo
            universo_elemento_combustivel_inox           = openmc.Universe()

            comb_celula = openmc.Cell(fill=fill, region=comb_regiao_interna)
            universo_elemento_combustivel_inox.add_cell(comb_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=comb_regiao_externa)
            universo_elemento_combustivel_inox.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_combustivel_inox
        
        ## Elemento de inox instrumentado
        def cria_universo_elemento_combustivel_inox_instrumentado(fill):
            #Dimensões do elemento combustível de alumínio
            comb_raio = 2
            comb_altura = 50
            
            # Definições das superfícies
            comb_cilindro = openmc.ZCylinder(r= comb_raio)
            comb_plano_sup = openmc.ZPlane(z0=  comb_altura/2)
            comb_plano_inf = openmc.ZPlane(z0= -comb_altura/2)
            
            # Definições das regiões
            comb_regiao_interna = -comb_cilindro & -comb_plano_sup & +comb_plano_inf
            comb_regiao_externa = ~comb_regiao_interna

            # Definições das células e universo
            universo_elemento_combustivel_inox_instrumentado           = openmc.Universe()

            comb_celula = openmc.Cell(fill=fill, region=comb_regiao_interna)
            universo_elemento_combustivel_inox_instrumentado.add_cell(comb_celula)

            extern_celula = openmc.Cell(fill=self.m_refrigerante, region=comb_regiao_externa)
            universo_elemento_combustivel_inox_instrumentado.add_cell(extern_celula)
            
            # Retorno da função
            return universo_elemento_combustivel_inox_instrumentado
            





        #
        # Código para carregar o reator conforme arquivo load
        #

        # Crie o dicionário de elementos, já com as coordenadas
        elemento = cria_elementosCarregaveis_com_coordenadas(tipo_geometria, pitch=6)

        # Carregue o universo de cada elemento baseado em sua chave e o load
        # Esse procedimento gasta processamento e ocupa mais memória, mas é uma forma de verificação que o load está correto
        for chave in elemento:                                                          # Itere sob todas as chaves do dicionário elemento
            elemento[chave].load = load[chave]                                          # O valor de load contem o tipo do elemento carregável, salve ele no respectivo atributo
            if load[chave] == "água" or load[chave] == "agua":                          # Caso o tipo seja string "água"
                elemento[chave].universo = self.m_refrigerante                          # Preencha só com material água
            if load[chave] == "grafite":                                                # Caso o tipo seja string "grafite"
                elemento[chave].universo = cria_universo_elemento_grafite()             # Preencha com o universo respectivo
            if load[chave] == "tubo_central_agua":                                      # E assim sucessivamente
                elemento[chave].universo = cria_universo_elemento_tuboCentralAgua()     #
            if load[chave] == "fonte":                                                  #
                elemento[chave].universo = cria_universo_elemento_fonte()               #
            if load[chave] == "terminal_pneumático_1" or load[chave] == "terminal_pneumatico_1":#
                elemento[chave].universo = cria_universo_elemento_terminalPneumático1() #
            if load[chave] == "barra_controle":                                         #
                elemento[chave].universo = cria_universo_elemento_barraDeControle(0)    #
            if type(load[chave]) == int:                                                # Caso o tipo seja inteira, significa que é um elemento combustível (número de série)
                elemento[chave].mat_combustivel = self.m_comb[load[chave]]              # Salve o material do combustível no respectivo atributo
                if load[chave]<2000:                                                    # Se o número de série for menor que 2000, significa que é do tipo alumínio
                    elemento[chave].universo = cria_universo_elemento_combustivel(self.m_comb[load[chave]]) # Crie o universo do combustível de aumínio com seu respectivo material baseado no número de série
                elif load[chave]>7000:                                                  # Numero de série for maior que 7000, significa que é aço inox
                    elemento[chave].universo = cria_universo_elemento_combustivel_inox(self.m_comb[load[chave]]) # E assim sucessivamente
                else:                                                                   # Caso não seja nenhuma das opções, então é o combustível instrumentado
                    elemento[chave].universo = cria_universo_elemento_combustivel_inox_instrumentado(self.m_comb[load[chave]])
                    










        # Geometria do núcleo
        ## Gerar uma célula a partir de um cilindro para cada elemento e gerar a região externa aos cilindros
        celulas_elemento = []
        regioes_externas_aos_pinos = []
        for chave in elemento:
            cilindro_elemento = openmc.ZCylinder(x0=elemento[chave].x, y0=elemento[chave].y,r=3)    # Cria cilindro para ser a fronteira entre o universo_elemento e a água
            regioes_externas_aos_pinos.append(+cilindro_elemento)                                   # Adiciona a região externa a esse cilindro na lista de regiões externas
            
            celula_elemento = openmc.Cell()                                                         # Cria a célula para ser preenchida com o universo_elemento
            celula_elemento.fill = elemento[chave].universo                                         # Preenche com o universo de acordo com a chave
            celula_elemento.region = -cilindro_elemento                                             # A região da célula é interna ao cilindro
            celula_elemento.translation = (elemento[chave].x, elemento[chave].y, 0.0)               # Translade o universo para a posição correta
            celulas_elemento.append(celula_elemento)                                                # Adiciona a lista de células
        
        região_externa_aos_pinos = regioes_externas_aos_pinos[0]                                    # Inicializar a variável com a primeira região da lista
        for fora_do_pino in regioes_externas_aos_pinos[1:]:                                         # Para cada região externa ao pino, de cada pino
            região_externa_aos_pinos = região_externa_aos_pinos & fora_do_pino                      # Adiciona à região_externa_aos_pinos a região externa a cada pino
        
        cilindro_nucleo_ativo = openmc.ZCylinder(r=100,boundary_type="vacuum")                      # Cria um cilindro delimitar o núcleo ativo
        celula_refrigente_nucleo_ativo = openmc.Cell()                                              # Cria célula que contém os espaços entre os elementos
        celula_refrigente_nucleo_ativo.fill = self.m_refrigerante                                   # Preenche com água (os espaços entre os elementos)
        celula_refrigente_nucleo_ativo.region = região_externa_aos_pinos & -cilindro_nucleo_ativo   # Define a região com externa a todos elementos e interna ao cilindro que delimita o núcleo ativo
        
        
        universo_nucleo_ativo = openmc.Universe()
        universo_nucleo_ativo.add_cells(celulas_elemento)
        universo_nucleo_ativo.add_cell(celula_refrigente_nucleo_ativo)
            
        # Criar a geometria contendo 
        self.Geometry = openmc.Geometry()
        self.Geometry.root_universe = universo_nucleo_ativo
        







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
        self.Settings = openmc.Settings()
        self.Settings.particles = particulas
        self.Settings.batches = ciclos
        #self.settings.statepoint = {'batches': range(5, n + 5, 5)} #Use para gerar statepoint.#.h5 intermediários
        self.Settings.create_delayed_neutrons = n_atrasados
        self.Settings.photon_transport = foton
        self.Settings.inactive = inativo
        self.Settings.source = openmc.IndependentSource(space=openmc.stats.Point())
        self.Settings.output = {'tallies': False} #Esta linha desabilita a geração do arquivo tallies.out
        printv(self.Settings)









    def plot2D_secao_transversal(
        self,
        geometria=None,
        filename=None,
        basis="xy",
        width=[150,150],
        pixels=[5000,5000],
        origin=(0,0,0)
        ):
        printv("################################################")
        printv("############        Plot 2D         ############")
        printv("################################################")
        if plot:
            if geometria is None:
                geometria = self.Geometry
            if filename is None:
                filename = 'plot_' + basis + '_' + str(width) + '_' + str(pixels) + '_' + str(origin)

            ############ Plotar Secão Transversal
            secao_transversal = openmc.Plot.from_geometry(geometria)
            secao_transversal.type = 'slice'
            secao_transversal.basis = basis
            secao_transversal.width = width
            secao_transversal.origin = origin
            secao_transversal.filename = filename
            secao_transversal.pixels = pixels
            secao_transversal.color_by = 'material'
            secao_transversal.colors = self.m_colors
        
            ############ Exportar Plots e Plotar
            plotagem = openmc.Plots([secao_transversal])
            plotagem.export_to_xml()
            self.lista_materiais.export_to_xml()
            self.Geometry.export_to_xml()
            openmc.plot_geometry()









    def plot3D(
        self,
        geometria,
        colors,
        width=(150., 150., 150.),
        pixels=(500, 500, 500),
        origin=(0,0,0)
        ):
        printv("################################################")
        printv("############        Plot 3D         ############")
        printv("################################################")
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
            self.lista_materiais.export_to_xml()
            self.Geometry.export_to_xml()
            openmc.voxel_to_vtk(plot_3d.filename+'.h5', plot_3d.filename)













    def simulacao_autovalor(self):
        printv("################################################")
        printv("#########     Executando simulação     #########")
        printv("#########        de autovalores        #########")
        printv("################################################")
        if simu:
            self.lista_materiais.export_to_xml()
            self.Geometry.export_to_xml()
            self.Settings.export_to_xml()
            openmc.run()

    
    ################################################
    ###########         Depleção        ############
    ################################################

    def simulacao_queima(
            self,
            timesteps=[1],
            power=250e3,
            chain_file="/opt/nuclear-data/chain_endfb71_pwr.xml",
            timestep_units='d',
            diff=False,
            results_file=""):
        print("################################################")
        print("###########         Depleção        ############")
        print("################################################")
        if simu:

            # Set up depletion operator
            model = openmc.model.Model(self.Geometry, self.lista_materiais, self.Settings)
            if diff:
                model.differentiate_depletable_mats(diff_volume_method = 'divide equally')

            if not os.path.exists(results_file): #Inicia uma queima nova
                op = openmc.deplete.CoupledOperator(model, chain_file, diff_burnable_mats=diff)
            else: #Continua uma queima de onde parou
                results = openmc.deplete.Results.from_hdf5(results_file)
                op = openmc.deplete.CoupledOperator(model, chain_file, diff_burnable_mats=diff, prev_results=results)
            
            # Deplete 
            CF4 = openmc.deplete.CF4Integrator(operator=op, timesteps=timesteps, power=power, timestep_units=timestep_units) 
            CF4.integrate()
