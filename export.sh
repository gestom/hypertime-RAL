a=$(pwd)

cd ~/papers/
rm -rf  2018_RAL_LTA_hypertime
git clone https://git.overleaf.com/11086351qbsqjjdnvnnc
mv 11086351qbsqjjdnvnnc 2018_RAL_LTA_hypertime
cd $a

cp fremen_basic/eval_scripts/tmp/graphs.pdf ~/papers/2018_RAL_LTA_hypertime/fig/door_graph.pdf
pdfcrop fremen_basic/eval_scripts/tmp/greg_door_2016_min.pdf ~/papers/2018_RAL_LTA_hypertime/fig/door_stat.pdf

cp long-term_topological_localisation/eval_scripts/graphs.pdf ~/papers/2018_RAL_LTA_hypertime/fig/localisation_graph.pdf
pdfcrop long-term_topological_localisation/eval_scripts/tranimage.pdf ~/papers/2018_RAL_LTA_hypertime/fig/localisation_stat.pdf

cp navigation/eval_scripts/tmp/graphs.pdf ~/papers/2018_RAL_LTA_hypertime/fig/nav_graph.pdf
pdfcrop navigation/eval_scripts/tmp/witham.pdf ~/papers/2018_RAL_LTA_hypertime/fig/nav_stat.pdf

cp pedestrians/eval_scripts/tmp/graphs.pdf ~/papers/2018_RAL_LTA_hypertime/fig/ped_graph.pdf
pdfcrop pedestrians/eval_scripts/tmp/lincoln.pdf ~/papers/2018_RAL_LTA_hypertime/fig/ped_stat.pdf

cd ~/papers/2018_RAL_LTA_hypertime

git add -f fig/door_stat.pdf
git add -f fig/door_graph.pdf
git add -f fig/localisation_stat.pdf
git add -f fig/localisation_graph.pdf
git add -f fig/nav_stat.pdf
git add -f fig/nav_graph.pdf
git add -f fig/ped_stat.pdf
git add -f fig/ped_graph.pdf

git commit -m "Figures update"
git push

cd $a 
