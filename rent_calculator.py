rent = int(input("Enter your hostel/flat rent = "))
food = int(input("Enter the amount of food ordered = "))
electricity_bill = int(input("Enter the total of electricity bill = "))
persons = int(input("Enter the number of persons living in room/flat = "))

output = (food + rent + electricity_bill) // persons

print("Each person will pay = ", output)
