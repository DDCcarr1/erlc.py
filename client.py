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
        
        try:
            if players:
                players_list = []
                for player in data.get('Players'):
                    player_details = player.get('Player') # str
                    player_id = int(player_details.split(':')[1]) # int
                    player_name = player_details.split(':')[0] # str
                    
                    players_list.append({
                        "team": player.get('Team'), # enum, str: 'Sheriff', 'Police', 'Fire', 'Civilian', 'Criminal', 'DOT'
                        "player": {
                            "id": player_id, # int
                            "name": player_name # str
                        },
                        "callsign": player.get('Callsign'), # str
                        "location": {
                            "position": {
                                "x": player.get('Location').get('LocationX'), # float
                                "z": player.get('Location').get('LocationZ') # float
                            },
                            "postal": int(player.get('Location').get('PostalCode')), # int
                            "street": player.get('Location').get('Street'), # str
                            "building": int(player.get('Location').get('Building')), # int
                        },
                        "staff-perms": player.get('Permissions'), # enum, str: 'Normal', 'Server Administrator', 'Server Moderator', 'Server Owner', 'Server Helper'
                        "wanted_level": player.get('WantedLevel') # int
                    })
                    
                server_information["details"]["players"] = players_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the players from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if staff:
                server_information["staff"] = {
                    "helpers": data.get('Helpers'), # dict, key: str (id), value: str (name)
                    "moderators": data.get('Mods'), # dict, key: str (id), value: str (name)
                    "administrators": data.get('Admins') # dict, key: str (id), value: str (name)
                }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the staff from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if join_logs:
                join_logs_list = []
                for join_log in data.get('JoinLogs'):
                    player_details = join_log.get('Player') # str
                    player_id = int(player_details.split(':')[1]) # int
                    player_name = player_details.split(':')[0] # str
                    
                    join_logs_list.append({
                        "join": join_log.get('Join'), # bool, True if player joined server, False if player left server
                        "timestamp": join_log.get('Timestamp'), # int, unix epoch timestamp
                        "player": {
                            "id": player_id, # int
                            "name": player_name # str
                        }
                    })
                    
                server_information["join_logs"] = join_logs_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the join logs from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if queue:
                server_information["queue"] = data.get('Queue') # list, int (player id)
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the queue from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
            
        try:
            if kill_logs:
                kill_logs_list = []
                for kill_log in data.get('KillLogs'):
                    player_killed_details = kill_log.get('Killed') # str
                    player_killed_id = int(player_killed_details.split(':')[1]) # int
                    player_killed_name = player_killed_details.split(':')[0] # str
                    
                    player_killer_details = kill_log.get('Killer') # str
                    player_killer_id = int(player_killer_details.split(':')[1]) # int
                    player_killer_name = player_killer_details.split(':')[0] # str
                    
                    kill_logs_list.append({
                        "killed": {
                            "id": player_killed_id, # int
                            "name": player_killed_name # str
                        },
                        "killer": {
                            "id": player_killer_id, # int
                            "name": player_killer_name # str
                        },
                        "timestamp": kill_log.get('Timestamp') # int, unix epoch timestamp
                    })
                    
                server_information["kill_logs"] = kill_logs_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the kill logs from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if command_logs:
                command_logs_list = []
                for command_log in data.get('CommandLogs'):
                    player_details = command_log.get('Player') # str
                    player_id = int(player_details.split(':')[1]) # int
                    player_name = player_details.split(':')[0] # str
                    
                    command_logs_list.append({
                        "player": {
                            "id": player_id, # int
                            "name": player_name # str
                        },
                        "command": command_log.get('Command'), # str
                        "timestamp": command_log.get('Timestamp') # int, unix epoch timestamp
                    })
                    
                server_information["command_logs"] = command_logs_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the command logs from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if mod_calls:
                mod_calls_list = []
                for mod_call in data.get('ModCalls'):
                    player_caller_details = mod_call.get('Caller') # str
                    player_caller_id = int(player_caller_details.split(':')[1]) # int
                    player_caller_name = player_caller_details.split(':')[0] # str
                    
                    player_staff_details = mod_call.get('Moderator') # str
                    player_staff_id = int(player_staff_details.split(':')[1]) # int
                    player_staff_name = player_staff_details.split(':')[0] # str
                    
                    mod_calls_list.append({
                        "caller": {
                            "id": player_caller_id, # int
                            "name": player_caller_name # str
                        },
                        "staff": {
                            "id": player_staff_id, # int
                            "name": player_staff_name # str
                        },
                        "timestamp": mod_call.get('Timestamp') # int, unix epoch timestamp
                    })
                    
                server_information["mod_calls"] = mod_calls_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the mod calls from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        try:
            if emergency_calls:
                emergency_calls_list = []
                for emergency_call in data.get('EmergencyCalls'):
                    emergency_calls_list.append({
                        "team": emergency_call.get('Team'), # enum, str: 'Sheriff', 'Police', 'Fire', 'Civilian', 'Criminal', 'DOT'
                        "caller": emergency_call.get('Caller'), # int (player id)
                        "players": emergency_call.get('Players'), # list, int (player id)
                        "position": emergency_call.get('Position'), # list, float (x, z)
                        "timestamp": emergency_call.get('Timestamp'), # int, unix epoch timestamp (time when emergency call began)
                        "call": emergency_call.get('Call'), # int (call number)
                        "description": emergency_call.get('Description'), # str
                        "location": emergency_call.get('PositionDescriptor') # str
                    })
                    
                server_information["emergency_calls"] = emergency_calls_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the emergency calls from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
         
        try:
            if vehicles:
                vehicles_list = []
                for vehicle in data.get('Vehicles'):
                    vehicles_list.append({
                        "name": vehicle.get('Name'), # str
                        "owner": vehicle.get('Owner'), # str (player name)
                        "plate": vehicle.get('Plate'), # str
                        "livery": vehicle.get('Texture'), # str
                        "color": {
                            "hex": vehicle.get('ColorHex'), # str, hex
                            "name": vehicle.get('ColorName') # str
                        }
                    })
                    
                    server_information["vehicles"] = vehicles_list
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the vehicles from the ER:LC API, but an exception occured.",
                "error": str(e)
            }
        
        
        server_information["code"] = 200 # int
        server_information["message"] = "Successfully retrieved server information from the ER:LC API." # str
        server_information["error"] = "" # str, empty
        
        return server_information
    
    async def run_command(self, command: str) -> dict:
        """
        Run a command as Remote Server Management in the ER:LC server. Remote Server Management has access to Co-Owner (owner) level commands as well as all lower-level commands.
        
        Args:
            command (str): The command to run's full body (ex. `:command arg1 arg2`).
            
        Returns:
            dict: The status of the command from the ER:LC API.
        """
        
        try:
            url = "https://api.erlc.gg/v1/server/command"
            
            payload = {
                "command": command
            }
            
            headers = {
                "server-key": self.server_key,
                "Content-Type": "application/json"
            }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse method parameters and add them to a list, but an exception occured.",
                "error": str(e)
            }
        
        try:
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
                async with request.post(url, headers=headers, data=json.dumps(payload)) as response:
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
            message = data.get('message')
            # parse data for errors and response from the ER:LC API
            if message == "Success":
                return {
                    "code": 200,
                    "message": "Successfully ran command on the ER:LC API.",
                    "response": message
                }
            
            elif message == "Missing command in request body":
                return {
                    "code": 400,
                    "message": "You did not provide a command in the request body."
                    "error": message
                }
                
            elif message == "The private server is currently offline.":
                return {
                    "code": 422,
                    "message": "The private server is currently offline.",
                    "commandId": data.get('commandId'),
                    "error": message
                }
                
            elif message == "Error communicating with Roblox":
                return {
                    "code": 500,
                    "message": "Error communicating with Roblox.",
                    "commandId": data.get('commandId'),
                    "error": message
                }
            
            else:
                return {
                    "code": 50, # undefined error? occured
                    "message": "An unknown error occured that is not an exception or outlined by the ER:LC API.",
                    "error": message
                }
        except Exception as e:
            return {
                "code": 10, # undefined exception occured
                "message": "Attempted to parse the data from the ER:LC API for errors, but an exception occured.",
                "error": str(e)
            }