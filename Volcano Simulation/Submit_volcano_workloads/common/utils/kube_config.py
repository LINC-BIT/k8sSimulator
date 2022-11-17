import kubernetes

from .. import consts


def load_kube_config(filename: str = consts.KUBE_CONFIG_FILENAME):
    kubernetes.config.kube_config.load_kube_config(config_file=filename)
