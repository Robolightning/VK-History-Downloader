import vk_api
import os
import datetime
import urllib.request
import requests
import time

if os.path.exists("Conversations") == False:
	os.mkdir("Conversations")
if os.path.exists("Conversations/token.txt") == False:
	fst = open("Conversations/token.txt", 'w', encoding='utf-8')
	const = input()
	fst.write(const)
	fst.close()
with open("Conversations/token.txt", 'r', encoding='utf-8') as f:
	vk_access_url = f.read()
pos = vk_access_url.find('=')
if pos != -1:
	token = vk_access_url[vk_access_url.find('=') + 1:vk_access_url.find('&')]
	SELF_ID = int(vk_access_url[vk_access_url.rfind('=') + 1:])
else:
	token = vk_access_url
	SELF_ID = 459749595

vk_session = vk_api.VkApi(token = token)
vk_session._auth_token()
vk = vk_session.get_api()

def get_dialogs(user_id):
	dialogs = vk.messages.getHistory(peer_id=user_id)
	return dialogs['count']

def get_full_name(user_id):
	user_get=vk.users.get(user_ids = (user_id))
	user_get=user_get[0]
	first_name=user_get['first_name']
	last_name=user_get['last_name']
	full_name=first_name+" "+last_name
	return full_name

def get_history(friend, mn, persent, disum, strcomm, offsetb, phototrue):
	if os.path.exists("Conversations/" + str(friend)) == False:
		os.mkdir("Conversations/" + str(friend))
	filecou = offsetb // 1000 + 1
	f = open("Conversations/" + str(friend) + "/text_" + str(filecou) + ".html", 'w', encoding='utf-8')
	if os.path.exists("Conversations/" + str(friend) + "/Attachments") == False:
		os.mkdir("Conversations/" + str(friend) + "/Attachments")
	if os.path.exists("Conversations/" + str(friend) + "/Attachments/Photo") == False:
		os.mkdir("Conversations/" + str(friend) + "/Attachments/Photo")
	f.write("<html>\n<body>\n\n")
	dialog_len = get_dialogs(friend)
	friend_history = []
	offset = offsetb
	resid = dialog_len - offset
	fn = str(friend)
	dia = False
	lastid = ''
	lastdt = ''
	if friend > 0 and friend < 2000000000:
		fn = get_full_name(friend)
		dia = True
	strcomm += "Собеседник: " + fn + ", " + str(dialog_len) + " сообщений в переписке\n"
	print(100*'\n')
	print(strcomm)
	while resid > 0:
		fh = vk.messages.getHistory(peer_id=friend, offset=offset, rev = 1)
		friend_history = fh['items']
		resid -= 20
		offset += 20
		if offset % 1000 == 0:
			print(100*'\n')
			print(strcomm + "\tОбрабатывается " + fn + ":", resid, 'сообщений осталось,', str(round(persent * (disum + offset), 1)) + "% выполнено")
			f.write("<body>\n<html>")
			f.close()
			filecou += 1
			f = open("Conversations/" + str(friend) + "/text_" + str(filecou) + ".html", 'w', encoding='utf-8')
		for index in friend_history:
			rmc = 1
			rmreal = False
			if 'reply_message' in index:
				rmc = 2
				rmreal = True
			for rm in range(0, rmc):
				t1 = ''
				t2 = ''
				idp = fn
				mself = False
				if index['from_id'] == SELF_ID:
					idp = mn
					mself = True
				elif dia == False:
					idp = str(index['from_id'])
				if rm == 1:
					t1 = '<p style="background-color:violet;">'
					t2 = '</p>'
				elif index['from_id'] == SELF_ID:
					t1 = '<p style="background-color:powderblue;">'
					t2 = '</p>'
				timee = datetime.datetime.fromtimestamp(index['date']).strftime(' (%H:%M:%S %Y-%m-%d)')
				if idp != lastid or timee != lastdt:
					if lastid != '' and rmreal == False:
						f.write("<br/>\n")
					f.write(t1 + "<b>" + idp + timee + "</b><br/>" + t2 + '\n')
				lastid = idp
				lastdt = timee
				if index['text'] != '':
					f.write(t1 + index['text'] + t2 + "<br/>\n")
				for ind in index['attachments']:
					if ind['type'] == 'sticker':
						imurl = ind['sticker']['images_with_background'][len(ind['sticker']['images_with_background']) - 1]['url']
						img = urllib.request.urlopen(imurl).read()
						imname = imurl[imurl.rfind('/') + 1:] + ".jpg"
						imname = imname.replace('?', 'question')
						out = open("Conversations/" + str(friend) + "/Attachments/" + imname, "wb")
						out.write(img)
						out.close
						f.write(t1 + "<img src=\"Attachments/" + imname + '" />' + t2 + '<br/>\n')
					if ind['type'] == 'photo':
						siz = []
						for iin in ind['photo']['sizes']:
							siz.append(iin['height'])
						maxx = max(siz)
						for iin in ind['photo']['sizes']:
							if iin['height'] == maxx:
								imurl = iin['url']
								photodim = iin['height'] * iin['width']
								break
						response = str(requests.head(imurl))
						if response == '<Response [200]>':
							img = urllib.request.urlopen(imurl).read()
						else:
							img = urllib.request.urlopen('http://vk.me/images/error404.png').read()
						imname = imurl[imurl.rfind('/') + 1:]
						imname = imname[:imname.find('.') + 4]
						imname = imname.replace('?', 'question')
						out = open("Conversations/" + str(friend) + "/Attachments/Photo/" + imname, "wb")
						out.write(img)
						out.close()
						if dia == True:
							if mself == True:
								if photodim == phototrue:
									outall = open("Conversations/MyPhotos/Photos/" + str(friend) + " " + str(filecou) + " " + datetime.datetime.fromtimestamp(index['date']).strftime('%H;%M;%S %Y-%m-%d ') + imname, "wb")
								else:
									outall = open("Conversations/MyPhotos/Other/" + str(friend) + " " + str(filecou) + " " + datetime.datetime.fromtimestamp(index['date']).strftime('%H;%M;%S %Y-%m-%d ') + imname, "wb")
							else:
								outall = open("Conversations/NotMyPhotos/" + str(friend) + " " + str(filecou) + " " + datetime.datetime.fromtimestamp(index['date']).strftime('%H;%M;%S %Y-%m-%d ') + imname, "wb")
							outall.write(img)
							outall.close()
						f.write(t1 + "<img src=\"Attachments/Photo/" + imname + '" />' + t2 + '<br/>\n')
					if ind['type'] == 'doc':
						docurl = ind['doc']['url']
						docname = docurl[docurl.rfind('/') + 1:]
						docname = docname[:docname.find('?')] + '.' + ind['doc']['ext']
						docname = docname.replace('?', 'question')
						fil = open("Conversations/" + str(friend) + "/Attachments/" + docname, "wb")
						try:
							ufr = requests.get(docurl)
						except:
							print("Some error in one doc")
						fil.write(ufr.content)
						fil.close()
						f.write(t1 + "<a href=\"Attachments/" + docname + "\">" + docname + "</a>" + t2 + "<br/>\n")
					if ind['type'] == 'link':
						linkurl = ind['link']['url']
						linkname = linkurl[:linkurl.find('?')]
						f.write(t1 + "<a href=\"" + linkurl + "\">" + linkname + "</a>" + t2 + "<br/>\n")
					if ind['type'] == 'audio_message':
						amurl = ind['audio_message']['link_mp3']
						if 'conversation_message_id' in index:
							idmess = index['conversation_message_id']
						else:
							idmess = ind['audio_message']['id']
						amname = str(idmess) + amurl[amurl.rfind('/') + 1:]
						amname = amname.replace('?', 'question')
						fil = open("Conversations/" + str(friend) + "/Attachments/" + amname, "wb")
						response = str(requests.head(amurl))
						if response == '<Response [200]>':
							ufr = requests.get(amurl)
							fil.write(ufr.content)
						fil.close()
						f.write(t1 + "<audio\ncontrols\nsrc=\"" + amurl + "\">\nYour browser does not support the\n<code>audio</code> element./n</audio>" + t2 + "<br/>\n")
				if rmreal == True:
					rmreal = False
					while 'reply_message' in index:
						index = index['reply_message']
			fs = open("Conversations/save.txt", 'w', encoding='utf-8')
			fs.write(str(friend) + " " + str(offset))
			fs.close()
	fs = open("Conversations/save.txt", 'w', encoding='utf-8')
	fs.write(str(friend) + " 0")
	fs.close()
	f.write("<body>\n<html>")
	f.close()
	return dialog_len

if __name__ == '__main__':
	mn = get_full_name(SELF_ID)
	d = vk.messages.getConversations()
	dico = d['count']
	cou = 0
	dialogs = []
	multiconversations = []
	groupchats = []
	friends = []
	elem = [[],[]]
	msumm = 0
	disum = 0
	ii = 0
	persent = 0
	strcomm = ''
	strcomm1 = ''
	phototrue = 0
	msumm = 0
	if os.path.exists("Conversations/savelist.txt") == False:
		fsl = open("Conversations/savelist.txt", 'w', encoding='utf-8')
		while cou < dico:
			d = vk.messages.getConversations(offset=cou)
			cou += 20
			dd = d['items']
			for i in dd:
				a = i['conversation']['peer']['id']
				b = get_dialogs(a)
				elem = [b, a]
				if a > 2000000000:
					multiconversations.append(elem)
					msumm += b
				elif a < 0:
					groupchats.append(elem)
					msumm += b
				elif a != 402965562 and a != 511451347:
					dialogs.append(elem)
					msumm += b
		strcomm1 = "Всего " + str(len(dialogs)) + " диалогов, " + str(len(multiconversations)) + " бесед и " + str(len(groupchats)) + " чата с группой\n"
		strcomm = strcomm1
		mft = open("Conversations/msumm.txt", 'w', encoding='utf-8')
		mft.write(str(msumm))
		mft.close()
		multiconversations.sort(reverse=True)
		groupchats.sort(reverse=True)
		dialogs.sort(reverse=True)
		for j in dialogs:
			friends.append(j[1])
		for j in groupchats:
			friends.append(j[1])
		for j in multiconversations:
			friends.append(j[1])
		if os.path.exists("Conversations/MyPhotos") == False:
			os.mkdir("Conversations/MyPhotos")
		if os.path.exists("Conversations/NotMyPhotos") == False:
			os.mkdir("Conversations/NotMyPhotos")
		if os.path.exists("Conversations/MyPhotos/Photos") == False:
			os.mkdir("Conversations/MyPhotos/Photos")
		if os.path.exists("Conversations/MyPhotos/Other") == False:
			os.mkdir("Conversations/MyPhotos/Other")
	else:
		mft = open("Conversations/msumm.txt", 'r', encoding='utf-8')
		msumm = int(mft.read())
		mft.close()
		fsl = open("Conversations/savelist.txt", 'r', encoding='utf-8')
		for linesf in fsl:
			friends.append(int(linesf))
		fsl.close()
	persent = 100.0 / msumm
	offsetb = 0
	friendb = friends[0]
	if os.path.exists("Conversations/save.txt") == False:
		fs = open("Conversations/save.txt", 'w', encoding='utf-8')
		fs.write(str(friendb) + " " + str(offsetb))
		fs.close()
	else:
		fs = open("Conversations/save.txt", 'r', encoding='utf-8')
		savestr = fs.read()
		friendb = int(savestr[:savestr.find(' ')])
		offsetb = int(savestr[savestr.find(' ') + 1:])
		fs.close()
		if os.path.exists("Conversations/phototest.txt") == True:
			fst = open("Conversations/phototest.txt", 'r', encoding='utf-8')
			phototrue = int(fst.read())
			fst.close()
	while friendb != friends[0]:
		friends.pop(0)
	fsl = open("Conversations/savelist.txt", 'w', encoding='utf-8')
	for el in friends:
		fsl.write(str(el) + '\n')
	fsl.close()
	tic = time.perf_counter()
	for friend in friends:
		disum += get_history(friend, mn, persent, disum, strcomm, offsetb, phototrue)
		offsetb = 0
		toc = time.perf_counter()
		ii += 1
		timesecall = ((toc - tic) / disum) * (msumm - disum)
		times = str(round(timesecall % 60))
		timem = str(round((timesecall % 3600) // 60))
		timeh = str(round(timesecall // 3600))
		timed = str(round(timesecall % 86400))
		if len(times) == 1:
			times = '0' + times
		if len(timem) == 1:
			timem = '0' + times
		strcomm = strcomm1 + "Обработано " + str(ii) + " переписок из " + str(len(friends)) + " " + str(round(persent * disum, 1)) + "%\nПриблизительно осталось времени: " + timed + ":" +  timeh + ":" + timem + ":" + times + "\n"
	os.remove("Conversations/msumm.txt")
	os.remove("Conversations/save.txt")
	os.remove("Conversations/savelist.txt")
	os.remove("Conversations/token.txt")
	os.remove("Conversations/phototest.txt")