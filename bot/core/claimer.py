import asyncio
import inspect
import pprint
import random

from time import time
from datetime import datetime, timezone
from random import randint
from urllib.parse import unquote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers


class Claimer:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.random_sleep = random.randint(*settings.RANDOM_SLEEP)

    async def get_tg_web_data(self, proxy: str | None) -> dict[str]:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('dotcoin_bot'),
                bot=await self.tg_client.resolve_peer('dotcoin_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://dot.dapplab.xyz/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            me = await self.tg_client.get_me()

            data_json = {
                'id': str(me.id),
                'tg_web_data': tg_web_data
            }

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return data_json

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=self.random_sleep)

    async def get_token(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> dict[str]:
        try:
            http_client.headers[
                "Authorization"] = f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impqdm5tb3luY21jZXdudXlreWlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg3MDE5ODIsImV4cCI6MjAyNDI3Nzk4Mn0.oZh_ECA6fA2NlwoUamf1TqF45lrMC0uIdJXvVitDbZ8"
            http_client.headers["Content-Type"] = "application/json"
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/functions/v1/getToken',
                                              json={"initData": tg_web_data})
            response.raise_for_status()

            if response.ok:
                response_json = await response.json()
                return response_json
            else:
                return False

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting access token: {error}")
            await asyncio.sleep(delay=10)

    async def get_profile_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/get_user_info',
                                              json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=10)

    async def get_tasks_data(self, http_client: aiohttp.ClientSession, is_premium: bool) -> dict[str]:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/get_filtered_tasks',
                                              json={"platform": "android", "locale": "en", "is_premium": is_premium})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Tasks Data: {error}")
            await asyncio.sleep(delay=10)


    async def complate_task(self, http_client: aiohttp.ClientSession, task_id: int) -> bool:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/complete_task',
                                              json={"oid": task_id})
            response.raise_for_status()
            response_json = await response.json()
            return response_json['success']

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complate task: {error}")
            await asyncio.sleep(delay=10)
            return False

    async def upgrade_boosts(self, http_client: aiohttp.ClientSession, boost_type: str, lvl: int) -> bool:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post(f'https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/{boost_type}',
                                              json={"lvl": lvl})
            response.raise_for_status()
            response_json = await response.json()
            return response_json['success']

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complate task: {error}")
            await asyncio.sleep(delay=10)
            return False

    async def save_coins(self, http_client: aiohttp.ClientSession, taps: int):
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/save_coins',
                                              json={"coins": taps})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when saving coins: {error}")
            await asyncio.sleep(delay=10)
            return False

    async def try_your_luck(self, http_client: aiohttp.ClientSession, luck_amount: int) -> bool:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/try_your_luck',
                                              json={"coins": luck_amount})
            response.raise_for_status()
            response_json = await response.json()
            return response_json['success']

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when was treing to get luck: {error}")
            await asyncio.sleep(delay=10)
            return False

    async def restore_attempt(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/restore_attempt',
                                              json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json['success']

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when was treing to restore attempt: {error}")
            await asyncio.sleep(delay=10)
            return False

    async def get_assets(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/get_assets',
                                              json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Assets Data: {error}")
            await asyncio.sleep(delay=10)

    async def spin_to_earn(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}]")
            response = await http_client.post('https://jjvnmoyncmcewnuykyid.supabase.co/rest/v1/rpc/spin_to_win',
                                              json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when trying claim game 'Spin to Win': {error}")
            await asyncio.sleep(delay=10)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                try:
                    sleep_by_min_attempt = random.randint(*settings.SLEEP_BY_MIN_ATTEMPT)

                    http_client = CloudflareScraper(headers=headers)
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)

                    get_token_data = await self.get_token(http_client=http_client,tg_web_data=tg_web_data['tg_web_data'])
                    access_token = get_token_data.get('token')
                    user_id = get_token_data.get('userId')
                    logger.info(f"Generate new access_token: {access_token[:64]}...")

                    http_client.headers["Authorization"] = f"Bearer {access_token}"
                    http_client.headers["X-Telegram-User-Id"] = f"{user_id}"
                    await asyncio.sleep(delay=self.random_sleep)

                    profile_data = await self.get_profile_data(http_client=http_client)

                    balance = profile_data['balance']
                    level = profile_data['level']
                    new_balance = balance
                    daily_attempts = profile_data['daily_attempts']
                    limit_attempts = profile_data['limit_attempts']

                    logger.info(f"{self.session_name} | Level: <c>{level}</c>, Balance: <c>{balance}</c>, | "
                                f"Daily_Attempts: <c>{daily_attempts}</c>, Limit_Attempts: <c>{limit_attempts}</c>")

                    gamex2_times = profile_data.get('gamex2_times', 0)
                    if gamex2_times > 0:
                        got_lucky = await self.try_your_luck(http_client=http_client, luck_amount=settings.LUCK_AMOUNT)

                        if got_lucky:
                            logger.success(f"{self.session_name} | Got lucky: Yes")
                        else:
                            logger.info(f"{self.session_name} | Got lucky: No")

                    spin_updated_at = profile_data.get('spin_updated_at')
                    #print('spin_updated_at: ', spin_updated_at)

                    if spin_updated_at == None:
                        spin_updated_atx = 0
                    else:
                        spin_updated_atx = int(datetime.fromisoformat(spin_updated_at).timestamp())

                    current_date_utc = int(datetime.now().astimezone(timezone.utc).timestamp())

                    if (spin_updated_atx + 28800) < current_date_utc:
                        asset_data = await self.get_assets(http_client=http_client)

                        dtc_asset = None
                        dtc_amount = 0

                        for index, value in enumerate(asset_data):
                            if value['name'].lower() == 'dotcoin':
                                dtc_asset = value
                                dtc_amount = value['amount']

                        if not dtc_asset == None and dtc_amount > 0:
                            logger.info(f"{self.session_name} | Sleeping {self.random_sleep} before spin to earn")
                            await asyncio.sleep(delay=self.random_sleep)

                            spin_to_earn_response = await self.spin_to_earn(http_client=http_client)
                            logger.info(f"{self.session_name} | spin_to_earn_response: {spin_to_earn_response}")

                            if spin_to_earn_response.get('success'):
                                logger.info(f"{self.session_name} | You won: "
                                            f" {spin_to_earn_response.get('amount')} {spin_to_earn_response.get('symbol')}")

                    restored_attempt = await self.restore_attempt(http_client=http_client)
                    await asyncio.sleep(delay=self.random_sleep)

                    while restored_attempt:
                        action = 'daily_attempts'
                        daily_attempts += 1
                        logger.info(f"{self.session_name} | Restore attempt: {restored_attempt}")
                        logger.success(f"{self.session_name} | action: <red>[{action}]</red> - <c>{daily_attempts}</c>")
                        restored_attempt = await self.restore_attempt(http_client=http_client)
                        await asyncio.sleep(delay=self.random_sleep)
                    else:
                        logger.info(f"{self.session_name} | Restore attempt: {restored_attempt}")

                    tasks_data = await self.get_tasks_data(http_client=http_client,
                                                           is_premium=profile_data['is_premium'])

                    for task in tasks_data:
                        task_id = task["id"]
                        task_title = task["title"]
                        task_reward = task["reward"]
                        task_status = task["is_completed"]

                        if task_status is True:
                            continue

                        if task["url"] is None and task["image"] is None:
                            continue

                        task_data_claim = await self.complate_task(http_client=http_client, task_id=task_id)
                        if task_data_claim:
                            logger.success(f"{self.session_name} | Successful claim task | "
                                           f"Task Title: <c>{task_title}</c> | "
                                           f"Task Reward: <g>+{task_reward}</g>")
                            continue

                    while daily_attempts > 0:
                        taps = randint(*settings.RANDOM_TAPS_COUNT)
                        save_coins_data = await self.save_coins(http_client=http_client, taps=taps)
                        if save_coins_data.get('status'):
                            daily_attempts -= 1
                            logger.success(f"{self.session_name} | action: <red>[save_coins/{taps}/{daily_attempts}]</red> - "
                                           f"<c>{save_coins_data}</c>")
                            sleep = randint(*settings.RANDOM_SLEEP)
                            await asyncio.sleep(delay=sleep)
                        else:
                            logger.error(
                                f"{self.session_name} | action: <red>[save_coins/{taps}/{daily_attempts}]</red> - "
                                f"<c>{save_coins_data}</c>")
                            sleep = randint(*settings.RANDOM_SLEEP)
                            await asyncio.sleep(delay=sleep)
                            break

                    profile_data = await self.get_profile_data(http_client=http_client)

                    balance = int(profile_data['balance'])
                    daily_attempts = int(profile_data['daily_attempts'])
                    multiple_lvl = profile_data['multiple_clicks']
                    attempts_lvl = profile_data['limit_attempts'] - 9

                    next_multiple_lvl = multiple_lvl + 1
                    next_multiple_price = (2 ** multiple_lvl) * 1000
                    next_attempts_lvl = attempts_lvl + 1
                    next_attempts_price = (2 ** attempts_lvl) * 1000

                    if (settings.AUTO_UPGRADE_TAP is True
                            and balance > next_multiple_price
                            and next_multiple_lvl <= settings.MAX_TAP_LEVEL):
                        logger.info(f"{self.session_name} | Sleep {self.random_sleep}s before upgrade tap to {next_multiple_lvl} lvl")
                        await asyncio.sleep(delay=self.random_sleep)

                        status = await self.upgrade_boosts(http_client=http_client, boost_type="add_multitap",
                                                           lvl=multiple_lvl)
                        if status is True:
                            logger.success(f"{self.session_name} | Tap upgraded to {next_multiple_lvl} lvl")
                            await asyncio.sleep(delay=self.random_sleep)
                        continue

                    if (settings.AUTO_UPGRADE_ATTEMPTS is True
                            and balance > next_attempts_price
                            and next_attempts_lvl <= settings.MAX_ATTEMPTS_LEVEL):
                        logger.info(
                            f"{self.session_name} | Sleep {self.random_sleep} before upgrade limit attempts to {next_attempts_lvl} lvl")
                        await asyncio.sleep(delay=self.random_sleep)

                        status = await self.upgrade_boosts(http_client=http_client, boost_type="add_attempts",
                                                           lvl=attempts_lvl)
                        if status is True:
                            new_daily_attempts = next_attempts_lvl + 9
                            logger.success(
                                f"{self.session_name} | Limit attempts upgraded to {next_attempts_lvl} lvl (<m>{new_daily_attempts}</m>)")
                            await asyncio.sleep(delay=self.random_sleep)
                        continue

                    logger.info(f"{self.session_name} | Minimum attempts reached: {daily_attempts}")
                    logger.info(f"{self.session_name} | Next try to tap coins in {sleep_by_min_attempt}s")
                    await http_client.close()
                    await asyncio.sleep(delay=sleep_by_min_attempt)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await http_client.close()
                    await asyncio.sleep(delay=300)


async def run_claimer(tg_client: Client, proxy: str | None):
    while True:
        try:
            await Claimer(tg_client=tg_client).run(proxy=proxy)
        except InvalidSession:
            logger.error(f"{tg_client.name} | Invalid Session")
