import fastf1
from loguru import logger
from datetime import datetime
from pprint import pprint

def get_next_game()->str:
    '''
    base on current time get next game time and info
    '''

    today = datetime.now()
    logger.info(f'current time: {today}')

    try:
        schedule = fastf1.get_event_schedule(2025).sort_values('EventDate')
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
            f"""下一場F1大獎賽是 {next_game['EventName']}，是今年的第{next_game['RoundNumber']}輪競賽，比賽時間如下：\n
            練習賽：{next_game['Session1Date']}, {next_game['Session2Date']}, {next_game['Session3Date']}\n
            排位賽：{next_game['Session4Date']}\n
            正賽：{next_game['Session5Date']}\n"""
        pprint(output_str)
        return output_str
    except Exception as e:
        logger.error(f'get_next_game error: {e}')

if __name__ == '__main__':
    get_next_game()
