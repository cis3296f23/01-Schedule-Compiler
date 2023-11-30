class Schedule:
    def __init__(self):
        self.days = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
        }

    def add_item(self, day, start_time, end_time):
        if day not in self.days:
            print(f"Invalid day: {day}")
            return
        
        time_slot = (start_time, end_time)
        
        self.days[day].append(time_slot)