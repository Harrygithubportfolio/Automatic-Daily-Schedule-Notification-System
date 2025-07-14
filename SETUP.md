# 🚀 Complete Setup Tutorial

This guide will walk you through setting up your automated calendar notification system step by step.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] AWS Account with admin access
- [ ] Google Account with calendar data
- [ ] Pushover account ([sign up free](https://pushover.net))
- [ ] Apple Calendar synced to Google Calendar
- [ ] Python 3.9+ installed locally (for setup scripts)

## 🎯 Overview

The setup process involves:
1. **Pushover Setup** (5 minutes)
2. **Apple-Google Calendar Sync** (5 minutes)
3. **Google Calendar API Setup** (10 minutes)
4. **AWS Infrastructure Setup** (15 minutes)
5. **Webhook Configuration** (5 minutes)
6. **Testing & Validation** (5 minutes)

**Total Time: ~45 minutes**

---

## 📱 Step 1: Pushover Setup

### 1.1 Create Pushover Account
1. Go to [pushover.net](https://pushover.net)
2. **Sign up** for a free account
3. **Download Pushover app** on your phone
4. **Log in** to the app

### 1.2 Create Application
1. Go to [pushover.net/apps/build](https://pushover.net/apps/build)
2. **Create a New Application**:
   - **Name**: `Calendar Notifications`
   - **Type**: `Application`
   - **Description**: `Automated calendar reminders`
3. **Save your credentials**:
   - **App Token**: `your_app_token_here`
   - **User Key**: `your_user_key_here` (from main dashboard)

---

## 🔄 Step 2: Apple-Google Calendar Sync

### 2.1 On Mac
1. **System Settings** → **Internet Accounts**
2. **Add Google Account** (if not already added)
3. **Enable "Calendars"** ✅
4. **Open Calendar app** → **Calendar menu** → **Refresh Calendars**

### 2.2 On iPhone
1. **Settings** → **Calendar** → **Accounts**
2. **Add Google Account** (if not already added)
3. **Enable "Calendars"** ✅
4. **Open Calendar app** → **Pull down to refresh**

### 2.3 Verify Sync
1. **Create test event** in Apple Calendar
2. **Check [calendar.google.com](https://calendar.google.com)**
3. **Confirm event appears** in Google Calendar
4. **Delete test event**

> ⚠️ **Important**: When creating events in Apple Calendar, make sure you select your Google calendar from the dropdown, not local calendar.

---

## 🔧 Step 3: Google Calendar API Setup

### 3.1 Create Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. **Create New Project**:
   - **Name**: `Calendar Notifications`
   - **Click "Create"**

### 3.2 Enable Calendar API
1. **APIs & Services** → **Library**
2. **Search**: `Google Calendar API`
3. **Click** on Google Calendar API
4. **Click "Enable"**

### 3.3 Configure OAuth Consent Screen
1. **APIs & Services** → **OAuth consent screen**
2. **Choose "External"** (unless you have Google Workspace)
3. **Fill required fields**:
   - **App name**: `Calendar Notifications`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. **Save and Continue** through all steps
5. **Add test user**: Your email address

### 3.4 Create OAuth Credentials
1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. **Application type**: `Desktop application`
4. **Name**: `Calendar Notifications Desktop`
5. **Click "Create"**
6. **Download JSON file** → Save as `credentials.json`

### 3.5 Generate OAuth Tokens
1. **Install Python dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Run the credential generator**:
   ```bash
   python setup/generate_google_credentials.py
   ```

3. **Follow prompts**:
   - Browser will open for Google authentication
   - Authorize the application
   - **Copy the base64 credentials** output

---

## ☁️ Step 4: AWS Infrastructure Setup

### 4.1 Create DynamoDB Table
1. **Go to DynamoDB Console**
2. **Create table**:
   - **Table name**: `calendar-webhook-info`
   - **Partition key**: `id` (String)
   - **Use default settings**
3. **Click "Create table"**

### 4.2 Create EventBridge Scheduler Role
1. **Go to IAM** → **Roles**
2. **Create role**:
   - **Custom trust policy**:
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
3. **Create policy** for Lambda invocation:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "lambda:InvokeFunction"
         ],
         "Resource": "arn:aws:lambda:*:*:function:schedule-notifier"
       }
     ]
   }
   ```
4. **Attach policy** to role
5. **Role name**: `EventBridge-Scheduler-Lambda-Role`
6. **Save role ARN**: `arn:aws:iam::YOUR_ACCOUNT:role/EventBridge-Scheduler-Lambda-Role`

### 4.3 Create Lambda Function
1. **Go to Lambda Console**
2. **Create function**:
   - **Author from scratch**
   - **Function name**: `schedule-notifier`
   - **Runtime**: `Python 3.9`
   - **Create function**

### 4.4 Configure Lambda Function
1. **Replace function code** with content from `lambda/lambda_function.py`
2. **Configuration** → **General configuration**:
   - **Timeout**: `2 minutes`
   - **Memory**: `512 MB`
3. **Configuration** → **Environment variables**:
   ```
   GOOGLE_CALENDAR_CREDENTIALS = [your_base64_credentials_from_step_3.5]
   PUSHOVER_TOKEN = [your_pushover_app_token]
   PUSHOVER_USER = [your_pushover_user_key]
   AWS_ACCOUNT_ID = [your_aws_account_id]
   SCHEDULER_ROLE_ARN = [role_arn_from_step_4.2]
   ```

### 4.5 Create Lambda Function URL
1. **Configuration** → **Function URL**
2. **Create function URL**:
   - **Auth type**: `NONE`
   - **CORS**: Enable
   - **Allow origin**: `*`
   - **Allow headers**: `Content-Type, X-Goog-Channel-ID, X-Goog-Resource-State`
   - **Allow methods**: `GET, POST`
3. **Save function URL**: `https://xyz.lambda-url.region.on.aws/`

### 4.6 Update Lambda Environment Variables
Add the Lambda Function URL:
```
LAMBDA_WEBHOOK_URL = [your_function_url_from_step_4.5]
```

### 4.7 Add IAM Permissions
1. **Configuration** → **Permissions**
2. **Click on execution role**
3. **Add permissions** → **Attach policies**:
   - `AmazonEventBridgeSchedulerFullAccess`
4. **Add inline policy** for DynamoDB:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "dynamodb:PutItem",
           "dynamodb:GetItem",
           "dynamodb:UpdateItem",
           "dynamodb:DeleteItem"
         ],
         "Resource": "arn:aws:dynamodb:region:account:table/calendar-webhook-info"
       }
     ]
   }
   ```

### 4.8 Create Daily Schedule
1. **Go to EventBridge** → **Schedules**
2. **Create schedule**:
   - **Name**: `daily-schedule-notification`
   - **Schedule expression**: `cron(0 8 * * ? *)`
   - **Timezone**: `(UTC+01:00) Europe/London`
   - **Target**: Your Lambda function
3. **Create schedule**

---

## 🔗 Step 5: Webhook Configuration

### 5.1 Set Up Google Calendar Webhook
1. **Run the webhook setup script**:
   ```bash
   python setup/setup_webhook.py
   ```
2. **Enter your Lambda Function URL** when prompted
3. **Verify successful setup**

---

## 🧪 Step 6: Testing & Validation

### 6.1 Test Lambda Function
1. **Go to Lambda** → **Test**
2. **Create test event**:
   ```json
   {
     "test": true,
     "source": "manual-test"
   }
   ```
3. **Run test** → Should see success with reminders created

### 6.2 Test Daily Summary
1. **Should receive Pushover notification** with today's schedule
2. **Check EventBridge** → **Schedules** for reminder schedules

### 6.3 Test Real-time Updates
1. **Create event** in Apple Calendar for tomorrow
2. **Wait 30 seconds** for sync
3. **Check Lambda CloudWatch logs** for webhook activity
4. **Should receive**: "Calendar Updated" notification

### 6.4 Test Event Reminders
1. **Create event** 45 minutes from now
2. **Wait for reminder creation**
3. **Should receive reminder** 30 minutes before event

---

## 🎯 Verification Checklist

- [ ] Daily summary received at 8 AM
- [ ] Events show correct times (timezone)
- [ ] Real-time webhook updates working
- [ ] 30-minute reminders being created
- [ ] All notifications reaching your devices

---

## 🔧 Troubleshooting

### No Events Found
- **Check**: Apple Calendar → Google Calendar sync
- **Solution**: Verify calendar selection when creating events

### Webhook Not Triggering
- **Check**: CloudWatch logs for webhook activity
- **Solution**: Verify Function URL is public and CORS enabled

### Permission Errors
- **Check**: IAM roles have correct policies
- **Solution**: Review all permissions in Step 4.7

### Wrong Times
- **Check**: Timezone configuration
- **Solution**: System uses London timezone by default

### Webhook Expires
- **Check**: System auto-renews webhooks
- **Solution**: Manual renewal with setup script if needed

---

## 💡 Pro Tips

1. **Use Google Calendar** as default when creating events
2. **Monitor CloudWatch logs** for debugging
3. **Test with future events** (>30 minutes away)
4. **Check webhook expiry** in daily logs
5. **Backup your environment variables**

---

## 🎉 Success!

Your automated calendar notification system is now live! You'll receive:

- **8 AM daily**: Complete schedule summary
- **30 minutes before events**: Individual reminders
- **Real-time**: Updates when calendar changes
- **Weekly**: Automatic system maintenance

**Enjoy never missing another meeting! 🚀**

---

## 📞 Support

If you encounter issues:

1. **Check CloudWatch logs** for detailed error messages
2. **Verify all environment variables** are set correctly
3. **Review IAM permissions** for all services
4. **Test individual components** (sync, webhook, reminders)

For additional help, open an issue on GitHub with your CloudWatch logs and configuration details (remove any sensitive information).