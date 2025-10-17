# Script de optimizacion super extrema final
# Migra TODOS los archivos restantes para maximizar el espacio

param(
    [switch]$DryRun = $false
)

$SourceDrive = "C:"
$TargetDrive = "E:"
$LogFile = "$TargetDrive\optimize_super_extreme_final_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$SourcePath = "$SourceDrive\Users\USER"

function Write-Log {
    param($Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Get-FileSize {
    param($Path)
    try {
        if (Test-Path $Path) {
            $Item = Get-Item $Path
            if ($Item.PSIsContainer) {
                $Size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            } else {
                $Size = $Item.Length
            }
            return [math]::Round($Size / 1MB, 2)
        }
        return 0
    }
    catch {
        return 0
    }
}

function Move-ItemSuperExtreme {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$Description
    )
    
    if (-not (Test-Path $SourcePath)) {
        Write-Log "WARNING: $Description does not exist at $SourcePath"
        return $false
    }
    
    $Size = Get-FileSize -Path $SourcePath
    Write-Log "Starting migration of $Description (${Size} MB) from $SourcePath to $TargetPath"
    
    if ($DryRun) {
        Write-Log "DRY RUN: Would migrate $Description"
        return $true
    }
    
    try {
        # Create parent directory if it doesn't exist
        $ParentDir = Split-Path $TargetPath -Parent
        if (-not (Test-Path $ParentDir)) {
            New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
            Write-Log "Created parent directory: $ParentDir"
        }
        
        # If target exists, rename it
        if (Test-Path $TargetPath) {
            $BackupName = "$TargetPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Log "Target exists, renaming to $BackupName"
            Rename-Item -Path $TargetPath -NewName $BackupName
        }
        
        # Move the item
        Write-Log "Moving item..."
        Move-Item -Path $SourcePath -Destination $TargetPath -Force
        Write-Log "SUCCESS: $Description migrated successfully"
        
        # Create symbolic link
        try {
            Write-Log "Creating symbolic link..."
            New-Item -ItemType SymbolicLink -Path $SourcePath -Target $TargetPath -Force | Out-Null
            Write-Log "Symbolic link created for $Description"
        }
        catch {
            Write-Log "WARNING: Could not create symbolic link for $Description`: $($_.Exception.Message)"
        }
        
        return $true
    }
    catch {
        Write-Log "ERROR: Failed to migrate $Description`: $($_.Exception.Message)"
        return $false
    }
}

Write-Log "=== STARTING SUPER EXTREME FINAL OPTIMIZATION ==="
Write-Log "Dry Run Mode: $DryRun"

# Check current space
$CDrive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$CFreeGB = [math]::Round($CDrive.FreeSpace / 1GB, 2)
Write-Log "Current free space on C:: ${CFreeGB} GB"

# Find ALL remaining files (including very small ones)
$AllFiles = Get-ChildItem -Path $SourcePath -File | Where-Object {$_.Length -gt 0} | ForEach-Object {
    $Extension = $_.Extension.ToLower()
    $Category = switch ($Extension) {
        ".md" { "Documentation" }
        ".py" { "Python_Code" }
        ".ps1" { "PowerShell_Scripts" }
        ".json" { "JSON_Files" }
        ".csv" { "CSV_Files" }
        ".txt" { "Text_Files" }
        ".log" { "Log_Files" }
        ".docx" { "Word_Documents" }
        ".xlsx" { "Excel_Files" }
        ".js" { "JavaScript_Files" }
        ".html" { "HTML_Files" }
        ".css" { "CSS_Files" }
        ".xml" { "XML_Files" }
        ".pdf" { "PDF_Files" }
        ".zip" { "Archive_Files" }
        ".rar" { "Archive_Files" }
        ".7z" { "Archive_Files" }
        ".yml" { "YAML_Files" }
        ".yaml" { "YAML_Files" }
        ".env" { "Environment_Files" }
        ".gitignore" { "Git_Files" }
        ".gitattributes" { "Git_Files" }
        ".editorconfig" { "Config_Files" }
        ".eslintrc" { "Config_Files" }
        ".prettierrc" { "Config_Files" }
        ".babelrc" { "Config_Files" }
        ".webpack" { "Config_Files" }
        ".ts" { "TypeScript_Files" }
        ".tsx" { "TypeScript_Files" }
        ".jsx" { "React_Files" }
        ".vue" { "Vue_Files" }
        ".svelte" { "Svelte_Files" }
        ".php" { "PHP_Files" }
        ".rb" { "Ruby_Files" }
        ".go" { "Go_Files" }
        ".rs" { "Rust_Files" }
        ".cpp" { "C++_Files" }
        ".c" { "C_Files" }
        ".h" { "Header_Files" }
        ".hpp" { "Header_Files" }
        ".java" { "Java_Files" }
        ".kt" { "Kotlin_Files" }
        ".swift" { "Swift_Files" }
        ".dart" { "Dart_Files" }
        ".scala" { "Scala_Files" }
        ".clj" { "Clojure_Files" }
        ".hs" { "Haskell_Files" }
        ".ml" { "OCaml_Files" }
        ".fs" { "F#_Files" }
        ".elm" { "Elm_Files" }
        ".ex" { "Elixir_Files" }
        ".exs" { "Elixir_Files" }
        ".erl" { "Erlang_Files" }
        ".hrl" { "Erlang_Files" }
        ".lua" { "Lua_Files" }
        ".r" { "R_Files" }
        ".m" { "Matlab_Files" }
        ".pl" { "Perl_Files" }
        ".pm" { "Perl_Files" }
        ".sh" { "Shell_Scripts" }
        ".bash" { "Bash_Scripts" }
        ".zsh" { "Zsh_Scripts" }
        ".fish" { "Fish_Scripts" }
        ".psm1" { "PowerShell_Modules" }
        ".psd1" { "PowerShell_Data" }
        ".psc1" { "PowerShell_Console" }
        ".ps1xml" { "PowerShell_XML" }
        ".sql" { "SQL_Files" }
        ".db" { "Database_Files" }
        ".sqlite" { "SQLite_Files" }
        ".sqlite3" { "SQLite_Files" }
        ".mdb" { "Access_Files" }
        ".accdb" { "Access_Files" }
        ".dbf" { "DBF_Files" }
        ".frm" { "MySQL_Files" }
        ".myi" { "MySQL_Files" }
        ".myd" { "MySQL_Files" }
        ".ibd" { "InnoDB_Files" }
        ".bak" { "Backup_Files" }
        ".tmp" { "Temporary_Files" }
        ".temp" { "Temporary_Files" }
        ".cache" { "Cache_Files" }
        ".lock" { "Lock_Files" }
        ".pid" { "PID_Files" }
        ".sock" { "Socket_Files" }
        ".pipe" { "Pipe_Files" }
        ".fifo" { "FIFO_Files" }
        ".dev" { "Device_Files" }
        ".sys" { "System_Files" }
        ".dll" { "DLL_Files" }
        ".exe" { "Executable_Files" }
        ".msi" { "Installer_Files" }
        ".deb" { "Debian_Files" }
        ".rpm" { "RPM_Files" }
        ".dmg" { "Disk_Image_Files" }
        ".iso" { "ISO_Files" }
        ".img" { "Image_Files" }
        ".bin" { "Binary_Files" }
        ".hex" { "Hex_Files" }
        ".dat" { "Data_Files" }
        ".raw" { "Raw_Files" }
        ".dump" { "Dump_Files" }
        ".core" { "Core_Files" }
        ".crash" { "Crash_Files" }
        ".log" { "Log_Files" }
        ".out" { "Output_Files" }
        ".err" { "Error_Files" }
        ".debug" { "Debug_Files" }
        ".trace" { "Trace_Files" }
        ".profile" { "Profile_Files" }
        ".bashrc" { "Bash_Config" }
        ".zshrc" { "Zsh_Config" }
        ".fishrc" { "Fish_Config" }
        ".vimrc" { "Vim_Config" }
        ".emacs" { "Emacs_Config" }
        ".gitconfig" { "Git_Config" }
        ".ssh" { "SSH_Files" }
        ".pem" { "Certificate_Files" }
        ".crt" { "Certificate_Files" }
        ".key" { "Key_Files" }
        ".p12" { "PKCS12_Files" }
        ".pfx" { "PKCS12_Files" }
        ".jks" { "Java_KeyStore" }
        ".keystore" { "Java_KeyStore" }
        ".truststore" { "Java_TrustStore" }
        ".pem" { "Certificate_Files" }
        ".crt" { "Certificate_Files" }
        ".key" { "Key_Files" }
        ".p12" { "PKCS12_Files" }
        ".pfx" { "PKCS12_Files" }
        ".jks" { "Java_KeyStore" }
        ".keystore" { "Java_KeyStore" }
        ".truststore" { "Java_TrustStore" }
        ".bat" { "Batch_Files" }
        ".cmd" { "Command_Files" }
        ".com" { "Command_Files" }
        ".scr" { "Screen_Saver_Files" }
        ".lnk" { "Shortcut_Files" }
        ".url" { "URL_Files" }
        ".webloc" { "Web_Loc_Files" }
        ".desktop" { "Desktop_Files" }
        ".app" { "Application_Files" }
        ".appx" { "AppX_Files" }
        ".appxbundle" { "AppX_Bundle_Files" }
        ".msix" { "MSIX_Files" }
        ".msixbundle" { "MSIX_Bundle_Files" }
        ".snap" { "Snap_Files" }
        ".flatpak" { "Flatpak_Files" }
        ".rpm" { "RPM_Files" }
        ".deb" { "Debian_Files" }
        ".pkg" { "Package_Files" }
        ".dmg" { "Disk_Image_Files" }
        ".iso" { "ISO_Files" }
        ".img" { "Image_Files" }
        ".bin" { "Binary_Files" }
        ".hex" { "Hex_Files" }
        ".dat" { "Data_Files" }
        ".raw" { "Raw_Files" }
        ".dump" { "Dump_Files" }
        ".core" { "Core_Files" }
        ".crash" { "Crash_Files" }
        ".log" { "Log_Files" }
        ".out" { "Output_Files" }
        ".err" { "Error_Files" }
        ".debug" { "Debug_Files" }
        ".trace" { "Trace_Files" }
        ".profile" { "Profile_Files" }
        ".bashrc" { "Bash_Config" }
        ".zshrc" { "Zsh_Config" }
        ".fishrc" { "Fish_Config" }
        ".vimrc" { "Vim_Config" }
        ".emacs" { "Emacs_Config" }
        ".gitconfig" { "Git_Config" }
        ".ssh" { "SSH_Files" }
        ".pem" { "Certificate_Files" }
        ".crt" { "Certificate_Files" }
        ".key" { "Key_Files" }
        ".p12" { "PKCS12_Files" }
        ".pfx" { "PKCS12_Files" }
        ".jks" { "Java_KeyStore" }
        ".keystore" { "Java_KeyStore" }
        ".truststore" { "Java_TrustStore" }
        default { "Other_Files" }
    }
    
    @{
        Source = $_.FullName
        Target = "$TargetDrive\$Category\$($_.Name)"
        Description = "$Category`: $($_.Name) ($([math]::Round($_.Length/1MB,2)) MB)"
    }
}

# Find ALL remaining directories
$AllDirs = Get-ChildItem -Path $SourcePath -Directory | Where-Object {$_.Name -notlike ".*" -and $_.Name -notin @("Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos", "Favorites", "Links", "Searches", "Saved Games", "3D Objects", "Contacts")} | ForEach-Object {
    @{
        Source = $_.FullName
        Target = "$TargetDrive\Super_Extreme_Remaining_Directories\$($_.Name)"
        Description = "Directory: $($_.Name)"
    }
}

# Combine all items
$ItemsToMigrate = @($AllFiles) + @($AllDirs)

# Calculate total space to be freed
$TotalSpaceToFree = 0
foreach ($Item in $ItemsToMigrate) {
    if (Test-Path $Item.Source) {
        $Size = Get-FileSize -Path $Item.Source
        $TotalSpaceToFree += $Size
    }
}

Write-Log "Total space to be freed in super extreme final optimization: $([math]::Round($TotalSpaceToFree / 1024, 2)) GB"
Write-Log "Items to migrate: $($ItemsToMigrate.Count)"
Write-Log ""

# Migrate items
$SuccessCount = 0
$TotalCount = $ItemsToMigrate.Count

foreach ($Item in $ItemsToMigrate) {
    Write-Log "--- Processing $($Item.Description) ---"
    
    if (Move-ItemSuperExtreme -SourcePath $Item.Source -TargetPath $Item.Target -Description $Item.Description) {
        $SuccessCount++
    }
    
    Write-Log ""
}

# Final summary
Write-Log "=== SUPER EXTREME FINAL OPTIMIZATION SUMMARY ==="
Write-Log "Items processed: $TotalCount"
Write-Log "Successful migrations: $SuccessCount"
Write-Log "Failed migrations: $($TotalCount - $SuccessCount)"

# Check space after migration
$CDriveAfter = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$CFreeAfterGB = [math]::Round($CDriveAfter.FreeSpace / 1GB, 2)
$SpaceFreedGB = $CFreeAfterGB - $CFreeGB

Write-Log "Free space on C: before super extreme final: ${CFreeGB} GB"
Write-Log "Free space on C: after super extreme final: ${CFreeAfterGB} GB"
Write-Log "Additional space freed: ${SpaceFreedGB} GB"

Write-Log "=== SUPER EXTREME FINAL OPTIMIZATION COMPLETED ==="
Write-Log "Log saved to: $LogFile"

if ($DryRun) {
    Write-Host "`nDRY RUN MODE - No actual changes made" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual migration" -ForegroundColor Yellow
} else {
    Write-Host "`nSUPER EXTREME FINAL OPTIMIZATION COMPLETED!" -ForegroundColor Green
    Write-Host "Freed additional $([math]::Round($SpaceFreedGB, 2)) GB on drive C:" -ForegroundColor Green
}
