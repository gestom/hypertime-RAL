a=900
b=950
c=1000
cat training.dat |sed -n 1,$a\p >training_data.txt 
cat training.dat |sed -n 1,$a\p  |cut -f 1 -d ' ' >test_times_0.txt
cat training.dat |sed -n 1,$a\p  |cut -f 2 -d ' ' >test_data_0.txt
cat training.dat |sed -n $a,$b\p |cut -f 1 -d ' ' >test_times_1.txt
cat training.dat |sed -n $a,$b\p |cut -f 2 -d ' ' >test_data_1.txt
cat training.dat |sed -n $b,$c\p |cut -f 1 -d ' ' >test_times_2.txt
cat training.dat |sed -n $b,$c\p |cut -f 2 -d ' ' >test_data_2.txt
