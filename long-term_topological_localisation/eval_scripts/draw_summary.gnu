set terminal fig color 
set xlabel 'Time [days]' offset 0.0,0.2
set ylabel 'Error rate [%]' offset 1.2,0.0
set size 0.8,1.0
set title 'Localisation error rate vs. number of features used'
set key outside below 
plot \
'FreMEn.txt' using 1:($2*100) with lines title 'FreMEn',\
'PythonHyper.txt' using 1:($2*100) with lines title 'PythonHyper',\
'Hypertime.txt' using 1:($2*100) with lines title 'Hypertime',\
'Mean.txt' using 1:($2*100) with lines title 'Mean',\
'Zero.txt' using 1:($2*100) with lines title 'Zero',\
'GMM.txt' using 1:($2*100) with lines title 'GMM',\
'VonMises.txt' using 1:($2*100) with lines title 'VonMises',\
'Interval.txt' using 1:($2*100) with lines title 'Interval',\
'Adaptive.txt' using 1:($2*100) with lines title 'Adaptive',\
