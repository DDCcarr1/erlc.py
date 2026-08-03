import asyncio
import aiohttp
import json
import sys
import os
import time

class Erlc:
    """
    A simple client for interacting with the ER:LC API using ER:LC API v2.
    
    Args:
        server_key (str): The server key for the ER:LC API. This is required for requests to work. To obtain a server key, visit https://erlc.link/sk.
        auth_key (str, optional, default=None): The public app key for the ER:LC API. To obtain an auth key, visit https://apidocs.erlc.gg/creating-public-applications.
    """
    
    def __init__(self, server_key: str, auth_key: str = None):
        try:
            self.server_key = server_key
            self.auth_key = auth_key
        except Exception as e:
            print("An error occured while initializing the ER:LC API client. Please check your server key and/or auth key.")
    
    async def get_info(self, players: bool = False, staff: bool = False, join_logs: bool = False, queue: bool = False, kill_logs: bool = False, command_logs: bool = False, mod_calls: bool = False, emergency_calls: bool = False, vehicles: bool = False, all: bool = False) -> dict:
        """
        Returns the server information from the ER:LC API, all in one request.
        
        Args:
            players (bool, optional, default=False): Include player list in response.
            staff (bool, optional, default=False): Include staff list (Helpers, Mods, Admins) in response.
            join_logs (bool, optional, default=False): Include join logs in response.
            queue (bool, optional, default=False): Include queue data in response.
            kill_logs (bool, optional, default=False): Include kill logs in response.
            command_logs (bool, optional, default=False): Include command logs in response.
            mod_calls (bool, optional, default=False): Include moderator (`!mod`) call logs in response.
            emergency_calls (bool, optional, default=False): Include emergency call logs in response.
            vehicles (bool, optional, default=False): Include vehicle list in response.
            all (bool, optional, default=False): Include all data in response (so you don't have to specify each individually).
        
        Returns:
            dict: The server information from the ER:LC API.
        """
        
        try:
            if all:
                players = True
                staff = True
                join_logs = True
                queue = True
                kill_logs = True
                command_logs = True
                mod_calls = True
                emergency_calls = True
                vehicles = True
            
            url = "https://api.erlc.gg/v2/server"
            params = []
        
            for key, value in locals().items():
                if key not in [self, url, params]:
                    params.append((key, value))
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse method parameters and add them to a list, but an exception occured.",
                "error": str(e)
            }
             
        try:
            params_added = 0
            for key, value in params:
                if params_added == 0:
                    url = url + "?"
                else:
                    url = url + "&"
                
                url = url + key + "=" + str(value)
                params_added = params_added + 1
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to add method parameters to the URL, but an exception occured.",
                "error": str(e)
            }
            
        try:
            headers = {
                "server-key": self.server_key
            }
        
            if self.auth_key is not None:
                headers["Authorization"] = self.auth_key
        except ValueError as e:
            return {
                "code": 20, # value error in headers
                "message": "Attempted to add the auth key to the headers, but an exception occured.",
                "error": str(e)
            }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to add the auth key to the headers, but an exception occured.",
                "error": str(e)
            }
        
        try:
            data = {}
            async with aiohttp.ClientSession() as request:
                async with request.get(url, headers=headers) as response:
                    data = await response.json()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            return {
                "code": 30, # client connector error
                "message": "Attempted to connect to the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        except aiohttp.client_exceptions.ClientResponseError as e:
            return {
                "code": 31, # client response error
                "message": "Attempted to send a request with the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to make a connection and send a request with the ER:LC API, but an exception occured.",
                "error": str(e)
            }
            
        try:
            # parse data for errors from the ER:LC API
            if data.get('code', False): # if an error code is returned
                code = data.get('code') # int
                error = data.get('message') if data.get('message', False) else data.get('error', "An unknown error occured.") # str
                
                # -- system errors (0, 1001, 1002) --
                
                # unknown error occured
                if code == 0:
                    return {
                        "code": code,
                        "error": error,
                        "message": "Unknown error occurred. If this persists, contact PRC via an API ticket."
                    }
                
                # error occured while communicating with roblox or the in-game private server
                elif code == 1001:
                    return {
                        "code": code,
                        "error": error,
                        "message": "An error occured while communicating with Roblox or the in-game private server."
                    }
                
                # internal server error
                elif code == 1002:
                    return {
                        "code": code,
                        "error": error,
                        "message": "An internal server error occured."
                    }
                
                # -- authentication errors (2000-2004) --
                
                # no provided server key
                elif code == 2000:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You did not provide a server-key."
                    }
                
                # incorrectly formatted server key
                elif code == 2001:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You provided an incorrectly formatted server-key."
                    }
                    
                # invalid or expired server key
                elif code == 2002:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You provided an invalid or expired server-key."
                    }
                    
                # invalid auth key
                elif code == 2003:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You provided an invalid global API key (auth key)."
                    }
                
                # currently banned
                elif code == 2004:
                    return {
                        "code": code,
                        "error": error,
                        "message": "Your server-key is currently banned from accessing the ER:LC API."
                    }
                
                # -- request errors (3001-3002) --
                
                # invalid command
                elif code == 3001:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You did not provide a valid command in the request body."
                    }
                    
                # offline server
                elif code == 3002:
                    return {
                        "code": code,
                        "error": error,
                        "message": "The server you are attempting to reach is currently offline (has no players)."
                    }
                
                # -- rate limit and access errors (4000-4003) --
                
                # unauthorized
                elif code == 4000:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You are not authorized to perform this action on this server."
                    }
                
                # rate limit
                elif code == 4001:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You are being rate limited."
                    }
                
                # restricted command
                elif code == 4002:
                    return {
                        "code": code,
                        "error": error,
                        "message": "You are not authorized to use this command on this server."
                    }
                    
                # prohibited message
                elif code == 4003:
                    return {
                        "code": code,
                        "error": error,
                        "message": "The message you are trying to send is prohibited."
                    }
                
                # -- special codes (9998, 9999) --
                
                # restricted resource
                elif code == 9998:
                    return {
                        "code": code,
                        "error": error,
                        "message": "The resource you are trying to access is restricted."
                    }
                    
                # out of date module
                elif code == 9999:
                    return {
                        "code": code,
                        "error": error,
                        "message": "The module running on the in-game server is out of date. To fix this, shutdown the server (kick all players) and retry your request."
                    }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the data from the ER:LC API for errors, but an exception occured.",
                "error": str(e)
            }

        try:
            # parse data to provide in format
            server_information = {
                "details": {
                    "name": data.get('Name'), # str
                    "owner": data.get('OwnerId'), # int
                    "co_owners": data.get('CoOwnerIds'), # list, int
                    "ingame_players": data.get('CurrentPlayers'), # int
                    "max_players": data.get('MaxPlayers'), # int
                    "join_key": data.get('JoinKey'), # str
                        "account_verified_requirement": data.get('AccountVerifiedRequirement'), # enum, str: 'Disabled', 'Email', 'Phone/ID'
                        "team_balance": data.get('TeamBalance') # bool, True if team balance is enabled, False if team balance is disabled
                    }
                }
            except Exception as e:
                return {
                    "code": 10, # undefined exception occured
                    "message": "Attempted to parse the data from the ER:LC API, but an exception occured.",
                    "error": str(e)
                }

                server_information["code"] = 200 # int
                server_information["message"] = "Successfully retrieved server information from the ER:LC API." # str
                server_information["error"] = "" # str, empty

                return server_information
            
            except Exception as e:
                return {
                    "code": 10, # undefined exception occured
                    "message": "Attempted to parse the data from the ER:LC API for errors, but an exception occured.",
                    "error": str(e)
                }