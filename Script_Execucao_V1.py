##Região a ser processada
region = 'JEQUITINHONHA'
caminho = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/PONTOS.gpkg'+'|'+'layername='+region

##Caminho resultado matriz - ORS Tools
uri = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/MATRIZ_DISTANCIA.gpkg|layername=PROVISORIO'
##Nome dos nós e seleção das cidades com UTI
name = 'PONTOS_'+region 
name1 = 'PONTOS '+region 
##name = region 
layer = QgsProject.instance().mapLayersByName(name1)[0]
layer.setName('PONTOS_'+region)
layer.selectByExpression("\"UTI_SUS\"IS NOT NULL")
##Processamento da matriz de distância e tempo
processing.run("ORS Tools:matrix_from_layers", 
{'INPUT_PROVIDER':0,'INPUT_START_LAYER':caminho,
'INPUT_START_FIELD':'ID','INPUT_END_LAYER':QgsProcessingFeatureSourceDefinition(caminho, 
selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
'INPUT_END_FIELD':'ID','INPUT_PROFILE':0,'OUTPUT':'ogr:dbname=\'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/MATRIZ_DISTANCIA.gpkg\' table=\"PROVISORIO\" (geom)'})

##Abrir matriz de distância
vlayer = iface.addVectorLayer(uri, '', "ogr")
##Mudar o nome do Layer Matriz
new_name = 'MATRIZ_DISTANCIA PROVISORIO'
layer1 = QgsProject.instance().mapLayersByName(new_name)[0]
layer1.setName(region+'_MATRIZ')

##Criar camada virtual
l = QgsVectorLayer( "?query=SELECT FROM_ID, TO_ID, DURATION_H,DIST_KM, make_line(a.geometry,b.geometry)FROM "+region+"_MATRIZ JOIN "+name+" a ON "+region+"_MATRIZ.FROM_ID = a.ID JOIN "+name+" b ON "+region+"_MATRIZ.TO_ID = b.ID WHERE a.ID!=b.ID", "FLUXO", "virtual")
##f = QgsVectorLayer( "?query=SELECT FROM_ID, TO_ID, DURATION_H,DIST_KM, min(DURATION_H) as fastest, make_line(a.geometry,b.geometry)FROM NORTE_MATRIZ JOIN MUNICIPIOS_NORTE a ON NORTE_MATRIZ.FROM_ID = a.ID JOIN MUNICIPIOS_NORTE b ON NORTE_MATRIZ.TO_ID = b.ID WHERE a.ID!=b.ID", "Fluxo_rápido", "virtual" )
from qgis.core import QgsVectorLayer, QgsProject
QgsProject.instance().addMapLayer(l)

##Salvar camada FLUXO
uri2 = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/FLUXO_'+region+'.gpkg'
layer = QgsProject.instance().mapLayersByName('FLUXO')[0]
save_options = QgsVectorFileWriter.SaveVectorOptions()
transform_context = QgsProject.instance().transformContext()
## Write to a GeoPackage (default)
error = QgsVectorFileWriter.writeAsVectorFormatV2(layer,uri2,transform_context,save_options)
if error[0] == QgsVectorFileWriter.NoError: 
    print("success!")
else:
    print(error)
vlayer2 = iface.addVectorLayer(uri2, '', "ogr")


##Join layers <http://www.qgistutorials.com/pt_BR/docs/3/processing_algorithms_pyqgis.html>
##params = {'INPUT': MUNICIPIOS_NORTE, 'FIELD':ID,'INPUT_2': NORTE_MATRIZ, 'FIELD_2': FROM_ID,'FIELDS_TO_COPY': '_' ,'OUTPUT':'H:\\AULA_QGIS\\ANALISE_INFRAESTRUTURA_PROXIMA\\RESULTADOS.gpkg|layername=JOIN'}
import processing
##processing.run("native:joinattributestable", {'INPUT': uri1, 'FIELD':'ID','INPUT_2': uri, 'FIELD_2': 'FROM_ID','FIELDS_TO_COPY': '_' ,'OUTPUT':'H:/AULA_QGIS/ANALISE_INFRAESTRUTURA_PROXIMA/RESULTADOS2.gpkg'})
uri3 = 'H:\\02_PROJETOS_DADOS_QGIS\\MG_ACESSIBILIDADE_HOSPITAIS\\FLUXO_'+region+'.gpkg|layername=FLUXO_'+region
uri4 = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/RESULTADOS_'+region+'.gpkg'
processing.run("gdal:executesql", {'INPUT':uri3,'SQL':'SELECT *, min(DURATION_H) as fastest FROM FLUXO_'+region+' GROUP BY FROM_ID','DIALECT':0,'OPTIONS':'','OUTPUT':uri4})
vlayer = iface.addVectorLayer(uri4, '', "ogr")

##f = QgsVectorLayer( "?query=SELECT *, min(DURATION_H) as fastest FROM FLUXO GROUP BY FROM_ID", "FASTEST", "virtual" )
##s = QgsVectorLayer( "?query=SELECT *, min(DIST_KM) as shortest FROM FLUXO GROUP BY FROM_ID", "SHORTEST", "virtual" )
##QgsProject.instance().addMapLayer(f)
##QgsProject.instance().addMapLayer(s)