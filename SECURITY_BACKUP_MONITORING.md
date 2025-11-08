# 🔐 Security, Backup & Monitoring Guide

## Security Measures Implemented

### ✅ Authentication & Authorization
- **Password Hashing**: PBKDF2 with SHA256 (Django default)
- **Minimum Password Length**: 8 characters
- **Password Complexity**: Must not be entirely numeric or common
- **Session Security**: HttpOnly cookies, 24-hour expiry
- **CSRF Protection**: Enabled on all forms
- **Login Required**: Decorators on sensitive views

### ✅ Network Security
- **HTTPS Only**: Render provides automatic SSL/TLS
- **Secure Headers**:
  - `X-Frame-Options: DENY` (Clickjacking protection)
  - `X-Content-Type-Options: nosniff` (MIME sniffing protection)
  - `X-XSS-Protection: 1; mode=block` (XSS filtering)
  - `Referrer-Policy: same-origin`
  - `HSTS` (HTTP Strict Transport Security)
- **Secure Cookies**: Session and CSRF cookies only sent over HTTPS

### ✅ Data Protection
- **SQL Injection**: Protected by Django ORM
- **XSS**: Template auto-escaping enabled
- **Input Validation**: Django forms validation
- **File Upload**: Not enabled (no upload vulnerabilities)

### ⚠️ Security Improvements Needed

**To implement later:**
1. **Rate Limiting**: Prevent brute force attacks
2. **Two-Factor Authentication (2FA)**: For admin accounts
3. **Email Verification**: Verify member email addresses
4. **Audit Logging**: Track admin actions
5. **API Authentication**: JWT tokens for future API

---

## 📦 Backup Strategy

### Automatic Backups (Render Database)

**PostgreSQL on Render:**
- Automatic daily backups (last 7 days on free tier)
- Point-in-time recovery
- Managed by Render

### Manual Backups (Recommended)

#### Daily Backup (Run this command):
```bash
python backup_database.py backup
```

#### Weekly Full Export:
```bash
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

#### Restore from Backup:
```bash
python backup_database.py restore --file backups/db_backup_20251108_120000.json
```

### Backup Schedule Recommendation

| Frequency | What | How |
|-----------|------|-----|
| **Daily** | Database snapshot | Automated script |
| **Weekly** | Full export | Manual export |
| **Monthly** | Download to external drive | Download from Render |
| **Before Updates** | Pre-deployment backup | Manual |

### Backup Storage

**Current:** Local backups folder (last 30 days)  
**Recommended:**
- Google Drive backup (free 15GB)
- Dropbox backup
- External hard drive (monthly)

---

## 📊 Logging & Monitoring

### Current Logging Setup

**Log Locations:**
- **Render Logs**: Dashboard → Logs tab
- **Local Logs**: `logs/django.log` (when running locally)

**What's Logged:**
- All HTTP requests
- Database queries (in DEBUG mode)
- Error messages and stack traces
- Security warnings
- Admin actions

### How to View Logs

#### On Render:
1. Go to Render Dashboard
2. Click your web service
3. Click **"Logs"** tab
4. Search/filter logs

#### Locally:
```bash
tail -f logs/django.log
```

### Log Levels

| Level | What It Means | Action Required |
|-------|---------------|-----------------|
| **DEBUG** | Detailed info | None (dev only) |
| **INFO** | General events | None |
| **WARNING** | Something unusual | Review |
| **ERROR** | Something failed | Investigate |
| **CRITICAL** | System failure | **Urgent!** |

### Monitoring Checklist

**Daily:**
- [ ] Check Render dashboard for uptime
- [ ] Review error logs (if any)

**Weekly:**
- [ ] Check database size (Render dashboard)
- [ ] Review slow queries
- [ ] Check disk space usage

**Monthly:**
- [ ] Review security logs
- [ ] Check for Django/package updates
- [ ] Verify backups are working

---

## 🚨 Alerting & Error Handling

### Render Built-in Monitoring

**What Render Monitors:**
- ✅ Service uptime/downtime
- ✅ Memory usage
- ✅ CPU usage
- ✅ Response times

**Email Alerts:**
- Automatic email when service crashes
- Configure in Render Dashboard → Notifications

### Custom Error Notifications

**To Add Later:**
1. **Sentry** (Error tracking)
   - Real-time error notifications
   - Stack traces
   - User impact tracking

2. **UptimeRobot** (Uptime monitoring)
   - Ping every 5 minutes
   - Email/SMS alerts
   - Free tier available

3. **Django Admin Emails**
   - Email admins on 500 errors
   - Already configured in settings

---

## 📈 Performance Monitoring

### Current Optimizations

✅ **Database:**
- Connection pooling (CONN_MAX_AGE = 600)
- Indexed fields (phone, timestamp)
- Query optimization with `select_related()` and `prefetch_related()`

✅ **Static Files:**
- WhiteNoise for efficient serving
- Compression enabled
- Browser caching

✅ **Sessions:**
- Cached sessions
- Local memory cache

### Performance Metrics to Track

**Response Times:**
- Login page: < 500ms (target)
- Dashboard: < 1s (target)
- Attendance submission: < 300ms (target)

**Database:**
- Query count per page: < 20 (target)
- Slow queries: None > 100ms (target)

---

## 🔍 Audit Trail

### What's Tracked

Currently:
- Login/logout events (Django default)
- Password changes
- Admin actions (Django admin history)

### To Implement:

**Admin Audit Log:**
```python
# Log when admin adds/edits/deletes members
# Log when admin changes service codes
# Log when admin exports data
```

**Usage:**
```bash
# View recent admin actions
python manage.py shell
>>> from django.contrib.admin.models import LogEntry
>>> LogEntry.objects.all()[:10]
```

---

## 🛡️ Security Best Practices

### For Administrators:

1. **Strong Passwords**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols
   - Use password manager

2. **Regular Updates**
   - Check for Django security patches
   - Update packages monthly
   - Review changelog before updating

3. **Access Control**
   - Don't share admin credentials
   - Create separate accounts for each admin
   - Remove inactive admin accounts

4. **Data Handling**
   - Don't export sensitive data to insecure locations
   - Delete old backups securely
   - Use encrypted connections only

### For Deployment:

1. **Environment Variables**
   - Never commit SECRET_KEY to Git
   - Use Render environment variables
   - Rotate keys annually

2. **Database**
   - Use PostgreSQL (not SQLite) in production
   - Enable automatic backups
   - Restrict database access

3. **Dependencies**
   - Pin exact versions in requirements.txt
   - Review dependencies for vulnerabilities
   - Use `pip-audit` to scan packages

---

## 📋 Incident Response Plan

### If Service Goes Down:

1. **Check Render Status**
   - Go to Render Dashboard
   - Check service status
   - View recent logs

2. **Check Recent Changes**
   - Review last deployment
   - Check git commits
   - Rollback if needed

3. **Review Logs**
   - Look for error messages
   - Check database connection
   - Verify environment variables

4. **Contact Support**
   - Render support (for platform issues)
   - Developer (for code issues)

### If Data is Lost:

1. **Don't Panic**
   - Stop all write operations
   - Assess extent of loss

2. **Restore from Backup**
   ```bash
   python backup_database.py restore --file <latest_backup>
   ```

3. **Verify Restoration**
   - Check member count
   - Verify recent attendance
   - Test functionality

4. **Investigate Cause**
   - Review logs
   - Check for bugs
   - Document incident

---

## ✅ Deployment Checklist

**Before Every Deployment:**
- [ ] Create backup
- [ ] Run tests locally
- [ ] Check for migrations
- [ ] Review changed files
- [ ] Test on local server
- [ ] Check environment variables
- [ ] Verify static files collected

**After Deployment:**
- [ ] Check logs for errors
- [ ] Test login functionality
- [ ] Test attendance marking
- [ ] Verify database connection
- [ ] Check mobile responsiveness
- [ ] Monitor for 30 minutes

---

## 🎓 Training & Documentation

### For New Admins:

1. **Read USER_GUIDE.md**
2. **Watch demo (if available)**
3. **Practice on test data**
4. **Shadow experienced admin**
5. **Get credentials**

### For Members:

1. **Welcome email with instructions**
2. **Link to USER_GUIDE.md**
3. **Demo at church service**
4. **Help desk at church**

---

## 📞 Emergency Contacts

**Service Down:**
- Render Support: support@render.com
- Developer: [Your contact]

**Data Issues:**
- Database Admin: [Contact]
- Church IT: [Contact]

**Security Incident:**
- Report immediately to developer
- Change all passwords
- Review access logs

---

## 🔄 Regular Maintenance Tasks

### Daily (Automated):
- Database backup
- Log rotation
- Cache clearing

### Weekly (Manual):
- Review error logs
- Check backup status
- Monitor disk space

### Monthly (Manual):
- Update dependencies
- Security audit
- Performance review
- Download backups to external drive

### Quarterly (Manual):
- Rotate SECRET_KEY
- Review user accounts
- Test disaster recovery
- Update documentation

---

## 📊 Success Metrics

Track these over time:

**Reliability:**
- Uptime %: Target 99.5%+
- Average response time: Target < 500ms
- Error rate: Target < 0.1%

**Usage:**
- Daily active users
- Attendance mark rate
- Member growth
- Admin actions

**Security:**
- Failed login attempts
- Suspicious activity
- Vulnerability patches applied

---

**This guide should be reviewed and updated quarterly.**

Last Updated: November 2025  
Next Review: February 2026
