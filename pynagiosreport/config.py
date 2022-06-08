'''
..  codeauthor:: Charles Blais <charles.blais@nrcan-rncan.gc.ca>
'''
import logging

from typing import List

from enum import Enum

from pathlib import Path

from functools import lru_cache

from pydantic import BaseSettings, BaseModel

from jinja2 import Template, Environment, FileSystemLoader


class LogLevels(Enum):
    DEBUG: str = 'DEBUG'
    INFO: str = 'INFO'
    WARNING: str = 'WARNING'
    ERROR: str = 'ERROR'


class MultitechFaxSettings(BaseModel):
    host: str
    port: int = 80
    url: str = '/ffws/v1/ofax'
    username: str = 'eqalert'
    password: str = '7a2eb62c3772be00ab403030034205cf'


class AppSettings(BaseSettings):
    log_level: LogLevels = LogLevels.WARNING
    log_format: str = '%(asctime)s.%(msecs)03d %(levelname)s \
%(module)s %(funcName)s: %(message)s'
    log_datefmt: str = '%Y-%m-%d %H:%M:%S'

    # Nagios plugins
    url = 'http://nagios-e1.seismo.nrcan.gc.ca'
    path_api = '/nagiosxi/api/v1/'
    path_status = '/nagiosxi/includes/components/xicore/status.php'
    apikey = ''

    templates_dir: str = str(Path(__file__).parent.joinpath(
        'files', 'templates'))

    smtp_server = 'mailhost.seismo.nrcan.gc.ca'
    email_subject = 'Nagios XI Report'
    email_from = 'cnsnopr@seismo.nrcan.gc.ca'

    fax_servers: List[MultitechFaxSettings] = [
        MultitechFaxSettings(
            host='faxserver-o2.seismo.nrcan.gc.ca',
        ),
        MultitechFaxSettings(
            host='faxserver-s1.seis.pgc.nrcan.gc.ca',
        ),
        MultitechFaxSettings(
            host='faxserver-s2.seis.pgc.nrcan.gc.ca',
        )]

    class Config:
        env_file = '.env'
        env_prefix = 'nagios_'

    @property
    def url_api(self) -> str:
        return f'{self.url}/{self.path_api}'

    @property
    def url_status(self) -> str:
        return f'{self.url}/{self.path_status}'

    @property
    def j2_templates_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True)

    @property
    def j2_status_template(self) -> Template:
        '''
        Jinja2 status output template
        '''
        return self.j2_templates_env.get_template('status.html.j2')

    @property
    def j2_fax_template(self) -> Template:
        '''
        Jinja2 status output template
        '''
        return self.j2_templates_env.get_template('schedule_fax.xml.j2')

    def configure_logging(self):
        '''
        Configure logging for app
        '''
        level = {
            LogLevels.DEBUG: logging.DEBUG,
            LogLevels.INFO: logging.INFO,
            LogLevels.WARNING: logging.WARNING,
            LogLevels.ERROR: logging.ERROR,
        }[self.log_level]
        logging.basicConfig(
            format=self.log_format,
            datefmt=self.log_datefmt,
            level=level)


@lru_cache()
def get_app_settings() -> AppSettings:
    return AppSettings()
