def say_hello(name):
    return f"hello {name}! welcome to AURA !"

def add_numbers(a, b):
    return a + b

def get_day_motivation(name):
    return f"you've got this {name}! Keep building Aura"

def get_greeting(hour):
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    elif hour < 21:
        return "Good Evening"
    else:
        return "Good Night"