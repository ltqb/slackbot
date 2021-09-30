import datetime
import json
import requests
import pandas as pd
import sys


# from flask_bootstrap import Bootstrap
# from flask import Flask,render_template
# app = Flask(__name__)
# bootstrap = Bootstrap(app)


# history count var
history_count=sys.argv[1]

#print(history_count)
def stamp_2_time(time_stamp):
    date_array = datetime.datetime.fromtimestamp(time_stamp)
    return date_array.strftime("%Y-%m-%d %H:%M:%S")


def get_infos_from_slack(slack_url, cookies, form_data):
    headers = {"Cookie": cookies}
    respone = requests.request(
        url=slack_url, headers=headers, files=form_data, method="post")
    json_str = json.loads(respone.text)
    return json_str


def get_slack_messages_in_channel(channel_id, slack_url, cookies, token, lines):
    result = get_infos_from_slack(
        slack_url=slack_url,
        cookies=cookies,
        form_data={
            "channel": (None, channel_id),
            "token": (None, token),
            "limit": (None, lines)
        }
    )
    return result


def get_slack_replies_from_dt(channel_id, ts, slack_url, cookies, token):
    result = get_infos_from_slack(
        slack_url=slack_url,
        cookies=cookies,
        form_data={
            "channel": (None, channel_id),
            "token": (None, token),
            "ts": (None, ts)
        }
    )
    return result

def get_user_name_from_slack(user_id,token,cookie):

    headers = {"Cookie": cookie}
    form_data={
            "token": token,
            "user": user_id
        }
    result=requests.post("https://ebay-eng.slack.com/api/users.profile.get? \
        _x_id=0906d395-1632649728.511&_x_csid=rLmLhysoBUk&slack_route=E3U2DUYG4%3AT0M05TDH6&_x_version_ts=1632532046&_x_gantry=true"
       ,headers=headers,data=form_data)
    return (str(json.loads(result.text)['profile']['display_name_normalized']))

def get_useful_infos():
    # slack url
    history_url = "https://ebay-eng.slack.com/api/conversations.history? \
        _x_id=0906d395-1632649728.511&_x_csid=rLmLhysoBUk&slack_route=E3U2DUYG4%3AT0M05TDH6&_x_version_ts=1632532046&_x_gantry=true"
    replies_url = "https://ebay-eng.slack.com/api/conversations.replies? \
        _x_id=0906d395-1632652208.544&_x_csid=SGaKvjV7tFM&slack_route=E3U2DUYG4%3AT0M05TDH6&_x_version_ts=1632532046&_x_gantry=true"

   # user token
    token = ""
   # user cookie
    cookie = ""
   # channel id
    channel = ''

    messages_list = get_slack_messages_in_channel(
        channel_id=channel,
        slack_url=history_url,
        cookies=cookie,
        token=token,
        lines=history_count
    )
    text_array = []
    user_array = []
    ct_array = []
    rt_arrry = []
    interval_array = []
    latest_response_time_array = []
    latest_response_interval_array = []
    replies_text_array = []

    # foreach message in slack channel
    for message in messages_list["messages"]:
        message_ts = message['ts']
        message_create_time = stamp_2_time(int(float(message_ts)))
        message_text = message['text']
        if 'user' not in message.keys():
            message_user="bot"
        else:
            message_user = get_user_name_from_slack(message['user'],token=token,cookie=cookie)
        replies_result = get_slack_replies_from_dt(
            channel_id=channel,
            ts=message_ts,
            slack_url=replies_url,
            cookies=cookie,
            token=token
        )
        replies_list = replies_result['messages']

        # generate ts array and replies text for dict
        #ts_list = [{'ts': x['ts'], 'text':x['text']}for x in replies_result['messages']]
        ts_list = []
        replies_text_list = []

        for message_replies in replies_result['messages']:
            reply_user=''
            ts_list.append(message_replies['ts'])
            if 'user' in message_replies.keys():
                reply_user=get_user_name_from_slack(message_replies['user'],token=token,cookie=cookie)
                replies_text_list.append(str(int(float(message_replies['ts']))-int(float(message_ts))) + " " +
                                      reply_user + ": " + message_replies['text'])
            else:
                replies_text_list.append(str(int(float(message_replies['ts']))-int(float(message_ts))) + "bot : " + message_replies['text'])

        response_time = ""
        response_interval = 0
        latest_response_time = ''
        latest_response_interval = 0
        replies_all_text = ''
        if len(replies_text_list) > 1:
            replies_all_text = '\n'.join(replies_text_list[1:])

        #
        if len(ts_list) > 1:
            response_time = stamp_2_time(int(float(ts_list[1])))
            response_interval = int(
                float(ts_list[1]))-int(float(message_ts))
            latest_response_time = stamp_2_time(int(float(ts_list[-1])))
            latest_response_interval = int(
                float(ts_list[-1]))-int(float(message_ts))
            print("User: {} ,Create Time: {} , Response time: {} ,Response Interval: {} s , Latest Response time: {} ,latest response interval: {}".format(
                message_user,
                message_create_time,
                stamp_2_time(int(float(ts_list[1]))),
                response_interval,
                latest_response_time,
                latest_response_interval
            ))
        else:
            response_time = ""
            print("User: {} ,Create Time: {} , Response time: ,No Response".format(
                message_user,
                message_create_time,)
            )
        text_array.append(message_text)
        user_array.append(message_user)
        ct_array.append(message_create_time)
        rt_arrry.append(response_time)
        interval_array.append(response_interval)
        latest_response_time_array.append(latest_response_time)
        latest_response_interval_array.append(latest_response_interval)
        replies_text_array.append(replies_all_text)
    writer = pd.ExcelWriter('output.xlsx')
    my_data = pd.DataFrame(data={
        'user': list(reversed(user_array)),
        'create_time': list(reversed(ct_array)),
        'response_time': list(reversed(rt_arrry)),
        'time_to_response': list(reversed(interval_array)),
        'latest_response': list(reversed(latest_response_time_array)),
        'time_to_latest_response': list(reversed(latest_response_interval_array)),
        'describe': list(reversed(text_array)),
        'replies': list(reversed(replies_text_array))
    })
    my_data.to_excel(writer, 'Sheet1')
    writer.save()

# @app.route('/')
# def flask_test_html():
#     return render_template('slack_history_handler.html')


if __name__ == "__main__":
    get_useful_infos()
    # app.run()
