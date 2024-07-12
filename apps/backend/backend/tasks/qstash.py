from upstash_qstash import Client, Receiver

from backend.settings import Config


receiver = Receiver({
    "current_signing_key": Config.QSTASH_CURRENT_SIGNING_KEY,
    "next_signing_key": Config.QSTASH_NEXT_SIGNING_KEY
})

client = Client(Config.QSTASH_TOKEN)

def init_scheduler():
    schedules = client.schedules()

    schedules_list = schedules.list()

    # clear all schedules
    for schedule in schedules_list:
        schedules.delete(schedule['scheduleId'])

    res = schedules.create({
        "destination": Config.SCHEDULE_URL,
        "cron": "0 0 * * *" # Every day at midnight,
    })

    return res['scheduleId']


def remove_scheduler(schedule_id):
    if not schedule_id:
        return
    schedules = client.schedules()

    schedules.delete(schedule_id)