from upstash_qstash import Client, Receiver

from backend.settings import Config


receiver = Receiver({
    "current_signing_key": Config.QSTASH_CURRENT_SIGNING_KEY,
    "next_signing_key": Config.QSTASH_NEXT_SIGNING_KEY
})

client = Client(Config.QSTASH_TOKEN)

def init_scheduler():
    schedules = client.schedules()

    res = schedules.create({
        "destination": Config.SCHEDULE_URL,
        "cron": "0 0 * * *" # Every day at midnight,
    })

    print(res)

    return res['scheduleId']