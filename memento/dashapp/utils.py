from datetime import datetime

import numpy as np
from dateutil import rrule

from config import config
from memento import db
from memento.models.models import User


def align_weekdays(dates_coord):
    i = -10
    for r in dates_coord:
        if i != r[1] and r[2] == 0:
            i = r[1]
            k = r[3] if r[3] != 0 else 7
        if r[3] < k - 1:
            r[2] += 1
    return dates_coord

def zero_stats(Z):
    Z[..., -1] = 0
    Z[...,-1,:] = 0
    return Z

def wrap_dates_by(Z, form=(4,5), split=5):
    """
        Reshapes activity matrix (lifeline) in the 3d tensor which is sliced as a cake by the year dimension.
    :param Z: activity matrix as numpy array
    :param form: tuple or list of length 2
    :param split: number years in each contigous split
    :return:
        ZZ - split numpy array
        Ys - number of splits
    """
    assert isinstance(form, (list, tuple)), print('Form should be of type list or tuple')
    assert len(form)==2, print(f'Form parameter can be list or tuple of length 2, you provided: {form}, len={len(form)}')
    Y = Z.shape[0]
    Ys = ((Y // split) + 1)
    ZZ = np.zeros([Ys*split, *form], dtype=Z.dtype)

    if len(Z.shape) == 3:
        Z = np.moveaxis(Z, (0,1,2), (0,2,1))
        ZZ[:Y, :Z.shape[1], :Z.shape[2]] = Z
    elif len(Z.shape) == 2:
        Z = Z.reshape(Y, form[0]-1, form[1]-1)
        ZZ[:Y, :Z.shape[1], :Z.shape[2]] = Z
    elif len(Z.shape) == 1:  #set(form).issubset({*Z.shape[1:], Z.shape[1] + 1, Z.shape[-1] + 1}):
        raise ValueError("Can't use on 1-d array. Use ordinary reshape numpy method. ")
    ZZ = np.split(ZZ, Ys)
    return ZZ, Ys

def get_data_from_db(current_username):
        user = db.session.query(User).filter_by(username=current_username).first()
        user_data = {entry: getattr(user.lifelines, entry) for entry in config['default'].AVAILABLE_DATAENTRIES}
        user_data['birthdate'] = user.birthdate
        user_data['liveyears'] = fetch_dates(user.birthdate) # TODO: remove hard constraint to 80 years livespan
        return user_data


def fetch_dates(birthdate):
        dates = rrule.rrule(rrule.DAILY, dtstart=datetime(year=birthdate.year, month=1, day=1),
                            until=datetime(year=birthdate.year+config['default'].LIFESPAN, month=12, day=25)) #TODO: invent a polite way to end this line
        dates = [(d.year-birthdate.year-1, d.month-1, d.day // 7, d.weekday(), d.strftime("%Y/%m/%d/%w")) for d in dates]  #d.isocalendar()[1],
        dates_coord, dates = np.array(dates)[:,:-1].astype(int), [(d, 'lifeday') for d in np.array(dates)[:,-1]]
        dates_coord = align_weekdays(dates_coord)
        dates_matrix = np.full([config['default'].LIFESPAN, 12, 6, 8, 2], fill_value='-'*12)
        dates_matrix[dates_coord[:,0], dates_coord[:,1], dates_coord[:,2], dates_coord[:,3], ...] = dates
        return dates_matrix