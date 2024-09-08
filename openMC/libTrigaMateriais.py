#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)
    
import openmc
import openMC.libTrigaFuncionalidades as func

"""
Classe para definir a composição dos materiais do reator

Para mais informações:
    https://docs.openmc.org/en/stable/usersguide/materials.html

Cada método da classe contem uma lista diferente de materiais.
Por exemplo, o método comb_fresco contem a lista de materiais considerando um reator Triga nunca usado (não quimadado)

Primeiro se define um material, depois uma geometria.
Se uma geometria suportar diferente lista de materiais, deve ser expressa quais materiais a geometria suporta,
e as diferentes listas de materiais tem que ter o mesmo nome.

Exemplo: Suponhamos que uma geometria_X suporte os materiais uranio_X e plutonio_X, e a unica diferença entre eles
seja o material físsil. Logo, em ambos métodos devem ter declarado uma varíavel self.combustivel com a composição especificada.

Contra-exemplo: Seguindo o exemplo anterior, caso sejam declaradas duas variáveis diferentes, como self.uranio e self.plutonio, 
o metodo geometria_X não conseguirá lidar com nome diferentes.

Exemplo alternativo: Caso uma lista precise ter self.uranio e self.plutonio ao mesmo tempo pois determinada geomeria necessita disso,
tudo bem, mas essa lista de composição será incompatível com geometrias que esperam encontrar self.combustivel
"""

class TrigaMateriais:
    def __init__(self, simu=True, verbose=True):
        func.simu = simu
        func.verbose = verbose
        
        # Inicializar a lista de materiais
        self.materiais = openmc.Materials([])
        
        # Inicializar o dicionário de cores
        self.colors = {}

    def export(self):
        # Apenas exportar xml caso for realizar simulação
        if func.simu:
            self.materiais.export_to_xml()
        func.printv(self.materiais)

        
    def materiais_padrão(self):
        func.printv("################################################")
        func.printv("############ Definição dos Materiais ###########")
        func.printv("############     materiais_padrão    ###########")
        func.printv("################################################")
        
        self.refrigerante = openmc.Material(name='Água Leve')
        self.refrigerante.add_nuclide('H1',  1.1187E-01, percent_type='wo')
        self.refrigerante.add_nuclide('H2',  3.3540E-05, percent_type='wo')
        self.refrigerante.add_nuclide('O16', 8.8574E-01, percent_type='wo')
        self.refrigerante.add_nuclide('O17', 3.5857E-04, percent_type='wo')
        self.refrigerante.add_nuclide('O18', 1.9982E-03, percent_type='wo')
        self.refrigerante.set_density('g/cm3', 1)
        self.materiais.append(self.refrigerante)
        self.colors[self.refrigerante] = 'blue'
        
        
        self.ar = openmc.Material(name='Ar')
        self.ar.add_nuclide('N14',  7.7826E-01, percent_type='ao')
        self.ar.add_nuclide('N15',  2.8589E-03, percent_type='ao')
        self.ar.add_nuclide('O16',  1.0794E-01, percent_type='ao')
        self.ar.add_nuclide('O17',  1.0156E-01, percent_type='ao')
        self.ar.add_nuclide('O18',  3.8829E-05, percent_type='ao')
        self.ar.add_nuclide('Ar36', 2.6789E-03, percent_type='ao')
        self.ar.add_nuclide('Ar38', 3.4177E-03, percent_type='ao')
        self.ar.add_nuclide('Ar40', 3.2467E-03, percent_type='ao')
        self.ar.set_density('g/cm3', 0.001225)
        self.materiais.append(self.ar)
        self.colors[self.ar] = 'white'
        
        
        self.aluminio = openmc.Material(name='Alúminio')
        self.aluminio.add_nuclide('Al27', 1, percent_type ='wo')
        self.aluminio.set_density('g/cm3', 2.7)
        self.materiais.append(self.aluminio)
        self.colors[self.aluminio] = 'gray'
        
        
        self.SS304 = openmc.Material(name='Aço INOX',)
        self.SS304.add_element('C',  4.3000E-04, percent_type = 'wo')
        self.SS304.add_element('Cr', 1.9560E-01, percent_type = 'wo')
        self.SS304.add_element('Ni', 9.6600E-02, percent_type = 'wo')
        self.SS304.add_element('Mo', 8.9000E-03, percent_type = 'wo')
        self.SS304.add_element('Mn', 5.4000E-04, percent_type = 'wo')
        self.SS304.add_element('Si', 5.0000E-04, percent_type = 'wo')
        self.SS304.add_element('Cu', 2.0000E-05, percent_type = 'wo')
        self.SS304.add_element('Co', 3.0000E-05, percent_type = 'wo')
        self.SS304.add_element('P',  2.7000E-04, percent_type = 'wo')
        self.SS304.add_element('S',  1.0000E-04, percent_type = 'wo')
        self.SS304.add_element('N',  1.4000E-04, percent_type = 'wo')
        self.SS304.add_element('Fe', 6.9687E-01, percent_type = 'wo')
        self.SS304.set_density('g/cm3', 7.92)
        self.materiais.append(self.SS304)
        self.colors[self.SS304] = 'silver'
        
        
    def comb_u20_fresco(self):
        func.printv("################################################")
        func.printv("############ Definição dos Materiais ###########")
        func.printv("############       comb_fresco       ###########")
        func.printv("################################################")
        
        self.combustivel = openmc.Material(name='Hidreto de Zircônio')
        self.combustivel.add_element('U',  0.12, percent_type = 'wo', enrichment=20)
        self.combustivel.add_element('H',  0.03, percent_type = 'wo')
        self.combustivel.add_element('Zr', 0.85, percent_type = 'wo')
        self.combustivel.set_density('g/cm3', 6.1)
        self.materiais.append(self.combustivel)
        self.colors[self.combustivel] = 'yellow'
