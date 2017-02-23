#include "NonrigidRegistration.hpp"

namespace registration {

void NonrigidRegistration::set_input(FeatureMat * const ioFloatingFeatures,
                            const FeatureMat * const inTargetFeatures,
                            const FacesMat * const inFloatingFaces,
                            const VecDynFloat * const inFloatingFlags,
                            const VecDynFloat * const inTargetFlags){
    _ioFloatingFeatures = ioFloatingFeatures;
    _inTargetFeatures = inTargetFeatures;
    _inFloatingFaces = inFloatingFaces;
    _inFloatingFlags = inFloatingFlags;
    _inTargetFlags = inTargetFlags;
}//end set_input()

void NonrigidRegistration::set_parameters(bool symmetric, size_t numNeighbours,
                                       float kappaa, size_t numIterations){
    _symmetric = symmetric;
    _numNeighbours = numNeighbours;
    _kappaa = kappaa;
    _numIterations = numIterations;
}//end set_parameters()


void NonrigidRegistration::update(){

    //# Initializes
    size_t numFloatingVertices = _ioFloatingFeatures->rows();
    size_t numTargetVertices = _inTargetFeatures->rows();
    FeatureMat correspondingFeatures = FeatureMat::Zero(numFloatingVertices, registration::NUM_FEATURES);
    VecDynFloat correspondingFlags = VecDynFloat::Zero(numFloatingVertices);

    //# Set up the filters
    //## Correspondence Filter (note: this part should be improved by using inheritance in the correspondence filter classes)

    BaseCorrespondenceFilter* correspondenceFilter = NULL;
    //std::unique_ptr<BaseCorrespondenceFilter> correspondenceFilter = new SymmetricCorrespondenceFilter;

    if (_symmetric) {
        correspondenceFilter = new SymmetricCorrespondenceFilter();
    }
    else {
        correspondenceFilter = new CorrespondenceFilter();
    }
    correspondenceFilter->set_floating_input(_ioFloatingFeatures, _inFloatingFlags);
    correspondenceFilter->set_target_input(_inTargetFeatures, _inTargetFlags);
    correspondenceFilter->set_output(&correspondingFeatures, &correspondingFlags);
    correspondenceFilter->set_parameters(_numNeighbours);

    //## Inlier Filter
    VecDynFloat floatingWeights = VecDynFloat::Ones(numFloatingVertices);
    InlierDetector inlierDetector;
    inlierDetector.set_input(_ioFloatingFeatures, &correspondingFeatures,
                                &correspondingFlags);
    inlierDetector.set_output(&floatingWeights);
    inlierDetector.set_parameters(_kappaa);
    //## Transformation Filter
    const size_t numNonrigidIterations = 12;
    size_t smoothingIterations[12] = {144,89,55,34,21,13,8,5,3,2,1,1};
    ViscoElasticTransformer transformer;
    transformer.set_input(&correspondingFeatures, &floatingWeights, _inFloatingFaces);
    transformer.set_output(_ioFloatingFeatures);

    //# Perform ICP
    time_t timeStart, timePreIteration, timePostIteration, timeEnd;
    timeStart = time(0);
    std::cout << "Starting Nonrigid Registration process..." << std::endl;
    for (size_t iteration = 0 ; iteration < _numIterations ; iteration++) {
        timePreIteration = time(0);
        //# Correspondences
        correspondenceFilter->set_floating_input(_ioFloatingFeatures, _inFloatingFlags);
        correspondenceFilter->set_target_input(_inTargetFeatures, _inTargetFlags);
        correspondenceFilter->update();

        //# Inlier Detection
        inlierDetector.update();

        //# Transformation
        transformer.set_parameters(10, 2.0, smoothingIterations[iteration],smoothingIterations[iteration]);
        transformer.update();

        //# Print info
        timePostIteration = time(0);
        std::cout << "Iteration " << iteration << "/" << _numIterations << " took "<< difftime(timePostIteration, timePreIteration) <<" second(s)."<< std::endl;
    }
    timeEnd = time(0);
    std::cout << "Nonrigid Registration Completed in " << difftime(timeEnd, timeStart) <<" second(s)."<< std::endl;

    delete correspondenceFilter;

}//end update()

}//namespace registration