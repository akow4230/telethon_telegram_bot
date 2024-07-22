from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE 
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)

    async def create_table_channels(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Channel (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            channel_id BIGINT NOT NULL UNIQUE,
            channel_url VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def add_channel(self, name, channel_id, channel_url):
        sql = "INSERT INTO Channel (name, channel_id, channel_url) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, name, channel_id, channel_url, fetchrow=True)

    async def select_all_channels(self):
        sql = "SELECT * FROM Channel"
        return await self.execute(sql, fetch=True)

    async def select_channel_by_id(self, channel_id):
        sql = "SELECT * FROM Channel WHERE id = $1"
        return await self.execute(sql, channel_id, fetchrow=True)

    async def update_channel_name(self, channel_id, new_name):
        sql = "UPDATE Channel SET name = $1 WHERE id = $2"
        return await self.execute(sql, new_name, channel_id, execute=True)

    async def delete_channel(self, channel_id):
        print(channel_id)
        sql = "DELETE FROM Channel WHERE id = $1"
        return await self.execute(sql, channel_id, execute=True)

    async def drop_channels(self):
        await self.execute("DROP TABLE Channel", execute=True)


    async def create_accounts(self):
        sql = """
        CREATE TABLE IF NOT EXISTS botusers (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        api_id BIGINT NOT NULL UNIQUE,
        api_hash VARCHAR(255) NOT NULL,
        session VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)
    async def select_all_accounts(self):
        sql = "SELECT * FROM botusers"
        return await self.execute(sql, fetch=True)


    async def select_account(self, telegram_id):
        # Convert telegram_id to an integer
        telegram_id = int(telegram_id)

        sql = "SELECT * FROM botusers WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)
    async def count_account(self):
        sql = "SELECT COUNT(*) FROM botusers"
        return await self.execute(sql, fetchval=True)


    async def delete_account(self):
        await self.execute("DELETE FROM botusers WHERE TRUE", execute=True)

    async def drop_accounts(self):
        await self.execute("DROP TABLE botusers", execute=True)

    async def update_user_name(self, username, telegram_id):
        sql = "UPDATE Users SET full_name=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

