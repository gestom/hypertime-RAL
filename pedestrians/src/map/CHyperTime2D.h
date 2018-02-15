#ifndef CHYPERTIME2D_H
#define CHYPERTIME2D_H

#include <opencv2/ml/ml.hpp>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "CTimer.h" 
#include "CTemporal.h"
#include "CHyperTime2D.h"
#include "CFrelement.h"

/**
@author Tom Krajnik
*/

using namespace cv;
using namespace std;

class CHyperTime2D
{
	public:
		CHyperTime2D(const char* name,float spatialCellSize,int temporalCellSize,const char* type,int order);
		CHyperTime2D(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize);
		void set(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize);
		~CHyperTime2D();
		
		float estimate(uint32_t t,float x,float y);

		/*changes the model order*/
		void print(bool verbose);
		void save(const char*name,bool lossy = false,int forceOrder = -1);
		bool load(const char*name);

		float estimate(unsigned int index,uint32_t timeStamp);
		float retrieve(unsigned int index);

		int getCellIndex(long int t,float x,float y);
		int getFrelementIndex(float  x,float  y);
		int generateFromData(long int *time, float *x,float *y,int number);
		int generateFromModel(int order,CHyperTime2D *grid=NULL);
		void update(int order);
		float computeError(int order = -1);
		void drawTime(long int time);
		void display(bool verbose);

		//center of the first cell
		float oX,oY,oT;		
		//size of the grid cells
		float spatialResolution;
		float temporalResolution;
		//grid dimensions
		int xDim,yDim,tDim;
		float* probs;	
		int* histogram;	
		int numCells;
		int numFrelements;
		bool debug;
		int events;
		uint32_t lastTimeStamp;
		float minProb,maxProb,residualEntropy,residualInformation;
		CHyperTime2D *temporalModel;
		EM* modelPositive;
		Mat samplesPositive;
		float corrective;
		float lastError;
		float temporalScale;
		int timeDimension;
		int covarianceType;
		int positives;
		long int *timeArray;
		vector<int> periods;
};

#endif
