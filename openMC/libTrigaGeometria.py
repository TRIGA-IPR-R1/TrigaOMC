#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)
    
import openmc
import openMC.libTrigaFuncionalidades as func
import libTrigaMateriais


"""
Classe para definir as configurações de simulação

Para mais informações:
    https://docs.openmc.org/en/stable/usersguide/settings.html

Uma simulação gera por padrão 3 arquivos: 
    - tallies.out
    - summary.h5
    - statepoint.#.h5

Para mais informações:
    https://docs.openmc.org/en/stable/usersguide/basics.html#result-files

O arquivo tallies.out foi desabilitado pois suas informações estão contidas nos statepoint's
"""

class TrigaGeometria:
    def __init__(self, simu=True, verbose=True):
        func.simu = simu
        func.verbose = verbose
        #Definindo Material primeiramente
        self.mat = libTrigaMateriais.TrigaMateriais(func.simu, func.verbose)
        
    def geometriaPadrao(self, mat):
        self.mat.materiais_padrão
        
        if mat == "comb_fresco":
            self.mat.comb_u20_fresco()
            self.mat.export()
        else:
            print("!!!!!!ERRO: Material inválido!!!!!")
            exit(0)
            
        
        # Exemplo de como definir uma geometria com um material
        universo = openmc.Universe()
        celula = openmc.Cell()
        celula.fill = self.mat.combustivel
        universo.add_cell(celula)
        
        """
        Geometria a ser criada...
        """
        
        self.geometrias = openmc.Geometry()
        if func.simu:
            self.geometrias.export_to_xml()
        func.printv(self.geometrias)