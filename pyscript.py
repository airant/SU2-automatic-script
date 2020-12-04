#!/usr/bin/env python
# -*- coding: utf-8 -* 
import os
import sys
from optparse import OptionParser

def main():
	# Command Line Options
	parser=OptionParser()
	#parser.add_option("-f","--file",dest="filename",help="read config from FILE",metavar="FILE")
	parser.add_option("-n", "--partitions", dest="partitions", default=2,help="number of PARTITIONS", metavar="PARTITIONS")

	(options, args) = parser.parse_args()
	options.partitions  = int( options.partitions )

	#if options.filename == None:
		#raise Exception("No config file provided. Use -f flag")

	flow = boundary()
	flow.Mach = [0.8]
	flow.AlphaAngle = [0,6,12,18,24,30]
	flow.BetaAngle  = [0]
	flow.checkBoundary()

	#Read config file
	conf = SU2Config()
	conf.ReadConfigFile('config.cfg')#默认配置文件：configbase.cfg
	conf.ReadConfig('MESH_FILENAME')

	index = 0

	CreatAeroCof('Aerocof.txt')
	for iIter in range(len(flow.AlphaAngle)):
		for jIter in range(len(flow.BetaAngle)):
			for kIter in range(len(flow.Mach)):
				index = index + 1
				addstr = 'Alpha'+str(flow.AlphaAngle[iIter])+'Beta'+str(flow.BetaAngle[jIter])+'Ma'+str(flow.Mach[kIter])
				os.mkdir(addstr)
				conf.WriteConfig(flow.Mach[kIter],'MACH_NUMBER')
				conf.WriteConfig(flow.AlphaAngle[iIter],'AOA')
				conf.WriteConfig(flow.BetaAngle[jIter],'SIDESLIP_ANGLE')

				#For Linux systems:
				RunLinuxSU2Case(addstr,conf.MeshName,options.partitions)

				aero = AeroCof(flow.AlphaAngle[iIter],flow.BetaAngle[jIter],flow.Mach[kIter])
				aero.ReadCof(addstr)
				WriteAeroCof('Aerocof.txt',aero)

class boundary():
	def __init__(self):
		pass
		self.Mach = 0
		self.AlphaAngle = 0
		self.BetaAngle = 0
		self.Pressure = 0
		self.Temperature = 0
	def checkBoundary(self):
		print('Mach number:',self.Mach)
		print('alpha:',self.AlphaAngle)
		print('beta :',self.BetaAngle)

class SU2Config():
	def __init__(self):
		self.ConfigFileName = ''
		self.Config = ''
		self.MeshName = ''
	def ReadConfigFile(self,filename):
		self.ConfigFileName = filename
		f = open(filename)
		self.Config = f.readlines()
		f.close()
		print('Read configure file:',filename)
	def ReadConfig(self,configname):
		p = self.SearchStr(configname)
		config = self.Config[p].split(configname+'= ')
		self.MeshName= config[1]

	def SearchStr(self,strname):
		index = 0
		for item in self.Config:
			a = item.find(strname)
			if a ==0:
				break
			index = index + 1
		return index

	def WriteConfig(self,conf,confTag):
		p = self.SearchStr(confTag)
		self.Config[p] = str(confTag) + ' = ' + str(conf) + '\n'
		fnew = open('config.cfg','w+')
		fnew.writelines(self.Config)
		fnew.close()


def CreatAeroCof(filename):
	f = open('Aerocof.txt','w')
	cfdnote = 'alpha beta Mach Cl Cd LD CMx CMy CMz\r\n'
	f.write(cfdnote)
	f.close()

def WriteAeroCof(filename,AeroCof):
	fans=open('Aerocof.txt','a')
	info= str(AeroCof.Alpha)+ ' '+str(AeroCof.Beta)+' '+str(AeroCof.Mach)+' '
	cfdans = str(AeroCof.Cl) +' '+str(AeroCof.Cd)+' '+str(AeroCof.LD)+' '+str(AeroCof.Cmx)+' '+str(AeroCof.Cmy)+' '+str(AeroCof.Cmz)
	fans.write(info)
	fans.write(cfdans)
	fans.write('\r\n')
	fans.close()

def RunLinuxSU2Case(addstr,meshfilename,n):
	os.system('cp config.cfg ./'+addstr)#复制每个case的config文件
	print('running SU2 CFD...')
	os.system('parallel_computation.py -f config.cfg -n '+str(n))#运行
	#os.system('cp forces_breakdown.dat ./'+addstr)#复制每个case的力系数文件
	#os.system('cp flow.vtk ./'+addstr)#复制每个case的流场文件
	#os.system('cp surface_flow.vtk ./'+addstr)#复制每个case的流场文件
	os.system('mv forces_breakdown.dat ./'+addstr)
	os.system('mv flow.dat ./'+addstr)
	os.system('mv surface_flow.dat ./'+addstr)

class AeroCof():
	def __init__(self,a,b,m):
		self.Alpha = a
		self.Beta  = b
		self.Mach  = m
		self.Cl = 0
		self.Cd = 0
		self.LD = 0
		self.Cmx = 0
		self.Cmy = 0
		self.Cmz = 0
	def ReadCof(self,FolderStr):
		systemsep = os.sep
		f = open(FolderStr + systemsep +'forces_breakdown.dat')
		confile = f.readlines()
		f.close

		for line in confile:
			line_list = line.split()
			if len(line_list) !=0:
				if ((line_list[0] == 'Total') and (line_list[1]=='CL:')):
					self.Cl = line_list[2]
					print('cl:',self.Cl)
				if ((line_list[0] == 'Total') and (line_list[1]=='CD:')):
					self.Cd = line_list[2]
					print('cd:',self.Cd)
				if ((line_list[0] == 'Total') and (line_list[1]=='CL/CD:')):
					self.LD = line_list[2]
				if ((line_list[0] == 'Total') and (line_list[1]=='CMx:')):
					self.Cmx = line_list[2]
				if ((line_list[0] == 'Total') and (line_list[1]=='CMy:')):
					self.Cmy = line_list[2]
				if ((line_list[0] == 'Total') and (line_list[1]=='CMz:')):
					self.Cmz = line_list[2]


				


if __name__ == '__main__':
    main()
