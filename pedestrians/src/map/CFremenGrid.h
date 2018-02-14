#ifndef CFREMENGRID_H
#define CFREMENGRID_H

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "CTimer.h" 
#include "CTemporal.h"

/**
@author Tom Krajnik
*/

using namespace std;

class CFremenGrid
{
	public:
		CFremenGrid(const char* name,float spatialCellSize,int temporalCellSize,const char* type,int order);
		CFremenGrid(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize);
		void set(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize);
		~CFremenGrid();
		
		float estimate(float x,float y,float z,uint32_t timeStamp);

		/*changes the model order*/
		void print(bool verbose);
		void save(const char*name,bool lossy = false,int forceOrder = -1);
		bool load(const char*name);

		float estimate(unsigned int index,uint32_t timeStamp);
		float retrieve(unsigned int index);

		int getCellIndex(long int t,float x,float y);
		int getFrelementIndex(float  x,float  y);
		int generateFromData(long int *time, float *x,float *y,int number);
		int generateFromModel(int order,CFremenGrid *grid=NULL);
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
		CTemporal *temporalArray[100000];
};

#endif
