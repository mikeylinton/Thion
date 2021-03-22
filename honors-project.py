import re;import argparse;import subprocess
inputfile=open('ScenarioA.in','r')

parser=argparse.ArgumentParser(description='Honors Project by Michael Linton.')
parser.add_argument('--verbose','-v',action=argparse.BooleanOptionalAction,help='Verbose')
args=parser.parse_args()

PLACEHOLDER=None;section=None
Players={}
Environment={}
PreConditions=[];MainFlow=[];PostConditions=[]
fileOut=[]

while True:
	line=inputfile.readline().strip()
	if not line:
		break

	if re.search("^\[.*\]$",line):
		item=line.strip('[').strip(']')
		sections=(
		"Environment",
		"Players",
		"PreConditions",
		"MainFlow",
		"PostConditions")
		if item in sections:
			section=item
		else:
			print("\nUnknown section type:",line,'\n',"Section types: [Environment] , [Players] , [Pre-conditions] , [Main-flow] , [Post-conditions]",'\n')
		line=inputfile.readline().strip()


	if re.search("^.*;$",line) and not re.search("^#",line):
		items=re.split(';+',line)
		items.remove('')
		for item in items:
			if section=="Environment":
				Environment[item]=0	#Default authority level
#				Domain,SubDomains=item.split('[');Domain=re.sub('\]$','',Domain)
#				head,tail=SubDomains.split(',');tail=re.sub('\]$','',tail)
				'''building,rooms=item.split('[');rooms=rooms.strip(']')
				rooms=re.split(',',rooms)
				Environment[building]=[0,False,{}]
				for room in rooms:
					Environment[building][2][room]=[0,False]'''
			elif section=="PreConditions" or section=="MainFlow" or section=="PostConditions":
				i=len(vars()[section])
				vars()[section].append([])
				action,elements=item.split('(');elements=elements.strip(')')
				elements=re.split(',',elements)
				vars()[section][i].append(action)
				for element in elements:
					vars()[section][i].append(element)

			elif section=="Players":
				Messages={}
				if re.search('^.*\[.*\]$',item):
					head,tail=item.split('[');messageList=tail.strip(']')
					player,pAuthority=head.split('(');pAuthority=pAuthority.strip(')')
					messageList=re.split(',',messageList)
					for message in messageList:
						name,mAuthority=message.split('(');mAuthority=mAuthority.strip(')')
						Messages[name]=mAuthority
				else:
					player,pAuthority=item.split('(');pAuthority=pAuthority.strip(')')
				Players[player]=[pAuthority,None,Messages,None]

	elif not re.search("^#",line):
		print("\nUnexpected error:",line,'\n')

fileOut.extend(
	(
	"\\documentclass{article}",
	"\n\\usepackage{tikz}",
	"\n\\usetikzlibrary{shapes.misc}",
	"\n\\usetikzlibrary{arrows.meta}",
	"\n\\usepackage{nopageno}",
	"\n\\newcommand\\unit{0.2675}",
	"\n\\newcommand\\step{\\unit*6}",
	"\n\\newcommand\\yMax{\\step*14}",
	"\n\\newcommand\\xMax{\\step*14}",
	"\n\\newcommand\\labelSpacing{\\step*0.4}",
	
	)
)

for domain in Environment:
fileOut.extend(
	(
	"\n\\newcommand\\y"+domain+"{\\yMax-\\unit}",
	"\n\\newcommand\\x"+domain+"{\\xMax-\\step/2}",
	"\n\\newcommand\\x"+domain+"Lock{\\x"+domain+"-\\step/2}"
	)
)

N=len(Players)
fileOut.append("\n\\newcommand\\flowSpacing{\\step*"+str((N+1))+"}")
for player in Players:
	fileOut.append("\n\\newcommand\\x"+player+"{\\xDLock-\\step*"+str(N)+"}");N-=1

fileOut.extend(
	(	
	"\n\\begin{document}",
    "\n\\hspace*{-50mm} \\vspace*{-100mm}",
    "\n\\tikzset{cross/.style={cross out,draw=black},cross/.default={1ex}}",
    "\n\\begin{tikzpicture}[>=latex]"
	)
)

for player in Players:
	fileOut.append("\n\\draw(\\x"+player+",\\yMax)node[circle,fill,inner sep=0.5ex,label=above:$"+player+"("+Players[player][0]+")$]{};")

step=0
for items in MainFlow:
	print(items)
	step+=1
	action=items.pop(0)

	if action=="enter":
		player=items.pop(0)
		domain=items.pop(0)
		if Players[player][3]==None:
			fileOut.append("\n\\draw[dotted](\\x"+player+",\\yMax)--(\\x"+player+",\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{};")
		else:
			fileOut.extend(
				(
				"\n\\draw"+Players[player][3]+"node[circle,fill,inner sep=0.5ex]{};",
        		"\n\\draw[dotted](\\xMax,\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{};"
				)
			)
		Players[player][3]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
	elif action=="exit":
		player=items.pop(0)
		domain=items.pop(0)
		fileOut.extend(
			(
			"\n\\draw"+Players[player][3]+"--(\\x"+player+",\\yMax-\\step*"+str(step)+");",
        	"\n\\draw[dotted](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\xMax,\\yMax-\\step*"+str(step)+");"
			)
		)
	elif action=="share" or action=="share.enc":
		source=items.pop(0).split('.')
		sender=source[0]
		originSender=source[len(source)-2]
		message=source[len(source)-1]
		print(len(source))
		receiver=items.pop(0)
		fileOut.extend(
			(
			"\n\\draw"+Players[sender][3]+"--(\\x"+sender+",\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{};",
        	"\n\\draw"+Players[receiver][3]+"--(\\x"+receiver+",\\yMax-\\step*"+str(step)+");",
        	"\n\\draw(\\x"+sender+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Msg("+Players[originSender][2][message]+")$]{};"
			)
		)
		if re.search(".enc$",action):
			fileOut.append("\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+sender+",\\yMax-\step*"+str(step)+")--(\\x"+receiver+",\\yMax-\\step*"+str(step)+");")
		else:
			fileOut.append("\n\\draw[-{Latex[angle=45:2ex]}](\\x"+sender+",\\yMax-\step*"+str(step)+")--(\\x"+receiver+",\\yMax-\\step*"+str(step)+");")
	elif action=="lock":
		player=items.pop(0)
		domain=items.pop(0)
		fileOut.extend(
			(
			"\n\\draw[dashed](\\xDLock,\\yMax-\step*0)--(\\xDLock,\\yMax-\\step*"+str(step)+");",
			"\n\\draw(\\xAlice,\\yMax-\\step*4)--(\\xAlice,\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{};",
			"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\xAlice,\\yMax-\\step*"+str(step)+")--(\\xDLock,\\yMax-\\step*"+str(step)+");",
			"\n\\draw(\\xAlice-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Lock$]{};"
			)
		)

fileOut.extend(
	(
	"\n\\end{tikzpicture}",
	"\n\\end{document}"
	)
)
for e in fileOut:
	print(e)

file = open('out.tex', 'w') #write to file 
for line in fileOut:
     file.write(line)
file.close() #close file
subprocess.call(["pdflatex","out.tex"])

'''if args.verbose:
	print("Environment");print("---------------")
	for building in Environment:
		print(building,':',Environment[building])
	print("---------------")

if args.verbose:
	print("Players");print("---------------")
	for player in Players:
		print(player,':',Players[player])
	print("---------------")

if args.verbose: print("PreConditions");print("---------------")
for string in PreConditions:
	state=string.pop(0)

	if state=="locked" or state=="unlocked":
		facility=string.pop(0)
		if state=="locked":
			locked=True
		else:
			locked=False
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			Environment[building][2][room][1]=locked
			if args.verbose: print(building,':',Environment[building])
		else:
			Environment[facility][1]=locked
			if args.verbose: print(building,':',Environment[facility])
		if args.verbose: print("---------------")
	
	if state=="location":
		player=string.pop(0)
		facility=string.pop(0)
		Players[player][1]=facility
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			if int(Environment[building][2][room][0])==0:
				Environment[building][2][room][0]=Players[player][0]
		else:
			if int(Environment[facility][0])==0:
				Environment[facility][0]=Players[player][0]
		if args.verbose: print(player,':',Players[player]);print("---------------")
		

if args.verbose: print("MainFlow");print("---------------")
unit=0
for string in MainFlow:
	if args.verbose: print(unit,string)
	action=string.pop(0)

	if action=="enter" or action=="exit" or action=="lock" or action=="unlock":
		#[player,facility]
		player=string.pop(0)
		facility=string.pop(0)
		empty=False
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			
			if action=="enter" and int(Environment[building][2][room][0])==0:
				Environment[building][2][room][0]=Players[player][0]	#Set Authority of room
			
			elif action=="exit":
				Players[player][1]=building	
				for p in Players:
					if Players[p][1]==facility:
						empty=False;break
				if empty:
					Environment[building][2][room][0]=0
			
			elif (action=="lock" or action=="unlock") and int(Environment[building][2][room][0])<=int(Players[player][0]):
				if action=="lock":
					Environment[building][2][room][1]=True
				else:
					Environment[building][2][room][1]=False
				 
		else:
			
			if action=="enter" and int(Environment[facility][0])==0:
				Environment[facility][0]=Players[player][0]
			
			elif action=="exit":
				Players[player][1]=None
				for p in Players:
					if Players[p][1]==facility:
						empty=False;break
				if empty:
					Environment[facility][0]=0
			
			elif (action=="lock" or action=="unlock") and int(Environment[facility][0])<=int(Players[player][0]):
				if action=="lock":
					Environment[facility][1]=True
				else:
					Environment[facility][1]=False
				
		if action=="enter":
			Players[player][1]=facility
		if args.verbose: print(building,':',Environment[building]);print(player,':',Players[player]);print("---------------")
	
	else:
		print("Action not found");print("---------------")

	if unit<10: print("Time",unit,"========")
	elif unit<100: print("Time",unit,"=======")
	else: print("Time",unit,"=======")
	for player in Players:
		facility=Players[player][1]
		if facility is not None:
			if re.search("\[.*\]",facility):
				building,room=facility.split('[');room=room.strip(']')
				print(player,'in',room,'in',building)
			else:
				print(player,'in',facility)
	print("===============")
	unit+=1
print("Total units:",unit);print("---------------")'''