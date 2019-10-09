<!DOCTYPE html>
<html>
<body>

<h1>Battery Stats</h1>
<?php
//Replace location of battery config file with the location on your system
$config = file_get_contents("battery.cfg");
$pos = strpos($config,"summary");
$pos = strpos($config,"'",$pos);
$summary = substr($config,$pos+1);
$summary = strstr($summary,"'",true);
$myfile = fopen($summary,"r") or die("Unable to open file!");

// $myfile = fopen("/media/sdcard/summary", "r") or die("Unable to open file!");
// Output one line until end-of-file
while(!feof($myfile)) {
  echo fgets($myfile) . "<br>";
}
fclose($myfile);
?>
</body>
</html>
