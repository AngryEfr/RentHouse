from amplitude import Amplitude, BaseEvent
from config_data.config import Config, load_config


config: Config = load_config('.env')
amplitude = Amplitude(config.tg_bot.amplitude_token)


def track_user(user_id, event):
    event = BaseEvent(event_type=event, user_id=str(user_id))
    amplitude.track(event)
