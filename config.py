class BaseConfig:
    DEBUG = True


class DevConfig(BaseConfig):
    NUMBER_OF_TWEETS = 100


class ProductionConfig(BaseConfig):
    DEBUG = False
    NUMBER_OF_TWEETS = 500

config_dict = {'dev': DevConfig, 'production': ProductionConfig}
