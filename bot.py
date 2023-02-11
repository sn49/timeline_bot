import nextcord
from nextcord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import arrow
from pypresence import Presence
from datetime import datetime
import pytz
import asyncio
from secret import important

ip=important.important


class job_check:
    stopValue=0


jb=job_check()


# Set up credentials and authorize client
scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name('secret/spreadjson.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet
spreadsheet = client.open('타임라인 기록')

# Select the worksheet


intents = nextcord.Intents.all()
# Define the Nextcord bot command
bot = commands.Bot(command_prefix='d!',intents=intents)

@bot.event
async def on_ready():
    worksheet = spreadsheet.worksheet('시트1')
    row=worksheet.row_count
    row_value = worksheet.row_values(row)

    print(row_value)
    print(len(row_value))


    if len(row_value)==7:

        # create timezone objects
        KST = pytz.timezone('Asia/Seoul')

        # create Arrow object for current time in Seoul
        ctime = arrow.now(KST)

        # create datetime object for start time
        start_time = datetime(int(row_value[0]), int(row_value[1]), int(row_value[2]), int(row_value[4]), int(row_value[5]), tzinfo=KST)

        # make both datetime objects timezone-aware and remove microseconds
        ctime = ctime.replace(microsecond=0).datetime.astimezone(KST)
        start_time = start_time.replace(microsecond=0).astimezone(KST)

        # calculate time difference
        time_diff = ctime - start_time

        timedelta=time_diff.total_seconds()

        # print time difference in seconds
        print(timedelta)


        dm=int(timedelta/60)
        ds=int(timedelta%60)

        print(dm)
        print(ds)

        await bot.change_presence(
            status=nextcord.Status.online,
            activity=nextcord.Game(f"{row_value[3]} {dm}분 {ds}초 동안 하는중")
        )


        while jb.stopValue==0:
            dm,ds = await change_second(dm,ds,row_value[3])
            await asyncio.sleep(3)
    else:
        await bot.change_presence(
            activity=nextcord.Game("뭔가를 안")
        )

    channel=bot.get_channel(ip.manage_channel_id)
    await channel.send(f"봇 켜짐 <@{ip.ownerid}>")
    
        

@bot.command()
async def write(ctx, mode:str, content=None):
    if ctx.author.id!=ip.ownerid:
        await ctx.send("이 봇을 만든 사람만 타임라인을 작성할 수 있습니다.")
        return
    worksheet = spreadsheet.worksheet('시트1')
    ctime=arrow.now("Asia/Seoul")
    ctime=ctime.datetime
    print("before if")
    if mode.lower()=="start":
        print("start start")
        
        row=worksheet.row_count


        cell_value = worksheet.acell(f'H{row}').value

        print(cell_value)

        if cell_value==None:
            await ctx.send("end로 끝내기를 해야합니다.")
            return
        
        if content==None:
            await ctx.send("start는 컨텐츠를 입력해야합니다.")
            return

        worksheet.add_rows(1)

        start_column = 'A'
        end_column = 'G'
        cell_range = f'{start_column}{row+1}:{end_column}{row+1}'
        print(cell_range)
        new_values = [f'{ctime.year}',f'{ctime.month}',f'{ctime.day}',f'{content}',f'{ctime.hour}',f'{ctime.minute}','~']
        worksheet.update(cell_range, [new_values])

        dm=0
        ds=0

        await bot.change_presence(
            activity=nextcord.Game(f"{content} {dm}분 {ds}초 동안 하는중")
        )

        await ctx.send(f"{content} 시작함")
        await asyncio.sleep(3)
        while jb.stopValue==0:
            dm,ds = await change_second(dm,ds,content)
            await asyncio.sleep(3)


    elif mode.lower()=="end":
        

        row=worksheet.row_count

        cell_value = worksheet.acell(f'H{row}').value

        print(cell_value)

        if cell_value!=None:
            await ctx.send("이미 끝내기를 했습니다.")
            return


        start_column = 'H'
        end_column = 'I'
        cell_range = f'{start_column}{row}:{end_column}{row}'
        new_values = [f'{ctime.hour}',f'{ctime.minute}']  
        worksheet.update(cell_range, [new_values])
        jb.stopValue=1
        await ctx.send(f"{bot.activity} 끝남")
        await bot.change_presence(
            activity=nextcord.Game("뭔가를 안")
        )
        

# Define the job to be run at 6:00 AM every day
async def job():
    channel=bot.get_channel(ip.public_channel_id)
    ctime=arrow.now("Asia/Seoul")
    ctime=ctime.datetime
    wd=("월","화","수","목","금","토","일")
    send_str=f"오늘은 {ctime.year}년 {ctime.month}월 {ctime.day}일 {wd[ctime.weekday()]}요일"
    await channel.send(send_str)

async def change_second(dm,ds,activity):

    ds+=3

    if ds>=60:
        dm+=1
        ds-=60

    await bot.change_presence(
        status=nextcord.Status.online,
        activity=nextcord.Game(f"{activity} {dm}분 {ds}초 동안 하는중")
    )

    return dm,ds




# Schedule the job with the AsyncIOScheduler    
scheduler = AsyncIOScheduler()
scheduler.add_job(job, 'cron', hour=6, minute=0)
scheduler.start()


# Run the bot
bot.run(ip.token)

