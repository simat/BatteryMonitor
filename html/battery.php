<!DOCTYPE html>
<html>
<body>

<h1>Battery Stats</h1>
<?php
$myfile = fopen("/batdat/summary", "r") or die("Unable to open file!");
// Output one line until end-of-file
while(!feof($myfile)) {
  echo fgets($myfile) . "<br>";
}
fclose($myfile);
?>
</body>
</html> 
