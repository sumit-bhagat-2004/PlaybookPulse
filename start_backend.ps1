#!/usr/bin/env pwsh
# PlaybookPulse Backend Startup Script
# Quick launcher for the backend server

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PlaybookPulse Backend Server" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Check if backend directory exists
if (-not (Test-Path ".\backend")) {
    Write-Host "❌ Backend directory not found!" -ForegroundColor Red
    Write-Host "   Make sure you're in the PlaybookPulse root directory" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Navigate to backend
Set-Location backend

# Check if .env exists
if (-not (Test-Path ".\.env")) {
    Write-Host "⚠️  Warning: .env file not found in backend directory" -ForegroundColor Yellow
    Write-Host "   Server may fail without proper configuration" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "🚀 Starting backend server..." -ForegroundColor Green
Write-Host ""
Write-Host "   Server URL: http://localhost:8000" -ForegroundColor White
Write-Host "   Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Start the server
uvicorn main:app --port 8000 --reload
