# Advanced File Organization PowerShell Script
# Organizes files into appropriate business area folders with subcategories

param(
    [string]$BasePath = "C:\Users\blatam\documentos_blatam"
)

Write-Host "Starting advanced file organization..." -ForegroundColor Green
Write-Host "Base path: $BasePath" -ForegroundColor Yellow

# Create organization log
$logFile = Join-Path $BasePath "organization_log.txt"
$logEntries = @()

function Log-Organization {
    param([string]$Action, [string]$Source, [string]$Destination)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Action`: $Source -> $Destination"
    $logEntries += $logEntry
    Write-Host $logEntry -ForegroundColor Cyan
}

function Get-FileCategory {
    param([string]$FileName)
    $fileNameLower = $FileName.ToLower()
    
    # Marketing patterns
    if ($fileNameLower -match "marketing|anchor.*text|seo|sem|social.*media|content.*marketing|digital.*marketing|email.*marketing|campaign|lead.*generation|analytics|automation|ai.*marketing") {
        return @{
            Category = "marketing"
            MainFolder = "01_Marketing"
            Subcategory = Get-MarketingSubcategory $fileNameLower
        }
    }
    
    # Technology patterns
    if ($fileNameLower -match "technology|tech|software|development|programming|code|api|database|cloud|ai|machine.*learning|data.*science|blockchain|quantum|iot|edge.*computing|devops|cybersecurity") {
        return @{
            Category = "technology"
            MainFolder = "05_Technology"
            Subcategory = Get-TechnologySubcategory $fileNameLower
        }
    }
    
    # Finance patterns
    if ($fileNameLower -match "finance|financial|investment|budget|accounting|fintech|cryptocurrency|crypto|risk.*management|compliance|audit|reporting") {
        return @{
            Category = "finance"
            MainFolder = "02_Finance"
            Subcategory = Get-FinanceSubcategory $fileNameLower
        }
    }
    
    # Sales patterns
    if ($fileNameLower -match "sales|ventas|selling|closing|pitch|proposal|customer|client|revenue|conversion|leads") {
        return @{
            Category = "sales"
            MainFolder = "09_Sales"
            Subcategory = Get-SalesSubcategory $fileNameLower
        }
    }
    
    # Operations patterns
    if ($fileNameLower -match "operations|operational|process|workflow|efficiency|optimization|management|administration") {
        return @{
            Category = "operations"
            MainFolder = "04_Operations"
            Subcategory = Get-OperationsSubcategory $fileNameLower
        }
    }
    
    # HR patterns
    if ($fileNameLower -match "human.*resources|hr|employee|staff|recruitment|training|performance|talent") {
        return @{
            Category = "hr"
            MainFolder = "03_Human_Resources"
            Subcategory = Get-HRSubcategory $fileNameLower
        }
    }
    
    return $null
}

function Get-MarketingSubcategory {
    param([string]$FileName)
    if ($FileName -match "anchor.*text") { return "01_Digital_Marketing" }
    if ($FileName -match "seo|sem|search.*engine") { return "05_SEO_SEM" }
    if ($FileName -match "social.*media|facebook|instagram|twitter|linkedin") { return "03_Social_Media" }
    if ($FileName -match "content.*marketing|blog|article") { return "02_Content_Marketing" }
    if ($FileName -match "email.*marketing|newsletter|mailchimp") { return "04_Email_Marketing" }
    if ($FileName -match "analytics|metrics|dashboard|report") { return "06_Analytics" }
    if ($FileName -match "automation|automated|workflow") { return "07_Automation" }
    if ($FileName -match "ai.*marketing|artificial.*intelligence.*marketing") { return "08_AI_Marketing" }
    return "01_Digital_Marketing"
}

function Get-TechnologySubcategory {
    param([string]$FileName)
    if ($FileName -match "ai|artificial.*intelligence|machine.*learning|neural.*network") { return "01_AI_Machine_Learning" }
    if ($FileName -match "cloud|aws|azure|google.*cloud") { return "02_Cloud_Computing" }
    if ($FileName -match "data.*science|data.*analysis|big.*data") { return "03_Data_Science" }
    if ($FileName -match "software.*development|programming|code|api") { return "04_Software_Development" }
    if ($FileName -match "cybersecurity|security|cyber.*security") { return "05_Cybersecurity" }
    if ($FileName -match "devops|deployment|ci.*cd") { return "06_DevOps" }
    if ($FileName -match "blockchain|cryptocurrency|crypto") { return "07_Blockchain" }
    if ($FileName -match "quantum|quantum.*computing") { return "08_Quantum_Computing" }
    if ($FileName -match "iot|internet.*of.*things|sensors") { return "09_IoT" }
    if ($FileName -match "edge.*computing") { return "10_Edge_Computing" }
    return "04_Software_Development"
}

function Get-FinanceSubcategory {
    param([string]$FileName)
    if ($FileName -match "financial.*planning|budget|planning") { return "01_Financial_Planning" }
    if ($FileName -match "investment|portfolio|trading") { return "02_Investment_Analysis" }
    if ($FileName -match "risk.*management|risk|compliance") { return "03_Risk_Management" }
    if ($FileName -match "accounting|bookkeeping|financial.*statements") { return "04_Accounting" }
    if ($FileName -match "fintech|financial.*technology") { return "06_Fintech" }
    if ($FileName -match "cryptocurrency|crypto|bitcoin|ethereum") { return "07_Cryptocurrency" }
    if ($FileName -match "financial.*modeling|model|forecast") { return "08_Financial_Modeling" }
    if ($FileName -match "compliance|regulatory|audit") { return "09_Compliance" }
    if ($FileName -match "reporting|reports|financial.*reports") { return "10_Reporting" }
    return "01_Financial_Planning"
}

function Get-SalesSubcategory {
    param([string]$FileName)
    if ($FileName -match "sales.*strategy|strategy") { return "01_Sales_Strategy" }
    if ($FileName -match "closing|close.*sales|techniques") { return "02_Closing_Techniques" }
    if ($FileName -match "customer|client|crm") { return "03_Customer_Management" }
    if ($FileName -match "lead.*generation|leads|prospects") { return "04_Lead_Generation" }
    if ($FileName -match "sales.*automation|automation") { return "05_Sales_Automation" }
    if ($FileName -match "sales.*analytics|metrics|kpi") { return "06_Sales_Analytics" }
    return "01_Sales_Strategy"
}

function Get-OperationsSubcategory {
    param([string]$FileName)
    if ($FileName -match "process|optimization|efficiency") { return "01_Process_Optimization" }
    if ($FileName -match "workflow|process.*management") { return "02_Workflow_Management" }
    if ($FileName -match "operational.*excellence|best.*practices") { return "03_Operational_Excellence" }
    if ($FileName -match "supply.*chain|logistics|procurement") { return "04_Supply_Chain" }
    if ($FileName -match "quality.*management|quality.*assurance") { return "05_Quality_Management" }
    return "01_Process_Optimization"
}

function Get-HRSubcategory {
    param([string]$FileName)
    if ($FileName -match "recruitment|hiring|talent.*acquisition") { return "01_Recruitment" }
    if ($FileName -match "training|development|learning") { return "02_Training_Development" }
    if ($FileName -match "performance|evaluation|review") { return "03_Performance_Management" }
    if ($FileName -match "employee.*relations|engagement") { return "04_Employee_Relations" }
    if ($FileName -match "compensation|benefits|payroll") { return "05_Compensation_Benefits" }
    return "01_Recruitment"
}

function Organize-File {
    param([string]$FilePath)
    $fileName = Split-Path $FilePath -Leaf
    $fileInfo = Get-FileCategory $fileName
    
    if (-not $fileInfo) {
        return $false
    }
    
    # Create target path
    $targetDir = Join-Path $BasePath $fileInfo.MainFolder
    $targetDir = Join-Path $targetDir $fileInfo.Subcategory
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    # Move file
    $targetPath = Join-Path $targetDir $fileName
    
    try {
        if ((Test-Path $FilePath) -and (-not (Test-Path $targetPath))) {
            Move-Item $FilePath $targetPath -Force
            Log-Organization "MOVED" $FilePath $targetPath
            return $true
        } elseif (Test-Path $targetPath) {
            Log-Organization "SKIPPED (exists)" $FilePath $targetPath
            return $false
        }
    } catch {
        Log-Organization "ERROR" $FilePath "Error: $($_.Exception.Message)"
        return $false
    }
}

# Get all files in the base directory (not in subdirectories)
$filesToOrganize = Get-ChildItem -Path $BasePath -File | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "organize*" }

Write-Host "Found $($filesToOrganize.Count) files to organize" -ForegroundColor Yellow

$organizedCount = 0
foreach ($file in $filesToOrganize) {
    if (Organize-File $file.FullName) {
        $organizedCount++
    }
}

Write-Host "Successfully organized $organizedCount files" -ForegroundColor Green

# Save organization log
$logEntries | Out-File -FilePath $logFile -Encoding UTF8
Write-Host "Organization log saved to: $logFile" -ForegroundColor Yellow

# Create organization summary
$summaryFile = Join-Path $BasePath "ORGANIZATION_SUMMARY.md"
$summaryContent = @"
# Advanced File Organization Summary

Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Business Areas and Subcategories

### 01_Marketing
**Category**: Marketing

**Subcategories**:
- 01_Digital_Marketing
- 02_Content_Marketing
- 03_Social_Media
- 04_Email_Marketing
- 05_SEO_SEM
- 06_Analytics
- 07_Automation
- 08_AI_Marketing
- 09_Lead_Generation
- 10_Campaigns

### 02_Finance
**Category**: Finance

**Subcategories**:
- 01_Financial_Planning
- 02_Investment_Analysis
- 03_Risk_Management
- 04_Accounting
- 05_Budgeting
- 06_Fintech
- 07_Cryptocurrency
- 08_Financial_Modeling
- 09_Compliance
- 10_Reporting

### 05_Technology
**Category**: Technology

**Subcategories**:
- 01_AI_Machine_Learning
- 02_Cloud_Computing
- 03_Data_Science
- 04_Software_Development
- 05_Cybersecurity
- 06_DevOps
- 07_Blockchain
- 08_Quantum_Computing
- 09_IoT
- 10_Edge_Computing

## Organization Log

$($logEntries -join "`n")
"@

$summaryContent | Out-File -FilePath $summaryFile -Encoding UTF8
Write-Host "Organization summary saved to: $summaryFile" -ForegroundColor Yellow

Write-Host "`nAdvanced file organization completed!" -ForegroundColor Green













