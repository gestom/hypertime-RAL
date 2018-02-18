set terminal fig color 
set xlabel 'Granularity' offset 0.0,0.2
set ylabel 'Mean squared error [-]' offset 1.2,0.0
set size 0.65,0.75
set title 'Prediction error rate of individiual models'
set key outside below 
set xtics ("Reconstruction" 0, "Prediction day 1" 1, "Prediction day 2" 2);
set style fill transparent solid 1.0 noborder;
set boxwidth XXX relative
plot \
