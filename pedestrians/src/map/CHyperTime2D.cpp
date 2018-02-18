#include "CHyperTime2D.h"

using namespace std;
static bool quick = false;

CHyperTime2D::CHyperTime2D(const char* name,float spatialCellSize,int temporalCellSize,const char* model,int order)
{
	lastError = 1000000000000;
	modelPositive = NULL;
	timeDimension = 2;
	covarianceType = EM::COV_MAT_GENERIC;
	positives = 0;
	corrective = 1.0;
	order = 1;
	periods.clear();
	temporalScale = 10;
	/*load grid info*/
	FILE* file=fopen(name,"r");
	long int minTime,maxTime;
	float minX,maxX,minY,maxY;
	fscanf(file,"%ld %ld\n",&minTime,&maxTime);
	fscanf(file,"%f %f\n",&minX,&maxX);
	fscanf(file,"%f %f\n",&minY,&maxY);
	set(minTime,minX,minY,(int)((maxTime-minTime)/temporalCellSize),(int)((maxX-minX)/spatialCellSize),(int)((maxY-minY)/spatialCellSize),spatialCellSize,temporalCellSize);

	/*fill the grid with data*/
	long int time;
	float x,y;
	Mat sample(1,2+timeDimension,CV_32FC1);
	int numPositives=0;
	timeArray = (long int*)calloc(1000000,sizeof(long int));
	periods.push_back(86400);
	periods.push_back(86400*7);
	while (feof(file)==0)
	{
		fscanf(file,"%ld %f %f\n",&time,&x,&y);
		histogram[getCellIndex(time,x,y)]++;
		sample.at<float>(0,0)=x;
		sample.at<float>(0,1)=y;
		sample.at<float>(0,2)=temporalScale*cos((float)time/86400*2*M_PI);
		sample.at<float>(0,3)=temporalScale*sin((float)time/86400*2*M_PI);
	//	sample.at<float>(0,4)=temporalScale*cos((float)time/86400/7*2*M_PI);
	//	sample.at<float>(0,5)=temporalScale*sin((float)time/86400/7*2*M_PI);
		samplesPositive.push_back(sample);
		timeArray[positives++] = time;
	}
	fclose(file);
}

CHyperTime2D::CHyperTime2D(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize)
{
	set(originT,originX,originY,dimT,dimX,dimY,spatialCellSize,temporalCellSize);
}

void CHyperTime2D::set(long int originT,float originX,float originY,int dimT,int dimX,int dimY,float spatialCellSize,int temporalCellSize)
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
	printf("%i %i %i\n",dimX,dimY,dimT);
	spatialResolution = spatialCellSize;
	temporalResolution = temporalCellSize;
	numFrelements = yDim*xDim;
	numCells = tDim*yDim*xDim;
	probs = (float*) malloc(numCells*sizeof(float));
	histogram = (int*) malloc(numCells*sizeof(int));
	memset(histogram,0,numCells*sizeof(int));
}

CHyperTime2D::~CHyperTime2D()
{
	free(histogram);
}

int CHyperTime2D::generateFromData(long int *time, float *x,float *y,int number)
{
	int cellIndex = 0;
	for (int i = 0;i<number;i++)
	{
		cellIndex = getCellIndex(time[i],x[i],y[i]);
		histogram[cellIndex]++; 
	}
	return 0;
}

void CHyperTime2D::display(bool verbose)
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

void CHyperTime2D::update(int order)
{
	float sumProb = 0;
	float sumHist = 0;
	for (int k = 0;k<0;k++)
	{
		if (modelPositive != NULL) delete modelPositive; 
		modelPositive = new EM(order,covarianceType,TermCriteria(TermCriteria::COUNT+TermCriteria::EPS, EM::DEFAULT_MAX_ITERS, FLT_EPSILON));
		modelPositive->train(samplesPositive);
		Mat meansPositive = modelPositive->get<Mat>("means");
		std::cout << meansPositive << std::endl;
		sumProb = 0;
		sumHist = 0;

		/*calculate relevant corrections*/
		for (int it = 0;it<tDim;it++){
			float t = it*temporalResolution+oT+temporalResolution/2;
			for (int ix = 0;ix<xDim;ix++)
			{
				float x = ix*spatialResolution+oX+spatialResolution/2;
				for (int iy = 0;iy<yDim;iy++)
				{
					float y = iy*spatialResolution+oY+spatialResolution/2;
					if (histogram[getCellIndex(t,x,y)]>0) sumProb += estimate(t,x,y);
					//printf("%.3f %.3f %.3f %f\n",x,y,t,estimate(t,x,y));
				}
			}
		}

		corrective = positives/sumProb;
		printf("UUU: %.3f %i %f\n",sumProb,positives,corrective);
		//	return;

		/*determine periodics*/
			CFrelement fremen(0);
			fremen.init(86400*7,5,1);
			float sumErr = 0;
			for (int it = 0;it<tDim;it++){
				float t = it*temporalResolution+oT+temporalResolution/2;
				for (int ix = 0;ix<xDim;ix++)
				{
					float x = ix*spatialResolution+oX+spatialResolution/2;
					for (int iy = 0;iy<yDim;iy++)
					{
						float y = iy*spatialResolution+oY+spatialResolution/2;
						float err = (corrective*estimate(t,x,y)-histogram[getCellIndex(t,x,y)]);
						fremen.add(t,err);
						sumErr += err*err;
					}
				}
			}
			sumErr = sqrt(sumErr);
			fremen.update(5+1);
			fremen.print(true);
		if (timeDimension == 0){
			for (int i = 0;i<5;i++) periods.push_back(fremen.predictFrelements[i].period);
		} 
		int period = periods[timeDimension/2];
		printf("Error: %.0f, last %.0f adding period %i \n",sumErr,lastError,period);
		if (lastError > sumErr){
			Mat hypertimePositive(positives,2,CV_32FC1);
			for (int i = 0;i<positives;i++)
			{
				hypertimePositive.at<float>(i,0)=temporalScale*cos((float)timeArray[i]/period*2*M_PI);
				hypertimePositive.at<float>(i,1)=temporalScale*sin((float)timeArray[i]/period*2*M_PI);
			}
			hconcat(samplesPositive, hypertimePositive,samplesPositive);
			timeDimension+=2;
		}
		lastError = sumErr;
	}

	if (modelPositive != NULL) delete modelPositive; 
	modelPositive = new EM(order,covarianceType,TermCriteria(TermCriteria::COUNT+TermCriteria::EPS, EM::DEFAULT_MAX_ITERS, FLT_EPSILON));
	modelPositive->train(samplesPositive);

	/*calculate relevant corrections*/
	for (int it = 0;it<tDim;it++){
		float t = it*temporalResolution+oT+temporalResolution/2;
		for (int ix = 0;ix<xDim;ix++)
		{
			float x = ix*spatialResolution+oX+spatialResolution/2;
			for (int iy = 0;iy<yDim;iy++)
			{
				float y = iy*spatialResolution+oY+spatialResolution/2;
				if (histogram[getCellIndex(t,x,y)]>0) sumProb += estimate(t,x,y);
			}
		}
	}
	corrective = positives/sumProb;
	printf("UUU: %.3f %i %f\n",sumProb,positives,corrective);
}

float CHyperTime2D::estimate(uint32_t t,float x,float y)
{
	/*is the model valid?*/
	if (modelPositive->isTrained()){
		Mat sample(1,2+timeDimension,CV_32FC1);
		sample.at<float>(0,0)=x;
		sample.at<float>(0,1)=y;
		for (int i = 0;i<timeDimension/2;i++){
			sample.at<float>(0,2+i)=temporalScale*cos((float)t/periods[i]*2*M_PI);
			sample.at<float>(0,3+i)=temporalScale*sin((float)t/periods[i]*2*M_PI);
		}
		Mat probs(1,2,CV_32FC1);
		Vec2f a = modelPositive->predict(sample, probs);
		return exp(a(0));
	}
	/*any data available?*/
	return positives;
}

float CHyperTime2D::computeError(int order)
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
				if (histogram[i] > 0){
					cellError[s] += pow(probs[i]-histogram[i],2);
					events += histogram[i];
				}
			}
		}
		//if (i%xDim == 0 && i != 0) fprintf(file,"\n");
		error+=cellError[s];
		//maxCellError = max(maxCellError,cellErrors[s]);
	}
	//fprintf(file,"%i  ",(int)(cellError*255/maxHist));
	fclose(file);
	return sqrt(error);
}

/*void CHyperTime2D::drawError(long int time)
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



int CHyperTime2D::generateFromModel(int order,CHyperTime2D *grid)
{
	if (grid == NULL) grid = this;
	grid->update(order);
	for (int ix = 0;ix<xDim;ix++)
	{
		float x = ix*spatialResolution+oX;
		for (int iy = 0;iy<yDim;iy++)
		{
			float y = iy*spatialResolution+oY;
			for (int it = 0;it<tDim;it++){
				float t = it*temporalResolution+oT;
				probs[getCellIndex(t,x,y)]= grid->corrective*grid->estimate(t,x,y);
			}
		}
	}
	return 0;
}


void CHyperTime2D::drawTime(long int time)
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


int CHyperTime2D::getFrelementIndex(float  x,float  y)
{
	int iX,iY;
	iX = (int)((x-oX)/spatialResolution);
	iY = (int)((y-oY)/spatialResolution);
	if (iX < xDim && iY < yDim && iX >= 0 && iY >=0) return iX+xDim*iY;
	return 0;
}

int CHyperTime2D::getCellIndex(long int t,float  x,float  y)
{
	int iX,iY,iT;
	iT = (int)((t-oT)/temporalResolution);
	iX = (int)((x-oX)/spatialResolution);
	iY = (int)((y-oY)/spatialResolution);
	if (iX < xDim && iY < yDim && iT < tDim && iX >= 0 && iY >=0 && iT >= 0) return iX+xDim*(iY+yDim*iT);
	return 0;
}

void CHyperTime2D::save(const char* filename,bool lossy,int forceOrder)
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
//	for (int i=0;i<numCells;i++) temporalArray[i]->save(f,false);
	fclose(f);
}

bool CHyperTime2D::load(const char* filename)
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
//	for (int i=0;i<numFrelements;i++) temporalArray[i]->load(f);
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

void CHyperTime2D::print(bool verbose)
{
	//for (int i = 0;i<numFrelements;i++) temporalArray[i]->print(verbose);
		//if (frelements[i].periodicities > 0)
		//{
			//printf("Cell: %i %i ",i,frelements[i].periodicities);
		//}
}
