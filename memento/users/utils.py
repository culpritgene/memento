import os
import secrets

import numpy as np
from PIL import Image
from flask import current_app as app
from loguru import logger

from config import config
from memento.models.models import Lifeline


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    logger.info('Saving picture to static/profile_pics/ under the name {}.'.format(picture_fn))

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def initial_lifeline_matrix(text_type=False):
    conf = config['default']
    lifeline_size = (conf.LIFESPAN, 12, 6, 8)
    if not text_type:
        logger.info('Creating template lifeline with numeric type of size:{}'.format(lifeline_size))
        logger.warning('Lifeline is added with non-zero entries for testing purposes!')
        return np.random.choice([0, 1], p=[0.9, 0.1], size=lifeline_size).tolist()
    else:
        logger.info("Creating template lifeline with text type of size:{} with default data: '---'".format(lifeline_size))
        return np.full(lifeline_size, fill_value='---').tolist()


def default_lifeline(user):
    lf = Lifeline(title='Main LifeLine',
                  mood=initial_lifeline_matrix(),
                  efficiency=initial_lifeline_matrix(),
                  imagination=initial_lifeline_matrix(),  ### TODO: add text
                  diary=initial_lifeline_matrix(text_type=True),
                  user=user)
    return lf

