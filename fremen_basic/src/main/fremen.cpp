#include <iostream>
#include <fstream>	
#include <cstdlib>	
#include "CFrelement.h"
#include "CPerGaM.h"
#include "CTimeAdaptiveHist.h"
#include "CTimeHist.h"
#include "CTimeNone.h"
#include "CTimeMean.h"
#include "CMises.h"
#include "CPythonHyperTime.h"
#include "CHyperTime.h"
#include "CTemporal.h"
#include "CTimer.h"
#define MAX_SIGNAL_LENGTH 1000000

CTemporal *temporalModel;

int trainingTimes[MAX_SIGNAL_LENGTH];
unsigned char trainingStates[MAX_SIGNAL_LENGTH];
int testingTime;
float predictions[MAX_SIGNAL_LENGTH];

int testingLength = 0;
int trainingLength = 0;
int dummyState = 0;
int dummyTime = 0;

int main(int argc,char *argv[])
{
	/*read training data*/
	FILE* file=fopen(argv[1],"r");
	while (feof(file)==0)
	{
		fscanf(file,"%i %i\n",&dummyTime,&dummyState);
		trainingTimes[trainingLength] = dummyTime;
		trainingStates[trainingLength] = dummyState;
		trainingLength++;
	}
	fclose(file);

	/*traning model*/
	if (argv[3][0] == 'I') temporalModel = new CTimeHist(0);
	else if (argv[3][0] == 'A') temporalModel = new CTimeAdaptiveHist(1);
	else if (argv[3][0] == 'F') temporalModel = new CFrelement(2);
	else if (argv[3][0] == 'M') temporalModel = new CTimeMean(3);
	else if (argv[3][0] == 'G') temporalModel = new CPerGaM(4);
	else if (argv[3][0] == 'Z') temporalModel = new CTimeNone(5);
	else if (argv[3][0] == 'V') temporalModel = new CMises(5);
	else if (argv[3][0] == 'H') temporalModel = new CHyperTime(5);
	else if (argv[3][0] == 'P') temporalModel = new CPythonHyperTime(5);
	else temporalModel = new CTimeNone(0);
		
	temporalModel->init(86400,4,1);

	if (atoi(argv[4])==0 && argv[4][0]!='0'){
		temporalModel->load(argv[4]);
	}else{
		for (int i = 0;i<trainingLength;i++){
			temporalModel->add(trainingTimes[i],trainingStates[i]);
		}
		temporalModel->update(atoi(argv[4]));
		temporalModel->save("model");
	}
	temporalModel->print(true);

	/*read testing timestamps and make predictions*/
	file=fopen(argv[2],"r");
	while (feof(file)==0){
		fscanf(file,"%i\n",&testingTime);
		predictions[testingLength++] = temporalModel->predict(testingTime);
	}
	fclose(file);

	file=fopen("predictions.txt","w");
	for (int i =0;i<testingLength;i++) fprintf(file,"%.3f\n",predictions[i]);
	fclose(file);
	return 0;
}
