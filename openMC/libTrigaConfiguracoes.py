#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)
    
import openmc
import openmc.stats
import openMC.libTrigaFuncionalidades as func

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

class TrigaConfiguracoes:
    def __init__(self, simu=True, verbose=True):
        func.simu = simu
        func.verbose = verbose
        
    def configuracoes(self, particulas=1000, ciclos=100, inativo=10, n_atrasados=True, foton=False):
        func.printv("################################################")
        func.printv("########### Definição da Simulação  ############")
        func.printv("################################################")

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
        
        # Apenas exportar xml caso for realizar simulação
        if func.simu:
            self.settings.export_to_xml()
        func.printv(self.settings)
