import pyodbc
print("Drivers available:")
for driver in pyodbc.drivers():
    print("-", driver)
