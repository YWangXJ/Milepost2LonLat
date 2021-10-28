import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# load shape file
shp_path=r".\shapefile\NJ_Roadway_Network.shp"
SRI_map = gpd.read_file(shp_path)
SRI_map = SRI_map.to_crs({'init': 'epsg:4326'})

# load crash data
crash_data_path = 'acc_19.csv'
df = pd.read_csv(crash_data_path)
df['sri_std_rte_identifier'] = df['sri_std_rte_identifier'].astype(str)
# original data longitude is positive
df['longitude'] = -df['longitude'].abs()

total = len(df);
cnt = 0;

for index, row in df.iterrows():
    sri_cur = row['sri_std_rte_identifier']
    mp_cur = row['milepost']
    if pd.notna(row['latitude']):#data already has lon lat info
        print(row['id'] + " already has lon lat info")
        continue
    
    ## SRI is not unique, need to find the row in SRI_map that contains the mp_cur
    SRI_map_filtered = SRI_map.loc[(SRI_map['SRI'] == df.iloc[0]['sri_std_rte_identifier']) & (SRI_map['MP_START'] < mp_cur) & (SRI_map['MP_END'] > mp_cur)]
    
    ## match exists 
    if len(SRI_map_filtered) != 0:
        mp_start = SRI_map_filtered['MP_START']
        mp_end = SRI_map_filtered['MP_END']
        ip = SRI_map_filtered['geometry'].interpolate(mp_cur - mp_start)

        df.at[index, 'latitude'] = ip.y
        df.at[index, 'longitude'] = ip.x
        cnt = cnt + 1
        print(str(cnt) + " of " + str(total) + "done.")

df.to_csv('acc_19_processed.csv',index = False)

geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
geometry[:3]
geo_df = gpd.GeoDataFrame(df, crs = {'init': 'epsg:4326'}, geometry = geometry)
geo_df.head()

fig, ax  = plt.subplots(figsize = (15, 15))
SRI_map.plot(ax = ax, alpha = 0.4, color = 'grey')
geo_df.plot(ax = ax, markersize = 20, color = 'red', marker = 'o', label = 'Accident')

plt.savefig('final.png')