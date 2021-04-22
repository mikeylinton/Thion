import re
import sys 
import subprocess
if (len(sys.argv)!=2):
	print("Usage: thion.py [inputFile]");exit(0)
section=None
Players={}
Environment=[]
PreConditions=[];MainFlow=[];PostConditions=[]
try:
	inputfile=open(sys.argv[1],'r')
except:
	print("File '"+sys.argv[1]+"' not found.");exit(0)
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
	"\n\\newcommand\\unit{0.2625}",
	"\n\\newcommand\\step{\\unit*6}",
	"\n\\newcommand\\yMax{\\step*14}",
	"\n\\newcommand\\xMax{\\step*14}",
	"\n\\newcommand\\labelSpacing{\\step*0.4}",
	
	)
)

for Location in Environment:
	fileOut.extend(
		(
		"\n\\newcommand\\y"+Location[0]+"{\\yMax-\\unit}",
		"\n\\newcommand\\x"+Location[0]+"{\\xMax-\\step/2}",
		"\n\\newcommand\\x"+Location[0]+"Lock{\\x"+Location[0]+"-\\step/2}"
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
step=1
for items in PreConditions:
	state=items.pop(0)

	if state=="location":
		player=items.pop(0)
		location=items.pop(0)

		if Players[player][4]==None:
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*1)"
			Players[player][4]=location
			step=2
	
	if state=="locked":
		location=items.pop(0)
		for Location in Environment:
			if location==Location[0]: Location[1]=True;break
			
		#for player in Players:
		#	if Players[player][4]==location:
		#		Environment[N][1]=True;break
lineCount=1
errorCount=0
for item in fileReader:
	lineCount+=1
	if item=="[MainFlow]": break
noStep=False
for items in MainFlow:
	action=items.pop(0)
	noStep=False
	if action=="enter":
		player=items.pop(0)
		location=items.pop(0)
		playerExists=False
		locationExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if locationExists and not Environment[N][1] and Players[player][4]!=location:
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
			Players[player][4]=location
		elif not playerExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.");noStep=True
		elif Players[player][4]==location:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' is already in '"+location+"'.");noStep=True
		if not locationExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.");noStep=True
		elif Environment[N][1]:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' cannot enter '"+location+"' while locked.");noStep=True
		if noStep: step-=1

	elif action=="exit":
		player=items.pop(0)
		location=items.pop(0)
		playerExists=False
		locationExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if playerExists and locationExists and not Environment[N][1] and Players[player][4]!=None:
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
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.");noStep=True
		elif Players[player][4]==None:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' is not in '"+location+"'.");noStep=True
		if not locationExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.");noStep=True
		elif Environment[N][1]:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' cannot exit '"+location+"' while locked.");noStep=True
		if noStep: step-=1

	elif action=="share":
		sender=items.pop(0)
		message=items.pop(0)
		recipient=items.pop(0)
		senderExists=False
		recipientExists=False
		messageExists=False
		messageEncrypted=False
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if re.search("^enc\[.*\]$",message):
				message=re.sub('\]$','',re.sub("^enc\[",'',message))
				messageEncrypted=True
		for Player in Players: 
			if Player==sender: senderExists=True
			if Player==recipient: recipientExists=True
			if senderExists and recipientExists: break
		if senderExists:
			for Message in Players[sender][1]: 
				if Message==message:messageExists=True;break
		if recipientExists and messageExists and Players[sender][4]==Players[recipient][4] and sender!=recipient and Players[sender][4]!=None:
			fileOut.append("\n\\draw[")
			if messageEncrypted:
				fileOut.append("dashdotted,")
			elif int(Players[recipient][0])<int(Players[sender][1][message]):
				fileOut.append("red,")
				ThreatReport.append("("+str(lineCount)+") '"+recipient+"' does not have the authority to read '"+message+"' from '"+sender+"' => Encrypt '"+message+"'.")
			elif int(Players[sender][0])<int(Players[sender][1][message]):
				fileOut.append("red,")
				ThreatReport.append("("+str(lineCount)+") '"+sender+"' does not have the authority to send '"+message+"' to '"+recipient+"' => Encrypt '"+message+"'.")
			else:
				for player in Players:
					if Players[player][4]==Players[sender][4] and player!=sender and player!=recipient:
						if int(Players[player][0])<int(Players[sender][1][message]):
							fileOut.append("red,")
							ThreatReport.append("("+str(lineCount)+") '"+player+"' does not have the authority to read '"+message+"' from '"+sender+"' to '"+recipient+"' => Encrypt '"+message+"'.")
							break
					if locationExists and not Environment[N][1] and Players[player][4]==None and player!=sender and player!=recipient:
						if int(Players[player][0])<int(Players[sender][1][message]):
							fileOut.append("orange,")
							ThreatReport.append("("+str(lineCount)+") 'Warning: '"+player+"' does not have the authority to read '"+message+"' from '"+sender+"' to '"+recipient+"' => Encrypt '"+message+"' AND/OR Lock '"+Players[sender][4]+"'.")
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
		if not senderExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+sender+"' not defined.");noStep=True
		if not recipientExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+recipient+"' not defined.");noStep=True
		if not messageExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: '"+sender+"' does not have the Message '"+message+"'.");noStep=True
		if sender==recipient:
			FeasibilityReport.append("("+str(lineCount)+") '"+sender+"' cannot share '"+message+"' to themselves.");noStep=True
		if senderExists and recipientExists and (Players[sender][4]==None and Players[recipient][4]==None):
			FeasibilityReport.append("("+str(lineCount)+") Both '"+sender+"' and '"+recipient+"' must be in the same location to share '"+message+"'.");noStep=True
		elif senderExists and Players[sender][4]==None:
			FeasibilityReport.append("("+str(lineCount)+") '"+sender+"' must be in the same location as '"+recipient+"' to share '"+message+"'.");noStep=True
		elif recipientExists and Players[recipient][4]==None:
			FeasibilityReport.append("("+str(lineCount)+") '"+recipient+"' must be in the same location as '"+sender+"' to receive '"+message+"'.");noStep=True
		if noStep: step-=1

	elif action=="lock":
		player=items.pop(0)
		location=items.pop(0)
		playerExists=False
		locationExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if playerExists and locationExists and Players[player][4]==location and not Environment[N][1]:	
			fileOut.extend(
				(
				"\n\\draw[dashed]"+Environment[N][2]+"--(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Lock$]{};"
				)
			)
			Environment[N][1]=True
			Environment[N][2]="(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif not locationExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.");noStep=True
		elif Environment[N][1]:
			FeasibilityReport.append("("+str(lineCount)+") '"+location+"' is already locked.");noStep=True
		if not playerExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.");noStep=True
		elif Players[player][4]!=location:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' must be in '"+location+"' to Lock it.");noStep=True
		
		if noStep: step-=1

	elif action=="unlock":
		player=items.pop(0)
		location=items.pop(0)
		playerExists=False
		locationExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if playerExists and locationExists and Players[player][4]==location and Environment[N][1]:	
			fileOut.extend(
				(
				"\n\\draw"+Environment[N][2]+"--(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw"+Players[player][2]+"node[circle,fill,inner sep=0.5ex]{}--(\\x"+player+",\\yMax-\\step*"+str(step)+"){};",
				"\n\\draw[dotted,-{Latex[angle=45:2ex]}](\\x"+player+",\\yMax-\\step*"+str(step)+")--(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+");",
				"\n\\draw(\\x"+player+"-\\labelSpacing,\\yMax-\\step*"+str(step)+")node[label=above:$Unlock$]{};"
				)
			)
			Environment[N][1]=False
			Environment[N][2]="(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+")"
			Players[player][3]=Players[player][2]="(\\x"+player+",\\yMax-\\step*"+str(step)+")"
		elif not locationExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.");noStep=True
		elif not Environment[N][1]:
			FeasibilityReport.append("("+str(lineCount)+") '"+location+"' is already unlocked.");noStep=True
		if not playerExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.");noStep=True
		elif Players[player][4]!=location:
			FeasibilityReport.append("("+str(lineCount)+") '"+player+"' must be in '"+location+"' to unlock it.");noStep=True
		if noStep: step-=1
	step+=1
	lineCount+=1
if noStep: step+=1

for player in Players:
	if Players[player][3]==None: Players[player][3] =Players[player][2]
	fileOut.append("\n\\draw"+Players[player][3]+"node[cross]{};")

fileOut.append("\n\\draw")
if not Environment[0][1]: fileOut.append("[dashed]")
location=Environment[0][0]
fileOut.extend(
	(
	Environment[0][2]+"--(\\x"+location+"Lock,\\yMax-\\step*"+str(step)+");",	 
	"\n\\draw(\\x"+location+"Lock,\yMax-\\step*"+str(step)+")node[rectangle,fill,inner sep=0.5ex]{};",
	"\n\\draw[very thick] (\\x"+location+"-\\flowSpacing-\\unit*2,\yMax-\\step*"+str(step)+"+\\unit) rectangle (\\x"+location+",\\y"+location+");",
	"\n\\draw(\\x"+location+"Lock,\\yMax)node[rectangle,fill,inner sep=0.5ex,label=right:$Lock$]{};"
	)
)

fileOut.extend(
	(
	"\n\\end{tikzpicture}",
	"\n\\end{document}"
	)
)
if len(PostConditions)>0:
	print("---------------------")
	print("Post Conditions")
	print("---------------------")
Failed=0
lineCount=1
for item in fileReader:
	lineCount+=1
	if item=="[PostConditions]": break
for items in PostConditions:
	state=items[0]
	

	if state=="location":
		player=items[1]
		location=items[2]
		playerExists=False
		locationExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if playerExists and locationExists:
			if Players[player][4]==location: 
				print("True:  '"+player+"' in '"+location+"'")
			else: 	
				print("False:  '"+player+"' in '"+location+"'")
				Failed+=1
		if not playerExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.")
		if not locationExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.")
	
	if state=="locked":
		location=items[1]
		locationExists=False
		N=0
		for Location in Environment:
			if location==Location[0]: locationExists=True;break
			else: N+=1
		if locationExists:
			for Location in Environment:
				if location==Location[0]: 
					if Location[1]: print("True: '"+location+"' locked");break
					else: print("False:  '"+location+"' locked");Failed+=1;break
		else: FeasibilityReport.append("("+str(lineCount)+") KeyError: Location '"+location+"' not defined.")

	if state=="has":
		player=items[1]
		message=items[2]
		playerExists=False
		messageExists=False
		for Player in Players: 
			if Player==player: playerExists=True;break
		for Message in Players[player][1]:
			if Message==message: messageExists=True;break
			else: N+=1
		if playerExists and messageExists:
			print("True: '"+player+"' has '"+message+"'")
		elif playerExists:
			print("False: '"+player+"' has '"+message+"'")
			Failed+=1 
		if not playerExists:
			FeasibilityReport.append("("+str(lineCount)+") KeyError: Player '"+player+"' not defined.")

	lineCount+=1
if len(PostConditions)>0:
	print("-----------------------------")
	print("Passed",str(len(PostConditions)-Failed)+'/'+str(len(PostConditions)),str(round(((len(PostConditions)-Failed)/len(PostConditions))*100,2))+'%')
	print("-----------------------------")

if len(FeasibilityReport)>0:
	print("\n------------------------")
	print("Feasibility Report")
	print("------------------------")
for item in FeasibilityReport: print(item)
if len(ThreatReport)>0:
	print("\n-------------------")
	print("Threat Report")
	print("-------------------")
for item in ThreatReport: print(item)
file = open('out.tex', 'w') #write to file 
for line in fileOut:
     file.write(line)
file.close() #close file
try:
	subprocess.call(["pdflatex","out.tex"])
except:
	print("\nout.tex could not be converted to a PDF.")
