#requires -Version 7.2
[CmdletBinding(DefaultParameterSetName='Fixture')]
param([Parameter(Mandatory,ParameterSetName='Fixture')][string]$FixturePath,
      [Parameter(Mandatory,ParameterSetName='Live')][uri]$Url)
$ErrorActionPreference='Stop'
if($PSCmdlet.ParameterSetName -eq 'Fixture'){
 $pages=Get-Content -LiteralPath $FixturePath -Raw | ConvertFrom-Json
 $result=@(foreach($page in $pages){foreach($row in $page.value){$row}})
}else{
 if($Url.Scheme -ne 'https' -or $Url.UserInfo){throw 'HTTPS without embedded credentials required'}
 $result=Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 30 -MaximumRedirection 0
}
ConvertTo-Json -InputObject $result -Depth 20
