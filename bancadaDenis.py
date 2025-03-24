import openmc
import numpy as np
import openmc.model

# ======================
# Materiais
# ======================

# Material 1 - Fonte de Cobalto (Co-60)
cobalto = openmc.Material(name='Fonte de Cobalto')
cobalto.add_nuclide('Co59', 1.0)
cobalto.set_density('g/cm3', 8.9)

# Material 2 - Aço
aco = openmc.Material(name='Aço')
aco.add_element('Fe', 0.98)
aco.add_element('C', 0.02)
aco.set_density('g/cm3', 7.85)

# Material 3 - Detector de Cristal de Iodeto de Cesio
csi = openmc.Material(name='Detector de CsI')
csi.add_nuclide('Cs133', 0.5)
csi.add_nuclide('I127', 0.5)
csi.set_density('g/cm3', 4.51)

# Material 4 - Água
agua = openmc.Material(name='Água')
agua.add_nuclide('H1', 2.0)
agua.add_nuclide('O16', 1.0)
agua.set_density('g/cm3', 1.0)

# Material 5 - Ar
ar = openmc.Material(name='Ar')
ar.add_nuclide('N14', 0.755)
ar.add_nuclide('O16', 0.231)
ar.add_nuclide('Ar40', 0.013)
ar.set_density('g/cm3', 0.001225)

# Criação do conjunto de materiais
materials = openmc.Materials([cobalto, aco, csi, agua, ar])
materials.export_to_xml()
#print(materials)

# ======================
# Geometria (& intersection, > union,  ~ complement.)
# ======================
# Fonte (Co-60)
Co60_cyl=openmc.ZCylinder(x0=0, y0=-13.34, r=0.35) 
plane_z_min = openmc.ZPlane(z0=0)
plane_z_max = openmc.ZPlane(z0=23.4)

fonte_cell = openmc.Cell(name='Fonte Co60')
fonte_cell.region = -Co60_cyl & +plane_z_min & -plane_z_max
fonte_cell.fill = cobalto

# Água
H2O_cyl=openmc.ZCylinder(x0=0, y0=-13.34, r=6) 

agua_cell = openmc.Cell(name='Água')
agua_cell.region = -H2O_cyl & +Co60_cyl & +plane_z_min & -plane_z_max
agua_cell.fill = agua

# Tarugo de Aço Altura 7.4-24.4 !! FALTA ARRUMAR ELE SENDO ALTURA NEGATIVA
tarugo_superficie = openmc.model.RectangularPrism(width=6.75, height=6.75, axis = 'z', origin=(0,0,0))
plane_z_min_tarugo = openmc.ZPlane(z0=7.4)
plane_z_max_tarugo = openmc.ZPlane(z0=24.4) 


tarugo_cell = openmc.Cell(name='Tarugo de Aço')
tarugo_cell.region = -tarugo_superficie & +plane_z_min_tarugo & -plane_z_max_tarugo 
tarugo_cell.fill = aco

# Detector de Cristal de CsI
CsI_start_point=(0,12.32,21.4)
CsI_end_point = (0,17.32,21.4)
plane_y_min = openmc.YPlane(y0=12.32)
plane_y_max = openmc.YPlane(y0=17.32)
radius_CsI=2
NaI_cyl=openmc.model.cylinder_from_points(CsI_start_point, CsI_end_point, radius_CsI)

detector_cell = openmc.Cell(name='Detector de CsI')
detector_cell.region = -NaI_cyl & +plane_y_min & -plane_y_max
detector_cell.fill = csi

# Ar
vazio_box = openmc.model.RectangularPrism(width=30, height=50, origin=(0, 0, 0), boundary_type='vacuum')
plane_z_max_vazio=openmc.ZPlane(z0=24.4)
plane_z_min_vazio=openmc.ZPlane(z0=-1)
vazio_box_completo= -vazio_box & +plane_z_min_vazio & -plane_z_max_vazio

ar_cell = openmc.Cell(name='Ar')
ar_cell.region =  ~-H2O_cyl & ~-tarugo_superficie & ~-NaI_cyl & ~vazio_box_completo & -plane_z_max_vazio & +plane_z_min_vazio
ar_cell.fill = ar

# Vacuo
vazio_cell = openmc.Cell(name='Vácuo Exterior')
vazio_cell.region = +vazio_box & +plane_z_max_vazio & -plane_z_min_vazio

# Criação do universo
universe_1 = openmc.Universe(cells=[fonte_cell, agua_cell, tarugo_cell, detector_cell, ar_cell, vazio_cell])
#universe_1.plot(width=(50,50), origin=(0,0,0), basis='xy')
geometry = openmc.Geometry()
geometry.root_universe = universe_1
geometry.export_to_xml()

# ======================
# Parâmetros de Plotagem
# ======================
plot = openmc.Plot()
plot.filename = 'geometry_plot.png'  
plot.basis = ('yz')
plot.width = (40 , 40)
plot.pixels = (400, 400)
plot.origin = (0, 0, 22)
#plot.color_by='materials'
plots = openmc.Plots([plot])
plot.show_edges = True  # Mostrar bordas das células
plot.show_labels = True  # Mostrar rótulos das células

plots.export_to_xml()
openmc.plot_geometry()

#from IPython.display import Image
#Image('geometry_plot.png')
#xdg-open geometry_plot.png


#secao_transversal = openmc.Plot.from_geometry(geometry)


# ======================
# Fonte
# ======================

# Espectro de energia do Cobalto-60
energy_dist = openmc.stats.Discrete([1.1732e6, 1.3325e6], [0.5, 0.5])

# Distribuição espacial (raio entre 0 e 0.35 cm, cilindro ao longo do eixo z)
radius_dist = openmc.stats.Uniform(a=0, b=0.35)  # Raio entre 0 e 0.35 cm
length_points = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 
                 17, 18, 19, 20, 21, 22, 23.46]  # Pontos de extensão em z
prob_length = [0, 1324, 1088, 1137, 1226, 1304, 1357, 1397, 1483, 1551, 1653, 
               1728, 1810, 1897, 2002, 2116, 2219, 2306, 2414, 2463, 2476, 
               2813, 2898, 3310]  # Distribuição ao longo de z (normalizar)

# Normalizando a distribuição probabilística em z
total_prob = sum(prob_length)
prob_length = [p / total_prob for p in prob_length]

# Distribuição da extensão ao longo de z com probabilidades normalizadas
length_dist = openmc.stats.Discrete(length_points, prob_length)

# Definindo uma distribuição espacial cilíndrica
space_dist = openmc.stats.CylindricalIndependent(
    r=radius_dist,
    phi=openmc.stats.Uniform(0, 2 * 3.141592653589793),  # Ângulo uniforme ao longo de 360°
    z=length_dist,
    origin=(0, -13.34, 0)  # Origem centralizada no ponto definido
)

# Criando a fonte com parâmetros definidos
source = openmc.IndependentSource(
    space=space_dist,
    angle=openmc.stats.Isotropic(),  # Ângulo isotrópico
    energy=energy_dist,              # Espectro de energia para Co-60
    strength=3.7e7                   # Intensidade da fonte (1 mCi ou 0,7mCi?)
)

# ======================
# Configurações
# ======================

settings = openmc.Settings()
settings.source = source
settings.batches = 100  # Número de batches para simulação
settings.inactive = 10  # Batches inativos
settings.particles = int(3E6)
 



