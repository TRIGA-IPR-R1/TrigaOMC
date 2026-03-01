#!/bin/python

#######################################################################
####                                                               ####
####          Biblioteca contendo as configurações de cada         ####
####                  núcleo do TRIGA IPR-R1                       ####
####                                                               ####
####    Centro de Desenvolvimento da Tecnologia Nuclear - CDTN     ####
####           Serviço de Tecnologia de Reatores - SETRE           ####
####                  Thalles Oliveira Campagnani                  ####
####                                                               ####
#######################################################################

# Opções de carregamento:
#   - 'tubo_central_agua':         Elemento tubo central contendo água
#   - 'terminal_pneumático_1':     Elemento terminal pneumático 1
#   - 'fonte':                     Elemento fonte de neutrons
#   - 'grafite':                   Elemento refletor de grafite
#   - 'barra_controle':            Elemento barra de controle
#   - 'agua':                      Sem elemento, automaticamente preenchido com água
#   - None:                        Também sem elemento, automaticamente preenchido com água
#   - [num_inteiro]:               Elemento combustível, sendo o número inteiro correspondente ao número de série do combustível
#
#
#
#
#
#
# Posições carregaveis do Reator TRIGA IPR-R1
# Obs: Geometria cilíndridrica representada de forma hexagonal
#
#
#											F1										
#																					
#									F30				F2								
#																					
#							F29				E1				F3						
#																					
#					F28				E24				E2				F4				
#																					
#			F27				E23				D1				E3				F5		
#																					
#	F26				E22				D17				D2				E4				F6
#																					
#			E21				D16				C1				D3				E5		
#																					
#	F25				D15				C12				C2				D4				F7
#																					
#			E20				C11				B1				C3				E6		
#																					
#	F24				D14				B6				B2				D5				F8
#																					
#			E19				C10				A1				C4				E7		
#																					
#	F23				D13				B5				B3				D6				F9
#																					
#			E18				C9				B4				C5				E8		
#																					
#	F22				D12				C8				C6				D7				F10
#																					
#			E17				D11				C7				D8				E9		
#																					
#	F21				E16				D10				D9								F11
#																	E10				
#			F20				E15				D10				E11				F12		
#																					
#					F19				E14				E12				F13				
#																					
#							F18				E13				F14						
#																					
#									F17				F15								
#																					
#											F16										
#
#
#
#
#
# Posições do "Hack" na lateral da piscina (para decaimento):
#       1
#       2
#       3
#       Etc...
#
#
#
#
#
# Instruções para declarar a configuração de um núcleo:
#
#   1° - Declarar um dicionário do python contendo como chaves as posições contidas no desenho hexagonal acima.
#   2° - Declarar uma lista do python contendo os combustíveis que já foram fabricados, porém não inseridos no núcleo (ou que foram inseridos, mas retirados).
#        Obs: considerar os elementos combustíveis nos poços de decaimento como posicionados no hack.
#        Obs2: não há a necessidade de posicionar elementos de grafite no hack para fins de simulação, a não ser que o material deles sejam marcado como queimáveis para algum estudo específico.
#
#   Exemplo:
#           nome_nucleo        = {}
#           nome_nucleo['A1']  = 'tubo_central_agua'
#           nome_nucleo['B1']  = 1314
#           nome_nucleo['B2']  = 1188
#           ...
#           nome_nucleo['D1']  = 'barra_controle'
#           ...
#           nome_nucleo['F1']  = 'grafite'
#           nome_nucleo['F2']  = 'grafite'
#           nome_nucleo['F3']  = 'grafite'
#           ...
#           
#           nome_hack = []
#           hack1.append(1147)
#           hack1.append(1179)







# Núcleo 1: Primeira configução do TRIGA IPR-R1, o qual atingiu sua primeira criticalidade em 1960
core1        = {}
core1['A1']  = 'tubo_central_agua'
core1['B1']  = 1314
core1['B2']  = 1188
core1['B3']  = 1289
core1['B4']  = 1286
core1['B5']  = 1230
core1['B6']  = 1297
core1['C1']  = 1269
core1['C2']  = 1298
core1['C3']  = 1330
core1['C4']  = 1315
core1['C5']  = 1345
core1['C6']  = 1235
core1['C7']  = 1212
core1['C8']  = 1222
core1['C9']  = 1263
core1['C10'] = 1351
core1['C11'] = 1274
core1['C12'] = 1311
core1['D1']  = 'barra_controle'
core1['D2']  = 1254
core1['D3']  = 1206
core1['D4']  = 1303
core1['D5']  = 1287
core1['D6']  = 1296
core1['D7']  = 1282
core1['D8']  = 1343
core1['D9']  = 1196
core1['D10'] = 'barra_controle'
core1['D11'] = 1199
core1['D12'] = 1347
core1['D13'] = 1220
core1['D14'] = 1218
core1['D15'] = 1209
core1['D16'] = 1280
core1['D17'] = 1350
core1['D18'] = 1272
core1['E1']  = 1348
core1['E2']  = 1197
core1['E3']  = 989
core1['E4']  = 1228
core1['E5']  = 1173
core1['E6']  = 1205
core1['E7']  = 1195
core1['E8']  = 1028
core1['E9']  = 1130
core1['E10'] = 1342
core1['E11'] = 1025
core1['E12'] = 1128
core1['E13'] = 1114
core1['E14'] = 1219
core1['E15'] = 1301
core1['E16'] = 1171
core1['E17'] = 1224
core1['E18'] = 'grafite'
core1['E19'] = 'grafite'
core1['E20'] = 1012
core1['E21'] = 1162
core1['E22'] = 1223
core1['E23'] = 1137
core1['E24'] = 1005
core1['F1']  = 'grafite'
core1['F2']  = 'grafite'
core1['F3']  = 'grafite'
core1['F4']  = 'grafite'
core1['F5']  = 'grafite'
core1['F6']  = 'grafite'
core1['F7']  = 'grafite'
core1['F8']  = 'fonte'
core1['F9']  = 'grafite'
core1['F10'] = 'grafite'
core1['F11'] = 'grafite'
core1['F12'] = 'terminal_pneumático_1'
core1['F13'] = 'grafite'
core1['F14'] = 'grafite'
core1['F15'] = 'grafite'
core1['F16'] = 'barra_controle'
core1['F17'] = 'grafite'
core1['F18'] = 'grafite'
core1['F19'] = 'grafite'
core1['F20'] = 'grafite'
core1['F21'] = 'grafite'
core1['F22'] = 'grafite'
core1['F23'] = 'grafite'
core1['F24'] = 'grafite'
core1['F25'] = 'grafite'
core1['F26'] = 'grafite'
core1['F27'] = 'grafite'
core1['F28'] = 'grafite'
core1['F29'] = 'grafite'
core1['F30'] = 'grafite'

hack1 = []
hack1.append(1147)
hack1.append(1179)
hack1.append(1214)

core_atual = {}
core_atual['A1']  = 'tubo_central_agua'
core_atual['B1']  = 1314
core_atual['B2']  = 1188
core_atual['B3']  = 1289
core_atual['B4']  = 1286
core_atual['B5']  = 1230
core_atual['B6']  = 1297
core_atual['C1']  = 'barra_controle'
core_atual['C2']  = 1298
core_atual['C3']  = 7194
core_atual['C4']  = 1315
core_atual['C5']  = 7192
core_atual['C6']  = 1235
core_atual['C7']  = 'barra_controle'
core_atual['C8']  = 1222
core_atual['C9']  = 7193
core_atual['C10'] = 1351
core_atual['C11'] = 7191
core_atual['C12'] = 1311
core_atual['D1']  = 1269
core_atual['D2']  = 1254
core_atual['D3']  = 1206
core_atual['D4']  = 1303
core_atual['D5']  = 1287
core_atual['D6']  = 1296
core_atual['D7']  = 1282
core_atual['D8']  = 1343
core_atual['D9']  = 1196
core_atual['D10'] = 1212
core_atual['D11'] = 1199
core_atual['D12'] = 1347
core_atual['D13'] = 1220
core_atual['D14'] = 1218
core_atual['D15'] = 1209
core_atual['D16'] = 1280
core_atual['D17'] = 1350
core_atual['D18'] = 1272
core_atual['E1']  = 1348
core_atual['E2']  = 1197
core_atual['E3']  = 989
core_atual['E4']  = 1228
core_atual['E5']  = 1173
core_atual['E6']  = 1205
core_atual['E7']  = 1195
core_atual['E8']  = 1028
core_atual['E9']  = 1130
core_atual['E10'] = 1342
core_atual['E11'] = 1025
core_atual['E12'] = 1128
core_atual['E13'] = 1114
core_atual['E14'] = 1219
core_atual['E15'] = 1301
core_atual['E16'] = 1171
core_atual['E17'] = 1224
core_atual['E18'] = 1179
core_atual['E19'] = 1214
core_atual['E20'] = 1012
core_atual['E21'] = 1162
core_atual['E22'] = 1223
core_atual['E23'] = 1147
core_atual['E24'] = 1005
core_atual['F1']  = 1137
core_atual['F2']  = 'grafite'
core_atual['F3']  = 'grafite'
core_atual['F4']  = 'grafite'
core_atual['F5']  = 'grafite'
core_atual['F6']  = 1330
core_atual['F7']  = 'grafite'
core_atual['F8']  = 'fonte'
core_atual['F9']  = 'grafite'
core_atual['F10'] = 'grafite'
core_atual['F11'] = 1345
core_atual['F12'] = 'terminal_pneumático_1'
core_atual['F13'] = 'grafite'
core_atual['F14'] = 'grafite'
core_atual['F15'] = 'grafite'
core_atual['F16'] = 'barra_controle'
core_atual['F17'] = 'grafite'
core_atual['F18'] = 'grafite'
core_atual['F19'] = 'grafite'
core_atual['F20'] = 'grafite'
core_atual['F21'] = 1263
core_atual['F22'] = 'grafite'
core_atual['F23'] = 'grafite'
core_atual['F24'] = 'grafite'
core_atual['F25'] = 'grafite'
core_atual['F26'] = 1274
core_atual['F27'] = 'grafite'
core_atual['F28'] = 'grafite'
core_atual['F29'] = 'grafite'
core_atual['F30'] = 'grafite'

hack_atual = []
hack_atual.append(7198)
hack_atual.append(7197)
hack_atual.append(7196)
hack_atual.append(7195)
hack_atual.append(6821)