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
				Environment.append({})
				Environment[i][item]=[0,"(\\x"+item+"Lock,\\yMax)"]
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

for domain in Environment[0]:
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

for items in PreConditions:
	state=items.pop(0)

	if state=="location":
		player=items.pop(0)
		domain=items.pop(0)
		if Players[player][4]==None:
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*1)"
			Players[player][4]=domain
	
	if state=="locked":
		player=items.pop(0)
		domain=items.pop(0)
		N=0
		for Domains in Environment:
			if domain in Domains: break
			else: N+=1
		if Players[player][4]==domain:
			Environment[N][domain][0]=Players[player][0]

if len(PreConditions)>0: step=2
else: step=1

for items in MainFlow:
	action=items.pop(0)

	if action=="enter":
		player=items.pop(0)
		domain=items.pop(0)
		if Environment[0][domain][0]==0 and Players[player][4]!=domain:
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
		elif int(Environment[0][domain][0])>0:
			print("A Player cannot Enter a Locked Domain.");step-=1
		elif Players[player][4]==domain:
			print("A Player cannot Enter a Domain they are already in.");step-=1
	elif action=="exit":
		player=items.pop(0)
		domain=items.pop(0)
		if Environment[0][domain][0]==0 and Players[player][4]!=None:
			fileOut.extend(
				(
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw[dotted](\\x"+player+",\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{}--(\\xMax,\\yMax-\\step*"+str(step)+");"
				)
			)
			Players[player][3]=Players[player][2]="(\\xMax,\\yMax-\\step*"+str(step)+")"
			Players[player][4]=None
		elif int(Environment[0][domain][0])>0:
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
				message=message.strip("enc").strip("[").strip("]")
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

	elif action=="lock":
		player=items.pop(0)
		domain=items.pop(0)
		N=0
		for Domains in Environment:
			if domain in Domains: break
			else: N+=1
		if Players[player][4]==domain and Environment[N][domain][0]==0:	
			fileOut.extend(
				(
				"\n\\draw[dashed]"+Environment[N][domain][1]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Lock$]{};"
				)
			)
			Environment[N][domain][0]=Players[player][0]
			Environment[N][domain][1]="(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif Players[player][4]!=domain:
			print("A Player must be in the same Domain to Lock it.");step-=1
		elif Environment[N][domain][0]!=0:
			 print("Domain is already Locked.");step-=1

	elif action=="unlock":
		player=items.pop(0)
		domain=items.pop(0)
		N=0
		for Domains in Environment:
			if domain in Domains: break
			else: N+=1
		if Players[player][4]==domain and Environment[N][domain][0]!=0:	
			fileOut.extend(
				(
				"\n\\draw"+Environment[N][domain][1]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Unlock$]{};"
				)
			)
			Environment[N][domain][0]=0
			Environment[N][domain][1]="(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif Players[player][4]!=domain:
			print("A Player must be in the same Domain to Unlock it.");step-=1
		elif Environment[N][domain][0]==0:
			print("Domain is already Unlocked.");step-=1
	step+=1
for player in Players:
	if Players[player][3]==None: Players[player][3] =Players[player][2]
	fileOut.append("\n\\draw"+Players[player][3]+"node[cross]{};")
fileOut.append("\n\\draw")
if int(Environment[0][domain][0])==0: fileOut.append("[dashed]")
fileOut.extend(
	(
	Environment[0][domain][1]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",	 
	"\n\\draw(\\x"+domain+"Lock,\yMax-\\step*"+str(step)+")node[rectangle,fill,inner sep=0.5ex]{};",
	"\n\\draw[very thick] (\\x"+domain+"-\\flowSpacing-\\unit*2,\yMax-\\step*"+str(step)+"+\\unit) rectangle (\\x"+domain+",\\y"+domain+");",
	"\n\\draw(\\x"+domain+"Lock,\\yMax)node[rectangle,fill,inner sep=0.5ex,label=right:$Lock$]{};"
	)
)

fileOut.extend(
	(
	"\n\\end{tikzpicture}",
	"\n\\end{document}"
	)
)
if len(PostConditions)>0:
	print("---------------")
	print("Post Conditions")
Failed=0
for items in PostConditions:
	state=items[0]
	

	if state=="location":
		if Players[items[1]][4]==items[2]: 
			print("True:",items)
		else: 
			print("False:",items)
			Failed+=1
	
	if state=="locked":
		if len(items)==3:
			player=items[1]
			domain=items[2]
		else:
			player=None
			domain=items[1]
		N=0
		for Domains in Environment:
			if domain in Domains: 
				if player==None and Environment[N][domain][0]!=0: print("True:",items);break
				elif player==None: print("False:",items);Failed+=1;break
				elif Environment[N][domain][0]==Players[player][0]: print("True:",items);break
				else: print("False:",items);Failed+=1;break
			else: N+=1

if len(PostConditions)>0:
	print("Passed",str(len(PostConditions)-Failed)+'/'+str(len(PostConditions)))
	print("---------------")


file = open('out.tex', 'w') #write to file 
for line in fileOut:
     file.write(line)
file.close() #close file
subprocess.call(["pdflatex","out.tex"])