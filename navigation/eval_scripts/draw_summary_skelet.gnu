set terminal fig color 
set xlabel 'Time [days]' offset 0.0,0.2
set ylabel 'Error rate [%]' offset 1.2,0.0
set size 0.8,1.0
set title 'Prediction error rate of individiual models'
set key outside below 
#set xtics ("Rec." 0, "Week 1" 1, "Week 2" 2, "Week 3" 3);
set style fill transparent solid 1.0 noborder;
set boxwidth XXX relative
plot [-0.5:*] [0:*]\
