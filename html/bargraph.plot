set terminal jpeg
set output "plot.jpg"
set xdata time
set timefmt "%Y%m%d"
set xrange ["20170301":"20170401"]
set format x "%d/%m"
set title "Daily Battery Energy in/out"
set ylabel "Battery Energy (kWh)"
#show title
#show ylabel
plot "plot" using 1:(-$2) title "Energy In" with histep,\
     "plot" using 1:3 title "Energy Out" with histep

