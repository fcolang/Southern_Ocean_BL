import numpy as np
import scipy.io as sio
from datetime import datetime, timedelta
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, MultipleLocator
import matplotlib.mlab as mlab
import scipy as sp
from scipy.interpolate import UnivariateSpline
import scipy.interpolate as si
from scipy.interpolate import interp1d
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pylab import plot,show, grid, legend
from skewt import SkewT
from matplotlib.pyplot import rcParams,figure,show,draw

base_dir = os.path.expanduser('~')
path_data_csv=base_dir+'/Dropbox/Monash_Uni/SO/MAC/Data/00 CSV/'
path_data=base_dir+'/Dropbox/Monash_Uni/SO/MAC/003 Cluster/'
#*****************************************************************************\
#*****************************************************************************\
#Reading CSV Cluster
#*****************************************************************************\
#*****************************************************************************\
#925-850-700
df_cluster= pd.read_csv(path_data + 'All_ClusterAnalysis.csv', sep=',', parse_dates=['Date'])
CL4=np.array(df_cluster['Cluster'])
dist_clu=np.array(df_cluster['Distance'])

path_data_save=base_dir+'/Dropbox/Monash_Uni/SO/MAC/003 Cluster/fronts/'

#*****************************************************************************\
# ****************************************************************************\
# ****************************************************************************\
#                            MAC Data Original Levels
#*****************************************************************************\
# ****************************************************************************\
path_databom=base_dir+'/Dropbox/Monash_Uni/SO/MAC/Data/MatFiles/files_bom/'
matb1= sio.loadmat(path_databom+'BOM_1995.mat')
bom_in=matb1['BOM_S'][:]
timesd= matb1['time'][:]
bom=bom_in

for y in range(1996,2011):
    matb= sio.loadmat(path_databom+'BOM_'+str(y)+'.mat')
    bom_r=matb['BOM_S'][:]
    timesd_r= matb['time'][:]
    bom=np.concatenate((bom,bom_r), axis=2)
    timesd=np.concatenate((timesd,timesd_r), axis=1)

ni=bom.shape
#*****************************************************************************\
#Delete special cases
indexdel1=[]
indexdel2=[]
#Delete when array is only NaN
for j in range(0,ni[2]):
    if np.isnan(np.nansum(bom[:,0,j]))==True:
        indexdel1=np.append(indexdel1,j)

bom=np.delete(bom, indexdel1,axis=2)
ni=bom.shape
timesd=np.delete(timesd, indexdel1)

#Delete when max height is lower than 2500 mts
for j in range(0,ni[2]):
    if np.nanmax(bom[:,1,j])<2500:
        indexdel2=np.append(indexdel2,j)

bom=np.delete(bom, indexdel2,axis=2) #(3000,8,3545)
ni=bom.shape
timesd=np.delete(timesd, indexdel2)
#*****************************************************************************\

#Convert Matlab datenum into Python datetime source: https://gist.github.com/vicow)
def datenum_to_datetime(datenum):
    days = datenum % 1
    hours = days % 1 * 24
    minutes = hours % 1 * 60
    seconds = minutes % 1 * 60
    return datetime.fromordinal(int(datenum)) \
        + timedelta(days=int(days)) \
        + timedelta(hours=int(hours)) \
        + timedelta(minutes=int(minutes)) \
        + timedelta(seconds=round(seconds)) \
        - timedelta(days=366)


#*****************************************************************************\
#Separation of Variables
pres=bom[:,0,:].reshape(ni[0],ni[2])
hght=bom[:,1,:].reshape(ni[0],ni[2])
temp=bom[:,2,:].reshape(ni[0],ni[2])
dwpo=bom[:,3,:].reshape(ni[0],ni[2])
mixr=bom[:,5,:].reshape(ni[0],ni[2])
wdir_initial=bom[:,6,:].reshape(ni[0],ni[2])
wspd=bom[:,7,:].reshape(ni[0],ni[2])*0.5444444
relh=bom[:,4,:].reshape(ni[0],ni[2])

u=wspd*(np.cos(np.radians(270-wdir_initial)))
v=wspd*(np.sin(np.radians(270-wdir_initial)))
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#                            MAC Data YOTC Levels
#*****************************************************************************\
#*****************************************************************************\
#Leyendo Alturas y press
file_levels = np.genfromtxt('./../../Read_Files/YOTC/levels.csv', delimiter=',')
hlev_yotc=file_levels[:,6]
plev_yotc=file_levels[:,4] #value 10 is 925
#*****************************************************************************\
#Interpolation to YOTC Levels
prutemp=np.empty((len(hlev_yotc),0))
prumixr=np.empty((len(hlev_yotc),0))
pruu=np.empty((len(hlev_yotc),0))
pruv=np.empty((len(hlev_yotc),0))
prurelh=np.empty((len(hlev_yotc),0))
prudwpo=np.empty((len(hlev_yotc),0))

for j in range(0,ni[2]):
#height initialization
    x=hght[:,j]
    x[-1]=np.nan
    new_x=hlev_yotc
#Interpolation YOTC levels
    yt=temp[:,j]
    rest=interp1d(x,yt)(new_x)
    prutemp=np.append(prutemp,rest)

    ym=mixr[:,j]
    resm=interp1d(x,ym)(new_x)
    prumixr=np.append(prumixr,resm)

    yw=u[:,j]
    resw=interp1d(x,yw)(new_x)
    pruu=np.append(pruu,resw)

    yd=v[:,j]
    resd=interp1d(x,yd)(new_x)
    pruv=np.append(pruv,resd)

    yr=relh[:,j]
    resr=interp1d(x,yr)(new_x)
    prurelh=np.append(prurelh,resr)

    ydp=dwpo[:,j]
    resr=interp1d(x,ydp)(new_x)
    prudwpo=np.append(prudwpo,resr)

tempmac_ylev=prutemp.reshape(-1,len(hlev_yotc)).transpose()
umac_ylev=pruu.reshape(-1,len(hlev_yotc)).transpose()
vmac_ylev=pruv.reshape(-1,len(hlev_yotc)).transpose()
mixrmac_ylev=prumixr.reshape(-1,len(hlev_yotc)).transpose()
relhmac_ylev=prurelh.reshape(-1,len(hlev_yotc)).transpose()
dwpomac_ylev=prudwpo.reshape(-1,len(hlev_yotc)).transpose()

wspdmac_ylev=np.sqrt(umac_ylev**2 + vmac_ylev**2)
wdirmac_ylev=np.arctan2(-umac_ylev, -vmac_ylev)*(180/np.pi)
wdirmac_ylev[(umac_ylev == 0) & (vmac_ylev == 0)]=0


relhum_my=relhmac_ylev.T
temp_my=tempmac_ylev.T
u_my=umac_ylev.T
v_my=vmac_ylev.T
mixr_my=mixrmac_ylev.T
dwpo_my=dwpomac_ylev.T

wsp_my=wspdmac_ylev.T
wdir_my=wdirmac_ylev.T

#*****************************************************************************\
#Cambiar fechas
timestamp = [datenum_to_datetime(t) for t in timesd]
time_my = np.array(timestamp)
time_my_ori = np.array(timestamp)

for i in range(0,ni[2]):
    #Cuando cae 23 horas del 31 de diciembre agrega un anio
    if (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==12:
        y1=time_my[i].year
        time_my[i]=time_my[i].replace(year=y1+1,hour=0, month=1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==1:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==3:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==5:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==7:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==8:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==31 and time_my[i].month==10:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==30 and time_my[i].month==4:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==30 and time_my[i].month==6:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==30 and time_my[i].month==9:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==30 and time_my[i].month==11:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)

    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==28 and time_my[i].month==2:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)
    #Bisiesto 2008
    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==29 and time_my[i].month==2 and time_my[i].year==2008:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)
    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==29 and time_my[i].month==2 and time_my[i].year==2004:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)
    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==29 and time_my[i].month==2 and time_my[i].year==2000:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)
    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==29 and time_my[i].month==2 and time_my[i].year==1996:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)
    if  (time_my[i].hour==23 or time_my[i].hour==22) and time_my[i].day==29 and time_my[i].month==2 and time_my[i].year==1992:
        m1=time_my[i].month
        time_my[i]=time_my[i].replace(hour=0, month=m1+1,day=1)


    #Cuando cae 23 horas, mueve hora a las 00 del dia siguiente
    if time_my[i].hour==23 or time_my[i].hour==22:
        d1=time_my[i].day
        time_my[i]=time_my[i].replace(hour=0,day=d1+1)
    else:
        time_my[i]=time_my[i]
    #Cuando cae 11 horas, mueve hora a las 12 del mismo dia
    if time_my[i].hour==11 or time_my[i].hour==10 or time_my[i].hour==13 or time_my[i].hour==14:
        time_my[i]=time_my[i].replace(hour=12)
    else:
        time_my[i]=time_my[i]

    #Cuando cae 1 horas, mueve hora a las 0 del mismo dia
    if time_my[i].hour==1 or time_my[i].hour==2:
        time_my[i]=time_my[i].replace(hour=0)
    else:
        time_my[i]=time_my[i]

#*****************************************************************************\
#*****************************************************************************\
#                          Dataframes 1995-2010                               \
#*****************************************************************************\
#*****************************************************************************\
date_index_all = pd.date_range('1995-01-01 00:00', periods=11688, freq='12H')
#*****************************************************************************\
#Dataframe MAC YOTC levels
t_list=temp_my.tolist()
u_list=u_my.tolist()
v_list=v_my.tolist()
rh_list=relhum_my.tolist()
mr_list=mixr_my.tolist()
dwpo_list=dwpo_my.tolist()
wsp_list=wsp_my.tolist()
wdir_list=wdir_my.tolist()


dmy={'temp':t_list,
'u':u_list,
'v':v_list,
'RH':rh_list,
'dewp':dwpo_list,
'mixr':mr_list,
'wsp':wsp_list,
'wdir':wdir_list,
'CL_4':CL4,
'dist_clu':dist_clu}

df_my= pd.DataFrame(data=dmy,index=time_my)
# Eliminate Duplicate Soundings
df_my=df_my.reset_index().drop_duplicates(cols='index',take_last=True).set_index('index')
df_my=df_my.reindex(date_index_all)
df_my.index.name = 'Date'

#*****************************************************************************\
#Reading FRONTS
#*****************************************************************************\
df_cfront= pd.read_csv(path_data_csv + 'df_cfront_19952010.csv', sep='\t', parse_dates=['Date'])
df_cfront= df_cfront.set_index('Date')


df_wfront= pd.read_csv(path_data_csv + 'df_wfront_19952010.csv', sep='\t', parse_dates=['Date'])
df_wfront= df_wfront.set_index('Date')

#*****************************************************************************\
#Concadanate dataframes
df_mycluwfro=pd.concat([df_my, df_wfront],axis=1)
df_myclucfro=pd.concat([df_my, df_cfront],axis=1)

#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#                           Cold Fronts
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
# Cluster 1
#*****************************************************************************\
df_CL4_G1 = df_myclucfro[df_myclucfro['CL_4']==1]
df_CL4_G1_DCF=df_CL4_G1[np.isfinite(df_CL4_G1['Dist CFront'])]
df_CL4_G1_CF=df_CL4_G1[np.isnan(df_CL4_G1['Dist CFront'])]
print len(df_CL4_G1),len(df_CL4_G1_CF), len(df_CL4_G1_DCF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G1_CF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G1_CF=np.nanmean(RH,axis=0)
temp_CL4_G1_CF=np.nanmean(T,axis=0)
dewp_CL4_G1_CF=np.nanmean(DP,axis=0)
mixr_CL4_G1_CF=np.nanmean(MX,axis=0)
v_CL4_G1_CF=np.nanmean(V,axis=0)
u_CL4_G1_CF=np.nanmean(U,axis=0)
wsp_CL4_G1_CF=np.sqrt(u_CL4_G1_CF**2 + v_CL4_G1_CF**2)
wdir_CL4_G1_CF=np.arctan2(-u_CL4_G1_CF, -v_CL4_G1_CF)*(180/np.pi)
wdir_CL4_G1_CF[(u_CL4_G1_CF == 0) & (v_CL4_G1_CF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G1_DCF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G1_DCF=np.nanmean(RH,axis=0)
temp_CL4_G1_DCF=np.nanmean(T,axis=0)
dewp_CL4_G1_DCF=np.nanmean(DP,axis=0)
mixr_CL4_G1_DCF=np.nanmean(MX,axis=0)
v_CL4_G1_DCF=np.nanmean(V,axis=0)
u_CL4_G1_DCF=np.nanmean(U,axis=0)
wsp_CL4_G1_DCF=np.sqrt(u_CL4_G1_DCF**2 + v_CL4_G1_DCF**2)
wdir_CL4_G1_DCF=np.arctan2(-u_CL4_G1_DCF, -v_CL4_G1_DCF)*(180/np.pi)
wdir_CL4_G1_DCF[(u_CL4_G1_DCF == 0) & (v_CL4_G1_DCF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#CF
temperature_c=temp_CL4_G1_CF
dewpoint_c=dewp_CL4_G1_CF
wsp=wsp_CL4_G1_CF*1.943844
wdir=wdir_CL4_G1_CF

mydataG1_CF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C1')))
#DCF
temperature_c=temp_CL4_G1_DCF
dewpoint_c=dewp_CL4_G1_DCF
wsp=wsp_CL4_G1_DCF*1.943844
wdir=wdir_CL4_G1_DCF

mydataG1_DCF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C1')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG1_CF)
S2=SkewT.Sounding(soundingdata=mydataG1_DCF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C1_CF_Dif.png', format='png', dpi=1200)

#*****************************************************************************\
# Cluster 2
#*****************************************************************************\

df_CL4_G2 = df_myclucfro[df_myclucfro['CL_4']==2]
df_CL4_G2_DCF=df_CL4_G2[np.isfinite(df_CL4_G2['Dist CFront'])]
df_CL4_G2_CF=df_CL4_G2[np.isnan(df_CL4_G2['Dist CFront'])]
print len(df_CL4_G2),len(df_CL4_G2_CF), len(df_CL4_G2_DCF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G2_CF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G2_CF=np.nanmean(RH,axis=0)
temp_CL4_G2_CF=np.nanmean(T,axis=0)
dewp_CL4_G2_CF=np.nanmean(DP,axis=0)
mixr_CL4_G2_CF=np.nanmean(MX,axis=0)
v_CL4_G2_CF=np.nanmean(V,axis=0)
u_CL4_G2_CF=np.nanmean(U,axis=0)
wsp_CL4_G2_CF=np.sqrt(u_CL4_G2_CF**2 + v_CL4_G2_CF**2)
wdir_CL4_G2_CF=np.arctan2(-u_CL4_G2_CF, -v_CL4_G2_CF)*(180/np.pi)
wdir_CL4_G2_CF[(u_CL4_G2_CF == 0) & (v_CL4_G2_CF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G2_DCF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G2_DCF=np.nanmean(RH,axis=0)
temp_CL4_G2_DCF=np.nanmean(T,axis=0)
dewp_CL4_G2_DCF=np.nanmean(DP,axis=0)
mixr_CL4_G2_DCF=np.nanmean(MX,axis=0)
v_CL4_G2_DCF=np.nanmean(V,axis=0)
u_CL4_G2_DCF=np.nanmean(U,axis=0)
wsp_CL4_G2_DCF=np.sqrt(u_CL4_G2_DCF**2 + v_CL4_G2_DCF**2)
wdir_CL4_G2_DCF=np.arctan2(-u_CL4_G2_DCF, -v_CL4_G2_DCF)*(180/np.pi)
wdir_CL4_G2_DCF[(u_CL4_G2_DCF == 0) & (v_CL4_G2_DCF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#CF
temperature_c=temp_CL4_G2_CF
dewpoint_c=dewp_CL4_G2_CF
wsp=wsp_CL4_G2_CF*1.943844
wdir=wdir_CL4_G2_CF

mydataG2_CF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C2')))
#DCF
temperature_c=temp_CL4_G2_DCF
dewpoint_c=dewp_CL4_G2_DCF
wsp=wsp_CL4_G2_DCF*1.943844
wdir=wdir_CL4_G2_DCF

mydataG2_DCF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C2')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG2_CF)
S2=SkewT.Sounding(soundingdata=mydataG2_DCF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C2_CF_Dif.png', format='png', dpi=1200)
#*****************************************************************************\
# Cluster 3
#*****************************************************************************\


df_CL4_G3 = df_myclucfro[df_myclucfro['CL_4']==3]
df_CL4_G3_DCF=df_CL4_G3[np.isfinite(df_CL4_G3['Dist CFront'])]
df_CL4_G3_CF=df_CL4_G3[np.isnan(df_CL4_G3['Dist CFront'])]
print len(df_CL4_G3),len(df_CL4_G3_CF), len(df_CL4_G3_DCF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G3_CF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G3_CF=np.nanmean(RH,axis=0)
temp_CL4_G3_CF=np.nanmean(T,axis=0)
dewp_CL4_G3_CF=np.nanmean(DP,axis=0)
mixr_CL4_G3_CF=np.nanmean(MX,axis=0)
v_CL4_G3_CF=np.nanmean(V,axis=0)
u_CL4_G3_CF=np.nanmean(U,axis=0)
wsp_CL4_G3_CF=np.sqrt(u_CL4_G3_CF**2 + v_CL4_G3_CF**2)
wdir_CL4_G3_CF=np.arctan2(-u_CL4_G3_CF, -v_CL4_G3_CF)*(180/np.pi)
wdir_CL4_G3_CF[(u_CL4_G3_CF == 0) & (v_CL4_G3_CF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G3_DCF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G3_DCF=np.nanmean(RH,axis=0)
temp_CL4_G3_DCF=np.nanmean(T,axis=0)
dewp_CL4_G3_DCF=np.nanmean(DP,axis=0)
mixr_CL4_G3_DCF=np.nanmean(MX,axis=0)
v_CL4_G3_DCF=np.nanmean(V,axis=0)
u_CL4_G3_DCF=np.nanmean(U,axis=0)
wsp_CL4_G3_DCF=np.sqrt(u_CL4_G3_DCF**2 + v_CL4_G3_DCF**2)
wdir_CL4_G3_DCF=np.arctan2(-u_CL4_G3_DCF, -v_CL4_G3_DCF)*(180/np.pi)
wdir_CL4_G3_DCF[(u_CL4_G3_DCF == 0) & (v_CL4_G3_DCF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#CF
temperature_c=temp_CL4_G3_CF
dewpoint_c=dewp_CL4_G3_CF
wsp=wsp_CL4_G3_CF*1.943844
wdir=wdir_CL4_G3_CF

mydataG3_CF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C3')))
#DCF
temperature_c=temp_CL4_G3_DCF
dewpoint_c=dewp_CL4_G3_DCF
wsp=wsp_CL4_G3_DCF*1.943844
wdir=wdir_CL4_G3_DCF

mydataG3_DCF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C3')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG3_CF)
S2=SkewT.Sounding(soundingdata=mydataG3_DCF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C3_CF_Dif.png', format='png', dpi=1200)
#*****************************************************************************\
# Cluster 4
#*****************************************************************************\


df_CL4_G4 = df_myclucfro[df_myclucfro['CL_4']==4]
df_CL4_G4_DCF=df_CL4_G4[np.isfinite(df_CL4_G4['Dist CFront'])]
df_CL4_G4_CF=df_CL4_G4[np.isnan(df_CL4_G4['Dist CFront'])]
print len(df_CL4_G4),len(df_CL4_G4_CF), len(df_CL4_G4_DCF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G4_CF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G4_CF=np.nanmean(RH,axis=0)
temp_CL4_G4_CF=np.nanmean(T,axis=0)
dewp_CL4_G4_CF=np.nanmean(DP,axis=0)
mixr_CL4_G4_CF=np.nanmean(MX,axis=0)
v_CL4_G4_CF=np.nanmean(V,axis=0)
u_CL4_G4_CF=np.nanmean(U,axis=0)
wsp_CL4_G4_CF=np.sqrt(u_CL4_G4_CF**2 + v_CL4_G4_CF**2)
wdir_CL4_G4_CF=np.arctan2(-u_CL4_G4_CF, -v_CL4_G4_CF)*(180/np.pi)
wdir_CL4_G4_CF[(u_CL4_G4_CF == 0) & (v_CL4_G4_CF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G4_DCF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G4_DCF=np.nanmean(RH,axis=0)
temp_CL4_G4_DCF=np.nanmean(T,axis=0)
dewp_CL4_G4_DCF=np.nanmean(DP,axis=0)
mixr_CL4_G4_DCF=np.nanmean(MX,axis=0)
v_CL4_G4_DCF=np.nanmean(V,axis=0)
u_CL4_G4_DCF=np.nanmean(U,axis=0)
wsp_CL4_G4_DCF=np.sqrt(u_CL4_G4_DCF**2 + v_CL4_G4_DCF**2)
wdir_CL4_G4_DCF=np.arctan2(-u_CL4_G4_DCF, -v_CL4_G4_DCF)*(180/np.pi)
wdir_CL4_G4_DCF[(u_CL4_G4_DCF == 0) & (v_CL4_G4_DCF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#CF
temperature_c=temp_CL4_G4_CF
dewpoint_c=dewp_CL4_G4_CF
wsp=wsp_CL4_G4_CF*1.943844
wdir=wdir_CL4_G4_CF

mydataG4_CF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C4')))
#DCF
temperature_c=temp_CL4_G4_DCF
dewpoint_c=dewp_CL4_G4_DCF
wsp=wsp_CL4_G4_DCF*1.943844
wdir=wdir_CL4_G4_DCF

mydataG4_DCF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Cold Fronts 4K','C4')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG4_CF)
S2=SkewT.Sounding(soundingdata=mydataG4_DCF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C4_CF_Dif.png', format='png', dpi=1200)

#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#                           Warm Fronts
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
#*****************************************************************************\
# Cluster 1
#*****************************************************************************\
df_CL4_G1 = df_mycluwfro[df_mycluwfro['CL_4']==1]
df_CL4_G1_DWF=df_CL4_G1[np.isfinite(df_CL4_G1['Dist WFront'])]
df_CL4_G1_WF=df_CL4_G1[np.isnan(df_CL4_G1['Dist WFront'])]
print len(df_CL4_G1),len(df_CL4_G1_WF), len(df_CL4_G1_DWF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G1_WF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G1_WF=np.nanmean(RH,axis=0)
temp_CL4_G1_WF=np.nanmean(T,axis=0)
dewp_CL4_G1_WF=np.nanmean(DP,axis=0)
mixr_CL4_G1_WF=np.nanmean(MX,axis=0)
v_CL4_G1_WF=np.nanmean(V,axis=0)
u_CL4_G1_WF=np.nanmean(U,axis=0)
wsp_CL4_G1_WF=np.sqrt(u_CL4_G1_WF**2 + v_CL4_G1_WF**2)
wdir_CL4_G1_WF=np.arctan2(-u_CL4_G1_WF, -v_CL4_G1_WF)*(180/np.pi)
wdir_CL4_G1_WF[(u_CL4_G1_WF == 0) & (v_CL4_G1_WF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G1_DWF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G1_DWF=np.nanmean(RH,axis=0)
temp_CL4_G1_DWF=np.nanmean(T,axis=0)
dewp_CL4_G1_DWF=np.nanmean(DP,axis=0)
mixr_CL4_G1_DWF=np.nanmean(MX,axis=0)
v_CL4_G1_DWF=np.nanmean(V,axis=0)
u_CL4_G1_DWF=np.nanmean(U,axis=0)
wsp_CL4_G1_DWF=np.sqrt(u_CL4_G1_DWF**2 + v_CL4_G1_DWF**2)
wdir_CL4_G1_DWF=np.arctan2(-u_CL4_G1_DWF, -v_CL4_G1_DWF)*(180/np.pi)
wdir_CL4_G1_DWF[(u_CL4_G1_DWF == 0) & (v_CL4_G1_DWF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#WF
temperature_c=temp_CL4_G1_WF
dewpoint_c=dewp_CL4_G1_WF
wsp=wsp_CL4_G1_WF*1.943844
wdir=wdir_CL4_G1_WF

mydataG1_WF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C1')))
#DWF
temperature_c=temp_CL4_G1_DWF
dewpoint_c=dewp_CL4_G1_DWF
wsp=wsp_CL4_G1_DWF*1.943844
wdir=wdir_CL4_G1_DWF

mydataG1_DWF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C1')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG1_WF)
S2=SkewT.Sounding(soundingdata=mydataG1_DWF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C1_WF_Dif.png', format='png', dpi=1200)

#*****************************************************************************\
# Cluster 2
#*****************************************************************************\

df_CL4_G2 = df_mycluwfro[df_mycluwfro['CL_4']==2]
df_CL4_G2_DWF=df_CL4_G2[np.isfinite(df_CL4_G2['Dist WFront'])]
df_CL4_G2_WF=df_CL4_G2[np.isnan(df_CL4_G2['Dist WFront'])]
print len(df_CL4_G2),len(df_CL4_G2_WF), len(df_CL4_G2_DWF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G2_WF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G2_WF=np.nanmean(RH,axis=0)
temp_CL4_G2_WF=np.nanmean(T,axis=0)
dewp_CL4_G2_WF=np.nanmean(DP,axis=0)
mixr_CL4_G2_WF=np.nanmean(MX,axis=0)
v_CL4_G2_WF=np.nanmean(V,axis=0)
u_CL4_G2_WF=np.nanmean(U,axis=0)
wsp_CL4_G2_WF=np.sqrt(u_CL4_G2_WF**2 + v_CL4_G2_WF**2)
wdir_CL4_G2_WF=np.arctan2(-u_CL4_G2_WF, -v_CL4_G2_WF)*(180/np.pi)
wdir_CL4_G2_WF[(u_CL4_G2_WF == 0) & (v_CL4_G2_WF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G2_DWF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G2_DWF=np.nanmean(RH,axis=0)
temp_CL4_G2_DWF=np.nanmean(T,axis=0)
dewp_CL4_G2_DWF=np.nanmean(DP,axis=0)
mixr_CL4_G2_DWF=np.nanmean(MX,axis=0)
v_CL4_G2_DWF=np.nanmean(V,axis=0)
u_CL4_G2_DWF=np.nanmean(U,axis=0)
wsp_CL4_G2_DWF=np.sqrt(u_CL4_G2_DWF**2 + v_CL4_G2_DWF**2)
wdir_CL4_G2_DWF=np.arctan2(-u_CL4_G2_DWF, -v_CL4_G2_DWF)*(180/np.pi)
wdir_CL4_G2_DWF[(u_CL4_G2_DWF == 0) & (v_CL4_G2_DWF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#WF
temperature_c=temp_CL4_G2_WF
dewpoint_c=dewp_CL4_G2_WF
wsp=wsp_CL4_G2_WF*1.943844
wdir=wdir_CL4_G2_WF

mydataG2_WF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C2')))
#DWF
temperature_c=temp_CL4_G2_DWF
dewpoint_c=dewp_CL4_G2_DWF
wsp=wsp_CL4_G2_DWF*1.943844
wdir=wdir_CL4_G2_DWF

mydataG2_DWF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C2')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG2_WF)
S2=SkewT.Sounding(soundingdata=mydataG2_DWF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C2_WF_Dif.png', format='png', dpi=1200)
#*****************************************************************************\
# Cluster 3
#*****************************************************************************\


df_CL4_G3 = df_mycluwfro[df_mycluwfro['CL_4']==3]
df_CL4_G3_DWF=df_CL4_G3[np.isfinite(df_CL4_G3['Dist WFront'])]
df_CL4_G3_WF=df_CL4_G3[np.isnan(df_CL4_G3['Dist WFront'])]
print len(df_CL4_G3),len(df_CL4_G3_WF), len(df_CL4_G3_DWF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G3_WF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G3_WF=np.nanmean(RH,axis=0)
temp_CL4_G3_WF=np.nanmean(T,axis=0)
dewp_CL4_G3_WF=np.nanmean(DP,axis=0)
mixr_CL4_G3_WF=np.nanmean(MX,axis=0)
v_CL4_G3_WF=np.nanmean(V,axis=0)
u_CL4_G3_WF=np.nanmean(U,axis=0)
wsp_CL4_G3_WF=np.sqrt(u_CL4_G3_WF**2 + v_CL4_G3_WF**2)
wdir_CL4_G3_WF=np.arctan2(-u_CL4_G3_WF, -v_CL4_G3_WF)*(180/np.pi)
wdir_CL4_G3_WF[(u_CL4_G3_WF == 0) & (v_CL4_G3_WF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G3_DWF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G3_DWF=np.nanmean(RH,axis=0)
temp_CL4_G3_DWF=np.nanmean(T,axis=0)
dewp_CL4_G3_DWF=np.nanmean(DP,axis=0)
mixr_CL4_G3_DWF=np.nanmean(MX,axis=0)
v_CL4_G3_DWF=np.nanmean(V,axis=0)
u_CL4_G3_DWF=np.nanmean(U,axis=0)
wsp_CL4_G3_DWF=np.sqrt(u_CL4_G3_DWF**2 + v_CL4_G3_DWF**2)
wdir_CL4_G3_DWF=np.arctan2(-u_CL4_G3_DWF, -v_CL4_G3_DWF)*(180/np.pi)
wdir_CL4_G3_DWF[(u_CL4_G3_DWF == 0) & (v_CL4_G3_DWF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#WF
temperature_c=temp_CL4_G3_WF
dewpoint_c=dewp_CL4_G3_WF
wsp=wsp_CL4_G3_WF*1.943844
wdir=wdir_CL4_G3_WF

mydataG3_WF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C3')))
#DWF
temperature_c=temp_CL4_G3_DWF
dewpoint_c=dewp_CL4_G3_DWF
wsp=wsp_CL4_G3_DWF*1.943844
wdir=wdir_CL4_G3_DWF

mydataG3_DWF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C3')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG3_WF)
S2=SkewT.Sounding(soundingdata=mydataG3_DWF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C3_WF_Dif.png', format='png', dpi=1200)
#*****************************************************************************\
# Cluster 4
#*****************************************************************************\


df_CL4_G4 = df_mycluwfro[df_mycluwfro['CL_4']==4]
df_CL4_G4_DWF=df_CL4_G4[np.isfinite(df_CL4_G4['Dist WFront'])]
df_CL4_G4_WF=df_CL4_G4[np.isnan(df_CL4_G4['Dist WFront'])]
print len(df_CL4_G4),len(df_CL4_G4_WF), len(df_CL4_G4_DWF)

#*****************************************************************************\
# With Fronts
#*****************************************************************************\
df=df_CL4_G4_WF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G4_WF=np.nanmean(RH,axis=0)
temp_CL4_G4_WF=np.nanmean(T,axis=0)
dewp_CL4_G4_WF=np.nanmean(DP,axis=0)
mixr_CL4_G4_WF=np.nanmean(MX,axis=0)
v_CL4_G4_WF=np.nanmean(V,axis=0)
u_CL4_G4_WF=np.nanmean(U,axis=0)
wsp_CL4_G4_WF=np.sqrt(u_CL4_G4_WF**2 + v_CL4_G4_WF**2)
wdir_CL4_G4_WF=np.arctan2(-u_CL4_G4_WF, -v_CL4_G4_WF)*(180/np.pi)
wdir_CL4_G4_WF[(u_CL4_G4_WF == 0) & (v_CL4_G4_WF == 0)]=0

#*****************************************************************************\
# Without Fronts
#*****************************************************************************\
df=df_CL4_G4_DWF
RH=np.empty([len(df),91])*np.nan
U=np.empty([len(df),91])*np.nan
V=np.empty([len(df),91])*np.nan
T=np.empty([len(df),91])*np.nan
DP=np.empty([len(df),91])*np.nan
MX=np.empty([len(df),91])*np.nan


for i in range(0,len(df)):
    RH[i,:]=np.array(df['RH'][i])
    U[i,:]=np.array(df['u'][i])
    V[i,:]=np.array(df['v'][i])
    T[i,:]=np.array(df['temp'][i])
    DP[i,:]=np.array(df['dewp'][i])
    MX[i,:]=np.array(df['mixr'][i])

#Mean profiles
rhum_CL4_G4_DWF=np.nanmean(RH,axis=0)
temp_CL4_G4_DWF=np.nanmean(T,axis=0)
dewp_CL4_G4_DWF=np.nanmean(DP,axis=0)
mixr_CL4_G4_DWF=np.nanmean(MX,axis=0)
v_CL4_G4_DWF=np.nanmean(V,axis=0)
u_CL4_G4_DWF=np.nanmean(U,axis=0)
wsp_CL4_G4_DWF=np.sqrt(u_CL4_G4_DWF**2 + v_CL4_G4_DWF**2)
wdir_CL4_G4_DWF=np.arctan2(-u_CL4_G4_DWF, -v_CL4_G4_DWF)*(180/np.pi)
wdir_CL4_G4_DWF[(u_CL4_G4_DWF == 0) & (v_CL4_G4_DWF == 0)]=0


#*****************************************************************************\
#Plot
#*****************************************************************************\
height_m=hlev_yotc
pressure_pa=plev_yotc
#WF
temperature_c=temp_CL4_G4_WF
dewpoint_c=dewp_CL4_G4_WF
wsp=wsp_CL4_G4_WF*1.943844
wdir=wdir_CL4_G4_WF

mydataG4_WF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C4')))
#DWF
temperature_c=temp_CL4_G4_DWF
dewpoint_c=dewp_CL4_G4_DWF
wsp=wsp_CL4_G4_DWF*1.943844
wdir=wdir_CL4_G4_DWF

mydataG4_DWF=dict(zip(('hght','pres','temp','dwpt','drct','sknt','StationNumber','SoundingDate'),(height_m,pressure_pa,temperature_c,dewpoint_c,wdir,wsp,'Warm Fronts 4K','C4')))

# #Individuals
S=SkewT.Sounding(soundingdata=mydataG4_WF)
S2=SkewT.Sounding(soundingdata=mydataG4_DWF)
S.make_skewt_axes()
S.add_profile(color='r',bloc=0)
S.soundingdata=S2.soundingdata
S.add_profile(color='b',bloc=1)
plt.savefig(path_data_save + '4K_C4_WF_Dif.png', format='png', dpi=1200)
show()
