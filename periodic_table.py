import periodictable

atomic_no = int(input("Enter the atomic number:"))

element = periodictable.elements[atomic_no]
print("Name:", element.name)
print("Symbol:", element.symbol)
print("Atomic Mass:", element.mass)
print("Density:", element.density)
