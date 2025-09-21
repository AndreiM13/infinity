import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# --- Set working directory manually ---
os.chdir(r"C:\Users\macov\Desktop\infinity")

st.title("Game Analytics Dashboard")

# --- Load CSVs ---
df_events = pd.read_csv("game_events.csv", parse_dates=['event_time'])
df_players = pd.read_csv("Players_Table.csv", parse_dates=['registration_date'])
df_purchases = pd.read_csv("Purchases_Table.csv", parse_dates=['purchase_time'])

# --- Preprocess Dates ---
df_events['date'] = df_events['event_time'].dt.date
df_purchases['date'] = df_purchases['purchase_time'].dt.date

# -------------------------
# Daily Active Users & Revenue
# -------------------------
dau = df_events.groupby('date')['player_id'].nunique().reset_index(name='DAU')
revenue_daily = df_events.groupby('date')['revenue_usd'].sum().reset_index(name='Revenue')
daily_summary = pd.merge(dau, revenue_daily, on='date')

st.subheader("Daily Active Users & Revenue Trends")
fig, ax1 = plt.subplots(figsize=(10,5))
ax1.plot(daily_summary['date'], daily_summary['DAU'], color='blue', marker='o', label='DAU')
ax1.set_xlabel('Date')
ax1.set_ylabel('DAU', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()
ax2.plot(daily_summary['date'], daily_summary['Revenue'], color='green', marker='x', label='Revenue')
ax2.set_ylabel('Revenue (USD)', color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("DAU and Revenue Over Time")
fig.tight_layout()
st.pyplot(fig)

# -------------------------
# Ad Watches Over Time
# -------------------------
ad_watch_daily = df_events[df_events['event_type'] == 'ad_watch'] \
    .groupby('date').size().reset_index(name='Ad_Watches')

st.subheader("Ad Watches Over Time")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(ad_watch_daily['date'], ad_watch_daily['Ad_Watches'], color='red', marker='o')
ax.set_xlabel('Date')
ax.set_ylabel('Ad Watches')
ax.set_title('Ad Watches Over Time')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# -------------------------
# Top 5 Levels with Highest Drop-Off (based on start_game)
# -------------------------
st.subheader("Top 5 Levels with Highest Drop-Off")

# Filter start_game events
start_df = df_events[df_events['event_type'] == 'start_game']

# Count unique players who started each level
level_players = start_df.groupby("level")["player_id"].nunique().sort_index()

# Compute drop-off = number of players who did NOT start the next level
drop_off = level_players - level_players.shift(-1)

# Remove last level and ensure drop-off is non-negative
drop_off = drop_off.dropna().clip(lower=0)

# Sort by largest drop-off to find top 5 levels
top_dropoff_levels = drop_off.sort_values(ascending=False).head(5)

# Display bar chart in Streamlit
fig, ax = plt.subplots(figsize=(8,5))
top_dropoff_levels.plot(kind='bar', color='#0a0a23', ax=ax)
ax.set_xlabel("Level")
ax.set_ylabel("Players Dropped Off")
ax.set_title("Top 5 Drop-Off Levels")
st.pyplot(fig)


# Revenue by Country
# Aggregate total revenue per country 
revenue_by_country = pd.merge(
    df_players,      
    df_purchases,    
    on='player_id',
    how='inner'      
)

revenue_by_country = revenue_by_country.groupby('country')['amount_usd'] \
    .sum().round(2).reset_index(name='total_revenue')

# Sort descending by revenue
revenue_by_country = revenue_by_country.sort_values(by='total_revenue', ascending=False)

# Streamlit subheader
st.subheader("Total Revenue per Country ")

# Plot bar chart
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(revenue_by_country['country'], revenue_by_country['total_revenue'], color='#0a0a23')
ax.set_xlabel('Country')
ax.set_ylabel('Total Revenue (USD)')
ax.set_title('Total Revenue per Country')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
