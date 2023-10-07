import requests
import json

class QBittorrent:
    """API Client for qBittorrent, using the WebUI API
    """

    def __init__(self, url: str):
        """Create a new QBittorrent API Client

        Args:
            url (string): URL to qBittorrent WebUI
        """
        self._session = requests.session()
        self._base_url = url

    def login(self, username: str, password: str) -> bool:
        """Login to qBittorrent WebUI

        Args:
            username (str): qBittorrent WebUI username
            password (str): qBittorrent WebUI password

        Returns:
            bool: Login success
        """
        url = self._base_url + "/api/v2/auth/login"
        response = self._session.post(url, 
            data={
                "username": username,
                "password": password
            })
        
        if response.status_code == 200 and response.text == 'Ok.':
            return True
        else:
            print(f"qBT Login failed: {response.text}")
            return False
        
    def get_feeds(self) -> dict[str, dict[str, str]]:
        """Get RSS feeds present on qBittorrent.

        Returns:
            dict[str, dict[str, str]]: Dict of feed name to url and uid
        """
        response = self._get('/rss/items')
        response.raise_for_status()
        return response.json()

    def add_feed(self, feed_name: str, feed_url: str) -> bool:
        """Add a feed to qBittorrent.
        Will return False if the feed name or url already exists.

        Args:
            feed_name (str): Feed name
            feed_url (str): Feed URL

        Returns:
            bool: Operation success
        """
        response = self._post('/rss/addFeed', {
            "url": feed_url,
            "path": feed_name
        })

        return response.status_code == 200
    
    def get_download_rules(self) -> dict[str, dict[str, str]]:
        """Get auto download rules present in qBittorrent.

        Returns:
            dict[str, dict[str, str]]: Dict of rule names to rules defintions
        """
        response = self._get('/rss/rules')
        response.raise_for_status()
        return response.json()
    
    def add_download_rule(self, rule_name: str, category_name: str, download_path: str, feed_urls: list[str], search_term: str) -> bool:
        """Add an auto download rule to qBittorrent.
        Will still return True if a rule by the same name already exists.

        Args:
            rule_name (str): Rule name
            category_name (str): Category name
            download_path (str): Download path
            feed_urls (list[str]): List of feed URLs
            search_term (str): Search term

        Returns:
            bool: Operation success
        """
        rule_def = {
            "addPaused": False,
            "affectedFeeds": feed_urls,
            "assignedCategory": category_name,
            "enabled": True,
            "episodeFilter": "",
            "ignoreDays": 0,
            "lastMatch": "",
            "mustContain": search_term,
            "mustNotContain": "",
            "previouslyMatchedEpisodes": [],
            "savePath": download_path,
            "smartFilter": False,
            "useRegex": False
        }

        response = self._post('/rss/setRule', {
            "ruleName": rule_name,
            "ruleDef": json.dumps(rule_def)
        })

        return response.status_code == 200

    def _get(self, endpoint: str, params: dict[str, str] = {}) -> requests.Response:
        """Make a GET request to the API

        Args:
            endpoint (str): Endpoint following the '/api/v2' location
            params (dict[str, str], optional): Query parameters. Defaults to {}.

        Returns:
            requests.Response: Response object
        """
        request_uri = self._base_url + "/api/v2" + endpoint
        return self._session.get(request_uri, params=params)
    
    def _post(self, endpoint: str, data) -> requests.Response:
        """Make a POST request to the API

        Args:
            endpoint (str): Endpoint following the '/api/v2' location
            data: Request body. Can be a dictionary, list of tuples, bytes, or file-like
            object

        Returns:
            requests.Response: Response object
        """
        request_uri = self._base_url + "/api/v2" + endpoint
        return self._session.post(request_uri, data=data)