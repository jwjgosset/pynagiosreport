'''
..  codeauthor:: Charles Blais
'''
from pydantic import BaseModel

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


class HostStatusCore(BaseModel):
    host_name: str
    modified_attributes: int
    check_command: str
    check_period: str
    notification_period: str
    importance: int
    check_interval: float
    retry_interval: float
    event_handler: str
    has_been_checked: int
    should_be_scheduled: int
    check_execution_time: float
    check_latency: float
    check_type: int
    current_state: int
    last_hard_state: int
    last_event_id: int
    current_event_id: int
    current_problem_id: int
    last_problem_id: int
    plugin_output: str
    long_plugin_output: str
    performance_data: str
    last_check: datetime.datetime
    next_check: datetime.datetime
    check_options: int
    current_attempt: int
    max_attempts: int
    state_type: int
    last_state_change: datetime.datetime
    last_hard_state_change: datetime.datetime
    last_time_up: datetime.datetime
    last_time_down: datetime.datetime
    last_time_unreachable: datetime.datetime
    last_notification: datetime.datetime
    next_notification: datetime.datetime
    no_more_notifications: int
    current_notification_number: int
    current_notification_id: int
    notifications_enabled: int
    problem_has_been_acknowledged: int
    acknowledgement_type: int
    active_checks_enabled: int
    passive_checks_enabled: int
    event_handler_enabled: int
    flap_detection_enabled: int
    process_performance_data: int
    obsess: int
    last_update: datetime.datetime
    is_flapping: int
    percent_state_change: float
    scheduled_downtime_depth: int

    # The following are for cross-compatibility with HostStatus
    @property
    def output(self) -> str:
        return self.plugin_output

    @property
    def status_update_time(self) -> datetime.datetime:
        return self.last_update


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


class ServiceStatusCore(BaseModel):
    host_name: str
    service_description: str
    modified_attributes: int
    check_command: str
    check_period: str
    notification_period: str
    importance: int
    check_interval: float
    retry_interval: float
    event_handler: str
    has_been_checked: int
    should_be_scheduled: int
    check_execution_time: float
    check_latency: float
    check_type: int
    current_state: int
    last_hard_state: int
    last_event_id: int
    current_event_id: int
    current_problem_id: int
    last_problem_id: int
    current_attempt: int
    max_attempts: int
    state_type: int
    last_state_change: datetime.datetime
    last_hard_state_change: datetime.datetime
    last_time_ok: datetime.datetime
    last_time_warning: datetime.datetime
    last_time_unknown: datetime.datetime
    last_time_critical: datetime.datetime
    plugin_output: str
    long_plugin_output: str
    performance_data: str
    last_check: datetime.datetime
    next_check: datetime.datetime
    check_options: int
    current_notification_number: int
    current_notification_id: int
    last_notification: int
    next_notification: int
    no_more_notifications: int
    notifications_enabled: int
    active_checks_enabled: int
    passive_checks_enabled: int
    event_handler_enabled: int
    problem_has_been_acknowledged: int
    acknowledgement_type: int
    flap_detection_enabled: int
    process_performance_data: int
    obsess: int
    last_update: datetime.datetime
    is_flapping: int
    percent_state_change: float
    scheduled_downtime_depth: int

    # The following are for cross-compatibility with ServiceStatus
    @property
    def display_name(self) -> str:
        return self.service_description

    @property
    def output(self) -> str:
        return self.plugin_output

    @property
    def status_update_time(self) -> datetime.datetime:
        return self.last_update
