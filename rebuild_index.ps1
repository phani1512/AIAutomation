# Read the original file
$lines = Get-Content "c:\Users\valaboph\WebAutomation\src\main\resources\web\index.html" -Encoding UTF8

# Build the head section
$head = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Test Automation Studio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css">
</head>
"@

# Build the footer section
$footer = @"

    <script src="app.js"></script>
    
    <!-- Prism.js for syntax highlighting -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-csharp.min.js"></script>
</body>
</html>
"@

# Extract body content (lines 1114-1753 in 1-indexed, which is 1113-1752 in 0-indexed)
$bodyContent = $lines[1113..1752] -join "`r`n"

# Combine everything
$output = $head + $bodyContent + $footer

# Write to new file
$output | Set-Content "c:\Users\valaboph\WebAutomation\src\main\resources\web\index.html" -Encoding UTF8 -NoNewline

# Count lines
$lineCount = (Get-Content "c:\Users\valaboph\WebAutomation\src\main\resources\web\index.html" | Measure-Object -Line).Lines
Write-Host "✅ File rebuilt successfully with $lineCount lines"
