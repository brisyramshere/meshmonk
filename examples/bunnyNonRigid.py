#import sys
#sys.path.append('/home/jonatan/projects/OpenMesh/build/Build/python')
import openmesh
#Importing the rest of utilities
import numpy
import time

from context import registration

"""
In this example, we will perform nonrigid registration of the stanford bunny.
"""

##########
# SET PARAMETERS
##########
# Data I/O
floatingMeshPath = "/home/jonatan/projects/kuleuven-algorithms/examples/data/fucked_up_bunny.obj"
targetMeshPath = "/home/jonatan/projects/kuleuven-algorithms/examples/data/bunny90.obj"
resultingMeshPath = "/home/jonatan/projects/kuleuven-algorithms/examples/data/bunnyNonRigid.obj"
# Correspondences
wknnNumNeighbours = 3
# Inlier Detection
kappaa = 3.0
adjustScale = False
# Transformation



##########
# PREPARE DATA
##########
# Load from file
floatingMesh = openmesh.TriMesh()
targetMesh = openmesh.TriMesh()
openmesh.read_mesh(floatingMesh, floatingMeshPath)
openmesh.read_mesh(targetMesh, targetMeshPath)


## Decimate the mesh
## create decimater and module handle
#decimator = openmesh.PolyMeshDecimater(floatingMesh)
#modHandle = openmesh.PolyMeshModQuadricHandle()
## add modules
#decimator.add(modHandle)
#decimator.module(modHandle).set_max_err(0.001)
#
## decimate
#decimator.initialize()
#decimator.decimate_to(100)
#
#floatingMesh.garbage_collection()
#openmesh.write_mesh(floatingMesh, "/home/jonatan/kuleuven-algorithms/examples/data/openmesh_decimated_bunny.obj")


# Obtain info and initialize matrices
numFloatingVertices = floatingMesh.n_vertices()
numTargetVertices = targetMesh.n_vertices()
## Initialize weights and flags
floatingWeights = numpy.ones((numFloatingVertices), dtype = float)
targetWeights = numpy.ones((numTargetVertices), dtype = float)
floatingFlags = numpy.ones((numFloatingVertices), dtype = float)
targetFlags = numpy.ones((numTargetVertices), dtype = float)

# Obtain the floating and target mesh features (= positions and normals)
floatingFeatures = registration.helpers.openmesh_to_numpy_features(floatingMesh)
targetFeatures = registration.helpers.openmesh_to_numpy_features(targetMesh)
correspondingFeatures = numpy.zeros((floatingFeatures.shape), dtype = float)
correspondingFlags = numpy.ones((floatingFlags.shape), dtype = float)


##########
# NONRIGID REGISTRATION
##########
"""

"""
## Initialize
originalFloatingPositions = numpy.copy(floatingFeatures[:,0:3])
regulatedDisplacementField = numpy.zeros((numFloatingVertices,3), dtype = float)
symCorrespondenceFilter = registration.core.SymCorrespondenceFilter(floatingFeatures,
                                                              floatingFlags,
                                                              targetFeatures,
                                                              targetFlags,
                                                              correspondingFeatures,
                                                              correspondingFlags,
                                                              wknnNumNeighbours)
## Set up inlier filter
inlierFilter = registration.core.InlierFilter(floatingFeatures, correspondingFeatures,
                                              correspondingFlags, floatingWeights,
                                              kappaa)


##TODO: HERE WE SHOULD START THE ANNEALING SCHEME
numViscousSmoothingIterationsList = [55, 34, 21, 13, 8, 5, 3, 2, 1, 1]
numElasticSmoothingIterationsList = [55, 34, 21, 13, 8, 5, 3, 2, 1, 1]
## Set up transformation filter
numNeighbourDisplacements = 10
sigmaSmoothing = 10.0
transformationFilter = registration.core.ViscoElasticFilter(floatingFeatures,
                                                            correspondingFeatures,
                                                            floatingWeights,
                                                            10,
                                                            sigmaSmoothing,
                                                            numViscousIterations = 1,
                                                            numElasticIterations = 1)
iteration = 0
for numViscousSmoothingIterations, numElasticSmoothingIterations in zip(numViscousSmoothingIterationsList, numElasticSmoothingIterationsList):
    timeStart = time.time()
    ## 1) Determine Nearest neighbours.
    symCorrespondenceFilter.set_floating_features(floatingFeatures, floatingFlags)
    symCorrespondenceFilter.update()
    ## 2) Determine inlier weights.
    inlierFilter.update()
    ## 3) Determine and update transformation.
    transformationFilter.set_parameters(numNeighbourDisplacements,
                                            sigmaSmoothing,
                                            numViscousSmoothingIterations,
                                            numElasticSmoothingIterations)
    transformationFilter.update()

    ## 4) Re-calculate the mesh's properties (like normals e.g.)
    floatingFeatures[:,3:6] = registration.helpers.openmesh_normals_from_positions(floatingMesh, floatingFeatures[:,0:3])
    
    timeEnd = time.time()
    print "Iteration " + str(iteration) + " took " + str(timeEnd-timeStart) 
    iteration = iteration + 1
##########
# EXPORT DATA
##########
# Save the mesh
openmesh.write_mesh(floatingMesh, resultingMeshPath)
print "Exported result."
