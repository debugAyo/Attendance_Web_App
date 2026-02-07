# RollCall - Step-by-Step Attendance Marking Guide

---

## 📱 For students: How to Mark Attendance

### Method 1: Quick Check-In (Recommended)

**Step 1: Get the class Code**
- The class code will be displayed during the school class
- It's usually shown on the screen or announced by the usher/pastor
- Example code: `SUN-001` or `WED-BIBLE-2024`

**Step 2: Open RollCall**
- Open your web browser (Chrome, Safari, Firefox, etc.)
- Go to: `https://attedance-web-app.onrender.com/`
- Or scan the QR code if provided

**Step 3: Enter Your Information**
- **Name**: Type your full name (e.g., "John Doe")
- **Phone Number**: Enter your phone number (e.g., "08012345678")
- **class Code**: Enter the code announced/displayed (e.g., "SUN-001")

**Step 4: Submit**
- Click the **"Mark Attendance"** button
- You'll see a success message: "Attendance marked successfully!"
- That's it! You're done! ✅

**⏱️ Total Time: Under 10 seconds!**

---

## 💻 For Administrators: How to Mark Attendance

### Option 1: students Mark Their Own Attendance

**Admin Preparation:**

**Step 1: Create a class**
1. Log in to admin dashboard: `https://attedance-web-app.onrender.com/login/`
2. Click **"Settings"** in the sidebar
3. Scroll to **"school classs"** section
4. Click **"Add New class"**
5. Fill in:
   - **class Name**: E.g., "Sunday class"
   - **class Code**: Create a unique code (e.g., "SUN-NOV-10")
6. Click **"Save"**

**Step 2: Display the class Code**
1. Project the code on the screen during class, OR
2. Write it on a whiteboard, OR
3. Have ushers announce it

**Step 3: Let students Check In**
- students use their phones to mark attendance (see "For students" section above)
- You can monitor attendance in real-time from the dashboard

**Step 4: View Results**
1. Go to **"Dashboard"** or **"Today's Attendance"**
2. See all students who checked in
3. Review the list for accuracy

---

### Option 2: Admin Marks Attendance Manually

**When to Use:**
- students don't have phones
- Internet is down
- Marking attendance for children
- Correcting mistakes

**Step 1: Go to Mark Attendance Page**
1. Log in to admin dashboard
2. Click **"Mark Attendance"** in the sidebar (or **"Offline Mode"**)

**Step 2: Select class**
- Choose the class from the dropdown
- Example: "Sunday class - SUN-NOV-10"

**Step 3: Mark students Present**

**Option A: Select from Existing students**
1. You'll see a list of all registered students
2. Check the boxes next to students who are present
3. Click **"Submit Attendance"**

**Option B: Quick Add (For First-Timers)**
1. If someone is not in the system yet
2. Use the **"Quick Add"** form
3. Enter:
   - Name
   - Phone number
   - (Optional) Email, gender, date of birth
4. Click **"Add & Mark Present"**

**Step 4: Save**
- Click **"Save Attendance"** or **"Submit"**
- You'll see a confirmation message
- Attendance is now recorded!

---

### Option 3: Offline Mode (No Internet Required)

**When to Use:**
- Internet connection is unstable
- During outdoor classs
- Remote locations

**Step 1: Activate Offline Mode**
1. Log in to admin dashboard
2. Click **"Offline Mode"** in the sidebar
3. The page will load all student data into your browser

**Step 2: Select class**
- Choose the class you're marking attendance for

**Step 3: Mark students Present**
- Search for students by name or phone
- Click to select each person who is present
- Selected students will be highlighted

**Step 4: Sync When Online**
- When internet is restored, click **"Sync Now"**
- All attendance records will be uploaded
- You'll see: "Attendance synced successfully!"

---

### Option 4: GPS Geofencing (NEW! - Prevent Fake Check-ins)

**What is Geofencing?**
- Define a virtual boundary around your school
- students must be physically inside this boundary to check in
- Uses precise GPS coordinates (99% accuracy)
- Prevents people from marking attendance from home

**Step 1: Set Up a Geofence**
1. Go to **"Site Locations"** in admin sidebar
2. Click **"Add Location"**
3. Use Google Maps to select your school:
   - Click directly on the map, OR
   - Click **"Get My Location"** for GPS accuracy
4. Set the radius (e.g., 100 meters)
5. Enable **"Require GPS"** option
6. Click **"Save"**

**Step 2: Fine-Tune Location**
- Switch to **Satellite** or **Hybrid** view
- Zoom in for precision (buildings clearly visible)
- Drag the marker to exact position
- Adjust radius as needed

**Step 3: How students Check In**
1. student opens attendance page on their phone
2. Browser asks for location permission → Allow
3. GPS verifies they're within the geofence radius
4. If inside: Check-in allowed ✅
5. If outside: Check-in blocked ❌

**Step 4: View Location Analytics**
1. Go to **"Geolocation"** in admin sidebar
2. See all check-in locations on a map
3. View statistics: inside vs outside geofence
4. Click on individual students to see history

**Pro Tips:**
- Set radius to ~100m for typical school buildings
- Use satellite view for precise placement
- Test by checking in yourself first
- Review location analytics weekly

---

## 👨‍💼 Admin Dashboard Overview

### Daily Routine (5 minutes)

**Morning Before class:**
1. ✅ Create today's class with unique code
2. ✅ Display class code for students
3. ✅ Ensure internet connection is stable

**During class:**
1. ✅ Monitor attendance in real-time (optional)
2. ✅ Help students who have issues checking in

**After class:**
1. ✅ Review "Today's Attendance" list
2. ✅ Mark any missed students manually if needed
3. ✅ Check for first-time visitors

**Weekly Review:**
1. ✅ View attendance trends in Dashboard
2. ✅ Check "Absentee Alert" for students to follow up
3. ✅ Contact inactive students (30+ days absent)

---

## 🎯 Best Practices

### For Smooth Attendance Tracking:

**1. Consistent class Codes**
- Use a clear naming pattern
- Example: `SUN-NOV-10`, `WED-NOV-13`
- Avoid confusing codes like `123ABC`

**2. Display Code Prominently**
- Show it on the screen for at least 5 minutes
- Repeat the announcement
- Have it ready before class starts

**3. Train Ushers**
- Ushers should know how to help students
- Have printed instructions available
- Designate a "tech helper" for questions

**4. Timing**
- Open attendance marking 15 minutes before class
- Keep it open during class
- Close it 30 minutes after class ends

**5. Follow Up**
- Review attendance same day
- Contact absent students within 48 hours
- Use the built-in contact buttons (Call/Email/SMS)

**6. Set Up Geofences (NEW!)**
- Define check-in zones around your school location
- Use Google Maps satellite view for precise placement
- Set appropriate radius (50-200m for typical school)
- Require GPS verification to prevent fake check-ins
- Review geolocation analytics weekly

---

## 🆘 Troubleshooting

### Common Issues & Solutions:

**Problem: "class code not recognized"**
- ✅ Solution: Check if class was created in admin panel
- ✅ Make sure code is typed exactly as created
- ✅ Codes are case-sensitive

**Problem: "Duplicate attendance error"**
- ✅ Solution: student already marked attendance
- ✅ They can only check in once per class
- ✅ Admin can delete and re-add if needed

**Problem: "Phone number already exists"**
- ✅ Solution: student is already registered
- ✅ They should use existing phone number
- ✅ Don't create duplicate profiles

**Problem: "Location permission denied" (NEW!)**
- ✅ Solution: Enable location classs in browser/device settings
- ✅ Use HTTPS (GPS requires secure connection)
- ✅ Try refreshing the page and allowing permission
- ✅ On mobile: Check app permissions for browser

**Problem: "Outside geofence - cannot check in" (NEW!)**
- ✅ Solution: Move closer to the school building
- ✅ Check if you're within the designated radius
- ✅ Contact admin if you believe you're inside the zone
- ✅ GPS may need a few seconds to get accurate position

**Problem: "Can't access the site"**
- ✅ Solution: Check internet connection
- ✅ Try a different browser
- ✅ Clear browser cache
- ✅ Use offline mode as backup

**Problem: "Forgot to mark attendance"**
- ✅ Solution: Admin can add manually
- ✅ Go to "Mark Attendance" page
- ✅ Select the student and past class
- ✅ Submit

---

## 📊 Viewing Attendance Reports

### Dashboard Metrics:

**1. Today's Attendance**
- See who checked in today
- View by class type
- Export to CSV for records

**2. Attendance Trends**
- Beautiful chart showing last 30 days
- Identify patterns (which days are highest)
- Track growth over time

**3. student Engagement**
- **Top Attendees**: Most faithful students
- **Absentees**: Missed 2+ consecutive classs
- **Inactive**: Not attended in 30+ days

**4. Demographics**
- Male vs Female ratio
- Children count (under 13)
- Visual pie chart

### Generate Reports:

**Export Options:**
1. Go to **"Manage students"**
2. Click **"Export to CSV"** button
3. Open in Excel or Google Sheets
4. Create custom reports as needed

---

## 🎓 Training New Admins

### Onboarding Checklist:

**Week 1: Learn the Basics**
- [ ] Log in and explore dashboard
- [ ] Create a test class
- [ ] Mark test attendance
- [ ] View reports

**Week 2: Practice**
- [ ] Create real class for Sunday
- [ ] Monitor attendance during class
- [ ] Review and correct attendance
- [ ] Export data to CSV

**Week 3: Advanced Features**
- [ ] Use offline mode
- [ ] Add new students
- [ ] Edit student profiles
- [ ] Create events on calendar

**Week 4: Full Independence**
- [ ] Run attendance completely independently
- [ ] Follow up with absent students
- [ ] Generate monthly reports
- [ ] Train another admin

---

## 📞 Support & Help

**Need Help?**
- Check this guide first
- Review video tutorials (if available)
- Contact: [Your Contact Info]
- Email: [Your Email]

**Feedback Welcome!**
- We're constantly improving RollCall
- Share suggestions for new features
- Report any bugs or issues
- Help us make it better!

---

## ✅ Quick Reference Card

**Print this and keep it handy:**

```
┌─────────────────────────────────────────┐
│      ROLLCALL QUICK REFERENCE          │
├─────────────────────────────────────────┤
│ student CHECK-IN:                        │
│ 1. Go to: attedance-web-app.onrender.com│
│ 2. Enter: Name + Phone + class Code  │
│ 3. Allow location permission (if asked)│
│ 4. Click "Mark Attendance"              │
│                                         │
│ ADMIN DASHBOARD:                        │
│ Login: attedance-web-app.onrender.com/login│
│                                         │
│ CREATE class:                         │
│ Settings → Add class → Save Code     │
│                                         │
│ VIEW ATTENDANCE:                        │
│ Dashboard → Today's Attendance          │
│                                         │
│ MARK MANUALLY:                          │
│ Mark Attendance → Select students        │
│                                         │
│ OFFLINE MODE:                           │
│ Offline Mode → Mark → Sync Later       │
│                                         │
│ GEOFENCING (NEW!):                      │
│ Site Locations → Add → Set on Map     │
│ Geolocation → View Analytics           │
└─────────────────────────────────────────┘
```

---

**Restudent: RollCall makes attendance tracking effortless! 🚀**
