'''
..  codeauthor:: Charles Blais
'''
from pydantic import BaseModel, validator

import datetime


class HostStatus(BaseModel):
    acknowledgement_type: int
    action_url: str
    active_checks_enabled: int
    address: str
    check_command: str
    check_options: int
    check_timeperiod_object_id: int
    check_type: int
    current_check_attempt: int
    current_notification_number: int
    current_state: int
    display_name: str
    event_handler: str
    event_handler_enabled: int
    execution_time: float
    failure_prediction_enabled: int
    flap_detection_enabled: int
    has_been_checked: int
    host_alias: str
    host_name: str
    host_object_id: int
    hoststatus_id: int
    icon_image: str
    icon_image_alt: str
    instance_id: int
    is_flapping: int
    last_check: datetime.datetime
    last_hard_state: int
    last_hard_state_change: datetime.datetime
    last_notification: datetime.datetime
    last_state_change: datetime.datetime
    last_time_down: datetime.datetime
    last_time_unreachable: datetime.datetime
    last_time_up: datetime.datetime
    latency: float
    long_output: str
    max_check_attempts: int
    modified_host_attributes: int
    next_check: datetime.datetime
    next_notification: datetime.datetime
    no_more_notifications: int
    normal_check_interval: int
    notes: str
    notes_url: str
    notifications_enabled: int
    obsess_over_host: int
    output: str
    passive_checks_enabled: int
    percent_state_change: float
    perfdata: str
    problem_has_been_acknowledged: int
    process_performance_data: int
    retry_check_interval: int
    scheduled_downtime_depth: int
    should_be_scheduled: int
    state_type: int
    status_update_time: datetime.datetime


class ServiceStatus(BaseModel):
    acknowledgement_type: int
    action_url: str
    active_checks_enabled: int
    check_command: str
    check_options: int
    check_timeperiod_object_id: int
    check_type: int
    current_check_attempt: int
    current_notification_number: int
    current_state: int
    display_name: str
    event_handler: str
    event_handler_enabled: int
    execution_time: float
    failure_prediction_enabled: int
    flap_detection_enabled: int
    has_been_checked: int
    host_address: str
    host_alias: str
    host_name: str
    host_object_id: int
    icon_image: str
    icon_image_alt: str
    instance_id: int
    is_flapping: int
    last_check: datetime.datetime
    last_hard_state: int
    last_hard_state_change: datetime.datetime
    last_notification: datetime.datetime
    last_state_change: datetime.datetime
    last_time_critical: datetime.datetime
    last_time_ok: datetime.datetime
    last_time_unknown: datetime.datetime
    last_time_warning: datetime.datetime
    latency: float
    long_output: str
    max_check_attempts: int
    modified_service_attributes: int
    next_check: datetime.datetime
    next_notification: datetime.datetime
    no_more_notifications: int
    normal_check_interval: int
    notes: str
    notes_url: str
    notifications_enabled: int
    obsess_over_service: int
    output: str
    passive_checks_enabled: int
    percent_state_change: float
    perfdata: str
    problem_has_been_acknowledged: int
    process_performance_data: int
    retry_check_interval: int
    scheduled_downtime_depth: int
    service_description: str
    service_object_id: int
    servicestatus_id: int
    should_be_scheduled: int
    state_type: int
    status_update_time: datetime.datetime


class MultitechSender(BaseModel):
    name: str = 'CHIS'
    organization: str = 'NRCan'
    email: str = ''


class MultitechRecipient(BaseModel):
    number: str
    name: str = 'nagios'
    organization: str = 'NRCan'

    @validator('number')
    def validate_number(cls, v):
        return str(v).replace('-', '')
