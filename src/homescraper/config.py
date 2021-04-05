import yaml


def parse_config(config_path):
    with open(config_path) as config:
        config_dict = yaml.full_load(config)

    return config_dict['queries'], config_dict['db_path'], config_dict['twilio']
