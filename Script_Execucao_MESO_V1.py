import processing
from qgis.core import QgsVectorLayer, QgsProject
mapcanvas = iface.mapCanvas()
layer = mapcanvas.layers()
myfilepath= layer[2].dataProvider().dataSourceUri()
##selec = QgsExpression("\"CD_GEOCMI\"=31041")
for feature in layer[2].getFeatures():
    ##Região a ser processada
    region = feature["CD_GEOCME"]
    ##region = '31062'
    caminho = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/MESO_'+region+'.gpkg'+'|'+'layername=MESO_'+region
    ##Caminho resultado matriz - ORS Tools
    uri = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/MT_MESO1.gpkg|layername=PROVISORIO'
    ##Nome dos nós e seleção das cidades com UTI
    name = 'MESO_'+region 
    ##name = region 
    layer = QgsProject.instance().mapLayersByName(name)[0]
    #layer.setName('PONTOS_'+region)
    layer.selectByExpression("\"UTI_SUS\"IS NOT NULL")
    ##Processamento da matriz de distância e tempo
    processing.run("ORS Tools:matrix_from_layers", 
    {'INPUT_PROVIDER':0,'INPUT_START_LAYER':caminho,
    'INPUT_START_FIELD':'ID','INPUT_END_LAYER':QgsProcessingFeatureSourceDefinition(caminho, 
    selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
    'INPUT_END_FIELD':'ID','INPUT_PROFILE':0,'OUTPUT':'ogr:dbname=\'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/MT_MESO1.gpkg\' table=\"PROVISORIO\" (geom)'})
    ##Inserir camada em um grupo
    root = QgsProject.instance().layerTreeRoot()
    myOriginalGroup = root.findGroup("RESULTADOS_MESO") # We assume the group exists
    myNewGroup = myOriginalGroup.addGroup("R"+region)
    vlayer = QgsVectorLayer(uri,'MATRIZ_'+region,"ogr")
    QgsProject.instance().addMapLayer(vlayer, False)
    myNewGroup.addLayer(vlayer)
    

   ##Criar camada virtual
    l = QgsVectorLayer( "?query=SELECT FROM_ID, TO_ID, DURATION_H,DIST_KM, make_line(a.geometry,b.geometry)FROM MATRIZ_"+region+" JOIN "+name+" a ON MATRIZ_"+region+".FROM_ID = a.ID JOIN "+name+" b ON MATRIZ_"+region+".TO_ID = b.ID WHERE a.ID!=b.ID", "FLUXO", "virtual")
    ##f = QgsVectorLayer( "?query=SELECT FROM_ID, TO_ID, DURATION_H,DIST_KM, min(DURATION_H) as fastest, make_line(a.geometry,b.geometry)FROM NORTE_MATRIZ JOIN MUNICIPIOS_NORTE a ON NORTE_MATRIZ.FROM_ID = a.ID JOIN MUNICIPIOS_NORTE b ON NORTE_MATRIZ.TO_ID = b.ID WHERE a.ID!=b.ID", "Fluxo_rápido", "virtual" )
    from qgis.core import QgsVectorLayer, QgsProject
    QgsProject.instance().addMapLayer(l, False)
    root = QgsProject.instance().layerTreeRoot()
    g = "R"+region
    myNewGroup = root.findGroup(g)
    myNewGroup.addLayer(l)
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
    #vlayer2 = iface.addVectorLayer(uri2, '', "ogr")
    ##Inserir camada em um grupo
    vlayer = QgsVectorLayer(uri2,'FLUXO_'+region,"ogr")
    QgsProject.instance().addMapLayer(vlayer, False)
    myNewGroup.addLayer(vlayer)
    
    ##Remover camada de Fluxo
    layer1 = QgsProject.instance().mapLayersByName('FLUXO')[0]
    QgsProject.instance().removeMapLayers( [layer1.id()] )
    ##Join layers <http://www.qgistutorials.com/pt_BR/docs/3/processing_algorithms_pyqgis.html>
    ##params = {'INPUT': MUNICIPIOS_NORTE, 'FIELD':ID,'INPUT_2': NORTE_MATRIZ, 'FIELD_2': FROM_ID,'FIELDS_TO_COPY': '_' ,'OUTPUT':'H:\\AULA_QGIS\\ANALISE_INFRAESTRUTURA_PROXIMA\\RESULTADOS.gpkg|layername=JOIN'}
    import processing
    ##processing.run("native:joinattributestable", {'INPUT': uri1, 'FIELD':'ID','INPUT_2': uri, 'FIELD_2': 'FROM_ID','FIELDS_TO_COPY': '_' ,'OUTPUT':'H:/AULA_QGIS/ANALISE_INFRAESTRUTURA_PROXIMA/RESULTADOS2.gpkg'})
    uri3 = 'H:\\02_PROJETOS_DADOS_QGIS\\MG_ACESSIBILIDADE_HOSPITAIS\\FLUXO_'+region+'.gpkg|layername=FLUXO_'+region
    uri4 = 'H:/02_PROJETOS_DADOS_QGIS/MG_ACESSIBILIDADE_HOSPITAIS/RESULTADOS_'+region+'.gpkg'
    processing.run("gdal:executesql", {'INPUT':uri3,'SQL':'SELECT *, min(DURATION_H) as fastest FROM FLUXO_'+region+' GROUP BY FROM_ID','DIALECT':0,'OPTIONS':'','OUTPUT':uri4})
    #vlayer = iface.addVectorLayer(uri4, '', "ogr")
    vlayer = QgsVectorLayer(uri4,'FLUXO_R'+region,"ogr")
    QgsProject.instance().addMapLayer(vlayer, False)
    myNewGroup.addLayer(vlayer)
    iface.mainWindow().findChild(QAction, 'mActionDeselectAll').trigger()
    ##f = QgsVectorLayer( "?query=SELECT *, min(DURATION_H) as fastest FROM FLUXO GROUP BY FROM_ID", "FASTEST", "virtual" )
    ##s = QgsVectorLayer( "?query=SELECT *, min(DIST_KM) as shortest FROM FLUXO GROUP BY FROM_ID", "SHORTEST", "virtual" )
    ##QgsProject.instance().addMapLayer(f)
    ##QgsProject.instance().addMapLayer(s)