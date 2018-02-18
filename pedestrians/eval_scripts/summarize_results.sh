d='lincoln'

function extend_figure
{
	w=$(identify $1 |cut -f 3 -d ' '|cut -f 1 -d x)
	h=$(identify $1 |cut -f 3 -d ' '|cut -f 2 -d x)
	if [ $w -lt 500 ]; then	convert $1 -bordercolor white -border $(((500-$w)/2))x0 $1;fi
	if [ $h -lt 400 ]; then	convert $1 -bordercolor white -border 0x$(((400-$h)/2)) $1;fi
	convert $1 -resize 500x400 $1
	w=$(identify $1 |cut -f 3 -d ' '|cut -f 1 -d x)
	h=$(identify $1 |cut -f 3 -d ' '|cut -f 2 -d x)
	if [ $w -lt 500 ]; then	convert $1 -bordercolor white -border $(((500-$w)/2))x0 $1;fi
	if [ $h -lt 400 ]; then	convert $1 -bordercolor white -border 0x$(((400-$h)/2)) $1;fi
	convert $1 -resize 500x400 $1
}

function create_graph
{
	echo digraph 
	echo { 
	echo node [penwidth="2" fontname=\"palatino bold\"]; 
	echo edge [penwidth="2"]; 
	for m in $(cut -f 1 -d ' ' models.tmp)
	do	
		e=0
		for n in $(cut -f 1 -d ' ' models.tmp)
		do
			#echo -ne Comparing $m and $n' ';
			#echo  Comparing $m and $n' ';
			if [ $(paste $m.txt $n.txt|tr \\t ' '|./t-test|grep -c higher) == 1 ]
			then
				echo \"$(grep $n best.txt|cut -d ' ' -f 2,4|sed s/' '/_/|sed s/\_0//)\" '->' \"$(grep $m best.txt|cut -d ' ' -f 2,4|sed s/' '/_/|sed s/\_0//)\" ;
				e=1
			fi
		done
		if [ $e == 0 ]; then echo \"$(grep $m best.txt|cut -d ' ' -f 2,4|sed s/' '/_/|sed s/\_0//)\";fi
	done
	echo }
}

rm best.txt
grep -v '#' ../src/models/test_models.txt|tr -d '!' >models.tmp
for m in $(cut -f 1 -d ' ' models.tmp)
do
	errmin=10000000
	indmin=0
	for o in $(cat models.tmp |grep $m|sed  -e 's/\s\+/\ /g'|cut -f 2-100 -d ' ');
	do
	rm ../results/$d/$m\_$o.txt
	for i in 5 10 
	do 
	for j in 5 10 15 30 
	do
	a=$(echo $i|awk '{print  $1/100}');
	b=$(echo $j|awk '{print $1*60}');
	a=$(grep Error ../results/$d/$(printf "%s_%03i_%04i_%04i.txt\n" $m $o $i $j)|cut -f 4 -d ' ')
	echo $i $j $a >>../results/$d/$m\_$o.txt
	done
	done

	err=$(cat ../results/$d/$m\_$o.txt|awk '{a=a+$3;i=i+1}END{print a/i}')
	sm=$(echo $err $errmin|awk '{a=0}($1 > $2){a=1}{print a}')
	if [ $sm == 0 ];
	then
	errmin=$err
	indmin=$o
	fi
	done
	cat ../results/$d/$m\_$indmin.txt|cut -f 3 -d ' ' >$m.txt
	echo Model $m param $indmin has $errmin error.  >>best.txt
done
create_graph |dot -Tpdf >$d.pdf
convert -density 200 $d.pdf -trim -bordercolor white $d.png 
extend_figure $d.png
cat best.txt |cut -f 2,4 -d ' '|tr ' ' _|sed s/$/.txt/|sed s/^/..\\/results\\/$d\\//
f=0
n=$((1+$(cat models.tmp|grep -c .)));
cat draw_summary_skelet.gnu|sed s/XXX/1.0\\/$n/ >draw_summary.gnu
for i in $(cut -f 1 -d ' ' models.tmp);
do 
	echo \'$(grep $i best.txt |cut -f 2,4 -d ' '|tr ' ' _|sed s/$/.txt/|sed s/^/..\\/results\\/$d\\//)\' 'using ($0+XXX):($1*100) with boxes title' \'$i\',\\|sed s/XXX/\($f-$n*0.5+1\)\\/$n\.0/ >>draw_summary.gnu;
	f=$(($f+1))
done

gnuplot draw_summary.gnu >graphs.fig
fig2dev -Lpdf graphs.fig graphs.pdf
convert -density 200 graphs.pdf -trim -resize 500x400 graphs.png
extend_figure graphs.png 
convert -size 900x450 xc:white \
	-draw 'Image src-over 25,50 500,400 'graphs.png'' \
	-draw 'Image src-over 525,90 375,300 '$d.png'' \
	-pointsize 24 \
	-draw 'Text 100,40 "Performance of temporal models for pedestrian presence prediction"' \
	-pointsize 18 \
	-gravity North \
	-draw 'Text 0,40 "Arrow A->B means that A performs statistically significantly better that B"' summary.png;
cp summary.png  ../results/summary.png
