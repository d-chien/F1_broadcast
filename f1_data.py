import fastf1
from loguru import logger
from datetime import datetime
from pprint import pprint
import pandas as pd
from fastf1.livetiming.data import LiveTimingData

fastf1.Cache.enable_cache('Cache')

def get_next_game()->str:
    '''
    base on current time get next game time and info
    '''

    today = datetime.now()
    logger.info(f'current time: {today}')

    try:
        schedule = fastf1.get_event_schedule(today.year).sort_values('EventDate')
        next_game = schedule.loc[schedule.EventDate>=today].iloc[0].to_dict()
        for k,v in next_game.items():
            try:
                next_game[k] = v.tz_convert('Asia/Taipei').strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f'{next_game[k]}')
            except:
                pass
        pprint(next_game)
        logger.info(f'next game data retrieved, next game: {next_game["EventName"]}')

        # format return data
        output_str = \
            f"""下一場F1大獎賽是 {next_game['EventName']}，是今年的第{next_game['RoundNumber']}輪競賽，比賽時間如下：
練習賽：{next_game['Session1Date']}, {next_game['Session2Date']}, {next_game['Session3Date']}
排位賽：{next_game['Session4Date']}
正賽：{next_game['Session5Date']}"""
        print(output_str)
        return output_str
    except Exception as e:
        logger.error(f'get_next_game error: {e}')

def last_session_result()->str:
    '''
    by overview the last session result, return the result of last one
    '''

    today = datetime.now()
    logger.info(f'current time: {today}')

    try:
        schedule = fastf1.get_event_schedule(today.year).sort_values('EventDate')
        lstGame = schedule.loc[schedule.EventDate<=today].iloc[-1].to_dict()
        session = fastf1.get_session(today.year, lstGame['RoundNumber'],'R')
        logger.info(f'get session: {today.year} round {lstGame["RoundNumber"]}')
        session.load()
        result = session.results
        logger.info('session load completed')

        data = result.loc[result.Position<=10,['BroadcastName','TeamName','ClassifiedPosition','Time']]
        pprint(data)
        logger.info('data retrieved')
        ttl_sec = pd.to_timedelta(data.loc[data.ClassifiedPosition=='1','Time'].values[0]).total_seconds()

        output_str = f'''前場賽事 {lstGame['EventName'].replace('Grand Prix','GP')}
冠軍：{data.loc[data.ClassifiedPosition=='1','TeamName'].values[0]} || {data.loc[data.ClassifiedPosition=='1','BroadcastName'].values[0]}
完賽時間： {int(ttl_sec//3600):02}:{int((ttl_sec%3600)//60):02d}:{ttl_sec%60:06.3f}
'''
        print(output_str)
        logger.info('完成資料產出')
        return output_str


    except Exception as e:
        logger.error(f'last_session_result error: {e}')




if __name__ == '__main__':
    last_session_result()
