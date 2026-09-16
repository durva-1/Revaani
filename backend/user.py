class User:

    def __init__(self, email, full_name, region, age_group, gender="Not specified"):
        self.email = email
        self.full_name = full_name
        self.region = region
        self.age_group = age_group
        self.gender = gender
        self.points = 0
        self.is_admin = False

    def update_profile(self, full_name, region, age_group, gender):
        self.full_name = full_name
        self.region = region
        self.age_group = age_group
        self.gender = gender

    def add_points(self, points):
        self.points += points

    def display_user(self):
        print("Name:", self.full_name)
        print("Email:", self.email)
        print("Region:", self.region)
        print("Age Group:", self.age_group)
        print("Gender:", self.gender)
        print("Points:", self.points)
