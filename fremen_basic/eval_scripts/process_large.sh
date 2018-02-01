dataset='greg_door'
grep -v '#' ../src/models/test_models.txt >models.tmp
#rm -rf ../results/$dataset/
mkdir ../results/$dataset/
for m in $(cut -f 1 -d ' ' models.tmp)
do	
for i in $(cat models.tmp |grep $m|sed  -e 's/\s\+/\ /g'|cut -f 2-100 -d ' ');
do
rm predictions.txt

rm ../results/$dataset/$m\_$i.txt
for l in $(seq -w 0 27) 
do 
echo ../bin/fremen ../data/$dataset/month_$l.min ../data/$dataset/month_00.tim.min $m $i
../bin/fremen ../data/$dataset/month_$l.min ../data/$dataset/month_00.tim.min $m $i
for t in $(seq -w 0 27)
do 
../bin/fremen ../data/$dataset/month_$l.min ../data/$dataset/month_$t.tim.min $m model 
e=$(paste predictions.txt ../data/$dataset/month_$t.val.min |awk '{a=$1-$2;c=($1>0.5)-$2;b+=a*a;d+=c*c;i=i+1;}END{print b/i,d/i}')
echo $e >>../results/$dataset/$m\_$i.txt
done
done
echo Model $m, parameter $i
done
done
