<!DOCTYPE html>
<html>
<head>
<style>
#header {
    background-color:black;
    color:white;
    text-align:center;
    padding:5px;
}
#bat {
    line-height:30px;
    background-color:#eeeeee;
    height:300px;
    width:300px;
    float:left;
    padding:5px;	      
}
#batdata {
    width:350px;
    height:300px;
    float:left;
    padding:10px;	 	 
}
#footer {
#    background-color:black;
#    color:white;
    width:650px;
#    float: left;
#    clear:both;
#    text-align:center;
   padding:5px;	 	 
}

#highest {
    font-weight: 900;
    font-size: 110%;
}

#lowest {
    font-style: oblique;
    font-weight: bold;
    font-size: 90%;
</style>

<?php
$summary = file_get_contents("/batdat/summary");
$highv = 3.6;
$lowv = 3.0;
#echo $summary
$pos = strpos($summary,"[current]");

function getdat($dataname) { 
   global $summary, $pos;
   $pos = strpos($summary, $dataname, $pos);
   $pos = strpos($summary,"[",$pos);
   $data = substr($summary,$pos+1);
   $data = strstr($data,"]",true);
   $data = explode(",",$data);
   return $data;
}

$batvolts = getdat("maxvoltages");
$batcolour = array_fill(0,count($batvolts),"yellow");
/* */
$minbatvolts = 100.0;
for ($x = 0; $x < count($batvolts)-1; $x++) {
    if ($batvolts[$x] >= $highv) {
       $batcolour[$x] = "red"; }
    if ($batvolts[$x] <= $lowv) {
       $batcolour[$x] = "fuchsia"; }
    $minbatvolts = min($minbatvolts,$batvolts[$x]);
    $maxbatvolts = max($maxbatvolts,$batvolts[$x]);       
}

$batvoltstype = array_fill(0,count($batvolts),"");

for ($x = 0; $x < count($batvolts)-1; $x++) {
    if ($batvolts[$x] == $maxbatvolts) {
       $batvoltstype[$x] = "highest"; }
    if ($batvolts[$x] == $minbatvolts) {
       $batvoltstype[$x] = "lowest"; }
}
/*
$arrlength = count($batvoltstype);

for($x = 0; $x < $arrlength; $x++) {
    echo ($x.$batvoltstype[$x]);
}
*/
$deltav = getdat("deltav");
$amps = getdat("amps");
$dod = getdat("dod");
$pos = strpos($summary,"[currentday]", $pos);
$dayah = getdat("ah");
$power = getdat("power");
?>

</head>
<body>
<div id="bat">
<table align="left" border="1" cellpadding="1" cellspacing="4" style="height:300px; width:300px">
	<tbody>
		<tr>
			<td style="background-color:<?php echo $batcolour[4] ?>; text-align:center">
			<p><span style="font-size:36px">&nbsp;5&nbsp; </span></p>

<!--                        <input name="batvolts" type="text" size=5 value="<?php echo ($batvolts[4]."V"); ?>"> -->
			<p id= "<?php echo $batvoltstype[4]; ?>" ><?php echo $batvolts[4]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[5] ?>; text-align:center">
			<p><span style="font-size:36px">6</span></p>

			<p id= "<?php echo $batvoltstype[5]; ?>" ><?php echo $batvolts[5]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[6] ?>; text-align:center">
			<p><span style="font-size:36px">7</span></p>

			<p id= "<?php echo $batvoltstype[6] ?>" ><?php echo $batvolts[6]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[7] ?>; text-align:center">
			<p><span style="font-size:36px">8</span></p>

			<p id= "<?php echo $batvoltstype[7]; ?>" ><?php echo $batvolts[7]."V"?><p>
			</td>
		</tr>
		<tr>
			<td style="background-color:<?php echo $batcolour[3] ?>; text-align:center">
			<p><span style="font-size:36px">4</span></p>

			<p id= "<?php echo $batvoltstype[3]; ?>" ><?php echo $batvolts[3]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[2] ?>; text-align:center">
			<p><span style="font-size:36px">3</span></p>

			<p id= "<?php echo $batvoltstype[2]; ?>" ><?php echo $batvolts[2]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[1] ?>; text-align:center">
			<p><span style="font-size:36px">2</span></p>

			<p id= "<?php echo $batvoltstype[1]; ?>" ><?php echo $batvolts[1]."V"?><p>
			</td>
			<td style="background-color:<?php echo $batcolour[0] ?>; text-align:center">
			<p><span style="font-size:36px">1</span></p>

			<p id= "<?php echo $batvoltstype[0]; ?>" ><?php echo $batvolts[0]."V"?><p>
			</td>
		</tr>
	</tbody>
</table>
</div>
<div id="batdata">
<p><b>Battery Voltage&nbsp;</b><?php echo $batvolts[8]."V"?></p>
<p><b>Delta Voltage&nbsp;</b><?php echo $deltav[0]."V"?></p>
<p><b>Battery Current&nbsp;</b><?php echo $amps[0]."A"?></p>
<p><b>Battery DOD&nbsp;</b><?php echo $dod[0]."Ah"?></p>

</div>
<div id="footer">
<h2> Daily Battery Statistics </h2>
<p><b>Daily Battery Charge In&nbsp;</b><?php echo $dayah[4]."Ah"?></p>
<p><b>Daily Battery Charge Out&nbsp;</b><?php echo $dayah[5]."Ah"?></p>
<p><b>Daily Battery Power In&nbsp;</b><?php echo $power[0]."kWh"?></p>
<p><b>Daily Battery Power Out&nbsp;</b><?php echo $power[1]."kWh"?></p>
<p><b>Daily Solar Power In&nbsp;</b><?php echo $power[2]."kWh"?></p>


</div>
</body>
</html> 
