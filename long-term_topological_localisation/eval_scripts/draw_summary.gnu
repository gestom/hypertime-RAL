set terminal fig color 
set xlabel 'Time [days]' offset 0.0,0.2
set ylabel 'Error rate [%]' offset 1.2,0.0
set size 0.8,1.0
set title 'Localisation error rate vs. number of features used'
set key outside below 
plot \
'FreMEn.txt' using 1:($2*100) with lines title 'FreMEn',\
'AdvHyperTime.txt' using 1:($2*100) with lines title 'AdvHyperTime',\
'NaiveHyperTime.txt' using 1:($2*100) with lines title 'NaiveHyperTime',\
'Mean.txt' using 1:($2*100) with lines title 'Mean',\
'Histogram.txt' using 1:($2*100) with lines title 'Histogram',\
