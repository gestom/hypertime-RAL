#include "CFrelement.h"
#include "CPerGaM.h"
#include "CTimeAdaptiveHist.h"
#include "CTimeHist.h"
#include "CTimeNone.h"
#include "CTimeMean.h"
#include "CMises.h"
#include "CPythonHyperTime.h"
#include "CHyperTime.h"

CTemporal* spawnTemporalModel(const char* type,int maxPeriod,int elements,int numClasses)
{
	CTemporal *temporalModel;
	if 	(strcmp(type,"Histogram")==0) 		temporalModel = new CTimeHist(0);
	else if (strcmp(type,"FreMEn")==0) 		temporalModel = new CFrelement(2);
	else if (strcmp(type,"Mean")==0) 		temporalModel = new CTimeMean(3);
	else if (strcmp(type,"None")==0) 		temporalModel = new CTimeNone(5);
	else if (strcmp(type,"NaiveHyperTime")==0)	temporalModel = new CHyperTime(5);
	else if (strcmp(type,"HyperTime")==0) 		temporalModel = new CPythonHyperTime(5);
	else if (strcmp(type,"VonMises")==0) 		temporalModel = new CMises(5);
	else if (strcmp(type,"Adaptive")==0) 		temporalModel = new CTimeAdaptiveHist(1);
	else if (strcmp(type,"Gaussian")==0) 		temporalModel = new CPerGaM(4);
	else temporalModel = new CTimeNone(0);
	temporalModel->init(maxPeriod,elements,numClasses);
	return temporalModel;
}
