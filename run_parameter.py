import numpy as np
from scipy.optimize import leastsq
from scipy.optimize import fmin_slsqp
from Simpson_BTK import BTK_Diff
import pandas as pd
import time
from data_to_csv import Dataplot
import random

# Rename Columns
def arrange_dataframe(df):
	df.columns = ['Vdc', 'G/GN']
	return df

def errors(parameter,V,T,factor,G_experiment):
	G= BTK_Diff(parameter,V,T)
	index_max = G_experiment.index(max(G_experiment))
	index_max_2 = len(V) - index_max
	index_min = G_experiment.index(min(G_experiment))
	res = 0
	for number in range(len(G)):
		if number < index_max + 25 and number >index_max -25:
			res = res + factor * (G[number] - G_experiment[number])**2
		elif number < index_max_2 + 25 and number >index_max_2 -25:
			res = res + factor * (G[number] - G_experiment[number])**2
		elif number < index_min + 13 and number >index_min -13:
			res = res + 3 * factor * (G[number] - G_experiment[number])**2
		else:
			res = res + (G[number] - G_experiment[number])**2
	return res

def run_parameter(filenames,Ts,bound):
	for number in range(len(filenames)):
		filename = 'Datas/' + filenames[number]
		df2 = pd.read_csv(filename)
		# Delta    Gama     Barrier Height    Spin Polarization
		bounds = bound[number]
		print("The range of fitting parameters.")
		print("Delta : ",bounds[0])
		print("Gama  : ",bounds[1])
		print("  Z   : ",bounds[2])
		print("  P   : ",bounds[3])

		time.sleep(0.5) 

		time_start=time.time()


		df2 = arrange_dataframe(df2)

		T = float(Ts[number])

		print("Temperature : ",T)
		parameter = [1.3, 0.4, 1.5, 0.0]
#		for i in range(4):
#			parameter[i] += random.uniform(0,0.1)
		print('Parameters: ',parameter)
		V = df2['Vdc'].values
		G_experiment = df2['G/GN'].values
		G_experiment = list(G_experiment)
		print("Data points : ",len(V))

		''' 梯度下降 '''
		# Weightness 
		factor = 38
		# annealing
		myerror = []
		myparameter = []

		for i in range(10):
			
			r1 = fmin_slsqp(errors,parameter,args=(V,T,factor,G_experiment),iter = 100,bounds = bounds)
			#r1 = parameter
			time_end=time.time()
			print('Parameters fitting totally cost : ',round(time_end-time_start,4),'s !')
			print('Superconducting Gap:' + str(round(r1[0],4)))
			print('Gama:' + str(round(r1[1],4)))
			print('Barrier Height:' + str(round(r1[2],4)))
			print('Spin Polarization:' + str(round(r1[3],4)))
			print(errors(r1,V,T,factor,G_experiment))
			for j in range(4):
				parameter[j] = r1[j] + random.uniform(-0.01*(10-i),0.01*(10-i))
#				parameter[j] += random.uniform(-0.0003*(9-i)*(8-i)*(7-i),0.0003*(9-i)*(8-i)*(7-i))
				if parameter[j] < 0:
					parameter[j] = 0
		r1 = fmin_slsqp(errors,r1,args=(V,T,factor,G_experiment),iter = 100,bounds = bounds)
		Dataplot(r1,T,df2,'Vdc','G/GN',filename)

if __name__ == "__main__":
	filenames = ['b2.csv','t1.csv']
	Ts = [1.6,1.66]
	bound = [[(0.5,2),(0,2),(0,10),(0,1)],[(0.5,2),(0,2),(0,10),(0,1)]]
	run_parameter(filenames,Ts,bound)
