import pandas as pd
import numpy as np
from datetime import datetime, timedelta

df = pd.read_csv(r"C:\Users\Ryze\OneDrive\Desktop\Mapup assessment\MapUp-Data-Assessment-F-main\datasets\dataset-3.csv")

def calculate_distance_matrix(df):
    """
    Calculates a distance matrix based on routes between toll locations.

    Args:
        df (pandas.DataFrame): Dataframe containing route information.

    Returns:
        pandas.DataFrame: Distance matrix with cumulative distances.
    """
    # Create an empty distance matrix with IDs as indices and columns
    distance_matrix = pd.DataFrame(index=df["id_start"].unique(), columns=df["id_end"].unique())

    # Fill the matrix with distances based on route information
    for row in df.itertuples():
        start_id, end_id, distance = row[1], row[2], row[3]
        distance_matrix.loc[start_id, end_id] = distance
        distance_matrix.loc[end_id, start_id] = distance

    # Update diagonal values to 0
    distance_matrix.fillna(0, inplace=True)

    # Update NaN values with cumulative distances (adding distances from intermediate points)
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix)):
            if pd.isna(distance_matrix.loc[i, j]):
                intermediate_routes = df[(df["id_start"] == i) & (df["id_end"] == j)]
                distance_matrix.loc[i, j] = sum(intermediate_routes["distance"])
                print(distance_matrix)

    return distance_matrix

def unroll_distance_matrix(df):
    """
    Unrolls a distance matrix into a DataFrame with start, end IDs, and distances.

    Args:
        df (pandas.DataFrame): Distance matrix.

    Returns:
        pandas.DataFrame: Unrolled DataFrame with columns 'id_start', 'id_end', and 'distance'.
    """
    # Create an empty DataFrame with desired columns
    unrolled_df = pd.DataFrame(columns=["id_start", "id_end", "distance"])

    # Iterate over each row of the distance matrix
    for i in range(len(df)):
        for j in range(len(df)):
            # Exclude diagonal elements (same start and end ID)
            if i != j:
                # Add a row with start, end ID, and distance values
                unrolled_df = unrolled_df.append(
                    {"id_start": i, "id_end": j, "distance": df.loc[i, j]}, ignore_index=True
                )

    return unrolled_df

def find_ids_within_ten_percentage_threshold(df, reference_id):
    """
    Finds IDs whose average distance falls within 10% of the reference ID's average.

    Args:
        df (pandas.DataFrame): Unrolled distance matrix.
        reference_id (int): Reference ID to compare against.

    Returns:
        pandas.DataFrame: DataFrame with IDs within the specified threshold.
    """
    # Calculate average distance for the reference ID
    reference_avg_distance = df[df["id_start"] == reference_id]["distance"].mean()

    # Calculate threshold bounds (10% above and below the reference average)
    lower_bound = reference_avg_distance * 0.9
    upper_bound = reference_avg_distance * 1.1

    # Filter IDs based on average distance within the threshold
    filtered_df = df[
        (df["id_start"] != reference_id)
        & (df["distance"].mean() <= upper_bound)
        & (df["distance"].mean() >= lower_bound)
    ]

    # Sort IDs based on their average distance
    filtered_df = filtered_df.sort_values(by="distance")

    return filtered_df


def calculate_toll_rate(df):
    """
    Calculates toll rates for each vehicle type based on distance and rate coefficients.

    Args:
        df (pandas.DataFrame): Unrolled distance matrix.

    Returns:
        pandas.DataFrame: DataFrame with additional columns for toll rates of different vehicles.
    """
    # Define rate coefficients for each vehicle type
    rate_coefficients = {
        "moto": 0.8,
        "car": 1.2,
        "rv": 1.5,
        "bus": 2.2,
        "truck": 3.6,
    }

    # Calculate toll rates for each vehicle type and add them as new columns
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df["distance"] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df):
    """
    Calculates time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: DataFrame with additional columns for time-based toll rates.
    """

    # Define time intervals for weekdays and weekends with their respective discount factors
    weekday_discounts = {
        "00:00:00-10:00:00": 0.8,
        "10:00:00-18:00:00": 1.2,
        "18:00:00-23:59:59": 0.8,
    }
    weekend_discount = 0.7

    # Define start and end time intervals for a full 24-hour period
    start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
    end_time = start_time + timedelta(hours=23, minutes=59, seconds=59)

    # Define days of the week
    days_of_week = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

    # Create empty columns for time-based toll rates
    for vehicle in ["moto", "car", "rv", "bus", "truck"]:
        df[f"time_based_{vehicle}"] = None

    # Group by unique `id_start` and `id_end` pairs
    grouped_df = df.groupby(["id_start", "id_end"])

    # Apply logic to each group
    for group_name, group_df in grouped_df:
        start_day = datetime.strptime(group_df["startDay"].iloc[0], "%Y-%m-%d").strftime("%A")
        current_time = start_time

        # Loop through each time interval for a full day
        while current_time <= end_time:
            end_day = start_day
            next_time = current_time + timedelta(hours=10)

            # Check if time interval goes beyond next day
            if next_time > end_time:
                end_time = current_time + timedelta(hours=end_time - current_time)
                end_day = days_of_week[(days_of_week.index(start_day) + 1) % 7]

            # Update start and end times for current interval
            group_df["start_time"] = current_time
            group_df["end_time"] = next_time
            group_df["start_day"] = start_day
            group_df["end_day"] = end_day

            # Apply discount factor based on time interval and weekday/weekend
            if start_day in ["Saturday", "Sunday"]:
                discount = weekend_discount
            else:
                for time_range, factor in weekday_discounts.items():
                    if time_range.split("-")[0] <= current_time.strftime("%H:%M:%S") <= time_range.split("-")[1]:
                        discount = factor
                        break

            # Apply discount factor to vehicle columns
            for vehicle in ["moto", "car", "rv", "bus", "truck"]:
                group_df[f"time_based_{vehicle}"] = group_df[vehicle] * discount

            # Update current time for next interval
            current_time = next_time

    # Return the updated DataFrame
    return df.reset_index()