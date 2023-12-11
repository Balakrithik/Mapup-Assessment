import pandas as pd
import numpy as np
from datetime import datetime, timedelta

df = pd.read_csv(r"C:\Users\Ryze\OneDrive\Desktop\Mapup assessment\MapUp-Data-Assessment-F-main\datasets\dataset-1.csv")
df2 = pd.read_csv(r"C:\Users\Ryze\OneDrive\Desktop\Mapup assessment\MapUp-Data-Assessment-F-main\datasets\dataset-2.csv")

def generate_car_matrix(df):
    """
    Creates a DataFrame for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values,
        where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Create a new DataFrame with 'id_2' as columns and 'id_1' as index
    car_matrix = df.pivot_table(
        index="id_1", columns="id_2", values="car", fill_value=0
    )

    # Set diagonal values to 0
    car_matrix.values[:: len(car_matrix) + 1] = 0

    return car_matrix

car_matrix = generate_car_matrix(df.copy())
print(car_matrix)

def get_type_count(df):
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Define type categories
    type_categories = {
        "low": (df["car"] <= 15),
        "medium": ((df["car"] > 15) & (df["car"] <= 25)),
        "high": (df["car"] > 25),
    }

    # Create a new column 'car_type' based on the categories
    df["car_type"] = pd.cut(df["car"], bins=[-1, 15, 25, 100], labels=type_categories.keys())

    # Count occurrences of each car type
    type_counts = df["car_type"].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_counts = dict(sorted(type_counts.items()))

    return sorted_type_counts

type_counts = get_type_count(df.copy())
print(type_counts)

def get_bus_indexes(df):
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    mean_bus_value = df['bus'].mean()
    bus_indexes = df[df['bus'] > 2 * mean_bus_value].index.tolist()
    bus_indexes.sort()

    return bus_indexes
# Call the function and print the result
bus_indexes = get_bus_indexes(df.copy())
print(bus_indexes)


def filter_routes(df):
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Calculate average 'truck' values per route
    avg_truck_route = df.groupby("route")["truck"].mean()

    # Filter routes with average 'truck' greater than 7
    filtered_routes = avg_truck_route[avg_truck_route > 7]

    # Return the sorted list of filtered route names
    return sorted(filtered_routes.index.to_list())

# Call the function and print the result
filtered_routes = filter_routes(df.copy())
print(filtered_routes)


def multiply_matrix(matrix):
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Define multiplication factors based on condition
    factors = {True: 0.75, False: 1.25}

    # Create a mask where values are greater than 20
    mask = matrix > 20

    # Apply multiplication factor based on the mask
    multiplied_matrix = matrix.applymap(lambda x: x * factors[x > 20])

    # Round the values to one decimal place
    rounded_matrix = multiplied_matrix.round(1)

    return rounded_matrix
rounded_matrix = multiply_matrix(df.copy())
print(rounded_matrix)

def time_check(dataset):
    # Write your logic here
    df2['start_datetime'] = pd.to_datetime(df2['startDay'] + ' ' + df2['startTime'], errors='coerce')
    df2['end_datetime'] = pd.to_datetime(df2['endDay'] + ' ' + df2['endTime'], errors='coerce')
    time_completeness = df2.groupby(['id', 'id_2']).apply(lambda x: check_timestamps(x)).reset_index(drop=True)

    return time_completeness

def check_timestamps(group):
    min_datetime = group['start_datetime'].min()
    max_datetime = group['end_datetime'].max()

    if pd.notna(min_datetime) and pd.notna(max_datetime):
        correct_range = (min_datetime.time() == pd.Timestamp('00:00:00').time()) and \
                        (max_datetime.time() == pd.Timestamp('23:59:59').time()) and \
                        (min_datetime.day_name() == 'Monday') and \
                        (max_datetime.day_name() == 'Sunday')
    else:
        correct_range = False

    return not correct_range

dataset_path = 'dataset-2.csv'
result_completeness = time_check(dataset_path)
print(result_completeness)