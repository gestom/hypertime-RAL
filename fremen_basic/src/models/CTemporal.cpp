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
	if (type[0] == 'I') temporalModel = new CTimeHist(0);
	else if (type[0] == 'A') temporalModel = new CTimeAdaptiveHist(1);
	else if (type[0] == 'F') temporalModel = new CFrelement(2);
	else if (type[0] == 'M') temporalModel = new CTimeMean(3);
	else if (type[0] == 'G') temporalModel = new CPerGaM(4);
	else if (type[0] == 'Z') temporalModel = new CTimeNone(5);
	else if (type[0] == 'V') temporalModel = new CMises(5);
	else if (type[0] == 'H') temporalModel = new CHyperTime(5);
	else if (type[0] == 'P') temporalModel = new CPythonHyperTime(5);
	else temporalModel = new CTimeNone(0);
	temporalModel->init(maxPeriod,elements,numClasses);
	return temporalModel;
}
