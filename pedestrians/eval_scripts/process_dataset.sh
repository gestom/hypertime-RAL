dataset='lincoln'
grep -v '#' ../src/models/test_models.txt|grep -v '!' >models.tmp
mkdir ../results/$dataset/
for m in $(cut -f 1 -d ' ' models.tmp)
do	
for o in $(cat models.tmp |grep $m|sed  -e 's/\s\+/\ /g'|cut -f 2-100 -d ' ');
do
rm ../results/$dataset/$(printf "%s_%02i" $m $o)*
echo Model $m, parameter $o
for i in 2 4 5 10 20 
do 
for j in 1 2 3 4 6 12 24 
do
a=$(echo $i|awk '{print  20/$1}');
b=$(echo $j|awk '{print 86400/$1}');
../bin/fremen ../data/$dataset/trenovaci_dva_tydny.txt ../data/$dataset/testovaci_dva_dny.txt $a $b $m $o >../results/$dataset/$(printf "%s_%02i_%02i_%02i.txt\n" $m $o $i $j)
echo -ne \\r $i, $j
done
done
echo Model $m, parameter $o
done
done
