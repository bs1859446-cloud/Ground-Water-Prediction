import pandas as pd

FILE = "groundwater_with_weather.csv"

print("=" * 70)
print("GROUNDWATER TEMPORAL COVERAGE CHECK")
print("=" * 70)

df = pd.read_csv(FILE)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Create unique location ID
df["Location_ID"] = (
    df["State"].astype(str) + "|" +
    df["District"].astype(str) + "|" +
    df["Block"].astype(str) + "|" +
    df["Village"].astype(str)
)

print("\n===== BASIC INFORMATION =====")

print("Total records :", len(df))
print("Unique locations :", df["Location_ID"].nunique())
print("Unique dates :", df["Date"].nunique())

# Number of observations per location
location_counts = df.groupby("Location_ID").size()

print("\n===== OBSERVATIONS PER LOCATION =====")

print("Locations with 1 observation :", (location_counts == 1).sum())
print("Locations with 2 observations:", (location_counts == 2).sum())
print("Locations with 3 observations:", (location_counts == 3).sum())
print("Locations with 4+ observations:", (location_counts >= 4).sum())

# Locations with repeated observations
repeated = location_counts[location_counts > 1]

print("\n===== TEMPORAL LOCATIONS =====")

print("Locations with repeated dates :", len(repeated))

if len(repeated) > 0:
    print("\nTop locations with multiple observations:")
    print(repeated.sort_values(ascending=False).head(20))

# Date distribution
print("\n===== DATE DISTRIBUTION =====")

date_counts = (
    df.groupby(df["Date"].dt.strftime("%Y-%m-%d"))
      .size()
      .sort_index()
)

print(date_counts)

# State temporal coverage
print("\n===== STATE TEMPORAL COVERAGE =====")

state_location = (
    df.groupby(["State", "Location_ID"])
      .size()
      .reset_index(name="Observations")
)

state_summary = (
    state_location.groupby("State")
    .agg(
        Locations=("Location_ID", "count"),
        Locations_With_2Plus=("Observations", lambda x: (x >= 2).sum())
    )
)

print(state_summary)

# Show repeated locations
print("\n===== SAMPLE REPEATED LOCATIONS =====")

for location in repeated.index[:20]:

    rows = df[df["Location_ID"] == location][
        ["State", "District", "Block", "Village", "Date", "WL_mbgl"]
    ].sort_values("Date")

    print("\n" + "-" * 70)
    print(rows.to_string(index=False))

print("\n" + "=" * 70)
print("TEMPORAL COVERAGE CHECK COMPLETED")
print("=" * 70)