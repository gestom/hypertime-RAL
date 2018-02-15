#include <iostream>
#include <fstream>	
#include <cstdlib>	
#include "CFrelement.h"
#include "CPerGaM.h"
#include "CTimeAdaptiveHist.h"
#include "CTimeHist.h"
#include "CTimeNone.h"
#include "CTimeMean.h"
#include "CTemporal.h"
#include "CFremenGrid.h"
#include "CHyperTime2D.h"
#include "CTimer.h"
#define MAX_SIGNAL_LENGTH 1000000

CTemporal *temporalModel;

long int trainingTimes[MAX_SIGNAL_LENGTH];
float trainingX[MAX_SIGNAL_LENGTH];
float trainingY[MAX_SIGNAL_LENGTH];

unsigned char trainingStates[MAX_SIGNAL_LENGTH];
int testingTime;
float predictions[MAX_SIGNAL_LENGTH];

int testingLength = 0;
int trainingLength = 0;
int dummyState = 0;
long int dummyTime = 0;

int main(int argc,char *argv[])
{
	if (strcmp(argv[5],"NaiveHyperTime")==0)
	{
		CHyperTime2D trainingGrid(argv[1],atof(argv[3]),atoi(argv[4]),argv[5],atoi(argv[6]));
		CHyperTime2D testingGrid(argv[2],atof(argv[3]),atoi(argv[4]),argv[5],atoi(argv[6]));

		float error = 0;
		testingGrid.generateFromModel(atoi(argv[6]),&trainingGrid);
		trainingGrid.print(true);
		error = testingGrid.computeError(1);
		printf("Error: %.3f %i %f %i\n",atof(argv[3]),atoi(argv[4]),error,testingGrid.events);
	}else{
		CFremenGrid trainingGrid(argv[1],atof(argv[3]),atoi(argv[4]),argv[5],atoi(argv[6]));
		CFremenGrid testingGrid(argv[2],atof(argv[3]),atoi(argv[4]),argv[5],atoi(argv[6]));

		float error = 0;
		testingGrid.generateFromModel(atoi(argv[6]),&trainingGrid);
		trainingGrid.print(true);
		error = testingGrid.computeError(1);
		printf("Error: %.3f %i %f %i\n",atof(argv[3]),atoi(argv[4]),error,testingGrid.events);

	}
	return 0;
}
