import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
import os
import json

def telegram_bot_sendtext(bot_message):
    tgToken=os.environ.get("tg_token")
    bot_token = tgToken
    bot_chatID = json.loads(os.environ.get("chat_ID"))
    for cid in bot_chatID:
        send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={cid}&parse_mode=HTML&text={bot_message}' 
        
        res=requests.get(send_text)
        writeLog(res,bot_message)
        
def writeLog(res,bot_message):
    if res.status_code==400 and 'message must be non-empty' not in res.text:
        f=open('log','a',encoding='utf-8')
        f.write(str(res.status_code)+'\n')
        f.write(str(res.text)+'\n')
        f.write(bot_message+'\n\n')
        telegram_bot_sendtext('Please Check Log, Message Bad Request')
        f.close()

def initial(subForum):
    removeLogAndCheckPath()
    checkJson(subForum)

def removeLogAndCheckPath():
    if os.path.exists('log'):
        os.remove('log')
    if not os.path.exists('src'):
        os.mkdir('src')

def checkJson(subForum):
    for forum in subForum:
        touchFile(forum[0])

def fetch(url):
    headers={'User-Agent': "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    resp=requests.get(url,headers=headers)
    return resp.text

def getDetails(soup):
    detailList=[]
    ts=soup.find_all('div','r-ent')
    for t in ts:
        if t.find('div','title').a!=None:
            like=t.find('div','nrec').text.replace('\n','')
            title=t.find('div','title').text.replace('\n','').replace('&','').replace('#','').replace('+','').replace('<','')
            href=t.find('div','title').a.get('href')
            detailList.append([like,title,href])

    return detailList

def compareOldAndNew(oldList,newList,forum):
    
    result=[]

    for item in newList:

        judge=True

        for oldItem in oldList:
            if item[2] in oldItem:
                judge=False

        if judge:
            result.append(item)
                
    return result

def sendNewToTelegram(result,forum):
    if len(result)!=0:
        msg=f'<b>{forum.upper()} </b>\n\n-------------------------------------\n'
        for item in result:
            msg=msg+f"<a href='https://www.ptt.cc{item[2]}'><b>[{item[0]}] {item[1]}</b></a>\n-------------------------------------\n"
        return msg
    return ''

def concatenateMsg(msgs):
    allMsg=[]
    temp=''
    for msg in msgs:
        
        if msg=='':
            continue

        if len(temp+msg)>4096:
            allMsg.append(temp)
            temp=msg
        else:
            temp=temp+msg+'\n'

    allMsg.append(temp)

    for m in allMsg:
        if m!='':
            telegram_bot_sendtext(m)

def writeJson(forum,data):
    with open(f'src/{forum}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def loadJson(forum):
    with open(f'src/{forum}.json', encoding='utf-8') as f:
        data = json.load(f)
    return data

def touchFile(forum):
    if not os.path.exists(f'src/{forum}.json'):
        myJson={forum:[]}
        writeJson(forum,myJson)

def notifier(subForum):
    msgs=[]

    for i in range(len(subForum)):

        target=subForum[i][0]

        url=f'https://www.ptt.cc/bbs/{target}/search?q=recommend%3A{subForum[i][1]}'

        targetJson=loadJson(target)
        oldList=targetJson[target]

        try:
            soup=BeautifulSoup(fetch(url),'lxml')
            newList=getDetails(soup)
            
            result=compareOldAndNew(oldList,newList,target)
            
            msg = sendNewToTelegram(result,target)
            msgs.append(msg)
            
            oldList=oldList+result
            
            if len(oldList)>100:
                oldList=oldList[50:]

            targetJson[target]=oldList
            writeJson(target,targetJson)

        except Exception as e:
            print(e)

    concatenateMsg(msgs)
            