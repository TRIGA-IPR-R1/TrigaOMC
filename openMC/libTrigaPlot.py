#!/usr/bin/python

if __name__ == '__main__':
    print("Isso é uma biblioteca, importe ela ao invés de a executar diretamente...")
    exit(1)
    
"""
Classe para definir as configurações de plotagem

Para mais informações:
    https://docs.openmc.org/en/stable/usersguide/plots.html

plot2D gera uma imagem em PNG

plot3D gera um voxel VTK
"""

import openmc
import openMC.libTrigaFuncionalidades as func

class TrigaPlot:
    def __init__(self, simu=True, verbose=True):
        func.simu = simu
        func.verbose = verbose
        
    def plot2D_secao_transversal(self, geometria, colors, basis="xz",width=[150,150],pixels=[5000,5000],origin=(0,0,0)):
        print("################################################")
        print("############        Plot 2D         ############")
        print("################################################")
        
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
        plotagem = openmc.Plots((secao_transversal,))
        if func.simu:
            plotagem.export_to_xml()  
            openmc.plot_geometry()

    def plot3D(self, geometria, colors, width=(150., 150., 150.), pixels=(500, 500, 500), origin=(0,0,0)):
        print("################################################")
        print("############        Plot 3D         ############")
        print("################################################")
        
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
        plotagem = openmc.Plots((plot_3d,))
        if func.simu:
            plotagem.export_to_xml()  
            openmc.plot_geometry()
            openmc.voxel_to_vtk(plot_3d.filename+'.h5', plot_3d.filename)
