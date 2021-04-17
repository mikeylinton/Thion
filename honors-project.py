import re;import argparse;import subprocess

parser=argparse.ArgumentParser(description='Honors Project by Michael Linton.')
parser.add_argument('--verbose','-v',action=argparse.BooleanOptionalAction,help='Verbose')
args=parser.parse_args()

PLACEHOLDER=None;section=None
Players={}
Environment=[]
PreConditions=[];MainFlow=[];PostConditions=[]
inputfile=open('inputFile','r')
fileReader=[]
fileOut=[]
ThreatReport=[]
FeasibilityReport=[]

while True:
	line=inputfile.readline().strip()
	if not line: break
	else: fileReader.append(line)

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
			print("\nUnknown section type:",line,'\n',"Section types: [Environment] , [Players] , [PreConditions] , [Main-flow] , [PostConditions]",'\n')

	elif re.search("^.*;$",line) and not re.search("^#",line):
		items=re.split(';+',line)
		items.remove('')
		for item in items:
			if section=="Environment":
				Environment.append([item,False,"(\\x"+item+"Lock,\\yMax)"])
			elif section=="PreConditions" or section=="MainFlow" or section=="PostConditions":
				i=len(vars()[section])
				vars()[section].append([])
				action,elements=item.split('(');elements=elements.strip(')')
				elements=re.split(',',elements)
				vars()[section][i].append(action.strip())
				for element in elements:
					vars()[section][i].append(element.strip())

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

for Domain in Environment:
	fileOut.extend(
		(
		"\n\\newcommand\\y"+Domain[0]+"{\\yMax-\\unit}",
		"\n\\newcommand\\x"+Domain[0]+"{\\xMax-\\step/2}",
		"\n\\newcommand\\x"+Domain[0]+"Lock{\\x"+Domain[0]+"-\\step/2}"
		)
	)
N=len(Players)
fileOut.append("\n\\newcommand\\flowSpacing{\\step*"+str((N+1))+"}")
for player in Players:
	fileOut.append("\n\\newcommand\\x"+player+"{\\x"+Environment[0][0]+"Lock-\\step*"+str(N)+"}");N-=1

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
		domain=items.pop(0)
		for Domain in Environment:
			if domain==Domain[0]: Domain[1]=True;break
			
		#for player in Players:
		#	if Players[player][4]==domain:
		#		Environment[N][1]=True;break

if len(PreConditions)>0: step=2
else: step=1
print("------------------------------")
print("----------- Report -----------")
print("------------------------------")
lineCount=1
for item in fileReader:
	lineCount+=1
	if item=="[MainFlow]": break

for items in MainFlow:
	action=items.pop(0)

	if action=="enter":
		player=items.pop(0)
		domain=items.pop(0)
		playerExists=False
		domainExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if not Environment[N][1] and Players[player][4]!=domain:
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
		elif not playerExists:
			print("KeyError: Player '"+player+"' not defined; line "+str(lineCount)+".");step-=1
		elif not domainExists:
			print("KeyError: Domain '"+domain+"' not defined; line "+str(lineCount)+".");step-=1
		elif Environment[N][1]: #and int(Players[Environment[0][domain][0]][0])>0:
			FeasibilityReport.append("'"+player+"' cannot Enter '"+domain+"' while Locked; line "+str(lineCount)+".");step-=1
		elif Players[player][4]==domain:
			FeasibilityReport.append("'"+player+"' is already in '"+domain+"'; line "+str(lineCount)+".");step-=1
	
	elif action=="exit":
		player=items.pop(0)
		domain=items.pop(0)
		playerExists=False
		domainExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if playerExists and domainExists and not Environment[N][1] and Players[player][4]!=None:
			fileOut.extend(
				(
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw[dotted](\\x"+player+",\\yMax-\\step*"+str(step)+")node[circle,fill,inner sep=0.5ex]{}--(\\xMax,\\yMax-\\step*"+str(step)+");"
				)
			)
			Players[player][3]=Players[player][2]="(\\xMax,\\yMax-\\step*"+str(step)+")"
			#	HARDCODED
			Players[player][4]=None
			#
		elif not playerExists:
			print("KeyError: Player '"+player+"' not defined; line "+str(lineCount)+".");step-=1
		elif not domainExists:
			print("KeyError: Domain '"+domain+"' not defined; line "+str(lineCount)+".");step-=1
		elif Environment[N][1]:
			FeasibilityReport.append("'"+player+"' cannot Exit '"+domain+"' while Locked; line "+str(lineCount)+".");step-=1
		elif Players[player][4]==None:
			FeasibilityReport.append("'"+player+"' cannot Exit outside the Environment; line "+str(lineCount)+".");step-=1

	elif action=="share":
		sender=items.pop(0)
		message=items.pop(0)
		recipient=items.pop(0)
		senderExists=False
		recipientExists=False
		messageExists=False
		messageEncrypted=False
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if re.search("^enc\[.*\]$",message):
				message=re.sub('\]$','',re.sub("^enc\[",'',message))
				messageEncrypted=True
		for Player in Players: 
			if Player==sender: senderExists=True
			if Player==recipient: recipientExists=True
			if senderExists and recipientExists: break
		for Message in Players[sender][1]: 
			#re.sub('\]$','',re.sub("^enc\[",'',message))
			if Message==message:messageExists=True;break
		if senderExists and recipientExists and messageExists and Players[sender][4]==Players[recipient][4] and sender!=recipient and Players[sender][4]!=None:
			fileOut.append("\n\\draw[")
			if messageEncrypted:
				fileOut.append("dashdotted,")
			elif int(Players[recipient][0])<int(Players[sender][1][message]):
				fileOut.append("red,")
				ThreatReport.append("'"+recipient+"' does not have the authority to read '"+message+"' from '"+sender+"'; step "+str(step)+", line "+str(lineCount)+".")
			elif int(Players[sender][0])<int(Players[sender][1][message]):
				fileOut.append("red,")
				ThreatReport.append("'"+sender+"' does not have the authority to send '"+message+"' to '"+recipient+"'; step "+str(step)+", line "+str(lineCount)+".")
			else:
				for player in Players:
					if Players[player][4]==Players[sender][4] and player!=sender and player!=recipient:
						if int(Players[player][0])<int(Players[sender][1][message]):
							fileOut.append("red,")
							ThreatReport.append("'"+player+"' does not have the authority to read '"+message+"' from '"+sender+"' to '"+recipient+"'; step "+str(step)+", line "+str(lineCount)+".")
							break
					if not Environment[N][1] and Players[player][4]==None and player!=sender and player!=recipient:
						if int(Players[player][0])<int(Players[sender][1][message]):
							fileOut.append("orange,")
							ThreatReport.append("Warning: '"+player+"' does not have the authority to read '"+message+"' from '"+sender+"' to '"+recipient+"'; step "+str(step)+", line "+str(lineCount)+".")
							break
			fileOut.extend(
				(
				"-{Latex[angle=45:2ex]}](\\x"+sender+",\\yMax-\step*"+str(step)+")--(\\x"+recipient+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[sender][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+sender+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[recipient][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+recipient+",\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+sender+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Msg("+Players[sender][1][message]+")$]{};"
				)
			)
			Players[sender][3]=Players[sender][2]="(\\x"+sender+",\\yMax-\\step*"+str(step)+")"
			Players[recipient][3]="(\\x"+recipient+",\\yMax-\\step*"+str(step)+")"
			Players[recipient][1][message]=Players[sender][1][message]
		elif not senderExists:
			print("KeyError: Player(sender) '"+sender+"' not defined; line "+str(lineCount)+".");step-=1
		elif not recipientExists:
			print("KeyError: Player(recipient) '"+recipient+"' not defined; line "+str(lineCount)+".");step-=1
		elif not messageExists:
			print("KeyError: Player(sender) '"+sender+"' does not own Message '"+message+"'; line "+str(lineCount)+".");step-=1
		elif Players[sender][4]!=Players[recipient][4]:
			FeasibilityReport.append("'"+sender+"' and '"+recipient+"' must be in the same Domain to Share '"+message+"'; line "+str(lineCount)+".");step-=1
		elif sender==recipient:
			FeasibilityReport.append("'"+sender+"' cannot share '"+message+"' to themselves; line "+str(lineCount)+".");step-=1
		elif Players[sender][4]==None:
			FeasibilityReport.append("'"+sender+"' and '"+recipient+"' must be in a Domain to Share '"+message+"'; line "+str(lineCount)+".");step-=1

	elif action=="lock":
		player=items.pop(0)
		domain=items.pop(0)
		playerExists=False
		domainExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if playerExists and domainExists and Players[player][4]==domain and not Environment[N][1]:	
			fileOut.extend(
				(
				"\n\\draw[dashed]"+Environment[N][2]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Lock$]{};"
				)
			)
			Environment[N][1]=True
			Environment[N][2]="(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif not playerExists:
			print("KeyError: Player '"+player+"' not defined; line "+str(lineCount)+".")
		elif not domainExists:
			print("KeyError: Domain '"+domain+"' not defined; line "+str(lineCount)+".")
		elif Players[player][4]!=domain:
			FeasibilityReport.append("'"+player+"' must be in '"+domain+"' to Lock it; line "+str(lineCount)+".");step-=1
		elif Environment[N][1]:
			FeasibilityReport.append("'"+domain+"' is already Locked; line "+str(lineCount)+".");step-=1

	elif action=="unlock":
		player=items.pop(0)
		domain=items.pop(0)
		playerExists=False
		domainExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if Players[player][4]==domain and Environment[N][1]:	
			fileOut.extend(
				(
				"\n\\draw"+Environment[N][2]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Unlock$]{};"
				)
			)
			Environment[N][1]=False
			Environment[N][2]="(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif not playerExists:
			print("KeyError: Player",player,"not defined; line "+str(lineCount)+".")
		elif not domainExists:
			print("KeyError: Domain",domain,"not defined; line "+str(lineCount)+".")
		elif Players[player][4]!=domain:
			FeasibilityReport.append("'"+player+"' must be in '"+domain+"' to Unlock it; line "+str(lineCount)+".");step-=1
		elif not Environment[N][1]:
			FeasibilityReport.append("'"+domain+"' is already Unlocked; line "+str(lineCount)+".");step-=1
	step+=1
	lineCount+=1


for player in Players:
	if Players[player][3]==None: Players[player][3] =Players[player][2]
	fileOut.append("\n\\draw"+Players[player][3]+"node[cross]{};")
N=0
for Domains in Environment:
	if domain in Domains: break
	else: N+=1
fileOut.append("\n\\draw")
if not Environment[N][1]: fileOut.append("[dashed]")
fileOut.extend(
	(
	Environment[N][2]+"--(\\x"+domain+"Lock,\\yMax-\\step*"+str(step)+");",	 
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
print('\n')
if len(PostConditions)>0:
	print("---------------")
	print("Post Conditions")
	print("---------------")
Failed=0
lineCount=1
for item in fileReader:
	lineCount+=1
	if item=="[PostConditions]": break
for items in PostConditions:
	state=items[0]
	

	if state=="location":
		player=items[1]
		domain=items[2]
		playerExists=False
		domainExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if playerExists and domainExists:
			if Players[player][4]==domain: 
				print("True:",items)
			else: 
				print("False:",items)
				Failed+=1
		elif not playerExists:
			print("KeyError: Player '"+player+"' not defined; line "+str(lineCount)+".")
		elif not domainExists:
			print("KeyError: Domain '"+domain+"' not defined; line "+str(lineCount)+".")
	
	if state=="locked":
		domain=items[1]
		domainExists=False
		N=0
		for Domain in Environment:
			if domain==Domain[0]: domainExists=True;break
			else: N+=1
		if domainExists:
			for Domain in Environment:
				if domain==Domain[0]: 
					if Domain[1]: print("True:",items);break
					else: print("False:",items);Failed+=1;break
		else: print("KeyError: Domain '"+domain+"' not defined; line "+str(lineCount)+".")
	lineCount+=1
if len(PostConditions)>0:
	print("-----------------")
	print("Passed",str(len(PostConditions)-Failed)+'/'+str(len(PostConditions)),str(round(((len(PostConditions)-Failed)/len(PostConditions))*100,2))+'%')
	print("-----------------\n")

if len(FeasibilityReport)>0:
	print("------------------")
	print("Feasibility Report")
	print("------------------")
for item in FeasibilityReport: print(item)
if len(FeasibilityReport)>0:
	print("-------------------")
	print("Passed",str(len(MainFlow)-len(FeasibilityReport))+'/'+str(len(MainFlow)),str(round(((len(MainFlow)-len(FeasibilityReport))/len(MainFlow))*100,2))+'%')
	print("-------------------\n")
if len(ThreatReport)>0:
	print("-------------")
	print("Threat Report")
	print("-------------")
for item in ThreatReport: print(item)
if len(ThreatReport)>0:
	print("-------------")
	print("Passed",str(len(MainFlow)-len(FeasibilityReport)-len(ThreatReport))+'/'+str(len(MainFlow)-len(FeasibilityReport)),str(round(((len(MainFlow)-len(FeasibilityReport)-len(ThreatReport))/(len(MainFlow)-len(FeasibilityReport)))*100,2))+'%')
	print("-------------")
file = open('out.tex', 'w') #write to file 
for line in fileOut:
     file.write(line)
file.close() #close file
subprocess.call(["pdflatex","out.tex"])