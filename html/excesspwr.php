<!DOCTYPE html>
<html>
<head>
<title>Excess Power</title>
</head>

<body>

<?php
//Replace location of battery config file with the location on your system
$config = file_get_contents("battery.cfg");
//error handler function
function customError($errno, $errstr) {
  echo "<b>Error:</b> [$errno] $errstr";
}

//set error handler
set_error_handler("customError");
?>
<style>
</style>

<?php
setlocale(LC_TIME,"");
$time = strftime("%Y%m%d%H%M%S");
$pos = strpos($config,"summary");
$pos = strpos($config,"'",$pos);
$summary = substr($config,$pos+1);
$summary = strstr($summary,"'",true);
$summary = file_get_contents($summary);

$pos = strpos($summary,"[current]");
$pos = strpos($summary, "timestamp = ",$pos);
$timestamp = substr($summary,$pos+12,14);

function getdat($dataname) {
   global $summary, $pos;
   $pos = strpos($summary, $dataname, $pos);
   $pos = strpos($summary,"[",$pos);
   $data = substr($summary,$pos+1);
   $data = strstr($data,"]",true);
   $data = explode(",",$data);
   return $data;
}

$excesssolar = getdat("excesssolar");
$minmaxdemandpwr = getdat("minmaxdemandpwr");
?>

<!-- <meta http-equiv="refresh" content="60"> -->
<meta http-equiv=cache-control" content="no-cache">
<meta http-equiv=pragma" content="no-cache">

<p><?php echo "Current Time ".$time; ?></p>
<p><?php echo "Timestamp ".$timestamp; ?></p>
<p><?php echo "Excess solar power available ".$excesssolar[0]."W"; ?></p>
<p><?php echo "Excess solar power available ".$excesssolar[0]."W"; ?></p>
<p><?php echo "Minimum demand energy ".$minmaxdemandpwr[0]."W"; ?></p>
<p><?php echo "Minimum demand energy ".$minmaxdemandpwr[0]."W"; ?></p>
<p><?php echo "Maximum demand energy ".$minmaxdemandpwr[1]."W"; ?></p>
<p><?php echo "Maximum demand energy ".$minmaxdemandpwr[1]."W"; ?></p>

</body>
</html>
