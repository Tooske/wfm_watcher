#!/usr/bin/python3

import argparse
import colorclass
import json
import os
import requests
import sys
import terminaltables
import time

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

print('Warframe Market Watcher')
print('https://github.com/snail23/wfm_watcher')
print('')

parser = argparse.ArgumentParser()

parser.add_argument(
    '-b', '--buyer',
    help='watch a user\'s buy orders (can specify multiple users)',
    metavar='USER',
    nargs='+',
    action='append'
)

parser.add_argument(
    '-i', '--item',
    help='watch an item\'s buy and sell orders (example: -i fleeting_expertise blind_rage streamline)',
    nargs='+',
    action='append'
)

parser.add_argument(
    '-s', '--seller',
    help='watch a user\'s sell orders (can specify multiple users)',
    metavar='USER',
    nargs='+',
    action='append'
)

args = parser.parse_args()

if (args.buyer == None) and (args.item == None) and (args.seller == None):
    parser.print_help()
    sys.exit()

colorclass.Windows.enable(auto_colors = True, reset_atexit = True)

def get_order(orders, item):
    item_name = item['item']['url_name']
    mod_rank = str(item.get('mod_rank', 0))

    if not item_name in orders:
        orders[item_name] = {}

    if not mod_rank in orders[item_name]:
        orders[item_name][mod_rank] = {}

    result = requests.get('https://api.warframe.market/v1/items/' + item_name + '/orders', verify=False, headers={'Connection': 'close'})
    data = json.loads(result.text)

    for order in data['payload']['orders']:
        if (order['region'] == 'en') and (order['platform'] == 'pc') and (str(order.get('mod_rank', 0)) == mod_rank):
            if order['order_type'] == 'buy':
                if (order['user']['status'] == 'ingame') or (order['user']['status'] == 'online'):
                    if 'buy' in orders[item_name][mod_rank]:
                        if order['platinum'] > orders[item_name][mod_rank]['buy']['platinum']:
                            orders[item_name][mod_rank]['buy'] = order

                    else:
                        orders[item_name][mod_rank]['buy'] = order

            elif order['order_type'] == 'sell':
                if (order['user']['status'] == 'ingame') or (order['user']['status'] == 'online'):
                    if 'sell' in orders[item_name][mod_rank]:
                        if order['platinum'] < orders[item_name][mod_rank]['sell']['platinum']:
                            orders[item_name][mod_rank]['sell'] = order

                    else:
                        orders[item_name][mod_rank]['sell'] = order

    diffs = {
        'buy': [],
        'sell': []
    }

    for order in data['payload']['orders']:
        if (order['region'] == 'en') and (order['platform'] == 'pc') and (str(order.get('mod_rank', 0)) == mod_rank):
            if order['order_type'] == 'buy':
                if (order['user']['status'] == 'ingame') or (order['user']['status'] == 'online'):
                    if order['id'] != item['id']:
                        if order['platinum'] <= orders[item_name][mod_rank]['buy']['platinum']:
                            diffs['buy'].append(order['platinum'])

            elif order['order_type'] == 'sell':
                if (order['user']['status'] == 'ingame') or (order['user']['status'] == 'online'):
                    if order['id'] != item['id']:
                        if order['platinum'] >= orders[item_name][mod_rank]['sell']['platinum']:
                            diffs['sell'].append(order['platinum'])

    diffs['buy'].sort(reverse=True)
    diffs['sell'].sort()

    if 'buy' in orders[item_name][mod_rank]:
        orders[item_name][mod_rank]['buy']['previous'] = diffs['buy'][0] if len(diffs['buy']) > 0 else 0

    if 'sell' in orders[item_name][mod_rank]:
        orders[item_name][mod_rank]['sell']['previous'] = diffs['sell'][0] if len(diffs['sell']) > 0 else 0

def get_stats(stats, item):
    item_name = item['item']['url_name']
    mod_rank = str(item.get('mod_rank', 0))

    if not item_name in stats:
        stats[item_name] = {}

    if not mod_rank in stats[item_name]:
        stats[item_name][mod_rank] = {
            'buy_48_hr': 0,
            'buy_90_day': 0,
            'sell_48_hr': 0,
            'sell_90_day': 0
        }

    result = requests.get('https://api.warframe.market/v1/items/' + item_name + '/statistics', verify=False, headers={'Connection': 'close'})
    data = json.loads(result.text)

    b48 = 0
    b90 = 0

    s48 = 0
    s90 = 0

    for stat in data['payload']['statistics_live']['48hours']:
        if (order['region'] == 'en') and (order['platform'] == 'pc') and (str(stat.get('mod_rank', 0)) == mod_rank):
            if stat['order_type'] == 'buy':
                stats[item_name][mod_rank]['buy_48_hr'] += stat['avg_price']
                b48 += 1

            elif stat['order_type'] == 'sell':
                stats[item_name][mod_rank]['sell_48_hr'] += stat['avg_price']
                s48 += 1

    for stat in data['payload']['statistics_live']['90days']:
        if (order['region'] == 'en') and (order['platform'] == 'pc') and (str(stat.get('mod_rank', 0)) == mod_rank):
            if stat['order_type'] == 'buy':
                stats[item_name][mod_rank]['buy_90_day'] += stat['avg_price']
                b90 += 1

            elif stat['order_type'] == 'sell':
                stats[item_name][mod_rank]['sell_90_day'] += stat['avg_price']
                s90 += 1

    if b48 > 0:
        stats[item_name][mod_rank]['buy_48_hr'] /= b48

    if b90 > 0:
        stats[item_name][mod_rank]['buy_90_day'] /= b90

    if s48 > 0:
        stats[item_name][mod_rank]['sell_48_hr'] /= s48

    if s90 > 0:
        stats[item_name][mod_rank]['sell_90_day'] /= s90

while True:
    os.system('cls') if os.name == 'nt' else os.system('clear')

    stats = {}

    if args.buyer:
        for users in args.buyer:
            for user in users:
                result = requests.get('https://api.warframe.market/v1/profile/' + user + '/orders', verify=False, headers={'Connection': 'close'})
                data = json.loads(result.text)

                orders = {}
                buy_orders = []

                for order in data['payload']['buy_orders']:
                    if (order['region'] == 'en') and (order['platform'] == 'pc'):
                        item_name = order['item']['url_name']
                        mod_rank = str(order.get('mod_rank', 0))

                        get_order(orders, order)
                        get_stats(stats, order)

                        buy_orders.append(
                        [
                            colorclass.Color(order['item']['en']['item_name']),
                            colorclass.Color(mod_rank),
                            colorclass.Color(str(order['item'].get('mod_max_rank', 0))),
                            colorclass.Color(str(order['quantity'])),
                            colorclass.Color(str(int(round(stats[item_name][mod_rank]['buy_90_day']))) + 'p'),
                            colorclass.Color(str(int(round(stats[item_name][mod_rank]['buy_48_hr']))) + 'p'),
                            colorclass.Color(str(order['platinum']) + 'p'),
                            colorclass.Color('{higreen}' + str(order['platinum'] - orders[item_name][mod_rank]['buy']['previous']) + 'p diff: yes{/green}' if ((order['id'] == orders[item_name][mod_rank]['buy']['id']) or (order['platinum'] == orders[item_name][mod_rank]['buy']['platinum'])) else '{hired}' + '[+' + str(orders[item_name][mod_rank]['buy']['user']['reputation']) + '] ' + orders[item_name][mod_rank]['buy']['user']['ingame_name'] + ': ' + str(orders[item_name][mod_rank]['buy']['platinum']) + 'p{/red}')
                        ])

                buy_orders.sort(key=lambda order: order[0])
                buy_orders.insert(0,
                [
                    colorclass.Color('Item'),
                    colorclass.Color('Rank'),
                    colorclass.Color('Max'),
                    colorclass.Color('Qty'),
                    colorclass.Color('90 day avg'),
                    colorclass.Color('48 hr avg'),
                    colorclass.Color('Price'),
                    colorclass.Color('Highest')
                ])

                output = terminaltables.SingleTable(buy_orders, colorclass.Color(' {hicyan}' + user + '\'s bids{/cyan} '));

                output.inner_heading_row_border = True
                output.inner_row_border = True
                output.justify_columns = {
                    0: 'left',
                    1: 'right',
                    4: 'right',
                    5: 'right',
                    6: 'right',
                    7: 'right'
                }

                print(output.table)

    if args.item:
        for items in args.item:
            for item in items:
                result = requests.get('https://api.warframe.market/v1/items/' + item + '/orders', verify=False, headers={'Connection': 'close'})
                data = json.loads(result.text)

                buy_orders = []
                sell_orders = []

                for order in data['payload']['orders']:
                    if (order['region'] == 'en') and (order['platform'] == 'pc'):
                        if (order['user']['status'] == 'ingame') or (order['user']['status'] == 'online'):
                            mod_rank = str(order.get('mod_rank', 0))

                            order['item'] = {
                                'url_name': item
                            }

                            get_stats(stats, order)

                            if order['order_type'] == 'buy':
                                buy_orders.append(
                                [
                                    colorclass.Color('[+' + str(order['user']['reputation']) + '] ' + order['user']['ingame_name']),
                                    colorclass.Color(mod_rank),
                                    colorclass.Color(str(order['quantity'])),
                                    colorclass.Color(str(int(round(stats[item][mod_rank]['buy_90_day']))) + 'p'),
                                    colorclass.Color(str(int(round(stats[item][mod_rank]['buy_48_hr']))) + 'p'),
                                    order['platinum'],
                                ])

                            elif order['order_type'] == 'sell':
                                sell_orders.append(
                                [
                                    colorclass.Color('[+' + str(order['user']['reputation']) + '] ' + order['user']['ingame_name']),
                                    colorclass.Color(mod_rank),
                                    colorclass.Color(str(order['quantity'])),
                                    colorclass.Color(str(int(round(stats[item][mod_rank]['sell_90_day']))) + 'p'),
                                    colorclass.Color(str(int(round(stats[item][mod_rank]['sell_48_hr']))) + 'p'),
                                    order['platinum'],
                                ])

                buy_orders.sort(key=lambda order: order[5], reverse=True)

                for order in buy_orders:
                    order[5] = colorclass.Color(str(order[5]) + 'p')

                buy_orders.insert(0,
                [
                    colorclass.Color('User'),
                    colorclass.Color('Rank'),
                    colorclass.Color('Qty'),
                    colorclass.Color('90 day avg'),
                    colorclass.Color('48 hr avg'),
                    colorclass.Color('Price'),
                ])

                sell_orders.sort(key=lambda order: order[5])

                for order in sell_orders:
                    order[5] = colorclass.Color(str(order[5]) + 'p')

                sell_orders.insert(0,
                [
                    colorclass.Color('User'),
                    colorclass.Color('Rank'),
                    colorclass.Color('Qty'),
                    colorclass.Color('90 day avg'),
                    colorclass.Color('48 hr avg'),
                    colorclass.Color('Price'),
                ])

                output = terminaltables.SingleTable(buy_orders, colorclass.Color(' {hicyan}Bids for ' + item + '{/cyan} '));

                output.inner_heading_row_border = True
                output.inner_row_border = True
                output.justify_columns = {
                    1: 'right',
                    3: 'right',
                    4: 'right',
                    5: 'right'
                }

                print(output.table)

                output = terminaltables.SingleTable(sell_orders, colorclass.Color(' {hicyan}Sales for ' + item + '{/cyan} '));

                output.inner_heading_row_border = True
                output.inner_row_border = True
                output.justify_columns = {
                    1: 'right',
                    3: 'right',
                    4: 'right',
                    5: 'right'
                }

                print(output.table)

    if args.seller:
        for users in args.seller:
            for user in users:
                result = requests.get('https://api.warframe.market/v1/profile/' + user + '/orders', verify=False, headers={'Connection': 'close'})
                data = json.loads(result.text)

                orders = {}
                sell_orders = []

                for order in data['payload']['sell_orders']:
                    if (order['region'] == 'en') and (order['platform'] == 'pc'):
                        item_name = order['item']['url_name']
                        mod_rank = str(order.get('mod_rank', 0))

                        get_order(orders, order)
                        get_stats(stats, order)

                        sell_orders.append(
                        [
                            colorclass.Color(order['item']['en']['item_name']),
                            colorclass.Color(mod_rank),
                            colorclass.Color(str(order['item'].get('mod_max_rank', 0))),
                            colorclass.Color(str(order['quantity'])),
                            colorclass.Color(str(int(round(stats[item_name][mod_rank]['sell_90_day']))) + 'p'),
                            colorclass.Color(str(int(round(stats[item_name][mod_rank]['sell_48_hr']))) + 'p'),
                            colorclass.Color(str(order['platinum']) + 'p'),
                            colorclass.Color('{higreen}' + str(orders[item_name][mod_rank]['sell']['previous'] - order['platinum']) + 'p diff: yes{/green}' if ((order['id'] == orders[item_name][mod_rank]['sell']['id']) or (order['platinum'] == orders[item_name][mod_rank]['sell']['platinum'])) else '{hired}' + '[+' + str(orders[item_name][mod_rank]['sell']['user']['reputation']) + '] ' + orders[item_name][mod_rank]['sell']['user']['ingame_name'] + ': ' + str(orders[item_name][mod_rank]['sell']['platinum']) + 'p{/red}')
                        ])

                sell_orders.sort(key=lambda order: order[0])
                sell_orders.insert(0,
                [
                    colorclass.Color('Item'),
                    colorclass.Color('Rank'),
                    colorclass.Color('Max'),
                    colorclass.Color('Qty'),
                    colorclass.Color('90 day avg'),
                    colorclass.Color('48 hr avg'),
                    colorclass.Color('Price'),
                    colorclass.Color('Lowest')
                ])

                output = terminaltables.SingleTable(sell_orders, colorclass.Color(' {hicyan}' + user + '\'s sales{/cyan} '));

                output.inner_heading_row_border = True
                output.inner_row_border = True
                output.justify_columns = {
                    0: 'left',
                    1: 'right',
                    4: 'right',
                    5: 'right',
                    6: 'right',
                    7: 'right'
                }

                print(output.table)

    time.sleep(300)
    
