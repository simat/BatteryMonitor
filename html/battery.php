<!DOCTYPE html>
<html>
<body>

<h1>Battery Stats</h1>
<?php
//Replace location of battery config file with the location on your system
$myfile = fopen("/home/pi/data/summary", "r") or die("Unable to open file!");
// Output one line until end-of-file
while(!feof($myfile)) {
  echo fgets($myfile) . "<br>";
}
fclose($myfile);
?>
</body>
</html>
