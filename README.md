# Warframe.market Watcher

Preface: if I were you, I would not share this to the general public unless you want the plat prices of the entire market to go down 10-20%. With that being said, I am a C/C++ programmer of 20+ years who hates Python because of how slow and ugly it is. BUT it is practical for little things like this when you want to throw some crap together in a day or so.

There might be bugs, use the issue tracker if you find any.

## Introduction

Ever wanted to make thousands of plat? Use [warframe.market](https://warframe.market) but need more features? So did I, so I made this. The Warframe.market Watcher is capable of keeping track of any user's sale/buy orders, checking if you were undercut, tracking all sales/bids for an item, and more!

## Features

- Track buy/sell orders of multiple users
- Track buy/sell orders of multiple items
- Realtime updates (refreshes every 5 minutes, this is a very slow operation because python sucks and also we don't want to ddos warframe.market)
- User order notifications if undercut and by how much
- Based on orders where the user is online/in game
- EN / PC only for now

## Installation

1. Install `python3` and `python3-pip`
2. `pip3 install setuptools`
3. `pip3 install wheel`
4. `pip3 install colorclass`
5. `pip3 install terminaltables`

Run with `python3 wfm_watcher.py` or just `./wfm_watcher.py` on linux

## Usage

```
$: ./wfm_watcher.py
Warframe Market Watcher
https://github.com/snail23/wfm_watcher

usage: wfm_watcher.py [-h] [-b USER [USER ...]] [-i ITEM [ITEM ...]]
                      [-s USER [USER ...]]

optional arguments:
  -h, --help            show this help message and exit
  -b USER [USER ...], --buyer USER [USER ...]
                        watch a user's buy orders (can specify multiple users)
  -i ITEM [ITEM ...], --item ITEM [ITEM ...]
                        watch an item's buy and sell orders (example: -i
                        fleeting_expertise blind_rage streamline)
  -s USER [USER ...], --seller USER [USER ...]
                        watch a user's sell orders (can specify multiple
                        users)
```
