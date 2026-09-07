#requires -Version 7.2
# Read-only OS/runtime inventory. Python version is not collected by this version.
[pscustomobject]@{system=[Runtime.InteropServices.RuntimeInformation]::OSDescription;machine=[Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString();powershell=$PSVersionTable.PSVersion.ToString()} | ConvertTo-Json
