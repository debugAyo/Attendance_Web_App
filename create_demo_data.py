"""
Script to create demo data for local presentation
Run with: python create_demo_data.py
"""
import os
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rollcall_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from attendance.models import SchoolClass, MemberAttendance

def create_demo_data():
    print("Creating demo data with 180 members...")
    
    # Nigerian names - realistic mix
    first_names_male = [
        "Chukwuemeka", "Oluwaseun", "Adeyemi", "Tunde", "Kunle", "Femi", "Segun", "Bayo",
        "Chinedu", "Obinna", "Ikenna", "Nnamdi", "Emeka", "Chibueze", "Uchenna", "Kelechi",
        "Ayodeji", "Olumide", "Babatunde", "Adebayo", "Adeola", "Biodun", "Damilare", "Kehinde",
        "Ibrahim", "Musa", "Yusuf", "Abdullahi", "Suleiman", "Usman", "Aliyu", "Ahmad",
        "Emmanuel", "Samuel", "David", "Daniel", "Michael", "Joseph", "Peter", "Paul",
        "Victor", "John", "James", "Matthew", "Mark", "Andrew", "Stephen", "Philip",
        "Tobi", "Jide", "Wale", "Lanre", "Dare", "Yemi", "Sola", "Tayo", "Gbenga", "Rotimi"
    ]
    
    first_names_female = [
        "Chioma", "Ngozi", "Amaka", "Ifeoma", "Adaobi", "Chiamaka", "Nneka", "Chinwe",
        "Oluwakemi", "Funmilayo", "Temitope", "Adesuwa", "Yetunde", "Omolara", "Folake", "Bunmi",
        "Blessing", "Grace", "Faith", "Hope", "Mercy", "Joy", "Peace", "Patience",
        "Esther", "Ruth", "Deborah", "Mary", "Sarah", "Rebecca", "Rachel", "Hannah",
        "Aminat", "Zainab", "Hadiza", "Khadija", "Fatima", "Aisha", "Hauwa", "Ramatu",
        "Tolu", "Bisi", "Nike", "Titi", "Lola", "Sade", "Bimbo", "Bolanle", "Ronke", "Peju",
        "Chidinma", "Chinyere", "Uchechi", "Adanna", "Ifunanya", "Nkechi", "Ego", "Uzoma"
    ]
    
    last_names = [
        "Okafor", "Eze", "Nwosu", "Okonkwo", "Okeke", "Udeh", "Nnadi", "Okoli", "Nwachukwu", "Onyeka",
        "Adebayo", "Oluwole", "Ajayi", "Ogunleye", "Adeleke", "Oladipo", "Adeoye", "Akinsanya", "Bakare", "Taiwo",
        "Mohammed", "Abubakar", "Bello", "Sani", "Garba", "Yusuf", "Ibrahim", "Umar", "Aliyu", "Hassan",
        "Okonkwo", "Nwankwo", "Ugwu", "Ezeh", "Chukwu", "Ezeji", "Nwofor", "Agbo", "Agu", "Onyekwere",
        "Williams", "Johnson", "Okafor", "Peters", "George", "Thomas", "Paul", "Emmanuel", "Simon", "Moses",
        "Adewale", "Olabisi", "Omotola", "Akintunde", "Oyewole", "Ogundele", "Babajide", "Fashola", "Soyinka", "Ojo"
    ]
    
    # Generate 180 members
    members_data = []
    phone_start = 8012345000
    
    # Split: 90 males, 90 females
    for i in range(90):
        # Male member
        members_data.append({
            "name": f"{random.choice(first_names_male)} {random.choice(last_names)}",
            "phone": f"0{phone_start + i}",
            "gender": "M",
            "dob": f"{random.randint(1970, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })
        
        # Female member
        members_data.append({
            "name": f"{random.choice(first_names_female)} {random.choice(last_names)}",
            "phone": f"0{phone_start + 90 + i}",
            "gender": "F",
            "dob": f"{random.randint(1970, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })
    
    # Create members
    created_profiles = []
    print(f"\nCreating {len(members_data)} members...")
    for idx, data in enumerate(members_data, 1):
        # Check if profile already exists
        if not Profile.objects.filter(phone=data['phone']).exists():
            profile = Profile.objects.create(
                name=data['name'],
                phone=data['phone'],
                gender=data['gender'],
                date_of_birth=data['dob'],
                role='member'
            )
            created_profiles.append(profile)
            if idx % 20 == 0:
                print(f"  ✓ Created {idx}/{len(members_data)} members...")
        else:
            created_profiles.append(Profile.objects.get(phone=data['phone']))
    
    print(f"✓ Total members created: {len(created_profiles)}")
    
    # Create school classes
    services_data = [
        {"name": "Morning Assembly", "code": "MON"},
        {"name": "Mathematics Class", "code": "MAT"},
        {"name": "Science Practical", "code": "SCI"},
    ]
    
    created_services = []
    print("\nCreating school classes...")
    for data in services_data:
        service, created = SchoolClass.objects.get_or_create(
            code=data['code'],
            defaults={'name': data['name']}
        )
        if created:
            print(f"  ✓ Created class: {data['name']}")
        else:
            print(f"  ⊗ Class already exists: {data['name']}")
        created_services.append(service)
    
    # Create attendance records for the past 8 weeks
    print("\nCreating attendance records for past 8 weeks...")
    today = datetime.now().date()
    total_attendance = 0
    
    # Generate attendance for past 8 weeks (main assembly - high attendance)
    for week in range(8):
        attendance_date = today - timedelta(days=7 * week)
        
        # Monday Assembly: 70-85% attendance (126-153 students)
        num_attending = random.randint(126, 153)
        attending_members = random.sample(created_profiles, k=num_attending)
        
        for profile in attending_members:
            if not MemberAttendance.objects.filter(
                phone=profile.phone,
                service=created_services[0],
                timestamp__date=attendance_date
            ).exists():
                MemberAttendance.objects.create(
                    name=profile.name,
                    phone=profile.phone,
                    service=created_services[0],
                    service_code=created_services[0].code,
                    timestamp=datetime.combine(attendance_date, datetime.min.time())
                )
                total_attendance += 1
        
        print(f"  ✓ Assembly {attendance_date}: {len(attending_members)} students attended")
    
    # Add Mathematics Class attendance (40-55% attendance)
    for week in range(8):
        math_date = today - timedelta(days=7 * week + 2)
        num_attending = random.randint(72, 99)  # 40-55% of 180
        math_attendees = random.sample(created_profiles, k=num_attending)
        
        for profile in math_attendees:
            if not MemberAttendance.objects.filter(
                phone=profile.phone,
                service=created_services[1],
                timestamp__date=math_date
            ).exists():
                MemberAttendance.objects.create(
                    name=profile.name,
                    phone=profile.phone,
                    service=created_services[1],
                    service_code=created_services[1].code,
                    timestamp=datetime.combine(math_date, datetime.min.time())
                )
                total_attendance += 1
        
        print(f"  ✓ Mathematics {math_date}: {len(math_attendees)} students attended")
    
    # Add Science Practical attendance (30-45% attendance)
    for week in range(8):
        sci_date = today - timedelta(days=7 * week + 4)
        num_attending = random.randint(54, 81)  # 30-45% of 180
        sci_attendees = random.sample(created_profiles, k=num_attending)
        
        for profile in sci_attendees:
            if not MemberAttendance.objects.filter(
                phone=profile.phone,
                service=created_services[2],
                timestamp__date=sci_date
            ).exists():
                MemberAttendance.objects.create(
                    name=profile.name,
                    phone=profile.phone,
                    service=created_services[2],
                    service_code=created_services[2].code,
                    timestamp=datetime.combine(sci_date, datetime.min.time())
                )
                total_attendance += 1
        
        print(f"  ✓ Science {sci_date}: {len(sci_attendees)} students attended")
    
    print("\n" + "="*60)
    print("✓✓✓ DEMO DATA CREATED SUCCESSFULLY! ✓✓✓")
    print("="*60)
    print(f"📊 Total Students: {Profile.objects.filter(role='member').count()}")
    print(f"   - Male: {Profile.objects.filter(role='member', gender='M').count()}")
    print(f"   - Female: {Profile.objects.filter(role='member', gender='F').count()}")
    print(f"📚 Total Classes: {SchoolClass.objects.count()}")
    print(f"✅ Total Attendance Records: {MemberAttendance.objects.count()}")
    print("="*60)
    print("\n🚀 Ready for your presentation!")
    print("\n📋 Next steps:")
    print("  1. Run: python manage.py runserver")
    print("  2. Open: http://localhost:8000")
    print("  3. Login with: Debug_Ayo (or your local admin)")
    print("  4. Explore the dashboard - you'll see charts and statistics!")
    print("\n💡 Tip: The dashboard will show beautiful charts with this data!")

if __name__ == '__main__':
    create_demo_data()
