# 📖 RollCall User Guide

## Quick Start Guide for school students & Administrators

---

## 👥 For school students

### How to Register (First Time Only)

1. **Visit the Website**
   - Go to: https://attedance-web-app.onrender.com/
   - Click **"Register as student"**

2. **Fill Out Registration Form**
   - Enter your full name
   - Enter your phone number (important!)
   - Create a username and password
   - Provide additional information (optional but helpful):
     - Date of birth
     - Gender
     - Email address

3. **Submit & Confirm**
   - Click **"Sign Up"**
   - You're now registered! ✅

---

### How to Mark Attendance

1. **Go to Attendance Page**
   - Visit: https://attedance-web-app.onrender.com/
   - Or click **"Mark Attendance"** from menu

2. **Select Your class**
   - Choose the class you're attending (e.g., "Sunday class", "Bible Study")

3. **Enter class Code**
   - Look for the code displayed at the school venue
   - Code is typically shown on screen/banner
   - Example: "SUN2025" or "WED123"

4. **Search for Your Name**
   - Start typing your name in the search box
   - Click your name when it appears

5. **Submit**
   - Click **"Mark Attendance"**
   - You'll see a confirmation message ✅

**Done!** Your attendance has been recorded.

---

### Frequently Asked Questions (students)

**Q: I forgot my password. What do I do?**
A: Contact your school administrator to reset it.

**Q: What if I don't have a smartphone?**
A: Visit the attendance desk at school - volunteers will help you check in.

**Q: The class code isn't working. Why?**
A: Make sure you're selecting the correct class and entering the code exactly as shown. Codes are case-sensitive.

**Q: Can I mark attendance for my family?**
A: Each family student should register separately and mark their own attendance.

**Q: What if I forget to mark attendance?**
A: Contact your school administrator after the class - they can manually add you.

---

## 👨‍💼 For school Administrators

### Admin Dashboard Overview

After logging in as admin, you'll see:
- **Dashboard**: Quick overview of today's attendance
- **Mark Attendance**: Manually mark students present
- **Offline Mode**: Mark attendance without internet
- **Manage students**: View and edit student profiles
- **Today's Attendance**: See who attended today
- **Summary**: Reports and statistics
- **Settings**: Manage classs and admin users
- **Geolocation** (NEW!): Location analytics and tracking
- **Site Locations** (NEW!): Manage geofenced check-in zones

---

### 🌍 How to Use Geolocation Features (NEW!)

#### Setting Up Geofences (Restricted Check-in Areas)

1. **Go to Site Locations**
   - Navigate to: `/admin/geofences/`
   - Or click **"Site Locations"** in sidebar

2. **Add a New Location**
   - Click **"Add Location"**
   - Use Google Maps to select your school location:
     - Click on the map OR
     - Click **"Get My Location"** for GPS accuracy
   - Set the check-in radius (e.g., 100m)
   - Fill in location details

3. **Fine-Tune Location**
   - Switch to **Satellite/Hybrid** view for precision
   - Drag the marker to adjust position
   - Zoom in for exact placement (e.g., Gidan Kwano, Minna)

4. **Configure Settings**
   - **Require GPS**: students must share location
   - **Allow Remote**: Allow check-ins outside geofence
   - **Active**: Enable/disable the location

#### Viewing Location Analytics

1. **Go to Geolocation Dashboard**
   - Navigate to: `/admin/geolocation/`
   - See all student locations on an interactive map

2. **Available Data**
   - Login locations (GPS + IP-based)
   - Attendance check-in locations
   - Inside/outside geofence statistics
   - Location accuracy indicators

3. **View Individual History**
   - Click on any student
   - See their complete location history
   - Track login patterns and locations

---

### How to Create a New class

1. **Go to Settings**
   - Click **"Settings"** in sidebar
   - Find **"school classs"** section

2. **Add class**
   - Click **"Add New class"**
   - Enter class name (e.g., "Sunday Worship", "Wednesday Bible Study")
   - Generate a unique code (e.g., "SUN2025")
   - Click **"Save"**

3. **Display Code at Venue**
   - Show the code on screen/banner during class
   - students will use this code to mark attendance

---

### How to Use Offline Mode (No Internet!)

**Perfect for schooles with poor internet connection**

#### Preparation (At Home, While Online):
1. **Open Offline Mode**
   - Go to Dashboard → Click **"Offline Mode"**
   - Page will load all student data

2. **Keep Browser Open**
   - Don't close the tab/browser
   - Take your device to school

#### At school (No Internet Needed):
1. **Select class**
   - Choose today's class from dropdown

2. **Search students**
   - Type student name or phone number
   - Click on student to select

3. **Mark Present**
   - Click **"Mark Present"**
   - student is saved locally on your device

4. **Repeat**
   - Continue marking all attendees

#### After class (Back Online):
1. **Click "Sync Now"**
   - All offline attendance uploads to server
   - You'll see confirmation: "15 records synced ✅"

**Pro Tip:** Always pre-load the offline page before leaving for school!

---

### How to View Reports

1. **Today's Attendance**
   - Click **"Today's Attendance"** in sidebar
   - See list of all attendees today
   - Export as CSV for Excel

2. **Summary & Analytics**
   - Click **"Summary"** in sidebar
   - View charts and trends:
     - Attendance over time
     - Top attendees
     - First-time visitors
     - Upcoming birthdays

3. **Export Data**
   - Click **"Export CSV"** button
   - Open in Excel/Google Sheets

---

### How to Manage students

1. **View All students**
   - Click **"Manage students"** in sidebar

2. **Edit student Info**
   - Click **"Edit"** button next to student name
   - Update information
   - Click **"Save"**

3. **Remove student**
   - Click **"Remove"** button
   - Confirm deletion
   - ⚠️ This cannot be undone

---

### How to Add Admin Users

**Note:** Only super admins can add new admins

1. **Go to Settings**
   - Click **"Settings"** → **"Admin Management"**

2. **Add New Admin**
   - Click **"Add Admin"**
   - Enter username and email
   - Set password
   - Click **"Create"**

---

## 🔒 Security & Privacy

### Data Protection
- All passwords are encrypted (hashed)
- HTTPS encryption for all connections
- Session expires after 24 hours of inactivity
- Admin access only for authorized users

### What Data We Collect
- Name, phone number, email (optional)
- Attendance records (date, time, class)
- Date of birth and gender (optional)
- **GPS Location Data** (when granted permission):
  - Latitude/longitude coordinates during login
  - Location during attendance check-in
  - IP-based approximate location (city level)

### What We DON'T Collect
- Financial information
- Social security numbers
- Location data without user permission

---

## 📊 Best Practices

### For Admins:
✅ **Change class codes regularly** (weekly or per event)  
✅ **Review attendance reports** after each class  
✅ **Keep student data updated**  
✅ **Pre-load offline mode** before class  
✅ **Export backups** monthly  

### For students:
✅ **Mark attendance within 24 hours** of class  
✅ **Keep your profile updated** (phone, email)  
✅ **Use strong passwords**  
✅ **Log out on shared devices**  

---

## 🆘 Troubleshooting

### Website Won't Load
- Check your internet connection
- Clear browser cache
- Try a different browser
- Wait 30 seconds (Render may be waking up)

### Can't Login
- Verify username/password
- Check CAPS LOCK is off
- Contact administrator to reset password

### Attendance Not Showing
- Wait 1-2 minutes for sync (if using offline mode)
- Refresh the page
- Check if you selected correct class

### Offline Mode Not Working
- Ensure you loaded the page while online first
- Don't close browser tab
- Check browser local storage isn't cleared

---

## 📞 Support

**Need Help?**
- Contact your school administrator
- Email: [your-school-email@example.com]
- Phone: [school-phone-number]

**Report Issues:**
- Technical problems: debugayo@github.com
- Feature requests: Use GitHub Issues

---

## 🔄 Version & Updates

**Current Version:** 1.1.0  
**Last Updated:** January 2026

**Recent Updates:**
- ✅ Offline attendance mode
- ✅ Mobile-responsive design
- ✅ Improved security
- ✅ Automatic backups
- ✅ **GPS Geolocation Tracking** (NEW!)
- ✅ **Geofencing for Check-ins** (NEW!)
- ✅ **Google Maps Integration** (NEW!)
- ✅ **Location History Dashboard** (NEW!)

**Coming Soon:**
- SMS attendance support
- Push notifications
- Multi-language support
- Mobile app (PWA)

---

## 📱 Mobile Tips

### Best Experience on Phone:
- Use Chrome, Safari, or Firefox
- Add to home screen for app-like experience
- Allow notifications (coming soon)
- Keep app updated

### iOS Users:
Safari → Share → Add to Home Screen

### Android Users:
Chrome → Menu → Add to Home Screen

---

## 🎓 Training Videos (Coming Soon)

- How to Register (2 min)
- How to Mark Attendance (1 min)
- Admin Dashboard Tour (5 min)
- Offline Mode Tutorial (3 min)

---

**Thank you for using RollCall! 🙏**

*Making attendance tracking simple, efficient, and reliable for schooles worldwide.*
