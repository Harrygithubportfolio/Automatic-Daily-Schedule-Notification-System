# 🔧 Common Issues & Troubleshooting Guide

This comprehensive guide covers all common issues users encounter when setting up the Automated Calendar Notification System and how to resolve them.

---

## 📱 Apple Calendar Sync Issues

### ❌ **Issue: Events created in Apple Calendar don't appear in Google Calendar**

**Symptoms:**
- Create event in Apple Calendar but it doesn't show up on calendar.google.com
- Lambda function shows "0 events" even though you have events

**Root Cause:** Events are being created in local "Calendar" instead of Google calendar

**Solution:**
1. **Check calendar selection when creating events:**
   - **Mac**: Look for "Calendar" dropdown in event details → Select Google calendar
   - **iPhone**: Tap "Calendar" field → Select Google calendar (shows Gmail address)

2. **Set Google calendar as default:**
   - **Mac**: Calendar → Preferences → General → Default Calendar → Select Google
   - **iPhone**: Settings → Calendar → Default Calendar → Select Google

3. **Move existing events:**
   - **Mac**: Select event → Edit → Change Calendar field to Google
   - **iPhone**: Edit event → Calendar → Select Google calendar

### ❌ **Issue: Sync is very slow (takes minutes)**

**Symptoms:**
- Events eventually appear but take 5+ minutes
- Changes don't reflect immediately

**Solutions:**
1. **Enable Push sync (iPhone):**
   - Settings → Calendar → Accounts → Google → Calendar → Push (ON)

2. **Force refresh (Mac):**
   - Calendar menu → Refresh Calendars (or Cmd+R)

3. **Check internet connection:**
   - Ensure stable internet on both devices

### ❌ **Issue: Some events sync, others don't**

**Symptoms:**
- Inconsistent syncing behavior
- Only certain events appear in Google Calendar

**Solutions:**
1. **Check calendar selection for each event:**
   - Edit non-syncing events → Change calendar to Google

2. **Verify calendar visibility:**
   - Mac: View → Calendars → Ensure Google calendar is checked
   - iPhone: Calendar app → Calendars (bottom) → Ensure Google calendar is selected

### ❌ **Issue: Duplicate events appearing**

**Symptoms:**
- Same event appears multiple times
- Events in both local and Google calendars

**Solutions:**
1. **Disable duplicate calendar sources:**
   - Choose either iCloud OR Google, not both
   - System Settings → Internet Accounts → Disable calendar for unused account

2. **Clean up duplicates:**
   - Delete events from local calendar, keep only Google calendar events

---

## 🔐 Google Calendar API Issues

### ❌ **Issue: "OAuth client was not found" error**

**Symptoms:**
- Browser shows "The OAuth client was not found" when running credential generator
- Error 401: invalid_client

**Solutions:**
1. **Verify OAuth client type:**
   - Google Cloud Console → APIs & Services → Credentials
   - Must be "Desktop application", not "Web application"

2. **Check project settings:**
   - Ensure Google Calendar API is enabled
   - OAuth consent screen must be configured
   - Your email must be added as test user

3. **Re-download credentials:**
   - Download fresh credentials.json file
   - Ensure no typos in file path

### ❌ **Issue: "Access blocked" during OAuth flow**

**Symptoms:**
- Google shows "This app is blocked" message
- Cannot complete OAuth authorization

**Solutions:**
1. **Configure OAuth consent screen:**
   - Google Cloud Console → APIs & Services → OAuth consent screen
   - Choose "External" user type
   - Fill all required fields (app name, support email, developer email)

2. **Add yourself as test user:**
   - OAuth consent screen → Test users → Add your email

3. **Verify app status:**
   - Ensure app is not in "Needs verification" status for testing

### ❌ **Issue: "Insufficient permissions" for webhooks**

**Symptoms:**
- Webhook setup fails with permission errors
- "This app hasn't been verified by Google" warnings

**Solutions:**
1. **Use correct scopes:**
   ```
   https://www.googleapis.com/auth/calendar.readonly
   https://www.googleapis.com/auth/calendar.events.readonly
   ```

2. **Add your email as test user** (allows unverified app usage)

3. **Re-generate credentials** with webhook scopes included

---

## ☁️ AWS Lambda Issues

### ❌ **Issue: "Handler 'lambda_handler' missing" error**

**Symptoms:**
- Lambda test fails with Runtime.HandlerNotFound
- Function code appears to be uploaded correctly

**Solutions:**
1. **Check file name:**
   - File must be named exactly `lambda_function.py`
   - Function name must be exactly `lambda_handler`

2. **Verify function structure:**
   ```python
   def lambda_handler(event, context):
       # Your code here
   ```

3. **Check for syntax errors:**
   - Use online Python syntax checker
   - Look for missing colons, parentheses, indentation issues

### ❌ **Issue: "Module not found" errors**

**Symptoms:**
- ImportError for modules like google, boto3, requests
- Function fails during import phase

**Solutions:**
1. **Check runtime version:**
   - Use Python 3.9 or later
   - Some modules require specific Python versions

2. **For zoneinfo errors:**
   - Ensure using Python 3.9+ runtime
   - Don't use pytz (not available in Lambda)

3. **For Google modules:**
   - Use deployment package if needed
   - Or switch to simpler implementation

### ❌ **Issue: Environment variables not found**

**Symptoms:**
- "GOOGLE_CALENDAR_CREDENTIALS not found in environment"
- "PUSHOVER_TOKEN not found"

**Solutions:**
1. **Check variable names exactly:**
   ```
   GOOGLE_CALENDAR_CREDENTIALS
   PUSHOVER_TOKEN
   PUSHOVER_USER
   LAMBDA_WEBHOOK_URL
   SCHEDULER_ROLE_ARN
   AWS_ACCOUNT_ID
   ```

2. **Verify values are set:**
   - Configuration → Environment variables
   - No extra spaces or quotes
   - Base64 credentials properly formatted

3. **Test with simple print:**
   ```python
   print(f"Found {len(os.environ.keys())} environment variables")
   ```

---

## 🔗 Webhook Issues

### ❌ **Issue: "Webhook verification failed"**

**Symptoms:**
- Google Calendar webhook setup fails
- "Invalid webhook URL" errors

**Solutions:**
1. **Check Lambda Function URL:**
   - Must be publicly accessible (Auth type: NONE)
   - CORS must be enabled
   - Must start with https://

2. **Test endpoint manually:**
   ```bash
   curl -X POST "your-lambda-url" -d '{"test": true}'
   ```

3. **Check CORS settings:**
   - Allow origin: *
   - Allow methods: GET, POST
   - Allow headers: Content-Type, X-Goog-Channel-ID, X-Goog-Resource-State

### ❌ **Issue: Webhooks stop working after a week**

**Symptoms:**
- Real-time updates stop working
- No webhook logs in CloudWatch

**Solutions:**
1. **Check webhook expiry:**
   - Webhooks expire after 6 days
   - System should auto-renew them

2. **Manual renewal:**
   - Re-run setup_webhook.py script
   - Check DynamoDB for webhook info

3. **Verify auto-renewal system:**
   - Check daily Lambda logs for renewal messages
   - Ensure SCHEDULER_ROLE_ARN is correct

---

## 📅 EventBridge Scheduler Issues

### ❌ **Issue: "ValidationException" when creating schedules**

**Symptoms:**
- Error about execution role permissions
- "Role cannot be assumed by scheduler.amazonaws.com"

**Solutions:**
1. **Fix role trust policy:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "scheduler.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

2. **Check role permissions:**
   - Role must have lambda:InvokeFunction permission
   - Resource must match your Lambda function ARN

3. **Verify SCHEDULER_ROLE_ARN:**
   - Must be full ARN, not just role name
   - Format: `arn:aws:iam::ACCOUNT:role/ROLE_NAME`

### ❌ **Issue: Schedule name too long**

**Symptoms:**
- "Member must have length less than or equal to 64"
- EventBridge schedule creation fails

**Solutions:**
1. **Check Lambda function code:**
   - Ensure using shortened schedule names
   - Should be: `reminder-{timestamp}` not `reminder-{long_event_id}-{timestamp}`

2. **Update code if needed:**
   ```python
   schedule_name = f"reminder-{int(reminder_time.timestamp())}"
   ```

---

## 🔔 Pushover Issues

### ❌ **Issue: Notifications not received**

**Symptoms:**
- Lambda shows "notification sent successfully"
- No notifications on devices

**Solutions:**
1. **Check Pushover app:**
   - Ensure app is installed and logged in
   - Check notification settings in app
   - Verify device is online

2. **Test with simple message:**
   - Use Pushover website to send test message
   - Verify tokens are correct

3. **Check message limits:**
   - Free tier: 7,500 messages/month
   - Check your usage on Pushover dashboard

### ❌ **Issue: Wrong tokens or "invalid user/token"**

**Symptoms:**
- Pushover API returns 400 error
- "User identifier is invalid" messages

**Solutions:**
1. **Verify token vs user key:**
   - PUSHOVER_TOKEN = App Token (from your app)
   - PUSHOVER_USER = User Key (from main dashboard)

2. **Check for typos:**
   - Tokens are case-sensitive
   - No extra spaces or quotes

3. **Regenerate if needed:**
   - Create new application on Pushover
   - Use fresh tokens

---

## ⏰ Timezone Issues

### ❌ **Issue: Event times wrong (showing 1 hour off)**

**Symptoms:**
- 5 PM event shows as "16:00" in notifications
- Times consistently off by 1 hour

**Solutions:**
1. **Update Lambda function:**
   - Ensure using latest code with zoneinfo
   - Check timezone conversion logic

2. **Verify system timezone:**
   - Code should use Europe/London timezone
   - Check for British Summer Time handling

3. **Test with different times:**
   - Create events at various times
   - Verify both BST and GMT periods

---

## 🏥 General Debugging Steps

### 🔍 **Step 1: Check CloudWatch Logs**
1. **Go to CloudWatch** → **Log groups**
2. **Find** `/aws/lambda/schedule-notifier`
3. **Look for recent executions**
4. **Check for error messages**

### 🔍 **Step 2: Test Individual Components**
1. **Test Lambda function** with manual test event
2. **Test Google Calendar API** with setup script
3. **Test Pushover** with simple notification
4. **Test Apple-Google sync** with test event

### 🔍 **Step 3: Verify All Prerequisites**
- [ ] AWS account with proper permissions
- [ ] Google Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] Pushover account and app created
- [ ] Apple Calendar synced to Google
- [ ] All environment variables set

### 🔍 **Step 4: Check Integration Points**
1. **Apple Calendar** → Google Calendar sync
2. **Google Calendar** → Lambda webhook
3. **Lambda** → EventBridge schedules
4. **EventBridge** → Lambda reminders
5. **Lambda** → Pushover notifications

---

## 🆘 Getting Additional Help

### **Before Asking for Help:**
1. **Check this troubleshooting guide** first
2. **Review CloudWatch logs** for specific errors
3. **Test each component individually**
4. **Verify all setup steps** were completed

### **When Reporting Issues:**
1. **Include specific error messages** (remove sensitive info)
2. **Describe what you were trying to do**
3. **Share relevant CloudWatch logs**
4. **Mention which step failed**
5. **Include your AWS region and Python version**

### **Common Log Patterns to Look For:**
- ✅ `✅ Pushover notification sent successfully`
- ❌ `❌ Error getting calendar events:`
- ❌ `No Google Calendar credentials found`
- ❌ `Webhook verification failed`
- ❌ `ValidationException when calling CreateSchedule`

---

## 💡 Prevention Tips

### **Avoid Common Mistakes:**
1. **Always select Google calendar** when creating events in Apple Calendar
2. **Test each step** before moving to the next
3. **Keep backups** of your environment variables
4. **Monitor CloudWatch logs** regularly
5. **Test the system** with future events (>30 minutes away)

### **Best Practices:**
1. **Use consistent naming** for AWS resources
2. **Set up monitoring** for webhook expiry
3. **Test sync** after any Apple/Google account changes
4. **Keep credentials secure** (never commit to git)
5. **Document your specific configuration** for future reference

---

**Remember: Most issues are due to calendar selection or missing environment variables. Double-check these first!** 🎯