
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_rows', 15)
pd.set_option('display.max_columns', None)
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.ticker as ticker
from matplotlib.animation import FuncAnimation
import streamlit.components.v1 as components


train = pd.read_csv("Video_Games_Sales_as_at_22_Dec_2016.csv")
df = pd.read_csv('/content/Video_Games_Sales_as_at_22_Dec_2016.csv',usecols=["Name","Year_of_Release","Genre","Global_Sales"])
df=df.dropna(subset=["Genre"])





# drop null-name
#Year of release=0
#genre- domain knowledge
#publisher= 'Unknown'
#Critic score- publisher wise, average scores
#critic count- drop
#user score- sales replicated into categories, each category's average user score is assigned to NA values
#user count-drop
#developer='Unknown'
#Rating= 'N' for not available

train=train.dropna(subset=["Name"])
train["Year_of_Release"] = train["Year_of_Release"].fillna(0)
train["Publisher"] = train["Publisher"].fillna("Unknown")
train = train.drop(columns=["Critic_Count","User_Count"])
train["Developer"] = train["Developer"].fillna("Unknown")
train["Rating"] = train["Rating"].fillna("N")


train["Critic_Score"] = train["Critic_Score"].fillna(train.groupby("Publisher")["Critic_Score"].transform("mean"))

train["Critic_Score"] = train["Critic_Score"].fillna(0)

bins = [0.0, 0.533, 2.073, 3.613, 5.153,10,20,30,np.inf]
names = ['<0.5', '0.5-2', '2-3.5', '3.5-5','5-10','10-20','20-30','30+']
train["Sales_Distribution"] = pd.cut(train["Global_Sales"],bins,labels=names)

train["User_Score"] = train["User_Score"].fillna(train.groupby("Sales_Distribution")["User_Score"].transform("mean"))

##

Platform_sales = train.groupby("Platform",as_index="False").agg({"Global_Sales":"sum"}).reset_index()
Market_share =  train.groupby("Platform").agg({"NA_Sales":"sum","EU_Sales":"sum","JP_Sales":"sum","Global_Sales":"sum"}).reset_index()
Market_share["Per_NA_Sales"] = Market_share["NA_Sales"]*100/Market_share["NA_Sales"].sum()
Market_share["Per_EU_Sales"] = Market_share["EU_Sales"]*100/Market_share["EU_Sales"].sum()
Market_share["Per_JP_Sales"] = Market_share["JP_Sales"]*100/Market_share["JP_Sales"].sum()
Market_share["Per_Global_Sales"] = Market_share["Global_Sales"]*100/Market_share["Global_Sales"].sum()


def bar():
  fig=plt.figure(figsize=(18, 6), dpi=80)
  sns.barplot(x=Platform_sales["Platform"],y=Platform_sales["Global_Sales"])
  st.pyplot(fig)

### Animation code
colors = dict(zip(['Sports','Platform','Racing',
                   'Role-Playing','Shooter',
                   'Misc','Simulation','Action','Fighting','Adventure','Strategy','Puzzle'],
                    ['#adb0ff', '#ffb3ff', '#90d595',
                     '#e48381', '#aafbff', '#f7bb5f', 
                     '#eafb50','#adb0ff','#ffb3ff','#90d595','#e48381','#aafbff']))
  
group_lk = df.set_index('Name')['Genre'].to_dict()
  
  
def draw_barchart(year):
    dff = df[df['Year_of_Release'].eq(year)].sort_values(by='Global_Sales',ascending=True).tail(10)
    ax.clear()
    ax.barh(dff['Name'], dff['Global_Sales'],
            color=[colors[group_lk[x]] for x in dff['Name']])
    dx = dff['Global_Sales'].max() / 200
      
    for i, (Global_Sales, Name) in enumerate(zip(dff['Global_Sales'],
                                          dff['Name'])):
        ax.text(Global_Sales-dx, i,Name,size=14, weight=600,ha='right', va='bottom')
        ax.text(Global_Sales-dx, i-.25, group_lk[Name], size=10, color='#444444', 
                ha='right', va='baseline')
        ax.text(Global_Sales+dx, i,     f'{Global_Sales:,.0f}', 
                size=14, ha='left',  va='center')
          
    # polished styles
    ax.text(1, 0.4, year, transform=ax.transAxes, 
            color='#777777', size=46, ha='right',
            weight=800)
    ax.text(0, 1.06, 'Global Sales (millions)',
            transform=ax.transAxes, size=12,
            color='#777777')
      
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
   
    ax.text(1, 0, 'by Sash and Vishal', 
            transform=ax.transAxes, ha='right', color='#777777', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)
    plt.show()
  


st.title("Video Game Sales Data Analysis")
st.sidebar.markdown("### Market percentage for each platform in each region")
page = st.sidebar.selectbox(
      "Select Region",
        ["North America","Japan","Europe"]
    )
typ = st.sidebar.selectbox(
    "Select chart type",
    ["Bar Chart","Pie Chart"]
)
if not st.sidebar.checkbox("Hide", True):
  st.subheader("Market percentage of Each Platform by Region")
  if page == "North America" and typ == "Pie Chart":
    Market_share_top = Market_share[["Platform","Per_NA_Sales"]].sort_values("Per_NA_Sales",ascending = False).head(9)
    x=100-Market_share_top["Per_NA_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by % of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("pastel")
    plt.pie(Market_share_top["Per_NA_Sales"],labels=Market_share_top["Platform"])
    st.pyplot(fig)
  elif page == "Japan" and typ == "Pie Chart":
    #Grouping the lesser significant % market shares as others for clearer visualizations
    Market_share_top = Market_share[["Platform","Per_JP_Sales"]].sort_values("Per_JP_Sales",ascending = False).head(9)
    x=100-Market_share_top["Per_JP_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by % of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("pastel")
    plt.pie(Market_share_top["Per_JP_Sales"],labels=Market_share_top["Platform"])
    st.pyplot(fig)
  elif page =="Europe" and typ == "Pie Chart":
    #Grouping the lesser significant % market shares as others for clearer visualizations
    Market_share_top = Market_share[["Platform","Per_EU_Sales"]].sort_values("Per_EU_Sales",ascending = False).head(9)
    x=100-Market_share_top["Per_EU_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by %of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("pastel")
    plt.pie(Market_share_top["Per_EU_Sales"],labels=Market_share_top["Platform"])
    st.pyplot(fig)
  elif page == "North America" and typ == "Bar Chart":
    #Grouping the lesser significant % market shares as others for clearer visualizations
    Market_share_top = Market_share[["Platform","Per_NA_Sales"]].sort_values("Per_NA_Sales",ascending = False).head(15)
    x=100-Market_share_top["Per_NA_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by % of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("coolwarm_r")
    sns.barplot(x=Market_share_top["Platform"],y=Market_share_top["Per_NA_Sales"],color="green")
    st.pyplot(fig)
  elif page == "Japan" and typ == "Bar Chart":
    #Grouping the lesser significant % market shares as others for clearer visualizations
    Market_share_top = Market_share[["Platform","Per_JP_Sales"]].sort_values("Per_JP_Sales",ascending = False).head(15)
    x=100-Market_share_top["Per_JP_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by % of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("coolwarm_r")
    sns.barplot(x=Market_share_top["Platform"],y=Market_share_top["Per_JP_Sales"],color="red")
    st.pyplot(fig)
  else:
    #Grouping the lesser significant % market shares as others for clearer visualizations
    Market_share_top = Market_share[["Platform","Per_EU_Sales"]].sort_values("Per_EU_Sales",ascending = False).head(15)
    x=100-Market_share_top["Per_EU_Sales"].sum()
    Market_share_top.loc[1] = ["Other",x]
    Market_share_top
    #Plotting the European market share by % of sales for each platform.
    fig=plt.figure(figsize=(18, 6), dpi=80)
    sns.color_palette("coolwarm_r")
    sns.barplot(x=Market_share_top["Platform"],y=Market_share_top["Per_EU_Sales"],color="orange")
    st.pyplot(fig)



    



def va(x=1):

  fig1=plt.figure(figsize=(18, 15), dpi=80)

  if x > 31:
    print("There are only 31 platforms so displaying all the 31 platforms")

  Platform_sales_top = Platform_sales.sort_values("Global_Sales",ascending = False).head(x)
  sns.barplot(x=Platform_sales_top["Platform"],y=Platform_sales_top["Global_Sales"])
  st.pyplot(fig1)
st.sidebar.markdown("### Top Platforms by sales")
x = st.sidebar.slider('Select the number of platforms',min_value=1)
if not st.sidebar.checkbox("Hide", True,key="1"):
  st.subheader("Top Platforms by sales")
  va(x)

st.sidebar.markdown("### Highest selling game by genre over the Years")
st.sidebar.markdown("Uncheck the box below to view the animation")
if not st.sidebar.checkbox("Hide",True,key="2"):
  st.subheader("Best performing games by genre over the Years")
  fig, ax = plt.subplots(figsize=(10, 6))
  animator = FuncAnimation(fig, draw_barchart,frames = range(1980, 2017))
  components.html(animator.to_jshtml(), height=1500,width = 3000,scrolling = True)

  

