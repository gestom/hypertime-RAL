#include "CFremenGrid.h"

using namespace std;
static bool quick = false;

CFremenGrid::CFremenGrid(const char* name,float spatialCellSize,int temporalCellSize,const char* model,int order)
{
	/*load grid info*/
	FILE* file=fopen(name,"r");
	long int minTime,maxTime;
	float minX,maxX,minY,maxY;
	fscanf(file,"%ld %ld\n",&minTime,&maxTime);
	fscanf(file,"%f %f\n",&minX,&maxX);
	fscanf(file,"%f %f\n",&minY,&maxY);
	set(minTime,minX,minY,(int)((maxTime-minTime)/temporalCellSize),(int)((maxX-minX)/spatialCellSize),(int)((maxY-minY)/spatialCellSize),spatialCellSize,temporalCellSize);

	temporalArray = (CTemporal**) calloc(10000000,sizeof(CTemporal));

	/*fill the grid with data*/
	long int time;
	float x,y;
	while (feof(file)==0)
	{
		fscanf(file,"%ld %f %f\n",&time,&x,&y);
		histogram[getCellIndex(time,x,y)]++;
		hasData[getFrelementIndex(x,y)]++;
	}
	fclose(file);
	/*spawnModels*/
	for (int i = 0;i<numFrelements;i++) temporalArray[i] = spawnTemporalModel(model,86400*7,order,1);
}

CFremenGrid::CFremenGrid(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize)
{
	set(originT,originX,originY,dimT,dimX,dimY,spatialCellSize,temporalCellSize);
}

void CFremenGrid::set(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize)
{
	lastTimeStamp = 0;
	minProb = 0.05;
	maxProb = 1-minProb;
	debug = false;
	oT = originT;
	oX = originX;
	oY = originY;
	tDim = dimT;
	xDim = dimX;
	yDim = dimY;
	printf("Dim: %i %i %i\n",dimX,dimY,dimT);
	spatialResolution = spatialCellSize;
	temporalResolution = temporalCellSize;
	numFrelements = yDim*xDim;
	numCells = tDim*yDim*xDim;
	probs = (float*) malloc(numCells*sizeof(float));
	histogram = (int*) malloc(numCells*sizeof(int));
	hasData = (int*) malloc(numFrelements*sizeof(int));
	memset(histogram,0,numCells*sizeof(int));
}

CFremenGrid::~CFremenGrid()
{
	free(histogram);
	for (int i = 0;i<numFrelements;i++) free(temporalArray[i]);
}

int CFremenGrid::generateFromData(long int *time, float *x,float *y,int number)
{
	int cellIndex = 0;
	for (int i = 0;i<number;i++)
	{
		cellIndex = getCellIndex(time[i],x[i],y[i]);
		histogram[cellIndex]++; 
	}
	return 0;
}

void CFremenGrid::display(bool verbose)
{
	for (int s = 0;s<numFrelements;s++)
	{
		int i = 0;
		for (int t = 0;t<tDim;t++){
			i = t*xDim*yDim+s;
			if (s == 63 || quick == false) {
				printf("AA: %.3f %i\n",probs[i],histogram[i]);
			}
		}
	}
}

void CFremenGrid::update(int order)
{
	for (int s = 0;s<numFrelements;s++)
	{
		if (s == 63 || quick == false){
			for (int t = 0;t<tDim;t++) temporalArray[s]->add(t*temporalResolution+oT,histogram[t*xDim*yDim+s]);
			temporalArray[s]->update(order);
			float sumProb = 0;
			float sumHist = 0;
			int index = 0;
			for (int t = 0;t<tDim;t++){
				 index = t*xDim*yDim+s;
				 sumProb += temporalArray[s]->predict(t*temporalResolution+oT);
				 sumHist += histogram[index];
			}
			if (sumProb > 0) temporalArray[s]->correction = sumHist/sumProb;
			//printf("Corr: %f\n",temporalArray[s]->correction);
		}
	}
}

float CFremenGrid::computeError(int order)
{
	events = 0;
	float error = 0;
	FILE* file = fopen("error.pgm","w");
	fprintf(file,"P2\n%i %i\n %i\n",xDim,yDim,255);
	float cellError[numFrelements];
	float maxCellError = 0;

	for (int s = 0;s<numFrelements;s++){
		cellError[s] = 0;
		if (s == 63 || quick == false){
			for (int t = 0;t<tDim;t++){
				int i = t*xDim*yDim+s;
				//if (hasData[s] > 0){
					events++;
					cellError[s] += pow(probs[i]-histogram[i],2);
				//}
//					events += histogram[i];
				//}
			}
		}
		//if (i%xDim == 0 && i != 0) fprintf(file,"\n");
		error+=cellError[s];
		//maxCellError = max(maxCellError,cellErrors[s]);
	}
	for (int s = 0;s<numFrelements;s++)
	{
		printf("%.0f ",cellError[s]);
		if ((s+1)%xDim==0) printf("\n");
	}
	//fprintf(file,"%i  ",(int)(cellError*255/maxHist));
	fclose(file);
	return sqrt(error);
}

/*void CFremenGrid::drawError(long int time)
{
	float maxHist = 0;
	char filename[10];
	sprintf(filename,"%05ld.pgm",time);
	FILE* file = fopen(filename,"w");
	for (int i = 0;i<numFrelements;i++) maxHist = max(probs[i],maxHist);
	fprintf(file,"P2\n#pic at time %ld\n%i %i\n %i\n",time,xDim,yDim,255);
	for (int i = 0;i<numFrelements;i++){
		 if (i%xDim == 0 && i != 0) fprintf(file,"\n");
		 fprintf(file,"%i  ",(int)(probs[i+xDim*yDim*time]*255/maxHist));
	}
	fclose(file);
}*/



int CFremenGrid::generateFromModel(int order,CFremenGrid *grid)
{
	if (grid == NULL) grid = this;
	grid->update(order);
	for (int s = 0;s<numFrelements;s++)
	{
		if (s == 63 || quick == false){
			for (int t = 0;t<tDim;t++) probs[t*xDim*yDim+s] = grid->temporalArray[s]->correction*grid->temporalArray[s]->predict(t*temporalResolution+oT);
		}
		//if (quick && s ==63) grid->frelements[s]->print();
	}
	return 0;
}


void CFremenGrid::drawTime(long int time)
{
	float maxHist = 0;
	char filename[10];
	sprintf(filename,"%05ld.pgm",time);
	FILE* file = fopen(filename,"w");
	for (int i = 0;i<numCells;i++) maxHist = max(probs[i],maxHist);
	fprintf(file,"P2\n#pic at time %ld\n%i %i\n %i\n",time,xDim,yDim,255);
	for (int i = 0;i<numFrelements;i++){
		 if (i%xDim == 0 && i != 0) fprintf(file,"\n");
		 fprintf(file,"%i  ",(int)(probs[i+xDim*yDim*time]*255/maxHist));
	}
	fclose(file);
}


int CFremenGrid::getFrelementIndex(float  x,float  y)
{
	int iX,iY;
	iX = (int)((x-oX)/spatialResolution);
	iY = (int)((y-oY)/spatialResolution);
	if (iX < xDim && iY < yDim && iX >= 0 && iY >=0) return iX+xDim*iY;
	return 0;
}

int CFremenGrid::getCellIndex(long int t,float  x,float  y)
{
	int iX,iY,iT;
	iT = (int)((t-oT)/temporalResolution);
	iX = (int)((x-oX)/spatialResolution);
	iY = (int)((y-oY)/spatialResolution);
	if (iX < xDim && iY < yDim && iT < tDim && iX >= 0 && iY >=0 && iT >= 0) return iX+xDim*(iY+yDim*iT);
	return 0;
}

void CFremenGrid::save(const char* filename,bool lossy,int forceOrder)
{
	FILE* f=fopen(filename,"w");
	fwrite(&xDim,sizeof(int),1,f);
	fwrite(&yDim,sizeof(int),1,f);
	fwrite(&tDim,sizeof(long int),1,f);
	fwrite(&oX,sizeof(float),1,f);
	fwrite(&oY,sizeof(float),1,f);
	fwrite(&oT,sizeof(long int),1,f);
	fwrite(&spatialResolution,sizeof(float),1,f);
	fwrite(&temporalResolution,sizeof(float),1,f);
	fwrite(probs,sizeof(float),numCells,f);
	for (int i=0;i<numCells;i++) temporalArray[i]->save(f,false);
	fclose(f);
}

bool CFremenGrid::load(const char* filename)
{
	int ret = 0;
	FILE* f=fopen(filename,"r");
	if (f == NULL){
		printf("FrOctomap %s not found, aborting load.\n",filename);
		return false;
	}
	ret += fread(&xDim,sizeof(int),1,f);
	ret += fread(&yDim,sizeof(int),1,f);
	ret += fread(&tDim,sizeof(long int),1,f);
	ret += fread(&oX,sizeof(float),1,f);
	ret += fread(&oY,sizeof(float),1,f);
	ret += fread(&oT,sizeof(long int),1,f);
	ret += fread(&spatialResolution,sizeof(float),1,f);
	ret += fread(&temporalResolution,sizeof(float),1,f);
	numCells = xDim*yDim*tDim;
	numFrelements = xDim*yDim;
	ret += fread(probs,sizeof(float),numCells,f);
	for (int i=0;i<numFrelements;i++) temporalArray[i]->load(f);
	/*cellArray = (CFrelement**) malloc(numCells*sizeof(CFrelement*));
	for (int i=0;i<numCells;i++) cellArray[i] = new CFrelement();
	for (int i=0;i<numCells;i++){
		cellArray[i]->load(f);
		cellArray[i]->signalLength = signalLength;
	}*/
	printf("Loaded a grid of %i bytes with %i cells as %ix%ix%i.\n",ret,numCells,tDim,xDim,yDim);
	fclose(f);
	//update();
	return true;
}

void CFremenGrid::print(bool verbose)
{
//	for (int i = 0;i<numCells;i++) printf("Histo: %i\n",histogram[i]);
// temporalArray[i]->print(verbose);
		//if (frelements[i].periodicities > 0)
		//{
			//printf("Cell: %i %i ",i,frelements[i].periodicities);
		//}
}
