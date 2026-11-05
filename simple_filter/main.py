import json
import os
import sys

DATA_FILENAME = "people.json"
DATA_KEYNAME = "people"

# Load the data from the JSON file

def load_data(fpath):
    """ loads data from the JSON file indicated """
    with open(fpath, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            return e

def do_clear():
    """ small utility to clear screen """
    os.system('cls' if os.name == 'nt' else 'clear')

#filter the data
def filter_data(age='', city='', name='', data_to_filter=None):
    """
    apply age, city and/or name filters to data_to_filter and return the filtered results
    """
    if (name == '' and age == '' and city == '') or data_to_filter is None:
        return []
    d = data_to_filter

    if age:
        d = filter_by_age(d,age)
    if name:
        d = filter_by_name(d,name.strip())
    if city:
        d = filter_by_city(d,city.strip())
    return d


def filter_by_age(data, age=''):  
    """
    filters in passed in data by age.  If a negative number is indicated, it looks for age <= n. 
    Positive , then looks for age >= n. if it's not a number then returns an empty array.
    """
    if age == '':
        # entered a blank value
        return data
    try:
        ageval = int(age)
    except ValueError:
        # entered a string value
        return []

    if ageval == 0:
        # entered 0
        return []


    results = []

    for person in data:
        try:
            if ageval > 0 and int(person["age"]) >= ageval:
                results.append(person)
            else:
                if int(person["age"]) <= -ageval:
                    results.append(person)
        except KeyError:
            continue
    
    return results

def filter_by_name(data,name=''):
    """ 
    filter data by the person's name, return results
    """

    if name != '':
        return [person for person in data if person["name"].casefold() == name.casefold()]
    return data

def filter_by_city(data,city=''):
    """ 
    filter data by the city name, return results 
    """
    if city != '':
        return [person for person in data if person["city"].casefold() == city.casefold()]
    return data


def main():
    """ 
    Load the data from the indicated filename.  filter the data according to the criteria passed in by inputs()
    Display the data returned, if any, to the user
    """
    do_clear()
    try:
        data = load_data(DATA_FILENAME)
        if not isinstance(data, dict):
            print("INVALID JSON FILE FORMAT!", data)
            sys.exit(1)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    while True:

        print("Search by age, name and/or city (leave blank for none)\n\n")
    
        try:
            age = input("Age:  ")
            name=input("Name:  ")
            city=input("City:  ")

            if age + name + city == '':
                print(f"\n\nNOTHING TO FILTER!  Please provide at least one criteria to search for.\n\n")
                do_clear()
                continue

            filtered_data = filter_data(age, city,name,data[DATA_KEYNAME])
        except KeyError as e:
            print(e)
            sys.exit(1)
        
        if filtered_data:
            do_clear()
            str_out = f"\n\nFound the following {len(filtered_data)} results:\n\n"
            for result in filtered_data:
                n = result['name']
                c = result['city']
                a = result['age']
                str_out += f"Name: {n}\nAge: {a}\nCity: {c}\n--------\n"
            print(str_out)
        else:
            print("No results matching that criteria.")

        do_another = input("Do another search? (press ENTER to continue, or 'X' to exit): ")
        if do_another.casefold() == 'x':
            sys.exit(0)


if __name__ == "__main__":
     main()  #run the main function