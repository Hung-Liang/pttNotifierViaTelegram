#!/usr/bin/env python3.8
from asyncio import streams
import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os
import json
import subprocess
from dotenv import load_dotenv
from library import initialUser, writeJson, loadJson, createUserJson, updateUserJson
load_dotenv()

############################### Bot ############################################
def start(bot, update):
    name=bot.message.from_user.name
    uid=bot.message.from_user.id
    
    if initialUser(uid,name):
        bot.message.reply_text(startMessage(name))
    else:
        bot.message.reply_text(alreadyRegisterMessage(name))

def add(bot, update):
    bot.message.reply_text(addMessage(), reply_markup=pageKeyboardMaker(1))

def delete(bot, update):
    uid=bot.message.from_user.id
    users=loadJson('users')
    bot.message.reply_text(deleteMessage(), reply_markup=deleteBoardMaker(users[str(uid)]['boards']))

def me(bot, update):
    uid=bot.message.from_user.id
    name=bot.message.from_user.name
    users=loadJson('users')
    bot.message.reply_text(userMessage(name,users[str(uid)]['boards']))

def deleteMe(bot, update):
    uid=bot.message.from_user.id
    name=bot.message.from_user.name
    users=loadJson('users')
    users.pop(str(uid))
    bot.message.reply_text(deleteUserMessage(name))
    writeJson('users',users)

def boardRegister(bot, update):
    board=bot.callback_query.data.split(',')[1]
    bot.callback_query.message.edit_text(chooseMessage(), reply_markup=selectThresholdKeyboard(board))

def deleteBoard(bot,update):
    infos=bot.callback_query.data.split(',')[1]
    uid=bot.callback_query.from_user.id
    name=bot.callback_query.from_user.name
    updateUserJson(uid,infos,True)
    bot.callback_query.message.edit_text(deleteConfirmMessage(name,infos))

def confirmAndWrite(bot, update):
    infos=bot.callback_query.data.split(',')[1:]
    uid=bot.callback_query.from_user.id
    name=bot.callback_query.from_user.name
    if updateUserJson(uid,infos):
        bot.callback_query.message.edit_text(confirmMessage(name,infos))
    else:
        bot.callback_query.message.edit_text(errorMessage())

def pageTurner(bot, update):
    page = bot.callback_query.data.split(',')[1]
    bot.callback_query.message.edit_text(addMessage(), reply_markup=pageKeyboardMaker(int(page)))

def stop(bot, update):
    uid=bot.message.from_user.id
    if str(uid)==os.environ.get("admin_id"):
        bot.message.reply_text('Bot Shutting Down')
        threading.Thread(target=shutdown).start()
    else:
        bot.message.reply_text('You do not have permission')

def getUsers(bot, update):
    uid=bot.message.from_user.id
    if str(uid)==os.environ.get("admin_id"):
        users=loadJson('users')
        for key in users:
            temp=users[key]['name']+'\n'
            for b in users[key]['boards']:
                temp=temp+b+' '+users[key]['boards'][b]+'\n'
            
            bot.message.reply_text(temp)

def error(update, context):
    print(f'Update {update} caused error {context.error}')

############################ Keyboards #########################################
def pageKeyboardMaker(page):
    boards=loadJson('boards','')
    
    pages=boards[str(page)]
    
    keyboard=[[
                InlineKeyboardButton(pages[i], callback_data='Board,'+pages[i]),
                InlineKeyboardButton(pages[i+1], callback_data='Board,'+pages[i+1])
             ] for i in range(0,len(pages),2)]
    
    changePage=[]
    
    if page!=1:
        changePage.append(InlineKeyboardButton('<< ?????????', callback_data=f'Page,{page-1}'))
    if page!=len(boards):
        changePage.append(InlineKeyboardButton('????????? >>', callback_data=f'Page,{page+1}'))
    
    keyboard.append(changePage)

    return InlineKeyboardMarkup(keyboard)

def selectThresholdKeyboard(data):
    keyboard=[[
                InlineKeyboardButton('10', callback_data=f'Confirm,{data},10'),
                InlineKeyboardButton('20', callback_data=f'Confirm,{data},20'),
                InlineKeyboardButton('30', callback_data=f'Confirm,{data},30'),
                InlineKeyboardButton('50', callback_data=f'Confirm,{data},50'),
                InlineKeyboardButton('70', callback_data=f'Confirm,{data},70'),
                InlineKeyboardButton('???', callback_data=f'Confirm,{data},100')
             ]]
    return InlineKeyboardMarkup(keyboard)

def deleteBoardMaker(boards):
    keyboard=[]
    counter=0
    buttons=[]
    validation=True
    for board in boards:
        if counter % 2 == 0 and counter!=0:
            keyboard.append(buttons)
            buttons=[]
            buttons.append(InlineKeyboardButton(board, callback_data=f'Delete,{board}'))
            validation=False
        else:
            buttons.append(InlineKeyboardButton(board, callback_data=f'Delete,{board}'))
            validation=True
        counter+=1
    if validation:
        keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def startMessage(name):
    return f'??????{name}???????????????PTT???????????????\n\n/me ??????????????????\n/add ?????????????????????\n/delete ????????????\n'

def alreadyRegisterMessage(name):
    return f'??????{name}?????????????????????????????????????????????\n\n/me ??????????????????\n/add ?????????????????????\n/delete ????????????\n/deleteMe ??????????????????'

def addMessage(page=1):
    return f'??????PTT?????????????????????????????????{page}???'

def deleteMessage():
    return f'??????????????????'

def confirmMessage(name,infos):
    return f'?????????{name}????????????{infos[0]}??????????????????{infos[1]}???????????????'

def deleteConfirmMessage(name,infos):
    return f'?????????{name}????????????{infos}?????????'

def userMessage(name,boards):
    message=f'??????{name}??????????????????????????????\n\n'
    for board in boards:
        message=message+f'{board}???????????????{boards[board]}\n'
    return message

def errorMessage():
    return '?????????????????????????????????????????????'

def chooseMessage():
    return f'??????????????????????????????????????????'

def shutdown():
    updater.stop()
    updater.is_idle = False

def deleteUserMessage(name):
    return f'??????{name}'


    
############################# Functions #########################################



############################# Handlers #########################################
createUserJson()
updater = Updater(os.environ.get("tg_token"), use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('me', me))
updater.dispatcher.add_handler(CommandHandler('add', add))
updater.dispatcher.add_handler(CommandHandler('delete', delete))
updater.dispatcher.add_handler(CommandHandler('deleteMe', deleteMe))
updater.dispatcher.add_handler(CallbackQueryHandler(pageTurner,pattern='Page'))
updater.dispatcher.add_handler(CallbackQueryHandler(boardRegister,pattern='Board'))
updater.dispatcher.add_handler(CallbackQueryHandler(confirmAndWrite,pattern='Confirm'))
updater.dispatcher.add_handler(CallbackQueryHandler(deleteBoard,pattern='Delete'))
updater.dispatcher.add_handler(CommandHandler('stop', stop))
updater.dispatcher.add_handler(CommandHandler('users', getUsers))
updater.dispatcher.add_error_handler(error)

updater.start_polling()
