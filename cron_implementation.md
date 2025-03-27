# Twitter Manager Cron Implementation Plan

## Architecture Overview

The Twitter Manager will run on two schedules:
1. Local cron job running hourly
2. GitHub Actions workflow running daily as a backup

## 1. Local Cron Implementation

### Required Changes

#### Script Modifications (`src/twitter_manager.py`):
- Remove internal scheduling logic
- Update main function to handle single execution
- Configure logging for background execution
- Add absolute path handling for imports

#### Systemd Service Setup:
```ini
[Unit]
Description=Twitter Manager Service
After=network.target

[Service]
Type=oneshot
User=<your-user>
WorkingDirectory=/path/to/twitter_manager
Environment=PYTHONPATH=/path/to/twitter_manager
EnvironmentFile=/path/to/twitter_manager/.env
ExecStart=/usr/bin/python3 -m src.twitter_manager
StandardOutput=append:/var/log/twitter_manager/output.log
StandardError=append:/var/log/twitter_manager/error.log

[Install]
WantedBy=multi-user.target
```

#### Cron Entry:
```crontab
0 * * * * /usr/bin/systemctl start twitter-manager.service
```

### Installation Steps

1. Create systemd service:
```bash
sudo nano /etc/systemd/system/twitter-manager.service
sudo systemctl daemon-reload
sudo systemctl enable twitter-manager.service
```

2. Set up logging:
```bash
sudo mkdir /var/log/twitter_manager
sudo chown <your-user>:<your-group> /var/log/twitter_manager
```

3. Configure cron job:
```bash
crontab -e
# Add the cron entry
```

## 2. Modified GitHub Actions Workflow

Update `.github/workflows/twitter-scheduler.yml`:
```yaml
name: Twitter Manager Daily Backup Schedule

on:
  schedule:
    - cron: '0 0 * * *'  # Runs daily at midnight UTC
  workflow_dispatch:  # Allows manual triggering

jobs:
  tweet:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    steps:
      # ... (rest of the workflow remains the same)
```

## Error Handling & Monitoring

1. Log files:
   - Local: `/var/log/twitter_manager/{output,error}.log`
   - GitHub Actions: Available in Actions tab

2. Monitoring:
   - Set up log rotation for local logs
   - Monitor GitHub Actions runs via dashboard
   - Consider adding error notifications via email

## Environment Variables

Ensure environment variables are properly set in:
1. `.env` file for local cron
2. GitHub repository secrets for Actions

## Testing Plan

1. Test local cron:
   - Manual service execution
   - Single cron execution
   - Environment variable loading
   - Log output verification

2. Test GitHub Actions:
   - Manual workflow trigger
   - Verify daily schedule
   - Check secret access

## Rollback Plan

If issues occur:
1. Disable local cron job
2. Revert GitHub Actions to hourly schedule
3. Restore original twitter_manager.py

## Maintenance

Regular tasks:
1. Monitor log files
2. Check execution history
3. Verify both systems are complementing each other
4. Update dependencies as needed