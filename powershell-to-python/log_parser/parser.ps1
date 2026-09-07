#requires -Version 7.2
param([Parameter(Mandatory)][string]$InputPath)
$ErrorActionPreference='Stop'
$counts=@{};$anomalies=@();$malformed=@();$number=0
foreach($line in (Get-Content -LiteralPath $InputPath)){
 $number++;if([string]::IsNullOrWhiteSpace($line)){continue}
 try{
  $record=$line | ConvertFrom-Json -AsHashtable
  if($record.level -isnot [string] -or $record.message -isnot [string]){throw 'Invalid record'}
  $level=$record.level.ToUpperInvariant()
  if($level -notin @('INFO','WARN','ERROR')){throw 'Invalid level'}
 }catch{$malformed+=$number;continue}
 if(-not $counts.ContainsKey($level)){$counts[$level]=0};$counts[$level]++
 if($level -in @('WARN','ERROR')){$anomalies+=@{line=$number;level=$level;message=$record.message}}
}
@{counts=$counts;anomalies=$anomalies;malformedLines=$malformed} | ConvertTo-Json -Depth 10
