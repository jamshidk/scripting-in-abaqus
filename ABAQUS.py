# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

import random

#### Creating the thin plate

#print(random.uniform(0,10))

mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=400.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(-50.0, -50.0),
    point2=(50.0, 50.0))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='plate', type=
    DEFORMABLE_BODY)
mdb.models['Model-1'].parts['plate'].BaseSolidExtrude(depth=5.0, sketch=
    mdb.models['Model-1'].sketches['__profile__'])
del mdb.models['Model-1'].sketches['__profile__']

#### creating a  random void ####
pt1=random.uniform(-25,25)
pt2=random.uniform(-25,25)
R=random.uniform(0,1)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=400.0)
mdb.models['Model-1'].sketches['__profile__'].ConstructionLine(point1=(0.0,
    -200.0), point2=(0.0, 200.0))
mdb.models['Model-1'].sketches['__profile__'].FixedConstraint(entity=
    mdb.models['Model-1'].sketches['__profile__'].geometry[2])
mdb.models['Model-1'].sketches['__profile__'].ArcByCenterEnds(center=(pt1, pt2)
    , direction=CLOCKWISE, point1=(pt1, pt2+R), point2=(pt1, pt2-R))
mdb.models['Model-1'].sketches['__profile__'].CoincidentConstraint(
    addUndoState=False, entity1=
    mdb.models['Model-1'].sketches['__profile__'].vertices[1], entity2=
    mdb.models['Model-1'].sketches['__profile__'].geometry[2])
mdb.models['Model-1'].sketches['__profile__'].Line(point1=(pt1, pt2+R), point2=(
    pt1, pt2-R))
mdb.models['Model-1'].sketches['__profile__'].VerticalConstraint(addUndoState=
    False, entity=mdb.models['Model-1'].sketches['__profile__'].geometry[4])
mdb.models['Model-1'].sketches['__profile__'].PerpendicularConstraint(
    addUndoState=False, entity1=
    mdb.models['Model-1'].sketches['__profile__'].geometry[3], entity2=
    mdb.models['Model-1'].sketches['__profile__'].geometry[4])
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='void', type=
    DEFORMABLE_BODY)
mdb.models['Model-1'].parts['void'].BaseSolidRevolve(angle=360.0,
    flipRevolveDirection=OFF, sketch=
    mdb.models['Model-1'].sketches['__profile__'])
del mdb.models['Model-1'].sketches['__profile__']


##################voided plate
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='plate-1', part=
    mdb.models['Model-1'].parts['plate'])
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='void-1', part=
    mdb.models['Model-1'].parts['void'])
mdb.models['Model-1'].rootAssembly.translate(instanceList=('void-1', ), vector=
    (0.0, 0.0, 2.5))
mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
    mdb.models['Model-1'].rootAssembly.instances['void-1'], ), instanceToBeCut=
    mdb.models['Model-1'].rootAssembly.instances['plate-1'], name='voidedplate'
    , originalInstances=SUPPRESS)

################################Assign Materials property

mdb.models['Model-1'].Material(name='Composite')
mdb.models['Model-1'].materials['Composite'].Density(table=((1600e-9, ), ))
mdb.models['Model-1'].materials['Composite'].SpecificHeat(table=((900, ), ))
mdb.models['Model-1'].materials['Composite'].Conductivity(table=((170e-3,
    170e-3, 70e-3), ), type=ORTHOTROPIC)
mdb.models['Model-1'].HomogeneousSolidSection(material='Composite', name=
    'CompositeSection', thickness=None)
mdb.models['Model-1'].parts['voidedplate'].Set(cells=
    mdb.models['Model-1'].parts['voidedplate'].cells.getSequenceFromMask((
    '[#1 ]', ), ), name='Set-1')
mdb.models['Model-1'].parts['voidedplate'].SectionAssignment(offset=0.0,
    offsetField='', offsetType=MIDDLE_SURFACE, region=
    mdb.models['Model-1'].parts['voidedplate'].sets['Set-1'], sectionName=
    'CompositeSection', thicknessAssignment=FROM_SECTION)
mdb.models['Model-1'].parts['voidedplate'].MaterialOrientation(
    additionalRotationType=ROTATION_NONE, axis=AXIS_1, fieldName='', localCsys=
    None, orientationType=GLOBAL, region=Region(
    cells=mdb.models['Model-1'].parts['voidedplate'].cells.getSequenceFromMask(
    mask=('[#1 ]', ), )), stackDirection=STACK_3)

################################Assign Steps

mdb.models['Model-1'].rootAssembly.regenerate()
mdb.models['Model-1'].HeatTransferStep(amplitude=STEP, deltmx=10.0, initialInc=
    1.0, maxInc=10.0, minInc=0.00001, name='Step-1', previous='Initial',
    timePeriod=100.0)
mdb.models['Model-1'].HeatTransferStep(deltmx=10.0, initialInc=1.0, maxInc=
    100.0, minInc=0.00001, name='Step-2', previous='Step-1', timePeriod=1000.0)

mdb.models['Model-1'].rootAssembly.Set(cells=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].cells.getSequenceFromMask(
    ('[#1 ]', ), ), edges=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].edges.getSequenceFromMask(
    ('[#1fff ]', ), ), faces=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].faces.getSequenceFromMask(
    ('[#7f ]', ), ), name='Set-1', vertices=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].vertices.getSequenceFromMask(
    ('[#3ff ]', ), ))
mdb.models['Model-1'].Temperature(createStepName='Initial',
    crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
    UNIFORM, magnitudes=(298.0, ), name='Predefined Field-1', region=
    mdb.models['Model-1'].rootAssembly.sets['Set-1'])

############################# Setting a interaction (Convection)

mdb.models['Model-1'].rootAssembly.Surface(name='Surf-1', side1Faces=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].faces.getSequenceFromMask(
    ('[#7f ]', ), ))
mdb.models['Model-1'].FilmCondition(createStepName='Step-1', definition=
    EMBEDDED_COEFF, filmCoeff=8e-5, filmCoeffAmplitude='', name='Int-1',
    sinkAmplitude='', sinkDistributionType=UNIFORM, sinkFieldName='',
    sinkTemperature=298.0, surface=
    mdb.models['Model-1'].rootAssembly.surfaces['Surf-1'])

################################### Assigning Heat SurfaceHeatFlux

mdb.models['Model-1'].rootAssembly.Surface(name='Surf-2', side1Faces=
    mdb.models['Model-1'].rootAssembly.instances['voidedplate-1'].faces.getSequenceFromMask(
    ('[#10 ]', ), ))
mdb.models['Model-1'].SurfaceHeatFlux(createStepName='Step-1', magnitude=500e-6
    , name='Load-1', region=
    mdb.models['Model-1'].rootAssembly.surfaces['Surf-2'])
mdb.models['Model-1'].loads['Load-1'].deactivate('Step-2')

###################################### Mesh part

mdb.models['Model-1'].parts['voidedplate'].seedPart(deviationFactor=0.1,
    minSizeFactor=0.1, size=2)
mdb.models['Model-1'].parts['voidedplate'].setElementType(elemTypes=(ElemType(
    elemCode=DC3D8, elemLibrary=STANDARD), ElemType(elemCode=DC3D6,
    elemLibrary=STANDARD), ElemType(elemCode=DC3D4, elemLibrary=STANDARD)),
    regions=(
    mdb.models['Model-1'].parts['voidedplate'].cells.getSequenceFromMask((
    '[#1 ]', ), ), ))
mdb.models['Model-1'].parts['voidedplate'].setMeshControls(elemShape=TET,
    regions=
    mdb.models['Model-1'].parts['voidedplate'].cells.getSequenceFromMask((
    '[#1 ]', ), ), technique=FREE)
mdb.models['Model-1'].parts['voidedplate'].generateMesh()

#################################Generate Job###############################
mdb.models['Model-1'].rootAssembly.regenerate()
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF,
    explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF,
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF,
    multiprocessingMode=DEFAULT, name='Job-1', nodalOutputPrecision=SINGLE,
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
    ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)

mdb.jobs['Job-1'].submit(consistencyChecking=OFF)




# Save by jamsh on 2020_08_26-08.30.42; build 6.14-2 2014_08_22-10.00.46 134497
