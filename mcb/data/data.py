from datetime import datetime, timedelta
import time as t
import typing
from . import nfl_api_parser as nflparser
import logging
logger = logging.getLogger(__name__)

NETWORK_RETRY_SLEEP_TIME = 10.0
NUM_RETRIES = 5

class Data:
    _priority_game_count: int = 0

    def __init__(self, config):
        # Save the parsed config
        self.config = config

        self.games = None

        # Flag to determine when to refresh data
        self.needs_refresh = True

        self.helmet_logos = self.config.helmet_logos
        
        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()
        # Fetch the teams info
        self.refresh_games()

        # self.playoffs = nflparser.is_playoffs()
        # self.games = nflparser.get_all_games()
        # self.game = self.choose_game()
        # self.gametime = self.get_gametime()

        # What game do we want to start on?
        self.current_game_index = 0
        self.current_division_index = 0
        # self.scores = {}

    def get_current_date(self):
        return datetime.utcnow()
    
    # def refresh_game(self):
    #     self.game = self.choose_game()
    #     self.needs_refresh = False

    def refresh_games(self):
        """
        Download game data from the ESPN NFL API.
        May block for a very long time during retries.
        """
        attempts_remaining = NUM_RETRIES
        while attempts_remaining > 0:
            try:
                all_games = nflparser.get_all_games()
                self.games = self._get_prioritized_games_store_count(all_games)

                self.games_refresh_time = t.time()
                self.network_issues = False
                break
            except Exception as e:
                self.network_issues = True
                logger.error("Networking error while refreshing the master list of games. {} retries remaining.".format(attempts_remaining))
                logger.error("Exception: {}".format(e))
                attempts_remaining -= 1
                t.sleep(NETWORK_RETRY_SLEEP_TIME)
            except ValueError:
                self.network_issues = True
                logger.error("Value Error while refreshing master list of games. {} retries remaining.".format(attempts_remaining))
                logger.error("ValueError: Failed to refresh list of games")
                attempts_remaining -= 1
                t.sleep(NETWORK_RETRY_SLEEP_TIME)

        # # If we run out of retries, just move on to the next game
        # if attempts_remaining <= 0 and self.config.rotation_enabled:
        #     self.advance_to_next_game()

    def get_gametime(self):
        tz_diff = t.timezone if (t.localtime().tm_isdst == 0) else t.altzone
        gametime = datetime.strptime(self.games[self.current_game_index]['date'], "%Y-%m-%dT%H:%MZ") + timedelta(hours=(tz_diff / 60 / 60 * -1))
        return gametime

    def current_game(self):
        if self.games is None:
            return None
        else:
            return self.games[self.current_game_index]

    # def update_scores(self, homescore, awayscore):
    #     self.scores[self.current_game_index] = {'home': homescore, 'away': awayscore}

    # def get_current_scores(self):
    #     if self.scores[self.current_game_index]:
    #         return self.scores[self.current_game_index]
    #     else:
    #         return {'home': 0, 'away': 0}

    # def refresh_overview(self):
    #     attempts_remaining = 5
    #     while attempts_remaining > 0:
    #         try:
    #             self.__update_layout_state()
    #             self.needs_refresh = False
    #             self.print_overview_debug()
    #             self.network_issues = False
    #             break
    #         except URLError, e:
    #             self.network_issues = True
    #             logger.error("Networking Error while refreshing the current overview. {} retries remaining.".format(attempts_remaining))
    #             logger.error("URLError: {}".format(e.reason))
    #             attempts_remaining -= 1
    #             time.sleep(NETWORK_RETRY_SLEEP_TIME)
    #         except ValueError:
    #             self.network_issues = True
    #             logger.error("Value Error while refreshing current overview. {} retries remaining.".format(attempts_remaining))
    #             logger.error("ValueError: Failed to refresh overview for {}".format(self.current_game().game_id))
    #             attempts_remaining -= 1
    #             time.sleep(NETWORK_RETRY_SLEEP_TIME)

    #     # If we run out of retries, just move on to the next game
    #     if attempts_remaining <= 0 and self.config.rotation_enabled:
    #         self.advance_to_next_game()

    def advance_to_next_game(self):
        self.current_game_index = (self.current_game_index + 1) % self._priority_game_count
        return self.current_game()

    # def game_index_for_preferred_team(self):
    #     if self.config.preferred_teams:
    #         return self.__game_index_for(self.config.preferred_teams[0])
    #     else:
    #         return 0
    @staticmethod
    def _get_games_involving_teams(games: typing.List, teams: typing.List[str]):
        """
        Return the subset of given games that involve at least one of the listed teams.
        """
        return list(game for game in games if set([game['awayteam'], game['hometeam']]).intersection(set(teams)))

    @staticmethod
    def _get_games_not_involving_teams(games: typing.List, teams: typing.List[str]):
        """
        Return the subset of given games that involve none of the listed teams.
        """
        return list(game for game in games if not set([game['awayteam'], game['hometeam']]).intersection(set(teams)))

    @staticmethod
    def _get_games_with_status(games: typing.List, state: str) -> typing.List:
        """
        Return the subset of given games that have the given state.

        state: str, should be one of: ['pre', 'post', 'in']
        """
        return list(game for game in games if game['state'] == state)

    # def __game_index_for(self, team_name):
    #     team_index = 0
    #     print(self.games)
    #     # team_idxs = [i for i, game in enumerate(self.games) if team_name in [game.awayteam, game.hometeam]]
    #     for game in enumerate(self.games):
    #         print(game)
    #     return team_index

    # def __next_game_index(self):
    #     counter = self.current_game_index + 1
    #     if counter >= len(self.games):
    #         counter = 0
    #     return counter

    def _get_prioritized_games_store_count(self, all_games: typing.List) -> typing.List:
        """
        Take a list of all games from the NFL API and return a prioritized version. (shallow copied)
        Also stores the length of the highest priority category.


        Priorities:
            1. Active games involving preferred teams
            2. Active games without preferred teams
            3. Upcoming games
            4. Completed games
        """
        games_in_progress = Data._get_games_with_status(all_games, 'in')
        # Split the list of games in progress
        games_in_prog_preferred = Data._get_games_involving_teams(games_in_progress, self.config.preferred_teams)
        games_in_prog_unpreferred = Data._get_games_not_involving_teams(games_in_progress, self.config.preferred_teams)

        upcoming_games = Data._get_games_with_status(all_games, 'pre')
        finished_games = Data._get_games_with_status(all_games, 'post')

        prioritized_list = games_in_prog_preferred + games_in_prog_unpreferred + upcoming_games + finished_games

        # Locate the highest priority list and note its length
        if len(games_in_prog_preferred) > 0:
            self._priority_game_count = len(games_in_prog_preferred)
            logger.debug("%d preferred-team games are active of %d total games"%(self._priority_game_count, len(prioritized_list)))
        elif len(games_in_prog_unpreferred) > 0:
            self._priority_game_count = len(games_in_prog_unpreferred)
            logger.debug("%d unpreferred-team games are active of %d total games"%(self._priority_game_count, len(prioritized_list)))
        elif len(upcoming_games) > 0:
            self._priority_game_count = len(upcoming_games)
            logger.debug("%d games are upcoming of %d total games"%(self._priority_game_count, len(prioritized_list)))
        else:
            self._priority_game_count = len(finished_games)
            logger.debug("%d == %d total games are finished"%(self._priority_game_count, len(prioritized_list)))

        return prioritized_list

    #
    # Debug info

    # def print_overview_debug(self):
    #     logger.log("Overview Refreshed: {}".format(self.overview.id))
    #     logger.log("Pre: {}".format(Pregame(self.overview, self.config.time_format)))
    #     logger.log("Live: {}".format(Scoreboard(self.overview)))
    #     logger.log("Final: {}".format(Final(self.current_game())))