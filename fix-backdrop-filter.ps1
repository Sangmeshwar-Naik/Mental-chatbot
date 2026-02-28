# Fix backdrop-filter compatibility across all HTML files
$files = @(
    "g:\My Drive\chatbot\mh-chatbot\features\coping-plan.html",
    "g:\My Drive\chatbot\mh-chatbot\games\color-therapy.html",
    "g:\My Drive\chatbot\mh-chatbot\mental-health-tools.html",
    "g:\My Drive\chatbot\mh-chatbot\games\reaction-time.html",
    "g:\My Drive\chatbot\mh-chatbot\social-wellness.html",
    "g:\My Drive\chatbot\mh-chatbot\features\therapy-exercises.html",
    "g:\My Drive\chatbot\mh-chatbot\games\memory-match.html",
    "g:\My Drive\chatbot\mh-chatbot\features\journal.html",
    "g:\My Drive\chatbot\mh-chatbot\games\bubble-shooter.html",
    "g:\My Drive\chatbot\mh-chatbot\wellness.html",
    "g:\My Drive\chatbot\mh-chatbot\games.html",
    "g:\My Drive\chatbot\mh-chatbot\games\block-blast.html",
    "g:\My Drive\chatbot\mh-chatbot\features\habit-tracker.html",
    "g:\My Drive\chatbot\mh-chatbot\features\voice-chat.html",
    "g:\My Drive\chatbot\mh-chatbot\games\chess.html",
    "g:\My Drive\chatbot\mh-chatbot\features\breathing.html",
    "g:\My Drive\chatbot\mh-chatbot\features\focus-timer.html",
    "g:\My Drive\chatbot\mh-chatbot\features\grounding.html",
    "g:\My Drive\chatbot\mh-chatbot\features\clinician-dashboard.html",
    "g:\My Drive\chatbot\mh-chatbot\features\kindness-challenge.html",
    "g:\My Drive\chatbot\mh-chatbot\features\mood-matching.html",
    "g:\My Drive\chatbot\mh-chatbot\features\wellness-bingo.html",
    "g:\My Drive\chatbot\mh-chatbot\features\mind-games.html",
    "g:\My Drive\chatbot\mh-chatbot\features\empathy-quiz.html",
    "g:\My Drive\chatbot\mh-chatbot\features\thought-record.html",
    "g:\My Drive\chatbot\mh-chatbot\features\mental-health-resources.html",
    "g:\My Drive\chatbot\mh-chatbot\features\medication-reminder.html",
    "g:\My Drive\chatbot\mh-chatbot\features\relaxation-scripts.html",
    "g:\My Drive\chatbot\mh-chatbot\features\self-care-planner.html",
    "g:\My Drive\chatbot\mh-chatbot\features\progress-dashboard.html",
    "g:\My Drive\chatbot\mh-chatbot\index.html"
)

$count = 0
foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        # Add -webkit-backdrop-filter before backdrop-filter if not already present
        $content = $content -replace '(?<!-webkit-)backdrop-filter:', "-webkit-backdrop-filter:`$0`n            backdrop-filter:"
        # Remove duplicate webkit prefixes if any
        $content = $content -replace '(-webkit-backdrop-filter:[^;]+;\s+){2,}', '$1'
        Set-Content $file -Value $content -NoNewline
        $count++
        Write-Host "✅ Fixed: $file" -ForegroundColor Green
    }
}

Write-Host "`n🎉 Fixed backdrop-filter in $count files!" -ForegroundColor Cyan
