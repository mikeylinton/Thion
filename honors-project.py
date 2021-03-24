import re;import argparse;import subprocess
inputfile=open('ScenarioA.in','r')

parser=argparse.ArgumentParser(description='Honors Project by Michael Linton.')
parser.add_argument('--verbose','-v',action=argparse.BooleanOptionalAction,help='Verbose')
args=parser.parse_args()

PLACEHOLDER=None;section=None
Players={}
Environment=[]
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
				i=len(Environment)
				Environment.append([])
				Environment[i]=[item,0,"(\\x"+item+"Lock,\\yMax)"]
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
				Players[player]=[pAuthority,Messages,"(\\x"+player+",\\yMax)",None,None]

	elif not re.search("^#",line):
		print("\nUnexpected error:",line,'\n')

fileOut.extend(
	(
	"\\documentclass{article}",
	"\\usepackage{tikz}",
	"\\usetikzlibrary{shapes.misc}",
	"\\usetikzlibrary{arrows.meta}",
	"\\usepackage{nopageno}",
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
		"\n\\newcommand\\y"+domain[0]+"{\\yMax-\\unit}",
		"\n\\newcommand\\x"+domain[0]+"{\\xMax-\\step/2}",
		"\n\\newcommand\\x"+domain[0]+"Lock{\\x"+domain[0]+"-\\step/2}"
		)
	)

N=len(Players)
fileOut.append("\n\\newcommand\\flowSpacing{\\step*"+str((N+1))+"}")
for player in Players:
	fileOut.append("\n\\newcommand\\x"+player+"{\\xBuildingALock-\\step*"+str(N)+"}");N-=1

fileOut.extend(
	(	
	"\n\\begin{document}",
	"\n\\pdfpageheight 450mm",
  	"\n\\pdfpagewidth 210mm",
    "\n\\hspace*{-50mm}"
	"\\vspace*{-100mm}",
    "\n\\tikzset{cross/.style={cross out,draw=black},cross/.default={1ex}}",
    "\n\\begin{tikzpicture}[>=latex]"
	)
)

for player in Players:
	fileOut.append("\n\\draw(\\x"+player+",\\yMax)node[label=above:$"+player+"("+Players[player][0]+")$]{};")

step=1
for items in MainFlow:
#	print(items)
	action=items.pop(0)

	if action=="enter":
		player=items.pop(0)
		domain=items.pop(0)
		if Environment[0][1]==0 and Players[player][4]!=domain:
			if Players[player][3]==None:
				fileOut.append("\n\\draw[dotted](\\x"+player+",\\yMax)node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};")
			else:
				fileOut.extend(
					(
					"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{};",
					"\n\\draw[dotted](\\xMax,\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};"
					)
				)
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
			Players[player][4]=domain
		elif int(Environment[0][1])>0:
			print("A Player cannot Enter a Locked Domain.");step-=1
		elif Players[player][4]==domain:
			print("A Player cannot Enter a Domain they are already in.");step-=1
	elif action=="exit":
		player=items.pop(0)
		domain=items.pop(0)
		if Environment[0][1]==0 and Players[player][4]!=None:
			fileOut.extend(
				(
				"\n\\draw"+Players[player][2]+"--(\\x"+player+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw[dotted](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\xMax,\\yMax-\\step*"+str(step)+");"
				)
			)
			Players[player][3]=Players[player][2]="(\\xMax,\\yMax-\\step*"+str(step)+")"
			Players[player][4]=None
		elif int(Environment[0][1])>0:
			print("A Player cannot Exit a Locked Domain.");step-=1
		elif Players[player][4]==None:
			print("A Player cannot Exit outside the Environment.");step-=1
	elif action=="share":
		sender=items.pop(0)
		message=items.pop(0)
		receiver=items.pop(0)
		if Players[sender][4]==Players[receiver][4] and sender!=receiver and Players[sender][4]!=None:
			fileOut.append("\n\\draw[")
			if re.search("^enc(.*)$",message):
				message=message.strip("enc[").strip("]")
				fileOut.append("dotted,")
			fileOut.extend(
				(
				"-{Latex[angle=45:2ex]}](\\x"+sender+",\\yMax-\step*"+str(step)+")--(\\x"+receiver+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[sender][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+sender+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[receiver][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+receiver+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+sender+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Msg("+Players[sender][1][message]+")$]{};"
				)
			)
			Players[sender][3]=Players[sender][2]="(\\x"+sender+",\\yMax-\\step*"+str(step)+")"
			Players[receiver][3]="(\\x"+receiver+",\\yMax-\\step*"+str(step)+")"
			Players[receiver][1][message]=Players[sender][1][message]
		elif Players[sender][4]!=Players[receiver][4]:
			print("Both Players must be in the same Domain to Share a Message.");step-=1
		elif sender==receiver:
			print("A player cannot share a Message to themselves.");step-=1
		elif Players[sender][4]==None:
			print("Both Players must be in a Domain to share a Message.");step-=1
	elif action=="lock" or action=="unlock":
		player=items.pop(0)
		domain=items.pop(0)
		if Players[player][4]==domain:	
			N=0
			for e in Environment:
				if e[0]==domain: break
				else: N+=1
			fileOut.append("\n\\draw")
			if action=="lock": fileOut.append("[dashed]")
			fileOut.extend(
				(
				Environment[N][2]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$"
				)
			)
			if action=="lock": 
				fileOut.append("Lock$]{};")
				Environment[0][1]=Players[player][0]
			else: 
				fileOut.append("Unlock$]{};")
				Environment[0][1]=0
			Environment[N][2]="(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		else:
			if action=="lock":
				print("A Player must be in the same Domain to Lock it.")
			else:
				print("A Player must be in the same Domain to Unlock it.")
			step-=1
	step+=1
for player in Players:
	if Players[player][3]==None: Players[player][3] =Players[player][2]
	fileOut.append("\n\\draw"+Players[player][3]+"node[cross]{};")
fileOut.append("\n\\draw")
if int(Environment[0][1])==0: fileOut.append("[dashed]")
fileOut.extend(
	(
	Environment[0][2]+"--(\\x"+Environment[0][0]+"Lock,\\yMax-\\step*"+str(step)+");",	 
	"\n\\draw(\\x"+Environment[0][0]+"Lock,\yMax-\\step*"+str(step)+")node[rectangle,fill,inner sep=0.5ex]{};",
	"\n\\draw[very thick] (\\x"+Environment[0][0]+"-\\flowSpacing-\\unit*2,\yMax-\\step*"+str(step)+"+\\unit) rectangle (\\x"+Environment[0][0]+",\\y"+Environment[0][0]+");",
	"\n\\draw(\\x"+Environment[0][0]+"Lock,\\yMax)node[rectangle,fill,inner sep=0.5ex,label=right:$Lock$]{};"
	)
)

fileOut.extend(
	(
	"\n\\end{tikzpicture}",
	"\n\\end{document}"
	)
)
#for e in fileOut:
#	print(e)

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